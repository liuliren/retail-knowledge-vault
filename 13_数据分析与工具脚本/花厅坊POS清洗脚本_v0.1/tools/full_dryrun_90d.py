#!/usr/bin/env python3
"""花厅坊 90 天脱敏合并表 full dry-run（CODEX-Full-DryRun-Execute-001）.

只读脱敏合并表（gitignored processed/），跑 ABC 九宫格 + IR + 安全库存，
输出 dry-run 结果到 gitignored processed/，打印纯统计摘要（无逐 SKU 明细/无敏感值）。
不读原始 xls、不写回真实数据、不出正式裁决。
"""
from __future__ import annotations

import argparse
import glob
import os
from pathlib import Path

import pandas as pd

from abc_classifier import (
    apply_abc, assign_gross_margin_rate_tier, assign_goldmine,
    assign_cost_reliable, assign_recently_sold, assign_old_inventory_risk,
    assign_data_quality_scope, assign_exclusion_pool,
)
from ir_calculator import apply_ir
from safety_stock import apply_safety_stock


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault", default=".")
    ap.add_argument("--proc", default="09_门店案例与项目复盘/乐易购花厅坊店/99_原始素材/01_门店数据材料/processed")
    args = ap.parse_args()
    procdir = Path(args.vault).resolve() / args.proc
    cands = list(procdir.glob("花厅坊_90天全量合并_脱敏_*.xlsx"))
    if not cands:
        print("BLOCKED: 未找到脱敏合并表")
        return 2
    src = max(cands, key=os.path.getmtime)  # 取最新（剔生鲜版）
    df = pd.read_excel(src)
    n = len(df)
    print(f"=== DRY-RUN (无敏感值) 输入={src.name} 行数={n} ===")

    # 1. ABC 九宫格（口径 §3.1 active；列名适配：销售额/毛利额）
    df = apply_abc(df, sales_col="销售额", profit_col="毛利额")

    # 1b. §3.1.1 毛利率分层 + §3.1.2 成本/动销闸 + §3.1.3 数据质量范围筛选（不改 9 格标签）
    df["gross_margin_rate_tier"] = assign_gross_margin_rate_tier(df, rate_col="毛利率", cat_col="类别名称")
    df["cost_reliable"] = assign_cost_reliable(df)
    df["recently_sold"] = assign_recently_sold(df)           # Fix-002 销量优先
    df["old_inventory_risk"] = assign_old_inventory_risk(df)  # Fix-002 库龄>90 风险标签(不排除金矿)
    scope_status, scope_reason = assign_data_quality_scope(df)  # 读 client_excluded + cost_reliable
    df["data_quality_scope_status"] = scope_status
    df["data_quality_scope_reason"] = scope_reason
    df["client_specific_exclusion"] = df.get("client_excluded", False)
    gm_cand, gm_reason = assign_goldmine(df)
    df["goldmine_candidate"] = gm_cand
    df["goldmine_reason"] = gm_reason
    df["exclusion_pool"] = assign_exclusion_pool(df)
    df["cost_missing_review_pool"] = df["exclusion_pool"].eq("cost_missing")
    df["dead_stock_review_pool"] = df["exclusion_pool"].eq("dead_stock")

    # 2. IR（毛利率 × ITO估算）
    df, ir_meta = apply_ir(df, margin_col="毛利率", ito_col="ITO估算")

    # 3. 安全库存 / 库龄（库存数量 / 库龄天数 / 销额ABC）
    df, ss_meta = apply_safety_stock(
        df, daily_sales_col="日均销量", inventory_col="库存数量",
        abc_col="销额ABC", age_col="库龄天数",
    )

    # ── 纯统计摘要（不出逐 SKU） ──
    print("\n[9格身份分布]")
    for k, v in df["身份"].value_counts().items():
        print(f"  {k}: {v} ({v/n*100:.1f}%)")
    inval = int((df["身份"] == "invalid_combination").sum())
    print(f"  invalid_combination={inval}（应为0）")

    print("\n[销额ABC分布]")
    for k, v in df["销额ABC"].value_counts().items():
        print(f"  {k}: {v}")
    print("[毛利ABC分布]")
    for k, v in df["毛利ABC"].value_counts().items():
        print(f"  {k}: {v}")

    nr = int(df["需复核"].fillna(False).astype(bool).sum())
    print(f"\n[需复核(C+乙)]={nr} ({nr/n*100:.1f}%)")
    print(f"[观察品出现]={int((df['身份']=='观察品').sum())}（应为0，已废止）")

    # §3.1.1 金矿候选分布
    print("\n[毛利率分层 gross_margin_rate_tier]")
    for k, v in df["gross_margin_rate_tier"].value_counts().items():
        print(f"  {k}: {v} ({v/n*100:.1f}%)")
    # §3.1.3 数据质量范围 + §3.1.2 池
    print("\n[数据质量范围 data_quality_scope_status]")
    for k, v in df["data_quality_scope_status"].value_counts().items():
        print(f"  {k}: {v} ({v/n*100:.1f}%)")
    elig = int((df["data_quality_scope_status"] == "eligible").sum())
    nc = int((df["销额ABC"] == "C").sum())
    nc_elig = int(((df["销额ABC"] == "C") & (df["data_quality_scope_status"] == "eligible")).sum())
    gm = int(df["goldmine_candidate"].sum())
    print(f"\n[金矿候选 goldmine_candidate]={gm}  占eligible-C行={gm/max(nc_elig,1)*100:.1f}% (eligible-C={nc_elig}/C={nc})")
    print("[复核池 exclusion_pool]")
    for k, v in df["exclusion_pool"].value_counts().items():
        print(f"  {k}: {v}")
    print(f"  cost_missing_review_pool={int(df['cost_missing_review_pool'].sum())}  dead_stock_review_pool={int(df['dead_stock_review_pool'].sum())}  client_specific_excluded={int((df['exclusion_pool']=='client_specific_excluded').sum())}")

    # Fix-002 老库存风险 + 金矿拆分
    oir = int(df["old_inventory_risk"].sum())
    rs = int(df["recently_sold"].sum())
    gm_oir = int((df["goldmine_candidate"] & df["old_inventory_risk"]).sum())
    gm_new = gm - gm_oir
    print(f"\n[Fix-002] recently_sold(销量≥4)={rs}  old_inventory_risk(库龄>90)={oir}")
    print(f"  金矿候选={gm}  其中老库存风险={gm_oir}  新货={gm_new}")

    # 阶段对比
    print("\n[阶段对比]")
    print("  初始P75: 金矿1686/dead_stock— /数据异常35%")
    print("  Fix-001(销量≥4且库龄≤90): 金矿16/dead_stock8089/cost_missing825/client_excluded808")
    print(f"  Fix-002(销量优先+库龄转风险): 金矿{gm}(老库存{gm_oir}/新货{gm_new})/dead_stock{int(df['dead_stock_review_pool'].sum())}/cost_missing{int(df['cost_missing_review_pool'].sum())}/client_excluded{int((df['exclusion_pool']=='client_specific_excluded').sum())}/old_inv_risk{oir}")

    # IR 覆盖
    ir_ok = int(pd.to_numeric(df.get("IR"), errors="coerce").notna().sum()) if "IR" in df else 0
    print(f"\n[IR可算]={ir_ok}/{n} ({ir_ok/n*100:.1f}%) status={ir_meta.get('status')}")

    # 安全库存 / 库龄
    if "库龄级" in df:
        print("[库龄级分布]")
        for k, v in df["库龄级"].value_counts().items():
            print(f"  {k}: {v}")
    if "补货信号" in df:
        print("[补货信号分布]")
        for k, v in df["补货信号"].value_counts().items():
            print(f"  {k}: {v}")
    print(f"[安全库存meta] age={ss_meta.get('age_status')} cov={ss_meta.get('safety_stock_coverage')}")

    # blocked / 降级 汇总
    print("\n[blocked/降级]")
    print(f"  ITO blocked={int((pd.to_numeric(df.get('ITO估算'),errors='coerce').isna()).sum())}/{n}")
    print(f"  库龄 blocked={int((df.get('库龄_状态')=='blocked_缺库龄').sum()) if '库龄_状态' in df else 'NA'}")
    print(f"  促销=unavailable（全表无促销字段）")
    print(f"  负毛利样本={int(df.get('负毛利清仓标记').sum()) if '负毛利清仓标记' in df else 'NA'}（POS汇总层实情）")

    # 红线自检：条码全脱敏
    bc_ok = bool((df["条码脱敏"] == "{{EAN13_已脱敏}}").all()) if "条码脱敏" in df else False
    print(f"\n[红线] 条码全脱敏={bc_ok}")

    # 输出 dry-run 结果（gitignored）——含内部进价列，仅本地
    out = procdir / f"花厅坊_90天_dryrun结果_scope_v0.3_{src.stem.split('_')[-1]}.xlsx"
    df.to_excel(out, index=False)
    print(f"\n[输出] {out.name}（gitignored，不入 git）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
