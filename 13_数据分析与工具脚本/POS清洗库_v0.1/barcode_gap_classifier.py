#!/usr/bin/env python3
"""条码缺口分类器 v0.1 — 销售出现但档案(库存注册表)查不到的条码,做成因分类(不做汰换判断)。

血统: 2026-07-07《门店类别对照与条码匹配方案_v0.1》§3(顺景 498 缺口三假说方案)——
  本脚本是把方案里已定义好的四条确定性判据(J1码长前缀/J2称重柜组/J3外租柜组白名单/
  J4 EAN校验位+销售日期分布)脚本化落地,判据本身不在本文件重新设计。

三类假说(MECE,一码一归属,判定顺序 = J1/J2→H1; 残差过J3→H2; 残差过J4→H3):
  H1 散称/称重码  — 称重柜组内店内自编码(码长≤8 或 13位且前缀落20-29区间),
                    库存档案只存母码、销售流水是称重子码 → 永不匹配
  H2 外租区特殊编码 — 联营/外租柜组走门店POS收银但不入门店库存档案
  H3 真实档案缺失   — 已删档(H0口径亚型)/未建档/借码,按EAN校验位+销售日期分布再细分

护城河边界: 本脚本只做"这是什么类型的缺口"分类归因,不做"留/汰"决策——
  H2/H3 的口径修正与档案治理动作仍需六哥现场核实签字(方案 §5)。

用法:
  python3 barcode_gap_classifier.py <master.csv> <registry.csv> --store 顺景 [--out <path>]

输入: hjy_sales_90d_master_v0.1.csv(分店,日期,柜组,条码,品名,...) +
      hjy_inventory_registry_v0.1.csv(分店,货号,条码,品名规格,...) —— 只读聚合件,不读raw。
输出: 条码级分类csv(条码/分类H1-H3/置信度/判据依据 + 审计辅助列) + 汇总统计打印到stdout。
"""
import argparse
import os
import sys

import pandas as pd

# ── 判据常量(方案 §3 J1-J4,称重柜组/外租候选柜组均为通用柜组品类名,非客户机密) ──
WEIGHING_COUNTERS = {
    "散装柜", "叶菜柜", "猪肉柜", "水产柜", "海产品柜",
    "散五谷杂粮柜", "水果柜", "熟食专柜", "冻品柜",
}
NONFOOD_LEASE_COUNTERS = {
    "家居用品柜", "内衣/袜柜", "文体柜", "家电柜",
    "家居纸品柜", "床上用品柜", "厨房用品柜",
}
J1_PREFIX_LO, J1_PREFIX_HI = 20, 29   # 国标店内自编码惯例前缀区间(13位码)
J1_SHORT_LEN = 8                       # 码长<=此值判为短自编码候选
J4_EDGE_DAYS = 15                       # J4首末销日期落在窗口边缘的判定天数


def ean13_valid(code: str) -> bool:
    """EAN-13 校验位算法: 偶数位(0-index)权1,奇数位权3,对10取补 == 第13位。"""
    if not (isinstance(code, str) and code.isdigit() and len(code) == 13):
        return False
    digits = [int(c) for c in code]
    body, check = digits[:12], digits[12]
    total = sum(d if i % 2 == 0 else d * 3 for i, d in enumerate(body))
    return (10 - total % 10) % 10 == check


def j1_structural_hit(code: str) -> bool:
    """J1: 码长<=8 的短自编码,或13位且前2位前缀落20-29区间 → H1结构候选。仅对纯数字码判定,非数字内容(如中文/字母混杂)一律不命中。"""
    if not code.isdigit():
        return False
    n = len(code)
    if n <= J1_SHORT_LEN:
        return True
    if n == 13 and J1_PREFIX_LO <= int(code[:2]) <= J1_PREFIX_HI:
        return True
    return False


def load_store_frames(master_path: str, registry_path: str, store: str):
    """读两个聚合csv,按--store子串过滤分店(如"顺景"匹配"顺景店")。"""
    sales = pd.read_csv(master_path, dtype=str)
    registry = pd.read_csv(registry_path, dtype=str)
    sales.columns = [c.strip("﻿") for c in sales.columns]
    registry.columns = [c.strip("﻿") for c in registry.columns]
    s = sales[sales["分店"].str.contains(store, na=False)].copy()
    r = registry[registry["分店"].str.contains(store, na=False)].copy()
    if s.empty:
        sys.exit(f"未匹配到分店含'{store}'的销售记录,请检查 --store 值")
    s["日期"] = pd.to_datetime(s["日期"], errors="coerce")
    return s, r


def counter_coverage(sales_df: pd.DataFrame, registry_codes: set) -> pd.Series:
    """各柜组"在册覆盖率" = 柜组内(在master中出现的)条码 命中registry的比例。
    用于J3辅证:覆盖率显著低于全店均值的柜组,支持"该柜组倒挂/外租未入档"假说。"""
    def cov(g):
        codes = set(g["条码"])
        if not codes:
            return float("nan")
        return len(codes & registry_codes) / len(codes)
    return sales_df.groupby("柜组").apply(cov, include_groups=False)


