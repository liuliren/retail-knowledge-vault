#!/usr/bin/env python3
"""金矿候选人工抽样复核包（CODEX-Goldmine-Sample-Pack-001）.

只读 gitignored dry-run 结果表，从 goldmine_candidate=True 中分层抽 80-100 条，
写抽样明细到 gitignored processed/review/。脱敏 SKU 标识(hash)，不输出货号/进价/条码真值。
不改规则/代码/不重跑/不写回。终端只打印计数（无逐 SKU 明细）。
"""
from __future__ import annotations

import argparse
import glob
import hashlib
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
    res = sorted(procdir.glob("花厅坊_90天_dryrun结果_*.xlsx"))
    if not res:
        print("BLOCKED: 无 dry-run 结果表")
        return 2
    df = pd.read_excel(res[-1])
    cand = df[df["goldmine_candidate"] == True].copy()  # noqa: E712
    cand["sku_display_id"] = cand["货号"].map(sid)
    print(f"金矿候选总数={len(cand)}")

    picks: list[pd.DataFrame] = []
    used: set[str] = set()

    def take(sub: pd.DataFrame, k: int, group: str):
        sub = sub[~sub["sku_display_id"].isin(used)].head(k).copy()
        sub["sample_group"] = group
        used.update(sub["sku_display_id"])
        picks.append(sub)

    rate = pd.to_numeric(cand["毛利率"], errors="coerce")
    inv_amt = pd.to_numeric(cand.get("库存成本金额"), errors="coerce")
    age = pd.to_numeric(cand.get("库龄天数"), errors="coerce")
    qty = pd.to_numeric(cand.get("销量"), errors="coerce")

    take(cand.assign(_r=rate).sort_values("_r", ascending=False), 20, "Top高毛利率")
    take(cand.assign(_i=inv_amt).sort_values("_i", ascending=False), 20, "高库存金额")
    take(cand.assign(_a=age).query("_a > 90").sort_values("_a", ascending=False), 20, "久未动销重滞")
    # 多小类均衡：每小类取 1，直到 30
    bal = cand[~cand["sku_display_id"].isin(used)].drop_duplicates("类别名称").head(30).copy()
    bal["sample_group"] = "多小类均衡"
    used.update(bal["sku_display_id"]); picks.append(bal)
    take(cand.assign(_q=qty).sort_values("_q", ascending=False), 10, "促销缺失风险(高销量)")

    pack = pd.concat(picks, ignore_index=True)
    cols = ["sample_group", "sku_display_id", "品名", "类别名称", "销额ABC", "毛利ABC",
            "身份", "毛利率", "gross_margin_rate_tier", "goldmine_candidate", "goldmine_reason",
            "销量", "销售额", "毛利额", "库存数量", "库存成本金额", "库龄天数", "库龄_状态",
            "ITO估算", "缺货标记", "新品标记", "促销标记"]
    cols = [c for c in cols if c in pack.columns]
    pack = pack[cols]
    pack["人工判断"] = ""
    pack["人工备注"] = ""
    pack["建议动作"] = ""

    outdir = procdir / "review"
    outdir.mkdir(parents=True, exist_ok=True)
    out = outdir / "花厅坊_90天_goldmine_candidate_人工复核抽样包_v0.1.xlsx"
    pack.to_excel(out, index=False)

    print(f"实际抽样={len(pack)} 去重后唯一={pack['sku_display_id'].nunique()}")
    print("[各层数量]")
    for g, c in pack["sample_group"].value_counts().items():
        print(f"  {g}: {c}")
    print(f"覆盖小类数={pack['类别名称'].nunique()}")
    print(f"全部来自候选={(pack['goldmine_candidate']==True).all()}")
    print(f"全部C行={(pack['销额ABC']=='C').all()}")
    print(f"含真实条码? 列='条码'在内={'条码' in pack.columns}(应False, 仅 sku_display_id hash)")
    print(f"输出={out.name}（gitignored review/）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
