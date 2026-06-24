#!/usr/bin/env python3
"""金矿候选抽样包·机器预判草稿（CODEX-Goldmine-Sample-Pack-001 辅助）.

只读 gitignored 抽样包，按规则给每行预填「人工判断(机器建议)」+理由，
写回 gitignored review/ 的 _机器预判 版。机器只出草稿，最终判定以六哥为准。
不改规则/代码/不重跑/不写回。终端只打印计数。
"""
from __future__ import annotations

import argparse
import glob
from pathlib import Path

import pandas as pd


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault", default=".")
    ap.add_argument("--proc", default="09_门店案例与项目复盘/乐易购花厅坊店/99_原始素材/01_门店数据材料/processed")
    args = ap.parse_args()
    rev = Path(args.vault).resolve() / args.proc / "review"
    src = list(rev.glob("花厅坊_90天_goldmine_candidate_人工复核抽样包_*.xlsx"))
    src = [p for p in src if "机器预判" not in p.name]
    if not src:
        print("BLOCKED: 无抽样包")
        return 2
    import os
    df = pd.read_excel(max(src, key=os.path.getmtime))  # 取最新（剔生鲜版）
    n = len(df)

    rate = pd.to_numeric(df.get("毛利率"), errors="coerce")
    qty = pd.to_numeric(df.get("销量"), errors="coerce")
    age = pd.to_numeric(df.get("库龄天数"), errors="coerce")
    inv_amt = pd.to_numeric(df.get("库存成本金额"), errors="coerce")
    grp = df.get("sample_group", pd.Series("", index=df.index)).astype(str)
    inv_p75 = inv_amt.quantile(0.75)

    sug = pd.Series("需现场看陈列", index=df.index, dtype="object")
    rsn = pd.Series("数据正常但难判，建议到货架前看", index=df.index, dtype="object")

    # 优先级从高到低（后写覆盖→倒序写）
    # 5 真金矿（兜底正向）
    good = (rate > 0) & (rate <= 0.8) & (qty > 3) & (age <= 90)
    sug[good] = "真金矿"; rsn[good] = "毛利率合理偏高+近期有动销+库龄不老"
    # 4 促销污染（促销风险层）
    promo = grp.str.contains("促销")
    sug[promo] = "伪金矿-促销污染"; rsn[promo] = "高销量层+促销字段缺失，疑促销/临时价抬高毛利率"
    # 3 高库存风险
    highinv = inv_amt >= inv_p75
    sug[highinv] = "伪金矿-高库存风险"; rsn[highinv] = f"库存金额≥抽样P75({inv_p75:.0f})，占资金"
    # 2 死货（重滞+极低销）
    dead = (age > 90) & (qty <= 3)
    sug[dead] = "伪金矿-死货"; rsn[dead] = "库龄>90重滞+90天销量≤3，疑死货"
    # 1 数据异常（最高优先）
    anom = rate.isna() | (rate <= 0) | (rate > 0.8)
    sug[anom] = "伪金矿-数据异常"; rsn[anom] = "毛利率缺失/≤0/>80%，疑数据异常"

    df["人工判断(机器建议)"] = sug
    df["机器建议理由"] = rsn
    # 保留人工最终列（覆盖机器建议用）
    if "人工判断" not in df.columns:
        df["人工判断"] = ""

    out = rev / "花厅坊_90天_goldmine_candidate_人工复核抽样包_机器预判_剔生鲜_v0.2.xlsx"
    df.to_excel(out, index=False)

    print(f"抽样行数={n}")
    print("[机器预判分布]")
    for k, v in df["人工判断(机器建议)"].value_counts().items():
        print(f"  {k}: {v} ({v/n*100:.0f}%)")
    real = int((df["人工判断(机器建议)"] == "真金矿").sum())
    print(f"\n[预判真金矿]={real}/{n} ({real/n*100:.0f}%)  → 若人工大体认可则可不上P85；伪金矿多则上P85+动销")
    print(f"[输出]={out.name}（gitignored review/）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
