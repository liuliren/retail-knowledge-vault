#!/usr/bin/env python3
"""B 桶(控补货)完整明细（CODEX-Goldmine-Bucket-B-Detail-001）.

只读 scope dry-run 结果,取 goldmine_candidate=True 且 B桶(老库存+90天销量≥12),
出完整明细到 gitignored review/。脱敏 SKU id,无货号/进价/真实条码。
含控补货信号(预计可售天数→偏紧补/充足控量)。非正式裁决·不写回·不改§3.1.x。
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
    oir = g["old_inventory_risk"].fillna(False).astype(bool)
    b = g[oir & (qty >= 12)].copy()  # B 桶口径(Review-003·六哥确认)
    b["sku_display_id"] = b["货号"].map(sid)

    # 控补货信号:预计可售天数 = 库存数量 / 日均销量
    inv_qty = pd.to_numeric(b["库存数量"], errors="coerce")
    daily = pd.to_numeric(b.get("日均销量"), errors="coerce")
    days_cover = (inv_qty / daily).where(daily > 0)
    b["预计可售天数"] = days_cover.round(1)

    def signal(d):
        if pd.isna(d):
            return "缺日均销量·需现场判"
        if d < 14:
            return "库存偏紧·适量补(防断货)"
        if d <= 45:
            return "健康·小批勤补维持"
        return "可售天数偏长·控量勤补(防再积压)"
    b["控补货建议"] = b["预计可售天数"].map(signal)

    cols = ["sku_display_id", "品名", "类别名称", "身份", "毛利率", "gross_margin_rate_tier",
            "销量", "日均销量", "库存数量", "预计可售天数", "库龄天数", "库存成本金额",
            "old_inventory_risk", "控补货建议", "goldmine_reason"]
    cols = [c for c in cols if c in b.columns]
    out_df = b[cols].copy()
    out_df["人工确认"] = ""
    out_df["实际补货策略"] = ""
    out_df["备注"] = ""

    outdir = procdir / "review"; outdir.mkdir(parents=True, exist_ok=True)
    out = outdir / "花厅坊_90天_B控补货_完整明细_v0.1.xlsx"
    out_df.to_excel(out, index=False)

    print(f"[B控补货完整明细] 行数={len(out_df)} 唯一={out_df['sku_display_id'].nunique()} 覆盖小类={b['类别名称'].nunique()}")
    print("[控补货建议分布]")
    for k, v in b["控补货建议"].value_counts().items():
        print(f"  {k}: {v}")
    dd = pd.to_numeric(b["预计可售天数"], errors="coerce")
    print(f"[预计可售天数] 中位={dd.median():.0f} 可算={dd.notna().sum()}/{len(b)}")
    print(f"[输出] {out.name}（gitignored review/，不入 git）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
