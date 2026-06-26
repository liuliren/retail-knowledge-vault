#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_master.py — 数据底座 N2: 用 N1 pipeline 自动生成"商品基础表草表" (选品库/汰换地基).

定位
----
N1 (retail_clean) 解决"读表/清洗/跨文件 join"; N2 在其上把花厅坊全品类
门店数据自动编译成 **一张商品基础表草表** —— 自动生成 90% + 标"待校准"让六哥
做 10% 数据标注, 不手工逐条。

复用资产 (不造轮子)
-------------------
- N1 : retail_clean.clean_store_file / aggregate_sales_by_barcode / clean_barcode
- L3 : category_mapper.infer_l3 (源类目同义归一 + 品名关键词推断 + 复杂类标 L4)
- 属性: sku_extractor.SKUAttributeExtractor (品牌/规格 + 置信度)
- 品牌库: B_category_skeleton.representative_brands + A_core_sku_seed.brand_name
          + _maintenance/brand_alias (canonical + aliases) → known_brands
- 字段: 草表列对齐 商品库_v0.1/01_字段字典.md (C raw/mapped 命名 + 诊断派生列)

铁律
----
① 只读原文件, 不改不删 (D 层 raw_sensitive);
② 客户裸值 (条码/进价) 只进 client_confidential CSV (该目录 *.csv 已 gitignore);
③ 覆盖报告脱敏: 0 条码 / 0 进价裸值, 只给汇总与 %;
④ 进价不准 → margin/backlog/DOS 标 reliability='仅参考' (N1 坑⑤)。

