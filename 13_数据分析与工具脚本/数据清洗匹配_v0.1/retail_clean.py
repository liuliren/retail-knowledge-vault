#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
retail_clean.py — 门店数据"清洗 + 跨文件匹配"硬化核心模块 (数据底座 N1).

定位: [[社区超市库存订货优化包]] 与 [[单品类诊断]] 共用的地基.
      把"LLM 每次看表猜字段 / 手撸 idx"沉淀成确定性、参数化、可复用的 pipeline.

设计原则
--------
1. 函数式、无副作用核心: read → locate_header → parse → drop_anomalies → join.
2. 参数化 (品类/门店/文件路径/候选字段/剔除规则), 不写死方便食品、不写死列序号.
3. 按表头名定位列 (build_colmap), 不按 idx —— 抗"空列打乱列位"与多行表头.
4. 只读原始数据, 不改不删原文件; 客户裸值 (条码/进价) 不打印、不落 git.

已硬化的 6 类坑 (花厅坊样板实战撞过) —— 详见同目录 README.md:
  ① WPS/CDFV2 .xls   → read_wps_xls() 用 python-calamine (pandas 常失败)
  ② 多行/合并表头     → locate_header() 扫描 + 跨相邻行补全 (库存表头在 r3, 明细在 r6)
  ③ 条码读成浮点      → clean_barcode() 去尾 .0 / 科学计数, join key 一致化
  ④ 负库存/异常剔除   → drop_anomalies() 规则化, 记录剔除行数+原因 (数据边界声明用)
  ⑤ 进价不准          → margin/turnover 输出标 reliability='仅参考' (见 [[花厅坊数据质量坑]])
  ⑥ 跨文件匹配        → join_by_barcode() 以条码为主键三表合一

