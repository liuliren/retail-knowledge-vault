#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
selftest_huachangfang.py — retail_clean 自测 (花厅坊·方便食品).

验证目标: 与六哥库存订货样板 run_inv.py 结果一致 —— 52 款有效 SKU、0 负库存.
路径用花厅坊原始素材 (D 层 raw_sensitive, 只读). 本脚本只打印聚合统计,
条码做掩码 (仅尾 4 位), 不打印进价裸值、不写客户明细 CSV → 不堆 context、不入 git.

跑法: cd 到 vault 根目录后  python3 13_.../数据清洗匹配_v0.1/selftest_huachangfang.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import retail_clean as rc  # noqa: E402

BASE = ("09_门店案例与项目复盘/乐易购花厅坊店/99_原始素材/01_门店数据材料/")
INV_FILE = BASE + "库存积压报表_方便食品_20260508.xls"
SALES_FILE = BASE + "方便食品_花厅坊商品明细_20260311-0612.xls"
ARCHIVE_FILE = BASE + "20260510_联营商品档案表.xls"   # 第三源(部分重叠), 演示三表 join

EXPECT_SKU = 52        # run_inv.py 基线
EXPECT_NEG_INV = 0


def mask(bc):
    """掩码条码: 只留尾 4 位 (不堆裸值进 context/日志)."""
    s = str(bc)
    return ("*" * max(0, len(s) - 4)) + s[-4:] if s else "(空)"


