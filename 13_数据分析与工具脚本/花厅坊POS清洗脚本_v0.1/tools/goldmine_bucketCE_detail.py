#!/usr/bin/env python3
"""C 缩面 + E 人工复核 完整明细（CODEX-Goldmine-Bucket-CE-Detail-001）.

只读 scope dry-run 结果,取 goldmine_candidate=True 的 C/E 桶,分别出完整明细到 gitignored review/。
脱敏 SKU id,无货号/进价/真实条码。桶判据=Review-003 优先级(A>B>C>D>E)。
非正式裁决·不写回·不改§3.1.x。
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


COMMON = ["sku_display_id", "品名", "类别名称", "身份", "毛利率", "gross_margin_rate_tier",
          "销量", "日均销量", "库存数量", "库龄天数", "库存成本金额",
          "old_inventory_risk", "goldmine_reason"]


def finalize(sub: pd.DataFrame, advice_col: str, advice: pd.Series, extra: list, name: str, outdir: Path):
    sub = sub.copy()
    sub["sku_display_id"] = sub["货号"].map(sid)
    sub[advice_col] = advice.values
    cols = ["sku_display_id", "品名", "类别名称", "身份", "毛利率", "gross_margin_rate_tier",
            "销量", "日均销量", "库存数量"] + extra + ["库龄天数", "库存成本金额",
            "old_inventory_risk", advice_col, "goldmine_reason"]
    cols = [c for c in cols if c in sub.columns]
    out_df = sub[cols].copy()
    out_df["人工确认"] = ""
    out_df["实际处置策略"] = ""
    out_df["备注"] = ""
    out = outdir / name
    out_df.to_excel(out, index=False)
    return out, sub


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
    daily = pd.to_numeric(g.get("日均销量"), errors="coerce")
    oir = g["old_inventory_risk"].fillna(False).astype(bool)
    p75 = inv.quantile(0.75)
    fast = qty >= 12
    high_inv = inv >= p75
    very_old = age > 365
    outdir = procdir / "review"; outdir.mkdir(parents=True, exist_ok=True)

    # ── C 缩面：oir & 非快销 & 库存金额≥P75 ──
    c = g[oir & ~fast & high_inv].copy()
    cdays = (pd.to_numeric(c["库存数量"], errors="coerce") / pd.to_numeric(c["日均销量"], errors="coerce")).where(pd.to_numeric(c["日均销量"], errors="coerce") > 0).round(1)
    c["预计可售天数"] = cdays
    cinv = pd.to_numeric(c["库存成本金额"], errors="coerce"); cinvmed = cinv.median()
    def csig(i):
        d = cdays.loc[i]; v = cinv.loc[i]
        if pd.notna(d) and d > 120:
            return "重点缩面·大幅降水位(可售>120天+占资金)"
        if pd.notna(v) and v >= cinvmed:
            return "缩面·降安全库存(金额偏高)"
        return "适度缩面观察"
    cadv = pd.Series([csig(i) for i in c.index], index=c.index)
    cout, c2 = finalize(c, "缩面建议", cadv, ["预计可售天数"], "花厅坊_90天_C缩面_完整明细_v0.1.xlsx", outdir)

    # ── E 人工复核：oir & 非快销 & 库存金额<P75 & 库龄≤365 ──
    e = g[oir & ~fast & ~high_inv & ~very_old].copy()
    eage = pd.to_numeric(e["库龄天数"], errors="coerce")
    def esig(i):
        a = eage.loc[i]
        if pd.isna(a):
            return "缺库龄·现场判"
        if a <= 180:
            return "中龄(91-180)·观察动销趋势"
        return "近一年(181-365)·关注是否转清库"
    eadv = pd.Series([esig(i) for i in e.index], index=e.index)
    eout, e2 = finalize(e, "复核提示", eadv, [], "花厅坊_90天_E人工复核_完整明细_v0.1.xlsx", outdir)

    print(f"[C缩面] 行数={len(c2)} 小类={c2['类别名称'].nunique()} 占用资金聚合≈{cinv.sum():.0f}")
    for k, v in cadv.value_counts().items():
        print(f"  {k}: {v}")
    print(f"[E人工复核] 行数={len(e2)} 小类={e2['类别名称'].nunique()} 库龄中位={eage.median():.0f}")
    for k, v in eadv.value_counts().items():
        print(f"  {k}: {v}")
    print(f"[输出] {cout.name} + {eout.name}（gitignored review/，不入 git）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