跑法
----
cd 到 vault 根目录:  python3 13_数据分析与工具脚本/商品库_v0.1/_build/build_master.py
"""
from __future__ import annotations
import os
import sys
import csv
import datetime
from collections import defaultdict

# ── 路径锚定 (相对 vault 根, 也兼容从任意目录跑) ──────────────────────────────
HERE = os.path.dirname(os.path.abspath(__file__))
VAULT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))   # → retail-knowledge-vault
sys.path.insert(0, os.path.join(VAULT, "13_数据分析与工具脚本", "数据清洗匹配_v0.1"))
sys.path.insert(0, os.path.join(VAULT, "13_数据分析与工具脚本", "脱敏测试链路_v0.1"))
sys.path.insert(0, os.path.join(VAULT, "13_数据分析与工具脚本", "SKU属性提取算法_v0.1"))

import retail_clean as rc                       # noqa: E402
import category_mapper as cm                    # noqa: E402
from sku_extractor import SKUAttributeExtractor  # noqa: E402

RAW = os.path.join(VAULT, "09_门店案例与项目复盘", "乐易购花厅坊店",
                   "99_原始素材", "01_门店数据材料")
LIB = os.path.join(VAULT, "13_数据分析与工具脚本", "商品库_v0.1")
OUT_DIR = os.path.join(VAULT, "09_门店案例与项目复盘", "乐易购花厅坊店",
                       "03_商品诊断", "商品基础表草表")
OUT_CSV = os.path.join(OUT_DIR, "花厅坊_商品基础表草表_v0.1.csv")
OUT_REPORT = os.path.join(OUT_DIR, "花厅坊_商品基础表_覆盖与待校准_v0.1.md")

CLIENT_ID = "hcp"
STORE_ID = "hcp_001"
IMPORT_DATE = datetime.date.today().isoformat()
DETAIL_PERIOD_DAYS = 93     # 明细窗口 2026-03-11 ~ 06-12 ≈ 93 天 (动销率/DOS 基)
INV_PERIOD_DAYS = 30        # 库存报表期间销量默认窗口 (仅在无明细时回退用)
DOS_SLOW_THRESHOLD = 120    # 可销天数 > 此值 → 高库存呆滞
PRICE_BAND = [(10, "low"), (30, "mid")]   # 通用价格带 (元); >30 → high。品类级带见 skeleton

# ── 库存积压报表: 大类标签 → 文件名 (SKU 全集来源) ───────────────────────────
# ⚠ 顺序敏感: 同条码跨报表去重按"首见保留"。"食品"/"百货"是 umbrella 母报表
#   (食品 ⊃ 休闲+方便食品+粮油+调味+酒水; 百货 ⊃ 个护), 故母报表排在最后,
#   让具体子类先认领条码 → inv_category 落到更具体的子类, 母报表只收残余。
INVENTORY_FILES = {
    "个护":   "库存积压报表_个护_20260508.xls",
    "休闲":   "库存积压报表_休闲_20260508.xls",
    "散装":   "库存积压报表_散装_20260508.xls",
    "方便食品": "库存积压报表_方便食品_20260508.xls",
    "粮油":   "库存积压报表_粮油_20260508.xls",
    "调味":   "库存积压报表_调味_20260508.xls",
    "酒水":   "库存积压报表_酒水_90天_202060508.xls",
    "百货":   "库存积压报表_百货_20260508.xls",   # umbrella (⊃ 个护)
    "食品":   "库存积压报表_食品_20260508.xls",   # umbrella (⊃ 休闲/方便/粮油/调味/酒水)
}
UMBRELLA_CATS = {"百货", "食品"}

# ── 商品明细 (动销来源): 自动发现 *_花厅坊商品明细_20260311-0612.xls (排除"副本") ──
def discover_detail_files():
    out = []
    for fn in sorted(os.listdir(RAW)):
        if fn.endswith("_花厅坊商品明细_20260311-0612.xls") and not fn.startswith("副本"):
            out.append(fn)
    return out


# ── 已知品牌库 (降启发式误判) ────────────────────────────────────────────────
def load_known_brands():
    brands = set()
    # B 骨架代表品牌
    bpath = os.path.join(LIB, "B_category_skeleton.csv")
    if os.path.exists(bpath):
        for r in csv.DictReader(open(bpath, encoding="utf-8-sig")):
            for b in (r.get("representative_brands") or "").split("|"):
                if b.strip():
                    brands.add(b.strip())
    # A 种子品牌
    apath = os.path.join(LIB, "A_core_sku_seed.csv")
    if os.path.exists(apath):
        for r in csv.DictReader(open(apath, encoding="utf-8-sig")):
            if (r.get("brand_name") or "").strip():
                brands.add(r["brand_name"].strip())
    # brand_alias canonical + aliases
    alpath = os.path.join(LIB, "_maintenance", "brand_alias.csv")
    if os.path.exists(alpath):
        for r in csv.DictReader(open(alpath, encoding="utf-8-sig")):
            if (r.get("brand_canonical") or "").strip():
                brands.add(r["brand_canonical"].strip())
            for a in (r.get("aliases") or "").split("|"):
                a = a.strip()
                if a and not a.isascii():       # 中文别名才作前缀匹配 (英文别名易误命中)
                    brands.add(a)
    return brands


def price_band(price):
    if price is None or price <= 0:
        return ""
    for thr, lab in PRICE_BAND:
        if price < thr:
            return lab
    return "high"


# ─────────────────────────────────────────────────────────────────────────────
# 主流程
# ─────────────────────────────────────────────────────────────────────────────
def main():
    if not os.path.isdir(RAW):
        print(f"[FATAL] 找不到原始素材目录: {RAW}", file=sys.stderr)
        return 1

    known_brands = load_known_brands()
    extractor = SKUAttributeExtractor(known_brands=known_brands)

    # ── 1. 清洗全部库存报表 → SKU 全集 (每条带 inv_category) ──────────────────
    inv_records = []          # list[dict] 带 inv_category
    inv_meta_by_cat = {}      # 品类 → meta (drop_log / 行数)
    for cat, fn in INVENTORY_FILES.items():
        path = os.path.join(RAW, fn)
        if not os.path.exists(path):
            inv_meta_by_cat[cat] = {"error": "文件缺失", "kept_rows": 0}
            continue
        try:
            recs, meta = rc.clean_store_file(path, "inventory")
        except Exception as e:                # noqa: BLE001
            inv_meta_by_cat[cat] = {"error": str(e), "kept_rows": 0}
            continue
        for r in recs:
            r["inv_category"] = cat
            r["source_file"] = fn
        inv_records.extend(recs)
        inv_meta_by_cat[cat] = meta

    # 同条码跨报表去重 (按大类分区, 极少冲突; 保留首见, 记冲突)
    seen = {}
    inv_dups = 0
    inv_unique = []
    for r in inv_records:
        bc = r.get("barcode", "")
        if bc in seen:
            inv_dups += 1
            continue
        seen[bc] = True
        inv_unique.append(r)
    inv_records = inv_unique

    # ── 2. 清洗全部明细 → 按条码聚合销量/动销天数 (跨文件合并) ────────────────
    sales_agg = {}            # barcode → {sale_qty, sale_value, active_days, name, l3_category}
    detail_meta = {}          # 文件 → kept_rows / unique_bc
    sales_collisions = 0
    for fn in discover_detail_files():
        path = os.path.join(RAW, fn)
        try:
            recs, meta = rc.clean_store_file(path, "sales")
            agg = rc.aggregate_sales_by_barcode(recs)
        except Exception as e:                # noqa: BLE001
            detail_meta[fn] = {"error": str(e), "kept_rows": 0, "unique_bc": 0}
            continue
        detail_meta[fn] = {"kept_rows": meta["kept_rows"], "unique_bc": len(agg)}
        for bc, d in agg.items():
            if bc in sales_agg:
                sales_collisions += 1
                s = sales_agg[bc]
                s["sale_qty"] = round(s["sale_qty"] + d["sale_qty"], 2)
                s["sale_value"] = round(s["sale_value"] + d["sale_value"], 2)
                s["active_days"] = max(s["active_days"], d["active_days"])
            else:
                sales_agg[bc] = dict(d)

    # ── 3. 逐 SKU enrich → master rows ───────────────────────────────────────
    master = []
    for r in inv_records:
        bc = r.get("barcode", "")
        name = r.get("name", "")
        raw_cat = r.get("l3_category", "")
        s = sales_agg.get(bc, {})

        # L3/L4 (源类目优先, 否则品名推断; 复杂类标需 L4 决策组)
        l3, l3_method = cm.infer_l3(name, raw_cat)
        l4 = "需L4决策组" if l3 in cm.COMPLEX_L3 else ""

        # 品牌 / 规格
        attrs = extractor.extract(name)
        brand = attrs.brand.value if attrs.brand.confidence >= 0.5 else ""
        brand_conf = round(attrs.brand.confidence, 2)
        spec = attrs.spec.value if attrs.spec else ""
        spec_conf = round(attrs.spec.confidence, 2)

        # 价格 (库存报表售价优先; 缺则销额÷销量反推)
        price = r.get("price")
        price_source = "报表"
        if not price or price <= 0:
            dq, dv = s.get("sale_qty"), s.get("sale_value")
            if dq and dv and dq > 0:
                price = round(dv / dq, 2)
                price_source = "反推(销额÷销量)"
            else:
                price = None
                price_source = "缺"
        pband = price_band(price)

        # 库存 / 销售
        inv = r.get("inventory")
        period_qty = r.get("period_qty")
        period_value = r.get("period_value")
        d_qty = s.get("sale_qty")
        d_value = s.get("sale_value")
        active_days = s.get("active_days")
        has_detail = bool(s)

        # 进价依赖 (仅参考)
        cost_ref = r.get("cost_ref")
        backlog_cost = r.get("backlog_cost")
        margin_rate = None
        if price and cost_ref and price > 0:
            margin_rate = round((price - cost_ref) / price, 4)

        # DOS 可销天数 (优先明细日均, 回退报表期间)
        dos, dos_basis = None, ""
        if d_qty and d_qty > 0:
            rate = d_qty / DETAIL_PERIOD_DAYS
            dos = round((inv or 0) / rate, 1) if rate else None
            dos_basis = "明细93天"
        elif period_qty and period_qty > 0:
            rate = period_qty / INV_PERIOD_DAYS
            dos = round((inv or 0) / rate, 1) if rate else None
            dos_basis = "报表期间(仅参考)"

        # 销额 (ABC 用): 优先明细, 否则报表期间
        best_value = d_value if (d_value is not None) else period_value
        best_value = best_value or 0.0

        # 呆滞标记
        slow, slow_reason = False, ""
        has_stock = inv is not None and inv > 0
        total_sold = (d_qty or 0) + (period_qty or 0)
        if has_stock and total_sold <= 0:
            slow, slow_reason = True, "有货无销"
        elif dos is not None and dos > DOS_SLOW_THRESHOLD:
            slow, slow_reason = True, f"高库存(DOS>{DOS_SLOW_THRESHOLD})"

        # 角色弱建议 (机器只给弱建议; 一律入待校准)
        role_weak = ""
        if margin_rate is not None and best_value > 0:
            if margin_rate >= 0.30:
                role_weak = "利润?"
            elif margin_rate < 0.12:
                role_weak = "引流?"
            else:
                role_weak = "补充?"

        # 待校准 reasons
        cal = []
        if not l3:
            # 区分: 有源类目只是未标准化(休食 mapper 不覆盖该大类) vs 真缺源类目
            cal.append("L3待标准化(有源类目)" if raw_cat else "缺类目(无源)")
        if l4:
            cal.append("争议类目(需L4决策组)")
        if not brand:
            cal.append("品牌待定")
        if price is None:
            cal.append("缺价格")
        if not spec:
            cal.append("缺规格")
        if not has_detail and not (period_qty or period_value):
            cal.append("无销售数据")
        # 角色判断永远归人 (机器只弱建议)
        cal.append("角色待定")
        calibrate = ";".join(cal)

        master.append({
            "client_id": CLIENT_ID,
            "store_id": STORE_ID,
            "barcode": bc,                       # client_confidential
            "raw_product_name": name,
            "inv_category": r.get("inv_category", ""),
            "raw_category_name": raw_cat,
            "category_l3": l3,
            "category_l3_method": l3_method,
            "category_l4": l4,
            "brand_name": brand,
            "brand_confidence": brand_conf,
            "spec_value": spec,
            "spec_confidence": spec_conf,
            "price": price if price is not None else "",
            "price_source": price_source,
            "price_band": pband,
            "inventory": inv if inv is not None else "",
            "last_buy_date": r.get("last_buy_date", ""),
            "last_sale_date": r.get("last_sale_date", ""),
            "period_qty": period_qty if period_qty is not None else "",
            "period_value": period_value if period_value is not None else "",
            "detail_sale_qty": d_qty if d_qty is not None else "",
            "detail_sale_value": d_value if d_value is not None else "",
            "active_days": active_days if active_days is not None else "",
            "has_detail": "Y" if has_detail else "N",
            "cost_ref": cost_ref if cost_ref is not None else "",        # 仅参考
            "margin_rate": margin_rate if margin_rate is not None else "",  # 仅参考
            "backlog_cost": backlog_cost if backlog_cost is not None else "",  # 仅参考
            "abc_class": "",          # 全集排序后回填
            "dos_days": dos if dos is not None else "",
            "dos_basis": dos_basis,
            "is_slow_moving": "Y" if slow else "N",
            "slow_reason": slow_reason,
            "business_role_weak": role_weak,
            "cost_reliability": "仅参考",
            "待校准": calibrate,
            "source_file": r.get("source_file", ""),
            "import_date": IMPORT_DATE,
            "_best_value": best_value,        # 内部排序用, 不写出
        })

    # ── 4. ABC 分级 (按 best_value 全集累计: A<=70% / B<=90% / C 其余) ─────────
    total_val = sum(m["_best_value"] for m in master) or 1.0
    ranked = sorted(master, key=lambda m: -m["_best_value"])
    cum = 0.0
    for m in ranked:
        if m["_best_value"] <= 0:
            m["abc_class"] = "C"           # 零销额 → C
            continue
        cum += m["_best_value"]
        ratio = cum / total_val
        m["abc_class"] = "A" if ratio <= 0.70 else ("B" if ratio <= 0.90 else "C")

    # ── 5. 写草表 CSV (含裸值; 目录 *.csv 已 gitignore) ──────────────────────
    os.makedirs(OUT_DIR, exist_ok=True)
    fields = [k for k in master[0].keys() if k != "_best_value"] if master else []
    with open(OUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for m in master:
            w.writerow({k: m[k] for k in fields})

    # ── 6. 统计 → 覆盖报告 (脱敏: 0 条码 / 0 进价裸值, 只汇总与 %) ─────────────
    stats = compute_stats(master, inv_meta_by_cat, detail_meta, sales_agg,
                           inv_dups, sales_collisions, known_brands)
    write_report(stats)

    # ── 7. 控制台摘要 ────────────────────────────────────────────────────────
    print("=" * 72)
    print("N2 商品基础表草表 · 花厅坊  生成完成")
    print("=" * 72)
    print(f"草表 CSV  : {OUT_CSV}")
    print(f"覆盖报告  : {OUT_REPORT}")
    print(f"总 SKU 数 : {stats['total_sku']}")
    print(f"自动填充率: 类目 {stats['fill_l3']:.0%}  品牌 {stats['fill_brand']:.0%}  "
          f"价格带 {stats['fill_priceband']:.0%}  规格 {stats['fill_spec']:.0%}")
    print(f"明细 join 率: {stats['join_detail']:.0%}  (有明细动销的 SKU)")
    print(f"待校准条目  : {stats['calib_rows']} 行涉及  "
          f"(类型分布见报告)")
    return 0


def compute_stats(master, inv_meta, detail_meta, sales_agg,
                  inv_dups, sales_collisions, known_brands):
    n = len(master) or 1
    fill_l3 = sum(1 for m in master if m["category_l3"]) / n
    fill_rawcat = sum(1 for m in master if m["raw_category_name"]) / n
    fill_brand = sum(1 for m in master if m["brand_name"]) / n
    fill_pb = sum(1 for m in master if m["price_band"]) / n
    fill_spec = sum(1 for m in master if m["spec_value"]) / n
    fill_price = sum(1 for m in master if m["price"] != "") / n
    join_detail = sum(1 for m in master if m["has_detail"] == "Y") / n

    # 各品类 SKU 数 + 明细 join 率 + 积压成本 (仅参考·汇总)
    by_cat = defaultdict(lambda: {"sku": 0, "detail": 0, "backlog": 0.0, "slow": 0})
    for m in master:
        c = by_cat[m["inv_category"]]
        c["sku"] += 1
        if m["has_detail"] == "Y":
            c["detail"] += 1
        if m["is_slow_moving"] == "Y":
            c["slow"] += 1
        bc = m["backlog_cost"]
        if isinstance(bc, (int, float)):
            c["backlog"] += bc

    # 待校准类型分布
    calib_types = defaultdict(int)
    calib_rows = 0
    for m in master:
        reasons = [x for x in m["待校准"].split(";") if x and x != "角色待定"]
        if reasons:
            calib_rows += 1
        for x in m["待校准"].split(";"):
            if x:
                calib_types[x] += 1

    # ABC 分布
    abc = defaultdict(int)
    for m in master:
        abc[m["abc_class"]] += 1

    # 剔除统计汇总 (来自 inv meta drop_log)
    drop_summary = defaultdict(int)
    for cat, meta in inv_meta.items():
        for k, v in (meta.get("drop_log") or {}).items():
            drop_summary[k] += v

    return {
        "total_sku": len(master),
        "fill_l3": fill_l3, "fill_rawcat": fill_rawcat,
        "fill_brand": fill_brand, "fill_priceband": fill_pb,
        "fill_spec": fill_spec, "fill_price": fill_price, "join_detail": join_detail,
        "by_cat": dict(by_cat), "calib_types": dict(calib_types),
        "calib_rows": calib_rows, "abc": dict(abc),
        "inv_meta": inv_meta, "detail_meta": detail_meta,
        "detail_unique_bc": len(sales_agg), "inv_dups": inv_dups,
        "sales_collisions": sales_collisions, "drop_summary": dict(drop_summary),
        "n_known_brands": len(known_brands),
    }


def write_report(s):
    L = []
    a = L.append
    a("---")
    a("title: 花厅坊 商品基础表草表 · 覆盖与待校准报告 v0.1")
    a("client_safety: client_shareable_summary   # 0 条码 / 0 进价裸值 / 只汇总与 %")
    a("fact_layer: observed")
    a(f"created: {IMPORT_DATE}")
    a("source: N2 build_master.py (复用 N1 retail_clean + category_mapper + sku_extractor)")
    a("summary: 花厅坊全品类门店数据自动编译成商品基础表草表的覆盖率/待校准/数据边界报告")
    a("---")
    a("")
    a("# 花厅坊 商品基础表草表 · 覆盖与待校准报告 v0.1")
    a("")
    a("> **结论先行**：库存报表全品类共 "
      f"**{s['total_sku']} 个 SKU** 已自动编译成一张商品基础表草表；"
      f"源类目保真 **{s['fill_rawcat']:.0%}**（标准化到休食 L3 schema 覆盖 {s['fill_l3']:.0%}）、"
      f"价格带 **{s['fill_priceband']:.0%}**、规格 **{s['fill_spec']:.0%}**、品牌 **{s['fill_brand']:.0%}**；"
      f"**{s['join_detail']:.0%}** 的 SKU 配到明细可算动销。"
      f"机器已把可商品化的机械活做掉，**{s['calib_rows']} 行**需六哥做数据标注（详见 §5 待办清单）。")
    a("")
    a("> 脱敏声明：本报告 **0 条码 / 0 进价裸值**，只给汇总与百分比；裸值在 client_confidential "
      "草表 CSV（该目录 *.csv 已 gitignore）。进价不准 → 毛利率/积压成本/DOS 一律标 **仅参考**。")
    a("")

    a("## 1. 总览")
    a("")
    a("| 指标 | 值 |")
    a("|---|---|")
    a(f"| 总 SKU 数（库存报表全集，去重后）| {s['total_sku']} |")
    a(f"| 库存报表大类数 | {len([c for c in s['by_cat']])} |")
    a(f"| 明细文件唯一条码数（动销来源）| {s['detail_unique_bc']} |")
    a(f"| 配到明细的 SKU（join 率）| {s['join_detail']:.0%} |")
    a(f"| 已知品牌库规模 | {s['n_known_brands']} |")
    a(f"| 跨报表重复条码（去重剔）| {s['inv_dups']} |")
    a(f"| 跨明细文件条码冲突（合并）| {s['sales_collisions']} |")
    a("")

    a("## 2. 自动填充率（机器做掉的 90%）")
    a("")
    a("| 字段 | 自动填充率 | 口径 |")
    a("|---|---|---|")
    a(f"| 源类目（raw）| {s['fill_rawcat']:.0%} | 报表 类别名称 原样保真（如 白酒/护肤/纸品）|")
    a(f"| 标准 L3 | {s['fill_l3']:.0%} | 映射到休食 L3 schema；非休食大类待扩映射表 |")
    a(f"| 品牌 | {s['fill_brand']:.0%} | 已知品牌库匹配（置信≥0.5）|")
    a(f"| 规格 | {s['fill_spec']:.0%} | 品名正则提取 |")
    a(f"| 价格 | {s['fill_price']:.0%} | 报表售价优先 / 销额÷销量反推 |")
    a(f"| 价格带 | {s['fill_priceband']:.0%} | 通用带 low<10/mid10-30/high>30（品类级带待校准）|")
    a("")
    a(f"> 类目读法：源类目几乎 100% 保真在 `raw_category_name` 列；**标准 L3 的 {s['fill_l3']:.0%}** "
      "是因 `category_mapper` 现仅覆盖休食大类。非休食（百货/个护/酒水/粮油/调味）的源类目齐全，"
      "只需**扩一次映射表**即可批量标准化——是性价比最高的下一步，而非逐条人工。")
    a("")

    a("## 3. 各品类覆盖（SKU 数 / 明细 join / 呆滞 / 积压·仅参考）")
    a("")
    a("| 库存大类 | SKU 数 | 配到明细 | 明细 join 率 | 呆滞 SKU | 积压成本(元·仅参考) |")
    a("|---|---|---|---|---|---|")
    for cat in INVENTORY_FILES:
        c = s["by_cat"].get(cat)
        if not c:
            meta = s["inv_meta"].get(cat, {})
            note = meta.get("error", "0 行")
            a(f"| {cat} | 0 | — | — | — | {note} |")
            continue
        jr = c["detail"] / c["sku"] if c["sku"] else 0
        a(f"| {cat} | {c['sku']} | {c['detail']} | {jr:.0%} | {c['slow']} | {c['backlog']:.0f} |")
    a("")
    a("**库存报表↔明细 配对说明**：明细 join 率反映该大类有多少 SKU 在明细文件里有动销记录。"
      "**酒水 / 散装**无对应 03-06 明细文件，join 率≈0，本轮**只入库存维度**（动销待补当期明细）。")
    a("")
    a("> ⚠ **umbrella 母报表去重说明**：`食品` 报表实为母类（含休闲/方便食品/粮油/调味/酒水），"
      "`百货` 报表含个护。脚本按\"具体子类优先认领条码\"去重（母报表最后处理），故上表 `食品`/`百货` "
      f"行的 SKU 数是**扣除子类后的残余**；全集去重共剔 {s['inv_dups']} 条跨报表重复，"
      f"最终唯一 SKU = {s['total_sku']}（已无重复计数）。")
    a("")

    a("## 4. ABC 分布 + 待校准类型分布")
    a("")
    a("| ABC（按销额）| SKU 数 |")
    a("|---|---|")
    for k in ("A", "B", "C"):
        a(f"| {k} | {s['abc'].get(k, 0)} |")
    a("")
    a("| 待校准类型 | 涉及 SKU 数 | 说明 |")
    a("|---|---|---|")
    desc = {
        "L3待标准化(有源类目)": "有报表源类目，只是休食 mapper 不覆盖 → 扩映射表即可批量解决",
        "缺类目(无源)": "既无源类目也无品名关键词 → 需人工归类",
        "争议类目(需L4决策组)": "复杂类（巧克力/酒水/冲调/果干蜜饯）需 L4 决策组分层",
        "品牌待定": "已知品牌库未命中 → 需确认品牌",
        "缺价格": "报表无售价且无销量可反推",
        "缺规格": "品名未含可识别规格",
        "无销售数据": "既无明细也无报表期间销量",
        "角色待定": "引流/利润/形象/补充/季节 = 经营判断，机器只给弱建议，一律归六哥",
    }
    for k, v in sorted(s["calib_types"].items(), key=lambda x: -x[1]):
        a(f"| {k} | {v} | {desc.get(k, '')} |")
    a("")

    a("## 5. 给六哥的数据标注待办清单（按字段/品类聚合·不逐条堆）")
    a("")
    a(f"机器已完成全集 {s['total_sku']} SKU 的自动编译；以下为需人工标注的 **10%**，按优先级：")
    a("")
    ct = s["calib_types"]
    a(f"1. **扩映射表（非逐条）**：约 **{ct.get('L3待标准化(有源类目)', 0)}** 个 SKU 有源类目、只缺标准 L3——"
      "建议**扩 `category_mapper` 覆盖百货/个护/酒水/粮油/调味**（一次扩表即批量解决，回报最高）；"
      f"另有约 **{ct.get('缺类目(无源)', 0)}** 个无源类目，才需逐条人工归类。")
    a(f"2. **复杂类 L4 决策组**：约 **{ct.get('争议类目(需L4决策组)', 0)}** 个 SKU 属复杂类"
      "（巧克力/酒水/冲调/果干蜜饯），需你定 L4 分层（价格带×品牌密度）。")
    a(f"3. **品牌确认**：约 **{ct.get('品牌待定', 0)}** 个 SKU 品牌库未命中，"
      "其中高销额（A/B 类）优先；低销额可批量略过。")
    a(f"4. **价格/规格补缺**：缺价 **{ct.get('缺价格', 0)}**、缺规格 **{ct.get('缺规格', 0)}**，"
      "缺价多为零库存或无售价品，按需补。")
    a(f"5. **角色裁定（核心 10%）**：全集均标 `角色待定`——引流/利润/形象/补充/季节是经营判断，"
      "机器仅在 `business_role_weak` 列给了弱建议（带 ?）。建议**只对 A/B 类**"
      f"（共 {s['abc'].get('A', 0) + s['abc'].get('B', 0)} 个）做角色裁定，C 类暂置。")
    a("")

    a("## 6. 数据边界声明")
    a("")
    a("- **进价不准**（N1 坑⑤）：毛利率、积压成本、DOS 全部标 `仅参考`，不作签字依据。")
    a("- **明细窗口**：2026-03-11~06-12（≈93 天）；库存快照：2026-05-08。两口径时点不一致，"
      "DOS 以明细日均优先、报表期间回退（已在 `dos_basis` 列标注）。")
    a("- **酒水/散装**无 03-06 明细 → 只入库存维度，动销空缺待补当期明细。")
    a("- **沙埔大道店**：本轮仅花厅坊；沙埔大道仅有休闲一类历史明细，未纳入本草表，**待补**。")
    a("- **剔除统计**（清洗边界，全品类汇总）：")
    if s["drop_summary"]:
        for k, v in s["drop_summary"].items():
            a(f"  - {k}: {v} 行")
    else:
        a("  - 无（或各报表无触发剔除规则）")
    a("")

    a("## 7. 机制 B 复盘（自动填充率 / 最需人工 / 可改进点）")
    a("")
    a(f"- **自动化程度**：源类目 {s['fill_rawcat']:.0%} / 标准 L3 {s['fill_l3']:.0%} / "
      f"价格带 {s['fill_priceband']:.0%} / 规格 {s['fill_spec']:.0%} / 品牌 {s['fill_brand']:.0%}。"
      "价格带/规格/源类目达成 90/10；**标准 L3 与品牌是两个弱环**——L3 靠扩映射表（机械、回报高），"
      f"品牌靠扩 known_brands（现仅 {s['n_known_brands']} 条）。")
    a("- **最需人工**：① 角色裁定（不可委托·护城河 10%）；② 复杂类 L4 分层；③ 品牌确认。")
    a("- **可改进点**：① 扩充 known_brands（从本草表 A/B 类高频品牌反哺 brand_alias）；"
      "② category_mapper 关键词库随未映射清单迭代（M-DEC 回路·越跑越全）；"
      "③ 补酒水/散装当期明细与沙埔大道数据，提升 join 覆盖。")
    a("")
    a("> 复用链：N1 `retail_clean`（读/清洗/join）→ `category_mapper`（L3/L4）→ "
      "`sku_extractor`（品牌/规格）→ N2 `build_master.py`（编译草表）。字段对齐 "
      "`商品库_v0.1/01_字段字典.md`。")
    a("")

    with open(OUT_REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(L))


if __name__ == "__main__":
    raise SystemExit(main())
