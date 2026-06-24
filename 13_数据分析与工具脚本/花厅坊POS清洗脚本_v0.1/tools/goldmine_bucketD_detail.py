#!/usr/bin/env python3
"""D 桶(清库)完整明细（CODEX-Goldmine-Bucket-D-Detail-001）.

只读 scope dry-run 结果,取 goldmine_candidate=True 且 D桶(老库存+库龄>365+非快销+非高库存金额),
出完整明细到 gitignored review/。脱敏 SKU id,无货号/进价/真实条码。
含清库信号(库龄+库存金额→清库力度)。非正式裁决·不写回·不改§3.1.x。
桶判据=Review-003优先级(A新货>B老&销量≥12>C老&库存金额≥P75非快销>D老&库龄>365非快销非高金额>E)。
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import os
from pathlib import Path

import pandas as pd


def sid(v) -> str:
    return "SKU_" + hashlib.sha1(str(v).encode("utf-8")).hexdigest()[:8]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault", default=".")
    ap.add_argument("--proc", default="09_门店案例与项目复盘/乐易购花厅坊店/99_原始素材/01_门店数据材料/processed")
    args = ap.parse_args()
    procdir = Path(args.vault).resolve() / args.proc
    res = [p for p in procdir.glob("花厅坊_90天_dryrun结果_scope_*.xlsx")]
    if not res:
        print("BLOCKED: 无 scope dry-run 结果"); return 2
    df = pd.read_excel(max(res, key=os.path.getmtime))
    g = df[df["goldmine_candidate"] == True].copy()  # noqa: E712
    qty = pd.to_numeric(g["销量"], errors="coerce")
    age = pd.to_numeric(g["库龄天数"], errors="coerce")
    inv = pd.to_numeric(g.get("库存成本金额"), errors="coerce")
    oir = g["old_inventory_risk"].fillna(False).astype(bool)
    p75 = inv.quantile(0.75)  # 与 Sample-Pack-003 同口径(候选池 P75)

    fast = qty >= 12
    high_inv = inv >= p75
    very_old = age > 365
    # D 桶(优先级后于 A/B/C)
    d = g[oir & ~fast & ~high_inv & very_old].copy()
    d["sku_display_id"] = d["货号"].map(sid)

    di = pd.to_numeric(d["库存成本金额"], errors="coerce")
    da = pd.to_numeric(d["库龄天数"], errors="coerce")
    # 清库信号:库龄越老 + 库存金额相对高 → 力度越大
    dimed = di.median()

    def signal(row):
        a = row["_age"]; v = row["_inv"]
        if pd.isna(a):
            return "缺库龄·现场判"
        if a > 540 and v >= dimed:
            return "重点清库(>1.5年+占资金)·促销/打包"
        if a > 540:
            return "优先清库(>1.5年)·轻促/汰换"
        if v >= dimed:
            return "清库(>1年+金额偏高)·促销"
        return "自然汰换/轻促(>1年金额低)"
    d["_age"] = da; d["_inv"] = di
    d["清库建议"] = d.apply(signal, axis=1)
    d = d.drop(columns=["_age", "_inv"])

    cols = ["sku_display_id", "品名", "类别名称", "身份", "毛利率", "gross_margin_rate_tier",
            "销量", "日均销量", "库存数量", "库龄天数", "库存成本金额",
            "old_inventory_risk", "清库建议", "goldmine_reason"]
    cols = [c for c in cols if c in d.columns]
    out_df = d[cols].copy()
    out_df["人工确认"] = ""
    out_df["实际清库策略"] = ""
    out_df["备注"] = ""

    outdir = procdir / "review"; outdir.mkdir(parents=True, exist_ok=True)
    out = outdir / "花厅坊_90天_D清库_完整明细_v0.1.xlsx"
    out_df.to_excel(out, index=False)

    print(f"[D清库完整明细] 行数={len(out_df)} 唯一={out_df['sku_display_id'].nunique()} 覆盖小类={d['类别名称'].nunique()}")
    print("[清库建议分布]")
    for k, v in d["清库建议"].value_counts().items():
        print(f"  {k}: {v}")
    print(f"[库龄] 中位={da.median():.0f} 最大={da.max():.0f}")
    print(f"[库存成本金额] 中位={di.median():.0f} 合计(占资金,聚合)={di.sum():.0f}")
    print(f"[输出] {out.name}（gitignored review/，不入 git）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