def main():
    if not os.path.exists(INV_FILE):
        print(f"[跳过] 找不到原始素材, 请在 vault 根目录运行. 缺: {INV_FILE}")
        return 1

    print("=" * 72)
    print("retail_clean 自测 · 花厅坊方便食品")
    print("=" * 72)

    # ── 1. 库存积压报表 (坑①②③④) ──
    inv, inv_meta = rc.clean_store_file(INV_FILE, "inventory")
    print("\n[1] 库存积压报表")
    print(f"    表头行 r{inv_meta['header_idx']}  (样板硬编码起点 r5=表头r3后第2行, 一致)")
    print(f"    定位到列: {list(inv_meta['located_cols'])}")
    print(f"    缺列: {inv_meta['missing_cols'] or '无'}")
    print(f"    原始数据行={inv_meta['raw_data_rows']}  解析后={inv_meta['parsed_rows']}  "
          f"剔除后有效={inv_meta['kept_rows']}")
    print(f"    剔除明细(数据边界声明用): {inv_meta['drop_log'] or '无'}")

    # ── 2. 销售明细 → 聚合 (坑①②③⑥) ──
    sales_rec, sales_meta = rc.clean_store_file(SALES_FILE, "sales")
    sales_agg = rc.aggregate_sales_by_barcode(sales_rec)
    print("\n[2] 商品销售明细")
    print(f"    表头行 r{sales_meta['header_idx']}  定位列: {list(sales_meta['located_cols'])}")
    print(f"    缺列: {sales_meta['missing_cols'] or '无'}")
    print(f"    明细行={sales_meta['kept_rows']}  →  聚合后唯一条码={len(sales_agg)}")

    # ── 3. 商品档案 (第三源) ──
    arc = {}
    if os.path.exists(ARCHIVE_FILE):
        arc_rec, arc_meta = rc.clean_store_file(ARCHIVE_FILE, "archive")
        arc = {r["barcode"]: r for r in arc_rec}
        print("\n[3] 商品档案表 (联营)")
        print(f"    表头行 r{arc_meta['header_idx']}  有效档案行={arc_meta['kept_rows']}")

    # ── 4. 跨文件 join (以条码主键, base=inventory) ──
    merged, stats = rc.join_by_barcode(sales=sales_agg, inventory=inv, archive=arc,
                                       base="inventory")
    print("\n[4] 跨文件匹配 (base=库存积压报表)")
    print(f"    全集SKU={stats['全集SKU数']}  "
          f"命中明细={stats['命中_sales']} (join率 {stats['join率_sales']:.0%})  "
          f"命中档案={stats['命中_archive']} (join率 {stats['join率_archive']:.0%})")
    print(f"    进价依赖字段标记: cost_reliability='仅参考' (坑⑤)")

    # ── 5. 样例统计 (掩码, 不泄裸值) ──
    neg_inv = sum(1 for r in merged if (r.get("inventory") or 0) < 0)
    have_sales = sum(1 for r in merged if r.get("sale_qty"))
    zero_inv = sum(1 for r in merged if (r.get("inventory") or 0) == 0)
    inv_total = sum(r.get("backlog_cost") or 0 for r in merged)
    print("\n[5] 样例统计")
    print(f"    有效SKU={len(merged)}  负库存={neg_inv}  当前库存=0={zero_inv}  "
          f"期间有销={have_sales}")
    print(f"    库存积压成本合计≈{inv_total:.0f}元 (仅参考·进价不准)")
    top = sorted([r for r in merged if r.get("sale_value")],
                 key=lambda x: -(x.get("sale_value") or 0))[:3]
    print("    销额TOP3(掩码):")
    for r in top:
        print(f"      {mask(r['barcode'])}  {r['name'][:14]:<14} "
              f"销{r.get('sale_qty')}  动销{r.get('active_days')}天  库存{r.get('inventory')}")

    # ── 6. v0.2 派生指标层 (ABC / 周转 / 呆滞 / 缺货) ──
    from datetime import date
    period_days = rc.compute_period_days(sales_rec, default=94)
    rc.enrich_turnover(merged, period_days, asof_date=date(2026, 5, 8),
                       stale_gap_days=30, slow_dos=90)
    rc.compute_abc(merged, value_key="period_value")
    summ = rc.summarize(merged)
    print("\n[6] 派生指标层 v0.2")
    print(f"    统计天数(明细跨度)={period_days}  (样板 run_inv PERIOD=94)")
    print(f"    ABC: {summ['ABC']}")
    print(f"    呆滞={summ['呆滞款数']}款 积压≈{summ['呆滞积压成本']:.0f}元  "
          f"慢周转(DOS>90)={summ['慢周转款数']}款  缺货疑似={summ['缺货疑似款数']}款")

    # ── 7. 端到端单入口编排 (build_dataset, skill 实际调用方式) ──
    merged2, report = rc.build_dataset(
        inventory_path=INV_FILE, sales_path=SALES_FILE, archive_path=ARCHIVE_FILE,
        base="inventory", asof_date=date(2026, 5, 8))
    s2 = report["summary"]
    print("\n[7] build_dataset 单入口编排")
    print(f"    period_days={report['period_days']}  summary={s2['ABC']} "
          f"呆滞{s2['呆滞款数']}款 慢周转{s2['慢周转款数']}款")

    # ── 8. 断言: 对齐 run_inv.py 全量基线 ──
    print("\n" + "=" * 72)
    checks = [
        ("有效SKU", len(merged), EXPECT_SKU),
        ("负库存", neg_inv, EXPECT_NEG_INV),
        ("ABC-A", summ["ABC"].get("A", 0), 11),
        ("ABC-B", summ["ABC"].get("B", 0), 10),
        ("ABC-C", summ["ABC"].get("C", 0), 31),
        ("呆滞款数", summ["呆滞款数"], 17),
        ("呆滞积压(元)", int(summ["呆滞积压成本"]), 812),
        ("慢周转款数", summ["慢周转款数"], 48),
        ("单入口一致", len(merged2), len(merged)),
    ]
    all_ok = True
    for name, got, exp in checks:
        ok = got == exp
        all_ok = all_ok and ok
        print(f"  {name:<12} {got} == {exp}? {'✅' if ok else '❌'}")
    print("=" * 72)
    print("全量基线对齐 run_inv.py:", "✅ 通过" if all_ok else "❌ 有偏差")
    print("=" * 72)
    return 0 if all_ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
