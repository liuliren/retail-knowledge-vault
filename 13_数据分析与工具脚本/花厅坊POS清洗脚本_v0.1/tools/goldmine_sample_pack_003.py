#!/usr/bin/env python3
"""金矿候选池 5 桶分层抽样（CODEX-Goldmine-Sample-Pack-003）.

只读 dry-run 结果(scope版),对 goldmine_candidate=True 按 A/B/C/D/E 五桶分层抽样(≤60),
横切标记毛利率>0.85 成本复核。写 gitignored review/。脱敏 SKU id,不出货号/进价/真实条码。
桶口径=Review-003(六哥临时认可,非方法论规则);不出正式明细/不写回/不改§3.1.x。
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
    g["sku_display_id"] = g["货号"].map(sid)
    qty = pd.to_numeric(g["销量"], errors="coerce")
    age = pd.to_numeric(g["库龄天数"], errors="coerce")
    inv = pd.to_numeric(g.get("库存成本金额"), errors="coerce")
    rate = pd.to_numeric(g["毛利率"], errors="coerce")
    oir = g["old_inventory_risk"].fillna(False).astype(bool)
    p75 = inv.quantile(0.75)

    # 桶判据(优先级·复刻 Review-003)
    fast = qty >= 12
    high_inv = inv >= p75
    very_old = age > 365
    bucket = pd.Series("E_人工复核", index=g.index, dtype="object")
    bucket[oir & ~fast & ~high_inv & very_old] = "D_清库"
    bucket[oir & ~fast & high_inv] = "C_缩面"
    bucket[oir & fast] = "B_控补货"
    bucket[~oir] = "A_保留"
    g["处置桶"] = bucket
    g["成本复核横切"] = (rate > 0.85)

    print("[全池5桶分布]")
    for k, v in g["处置桶"].value_counts().items():
        print(f"  {k}: {v}")
    print(f"  成本复核横切(毛利率>0.85)全池={int(g['成本复核横切'].sum())}")

    # 分层抽样 ≤60：A8/B15/C10/D15/E10(不足取全)
    quota = {"A_保留": 8, "B_控补货": 15, "C_缩面": 10, "D_清库": 15, "E_人工复核": 6}
    picks = []
    for b, q in quota.items():
        sub = g[g["处置桶"] == b].head(q)
        picks.append(sub)
    pack = pd.concat(picks, ignore_index=True)
    # 强制纳入成本复核横切样本(毛利率>0.85),去重,保 ≤60
    cr = g[g["成本复核横切"] == True]
    cr = cr[~cr["sku_display_id"].isin(pack["sku_display_id"])]
    pack = pd.concat([pack, cr], ignore_index=True).drop_duplicates("sku_display_id").head(60)

    cols = ["处置桶", "成本复核横切", "sku_display_id", "品名", "类别名称", "身份",
            "毛利率", "gross_margin_rate_tier", "销量", "销售额", "库存数量", "库存成本金额",
            "库龄天数", "old_inventory_risk", "goldmine_reason"]
    cols = [c for c in cols if c in pack.columns]
    pack = pack[cols]
    pack["人工判断"] = ""
    pack["建议动作"] = ""
    pack["人工备注"] = ""

    outdir = procdir / "review"; outdir.mkdir(parents=True, exist_ok=True)
    out = outdir / "花厅坊_90天_goldmine_5桶分层抽样_v0.3.xlsx"
    pack.to_excel(out, index=False)

    print(f"\n[抽样] 总={len(pack)}(≤60) 唯一={pack['sku_display_id'].nunique()}")
    print("[各桶抽样数]")
    for k, v in pack["处置桶"].value_counts().items():
        print(f"  {k}: {v}")
    print(f"  含成本复核横切={int((pack['成本复核横切']==True).sum())}")
    print(f"[输出] {out.name}（gitignored review/）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