def classify_gaps(sales_df: pd.DataFrame, registry_df: pd.DataFrame) -> pd.DataFrame:
    """核心分类流程: 对(销售出现但registry查不到)的每个条码跑J1→J3→J4,MECE归类。"""
    registry_codes = set(registry_df["条码"])
    sales_codes = set(sales_df["条码"])
    missing = sorted(sales_codes - registry_codes)
    if not missing:
        return pd.DataFrame(columns=[
            "条码", "分类", "置信度", "判据依据", "子类型", "码长", "前缀",
            "主要柜组", "销售笔数", "首销日期", "末销日期",
        ])

    cov_by_counter = counter_coverage(sales_df, registry_codes)
    overall_cov = len(sales_codes & registry_codes) / len(sales_codes) if sales_codes else 0.0

    window_start = sales_df["日期"].min()
    window_end = sales_df["日期"].max()
    late_th = window_end - pd.Timedelta(days=J4_EDGE_DAYS)
    early_th = window_start + pd.Timedelta(days=J4_EDGE_DAYS)

    sub = sales_df[sales_df["条码"].isin(missing)]
    grouped = sub.groupby("条码")

    rows = []
    for code, g in grouped:
        n = len(code)
        prefix = code[:2] if code[:2].isdigit() else ""
        dominant_counter = g["柜组"].mode().iat[0] if not g["柜组"].mode().empty else ""
        sales_count = len(g)
        first_date = g["日期"].min()
        last_date = g["日期"].max()

        # ── J1/J2: 散称/称重码判定 ──
        if j1_structural_hit(code):
            if dominant_counter in WEIGHING_COUNTERS:
                cat, conf, subtype = "H1", "high", "称重母码-柜组吻合"
                basis = f"J1结构(码长{n}/前缀{prefix})+J2柜组({dominant_counter}∈称重柜组)"
            else:
                cat, conf, subtype = "H1", "medium", "结构吻合但柜组证据弱"
                basis = f"J1结构(码长{n}/前缀{prefix})命中,J2柜组({dominant_counter or '未知'})未落称重区——证据弱"

        # ── J3: 外租区特殊编码判定 ──
        elif dominant_counter in NONFOOD_LEASE_COUNTERS:
            c_cov = cov_by_counter.get(dominant_counter, float("nan"))
            if pd.notna(c_cov) and c_cov < overall_cov:
                cat, conf, subtype = "H2", "high", "外租候选柜组+覆盖率倒挂"
                basis = (f"J3柜组白名单({dominant_counter})命中,该柜组在册覆盖率"
                         f"{c_cov:.1%}<全店均值{overall_cov:.1%}(动销/在册倒挂)")
            else:
                cat, conf, subtype = "H2", "medium", "外租候选柜组但倒挂特征弱"
                basis = (f"J3柜组白名单({dominant_counter})命中,但该柜组覆盖率"
                         f"{'NA' if pd.isna(c_cov) else f'{c_cov:.1%}'}未显著低于均值{overall_cov:.1%}——证据弱")

        # ── J4: 残差(真实档案缺失)细分 ──
        else:
            valid = ean13_valid(code)
            if valid and pd.notna(first_date) and first_date >= late_th:
                cat, conf, subtype = "H3", "medium", "疑似新品未及时建档"
            elif valid and pd.notna(last_date) and last_date <= early_th:
                cat, conf, subtype = "H3", "high", "疑似已清档(H0口径-窗口内清档)"
            elif valid and sales_count <= 2:
                cat, conf, subtype = "H3", "medium", "疑似借码/万能码(极低频)"
            elif valid:
                cat, conf, subtype = "H3", "medium", "真实档案缺失-待人工复核"
            else:
                cat, conf, subtype = "H3", "low", "非标准EAN校验未通过-证据弱"
            basis = (f"J4残差判(EAN合法={valid},首销{_fmt(first_date)},末销{_fmt(last_date)},"
                     f"窗口{_fmt(window_start)}~{_fmt(window_end)}) → {subtype}")

        rows.append({
            "条码": code, "分类": cat, "置信度": conf, "判据依据": basis, "子类型": subtype,
            "码长": n, "前缀": prefix, "主要柜组": dominant_counter,
            "销售笔数": sales_count, "首销日期": _fmt(first_date), "末销日期": _fmt(last_date),
        })
    return pd.DataFrame(rows)


def _fmt(ts) -> str:
    return "" if pd.isna(ts) else ts.strftime("%Y-%m-%d")


def print_summary(df: pd.DataFrame, store: str):
    total = len(df)
    print(f"\n=== {store} 条码缺口分类汇总(共 {total} 个未匹配条码) ===")
    if total == 0:
        print("无未匹配条码。")
        return
    by_cat = df["分类"].value_counts()
    for cat in ("H1", "H2", "H3"):
        n = int(by_cat.get(cat, 0))
        pct = n / total * 100
        conf_mix = df[df["分类"] == cat]["置信度"].value_counts().to_dict()
        print(f"  {cat}: {n:4d} 个 ({pct:5.1f}%)  置信度分布={conf_mix}")
    print("\n  子类型细分:")
    for subtype, n in df["子类型"].value_counts().items():
        print(f"    {subtype}: {n} ({n/total*100:.1f}%)")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("master", help="销售90天master csv路径(如 hjy_sales_90d_master_v0.1.csv)")
    p.add_argument("registry", help="库存/档案注册表 csv路径(如 hjy_inventory_registry_v0.1.csv)")
    p.add_argument("--store", required=True, help="分店名子串,如 顺景 (匹配'顺景店')")
    p.add_argument("--out", default=None, help="分类结果csv落盘路径;默认落在registry同目录下(已gitignored)")
    a = p.parse_args()

    sales_df, registry_df = load_store_frames(a.master, a.registry, a.store)
    result = classify_gaps(sales_df, registry_df)

    out_path = a.out or os.path.join(
        os.path.dirname(os.path.abspath(a.registry)),
        f"barcode_gap_classification_{a.store}.csv",
    )
    result.to_csv(out_path, index=False)
    print(f"分类明细({len(result)}行) → {out_path}")
    print_summary(result, a.store)


if __name__ == "__main__":
    main()