依赖: python-calamine
"""
from __future__ import annotations
import re
from collections import defaultdict

# ────────────────────────────────────────────────────────────────────────────
# 字段候选表 (参数化的核心) —— 跨店并集; 新店/新报表只需加候选名即兼容.
# 每个 std_field 映射到一组源表头候选名 (按优先级). build_colmap 按名定位列序号.
# ────────────────────────────────────────────────────────────────────────────

# 库存积压报表 (给: 当前库存 / 进货日期 / 售价 / 进价参考)
INVENTORY_FIELDS = {
    "barcode":        ["货号", "商品条码", "条码"],
    "name":           ["品名", "商品名称"],
    "l3_category":    ["类别名称", "类别", "商品类别"],
    "price":          ["零售价", "售价", "零售单价"],
    "inventory":      ["当前库存", "库存", "库存数量", "即时库存"],
    "period_qty":     ["期间销量", "期间销售数量"],
    "period_value":   ["期间销售额", "期间销售金额"],
    "period_margin":  ["期间毛利"],
    "last_sale_date": ["最近销售日期"],
    "last_buy_date":  ["最近进货日期"],
    "cost_ref":       ["参考进价", "进价", "成本价"],
    "supplier":       ["供应商", "供应商名称", "主供应商"],
    "backlog_cost":   ["库存进价合计金额", "库存成本合计"],
}

# 商品销售明细 (给: 销量 / 销额 / 动销天数)
SALES_FIELDS = {
    "barcode":     ["货号", "商品条码", "条码"],
    "name":        ["品名", "商品名称", "简称"],
    "l3_category": ["类别名称", "类别"],
    "sale_date":   ["销售日期", "日期"],
    "sale_qty":    ["销售数量", "数量"],
    "sale_value":  ["销售金额", "金额"],
    "subtotal_qty":   ["数量小计"],
    "subtotal_value": ["金额小计"],
    "price":       ["零售价", "售价"],
    "cost_ref":    ["进价", "成本价"],
    "supplier":    ["供应商名称", "主供应商", "供应商"],
}

# 商品档案表 (给: 类目 / 供应商 / 单位)
ARCHIVE_FIELDS = {
    "barcode":     ["货号", "商品条码", "条码", "自编码"],
    "name":        ["品名", "商品名称"],
    "l3_category": ["类别名称", "类别", "商品类别"],
    "price":       ["零售价", "售价"],
    "cost_ref":    ["进货价", "进价", "成本价", "参考进价"],
    "supplier":    ["供应商名称", "供应商", "主供应商"],
    "unit":        ["单位", "计价方式"],
}

# 表头识别用关键词 (locate_header 默认): 任意源表的表头都应含其中数个.
HEADER_HINT_KEYWORDS = ["货号", "品名", "商品名称", "条码", "零售价", "当前库存",
                        "销售数量", "数量小计", "类别名称"]

# 已知会被误当数据/SKU 的汇总行标记 (按名或货号过滤)
SUBTOTAL_TOKENS = {"小计", "合计", "总计", "小  计", "本页合计", "累计"}

# 标记为"进价依赖" 的派生字段: 进价不准时这些字段 reliability = '仅参考'
COST_DEPENDENT_FIELDS = ("margin_rate", "margin_band", "backlog_cost", "turnover_days")


# ────────────────────────────────────────────────────────────────────────────
# 坑①: WPS/CDFV2 .xls 读取
# ────────────────────────────────────────────────────────────────────────────
def read_wps_xls(path, sheet=0):
    """用 python-calamine 读 WPS/CDFV2 .xls (pandas/xlrd 常对这类格式失败).

    也兼容 .xlsx. 返回 list[list]: 原始单元格矩阵 (不做任何裁剪).
    sheet: int 索引 或 str 表名.
    """
    from python_calamine import CalamineWorkbook
    wb = CalamineWorkbook.from_path(str(path))
    sht = wb.get_sheet_by_name(sheet) if isinstance(sheet, str) else wb.get_sheet_by_index(sheet)
    return sht.to_python()


# ────────────────────────────────────────────────────────────────────────────
# 坑②: 多行/合并表头 + 列位被空列打乱 → 按表头名定位
# ────────────────────────────────────────────────────────────────────────────
def _norm_cell(c):
    return str(c).strip() if c is not None else ""


def _match_col(cells, candidates):
    """在一行单元格里按候选名找列序号: 先精确匹配, 再子串匹配. 找不到返回 None."""
    for cand in candidates:                       # 精确优先 (避免 '货号'命中'自编货号'类误匹配)
        if cand in cells:
            return cells.index(cand)
    for cand in candidates:                       # 退化: 子串匹配
        for j, c in enumerate(cells):
            if c and cand in c:
                return j
    return None


def locate_header(rows, field_candidates=None, header_keywords=None,
                  scan_rows=30, min_fields=2):
    """定位表头行并建立 {std_field: col_idx} 映射 (抗多行表头/空列错位).

    参数
    ----
    rows            : read_wps_xls 的原始矩阵.
    field_candidates: {std_field: [候选表头名,...]}; 缺省用 HEADER_HINT_KEYWORDS 仅做行定位.
    header_keywords : 仅用于"找表头在第几行"的关键词集; 缺省取 field_candidates 的全部候选名.
    scan_rows       : 前若干行内搜索表头 (默认 30).
    min_fields      : 命中至少几个字段才认定为表头行.

    返回
    ----
    (header_idx, colmap):
      header_idx: 表头行号 (找不到则 -1);
      colmap    : {std_field: idx_or_None}. 仅当传入 field_candidates 时非空.

    硬化点: 找到主表头行后, 对仍为 None 的字段再扫描相邻行 (±2),
            以补全像 '行号' 这种被拆到下一行的合并表头碎片.
    """
    fc = field_candidates or {}
    if header_keywords is None:
        kws = set()
        for cands in fc.values():
            kws.update(cands)
        header_keywords = list(kws) if kws else HEADER_HINT_KEYWORDS

    best_idx, best_hits = -1, 0
    for i in range(min(scan_rows, len(rows))):
        cells = [_norm_cell(c) for c in rows[i]]
        hits = sum(1 for kw in header_keywords
                   if kw in cells or any(c and kw in c for c in cells))
        if hits > best_hits:
            best_idx, best_hits = i, hits

    if best_idx < 0 or best_hits < min_fields:
        return -1, {}

    if not fc:
        return best_idx, {}

    header_cells = [_norm_cell(c) for c in rows[best_idx]]
    colmap = {f: _match_col(header_cells, cands) for f, cands in fc.items()}

    # 补全被拆到相邻行的表头碎片
    for delta in (-1, 1, -2, 2):
        if all(v is not None for v in colmap.values()):
            break
        ni = best_idx + delta
        if not (0 <= ni < len(rows)):
            continue
        adj = [_norm_cell(c) for c in rows[ni]]
        for f, v in colmap.items():
            if v is None:
                colmap[f] = _match_col(adj, fc[f])
    return best_idx, colmap


# ────────────────────────────────────────────────────────────────────────────
# 坑③: 条码读成浮点 → 一致化
# ────────────────────────────────────────────────────────────────────────────
def clean_barcode(x):
    """归一条码为字符串 join key: 去尾 '.0'、展开科学计数、去空白. 空值返回 ''."""
    if x is None:
        return ""
    s = str(x).strip()
    if not s:
        return ""
    if re.fullmatch(r"\d+\.0+", s):               # 6901234567890.0 → 6901234567890 (合成示例)
        s = s.split(".")[0]
    elif re.fullmatch(r"[\d.]+[eE]\+?\d+", s):     # 科学计数 6.9e12
        try:
            s = str(int(float(s)))
        except (ValueError, OverflowError):
            pass
    return s


def is_barcode(x, min_len=8):
    """是否像条码: 纯数字且长度 >= min_len (默认 8). 用于过滤汇总行/空行."""
    s = clean_barcode(x)
    return s.isdigit() and len(s) >= min_len


def to_num(x):
    """安全转 float; 失败/空返回 None (区别于 0.0, 便于判'缺失'与'真实为0')."""
    if x is None:
        return None
    s = str(x).strip()
    if not s:
        return None
    try:
        return float(s)
    except (ValueError, TypeError):
        return None


# ────────────────────────────────────────────────────────────────────────────
# 行解析: 原始矩阵 → std_field 记录 list
# ────────────────────────────────────────────────────────────────────────────
_NUMERIC_STD_FIELDS = {
    "price", "inventory", "period_qty", "period_value", "period_margin",
    "cost_ref", "backlog_cost", "sale_qty", "sale_value",
    "subtotal_qty", "subtotal_value",
}


def parse_rows(rows, header_idx, colmap, require_barcode=True):
    """把原始矩阵 (表头后) 转成 [{std_field: value}], 按 colmap 取列、数值字段转 float.

    require_barcode=True: 跳过 barcode 列非条码的行 (天然滤掉汇总行/页脚/空行).
    """
    out = []
    bc_idx = colmap.get("barcode")
    name_idx = colmap.get("name")
    for r in rows[header_idx + 1:]:
        rec = {}
        for f, idx in colmap.items():
            v = r[idx] if (idx is not None and idx < len(r)) else None
            rec[f] = to_num(v) if f in _NUMERIC_STD_FIELDS else (_norm_cell(v) if v is not None else "")
        # 汇总行/小计行过滤
        nm = rec.get("name", "")
        if any(tok in nm for tok in SUBTOTAL_TOKENS):
            continue
        if require_barcode:
            if bc_idx is None or not is_barcode(r[bc_idx] if bc_idx < len(r) else None):
                continue
            rec["barcode"] = clean_barcode(r[bc_idx])
        else:
            if bc_idx is not None and bc_idx < len(r):
                rec["barcode"] = clean_barcode(r[bc_idx])
        out.append(rec)
    return out


# ────────────────────────────────────────────────────────────────────────────
# 坑④: 负库存/异常剔除 (规则化, 记录原因)
# ────────────────────────────────────────────────────────────────────────────
DEFAULT_DROP_RULES = {
    "drop_empty_barcode":      True,    # 空货号
    "drop_empty_name":         True,    # 空品名
    "drop_negative_inventory": True,    # 当前库存 < 0 (生鲜重灾区)
    "drop_nonpositive_price":  True,    # 零售价 <= 0
}


def drop_anomalies(records, rules=None):
    """按规则剔除异常行, 返回 (kept_records, drop_log).

    drop_log: {原因: 行数} —— 直接用于交付件的"数据边界声明".
    规则仅在对应字段存在时生效 (如只有明细无库存时, 负库存规则自动跳过).
    """
    rules = {**DEFAULT_DROP_RULES, **(rules or {})}
    kept, log = [], defaultdict(int)
    for rec in records:
        bc = rec.get("barcode", "")
        nm = rec.get("name", "")
        inv = rec.get("inventory")
        price = rec.get("price")

        if rules["drop_empty_barcode"] and not bc:
            log["空货号"] += 1
            continue
        if rules["drop_empty_name"] and not nm:
            log["空品名"] += 1
            continue
        if rules["drop_negative_inventory"] and inv is not None and inv < 0:
            log["负库存(剔除)"] += 1
            continue
        if rules["drop_nonpositive_price"] and price is not None and price <= 0:
            log["零售价<=0(剔除)"] += 1
            continue
        kept.append(rec)
    return kept, dict(log)


# ────────────────────────────────────────────────────────────────────────────
# 销售明细聚合 (明细是多行/天 → 按条码汇总销量与动销天数)
# ────────────────────────────────────────────────────────────────────────────
def aggregate_sales_by_barcode(sales_records):
    """把逐笔/逐日销售明细按条码聚合.

    返回 {barcode: {name, l3_category, supplier, sale_qty, sale_value, active_days}}.
    active_days = 有正销量的不同销售日期数 (动销天数).
    """
    agg = defaultdict(lambda: {"name": "", "l3_category": "", "supplier": "",
                               "sale_qty": 0.0, "sale_value": 0.0, "_days": set()})
    for r in sales_records:
        bc = r.get("barcode", "")
        if not bc:
            continue
        d = agg[bc]
        d["name"] = d["name"] or r.get("name", "")
        d["l3_category"] = d["l3_category"] or r.get("l3_category", "")
        d["supplier"] = d["supplier"] or r.get("supplier", "")
        q = r.get("sale_qty") or 0.0
        v = r.get("sale_value") or 0.0
        d["sale_qty"] += q
        d["sale_value"] += v
        if q > 0 and r.get("sale_date"):
            d["_days"].add(str(r.get("sale_date"))[:10])
    out = {}
    for bc, d in agg.items():
        out[bc] = {"name": d["name"], "l3_category": d["l3_category"],
                   "supplier": d["supplier"],
                   "sale_qty": round(d["sale_qty"], 2),
                   "sale_value": round(d["sale_value"], 2),
                   "active_days": len(d["_days"])}
    return out


# ────────────────────────────────────────────────────────────────────────────
# 坑⑥: 跨文件匹配 (以条码为主键三表合一)
# ────────────────────────────────────────────────────────────────────────────
def _index_by_barcode(data):
    """把 list[dict] 或 {barcode: dict} 统一成 {barcode: dict}."""
    if isinstance(data, dict):
        return {clean_barcode(k): v for k, v in data.items() if clean_barcode(k)}
    out = {}
    for rec in (data or []):
        bc = clean_barcode(rec.get("barcode", ""))
        if bc and bc not in out:
            out[bc] = rec
    return out


def join_by_barcode(sales=None, inventory=None, archive=None, base="inventory"):
    """以条码为主键, 把 销售明细 ↔ 库存积压报表 ↔ 商品档案 合并成统一记录.

    分工 (任一源可缺):
      inventory : 当前库存 / 进货日期 / 售价 / 进价参考 (通常定义 SKU 全集)
      sales     : 销量 / 销额 / 动销天数 (active_days)
      archive   : 类目 / 供应商 / 单位

    参数
    ----
    sales/inventory/archive: list[dict] 或 {barcode: dict}.
                             sales 建议先经 aggregate_sales_by_barcode.
    base: 哪个源定义 SKU 全集 ('inventory'|'sales'|'archive'|'union').

    返回
    ----
    (merged_list, stats):
      merged_list: 统一记录 list, 每条含 barcode + 三源字段 + 数据可靠性标记;
                   进价依赖字段 (margin/backlog/turnover) 标 cost_reliability='仅参考'.
      stats      : {base, 全集SKU数, 各源匹配数, join率} 供数据边界声明.
    """
    inv = _index_by_barcode(inventory)
    sal = _index_by_barcode(sales)
    arc = _index_by_barcode(archive)
    src = {"inventory": inv, "sales": sal, "archive": arc}

    if base == "union":
        keys = set(inv) | set(sal) | set(arc)
    else:
        keys = set(src.get(base, {}))
        if not keys:                              # base 源为空时回退到并集, 不静默丢数据
            keys = set(inv) | set(sal) | set(arc)

    merged = []
    matched = defaultdict(int)
    for bc in keys:
        i, s, a = inv.get(bc, {}), sal.get(bc, {}), arc.get(bc, {})
        if i:
            matched["inventory"] += 1
        if s:
            matched["sales"] += 1
        if a:
            matched["archive"] += 1

        rec = {
            "barcode": bc,
            "name": i.get("name") or s.get("name") or a.get("name") or "",
            "l3_category": (a.get("l3_category") or i.get("l3_category")
                            or s.get("l3_category") or ""),
            "supplier": a.get("supplier") or i.get("supplier") or s.get("supplier") or "",
            "price": i.get("price") or a.get("price") or s.get("price"),
            # 库存侧
            "inventory": i.get("inventory"),
            "last_buy_date": str(i.get("last_buy_date") or "")[:10],
            "last_sale_date": str(i.get("last_sale_date") or "")[:10],
            # 销售侧
            "sale_qty": s.get("sale_qty"),
            "sale_value": s.get("sale_value"),
            "active_days": s.get("active_days"),
            # 进价依赖字段 —— 标"仅参考"(坑⑤: 花厅坊进价不准)
            "cost_ref": i.get("cost_ref") or a.get("cost_ref"),
            "backlog_cost": i.get("backlog_cost"),
            "cost_reliability": "仅参考",
        }
        merged.append(rec)

    base_n = len(keys) or 1
    stats = {
        "base": base,
        "全集SKU数": len(keys),
        "命中_inventory": matched["inventory"],
        "命中_sales": matched["sales"],
        "命中_archive": matched["archive"],
        "join率_sales": round(matched["sales"] / base_n, 3),
        "join率_archive": round(matched["archive"] / base_n, 3),
        "cost_dependent_fields": list(COST_DEPENDENT_FIELDS),
        "note": "进价不准 → margin/backlog/turnover 仅参考 (见 花厅坊数据质量坑)",
    }
    return merged, stats


# ────────────────────────────────────────────────────────────────────────────
# 高层便捷封装: 路径 + 源类型 → 干净记录 (参数化 门店/品类/规则)
# ────────────────────────────────────────────────────────────────────────────
_FIELD_PRESETS = {
    "inventory": INVENTORY_FIELDS,
    "sales": SALES_FIELDS,
    "archive": ARCHIVE_FIELDS,
}


def clean_store_file(path, source_type, sheet=0, drop_rules=None,
                     field_candidates=None, require_barcode=True):
    """一站式: 读 .xls → 定位表头 → 解析 → 剔除异常.

    source_type: 'inventory' | 'sales' | 'archive' (决定默认字段候选表).
    field_candidates: 显式覆盖字段候选 (新报表/新店扩展点).
    返回 (records, meta): meta 含 header_idx / colmap命中 / drop_log / 行数.
    """
    fc = field_candidates or _FIELD_PRESETS.get(source_type)
    if fc is None:
        raise ValueError(f"未知 source_type={source_type!r}, 或请显式传 field_candidates")
    raw = read_wps_xls(path, sheet=sheet)
    hidx, colmap = locate_header(raw, field_candidates=fc)
    if hidx < 0:
        raise RuntimeError(f"未能在前若干行定位表头: {path}")
    parsed = parse_rows(raw, hidx, colmap, require_barcode=require_barcode)
    kept, drop_log = drop_anomalies(parsed, rules=drop_rules)
    meta = {
        "source_type": source_type,
        "header_idx": hidx,
        "located_cols": {f: i for f, i in colmap.items() if i is not None},
        "missing_cols": [f for f, i in colmap.items() if i is None],
        "raw_data_rows": len(raw) - hidx - 1,
        "parsed_rows": len(parsed),
        "kept_rows": len(kept),
        "drop_log": drop_log,
    }
    return kept, meta


if __name__ == "__main__":
    import sys
    print("retail_clean.py 是库模块. 自测请跑: python3 selftest_huachangfang.py", file=sys.stderr)
