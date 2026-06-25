#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
脱敏测试链路 v0.1 — 单品类商品明细 raw .xls → 脱敏 SKU 标准表 csv

设计原则(CLAUDE.md §7 keys not prompts):
- raw 裸值(货号=条码 / 进价 / 供应商)只流过本脚本,不进 Agent 上下文。
- 本脚本吞进吐出:输入 D 层 raw,输出脱敏 SKU 表(0 裸条码 / 0 裸进价 / 0 供应商)。
- 进价仅用于现场计算毛利率,随即丢弃;只保留毛利率分档。
- 条码(货号)→ 稳定 SKU 序号;供应商整列丢弃。

用法:
  python3 sanitize.py <raw.xls> <out.csv> --category 巧克力

依赖: python-calamine (pip install --user python-calamine) — 治国产 ERP 怪 .xls。
"""
import sys, csv, argparse, re
from collections import defaultdict

try:
    from python_calamine import CalamineWorkbook
except ImportError:
    sys.exit("缺依赖: 请先 `python3 -m pip install --user python-calamine`")

# 敏感字段:绝不写入输出
DROP_FIELDS = {"货号", "自编码", "进价", "进销差价", "进销差价率", "主供应商", "供应商名称", "供应商编码"}

def find_header(data, max_scan=30):
    """扫描定位真表头行(国产 ERP 导出常有标题横幅)。"""
    for i, row in enumerate(data[:max_scan]):
        cells = [str(c).strip() for c in row]
        if "品名" in cells and ("数量小计" in cells or "销售数量" in cells):
            return i, cells
    raise RuntimeError("未找到表头行(需含'品名'+'数量小计/销售数量')")

def cidx(headers, *names):
    for n in names:
        if n in headers:
            return headers.index(n)
    return None

def to_float(v):
    try:
        if v is None or v == "":
            return 0.0
        return float(v)
    except (ValueError, TypeError):
        return 0.0

def is_barcode_like(s):
    """纯数字且长度>=8 → 疑似条码,脱敏时不得外泄。"""
    s = str(s).strip()
    return s.isdigit() and len(s) >= 8

def clean_name(name):
    """品名脱敏:源系统误把条码填进品名时,刷成占位,防条码经品名漏出。"""
    return "(未命名SKU)" if is_barcode_like(name) else str(name).strip()

def guess_brand(name):
    """从品名提取品牌(推断·近似):剥离前导规格/数字,取首段 2-4 个中文。"""
    s = str(name).strip()
    if is_barcode_like(s) or not s:
        return "未知"
    s = re.sub(r"^[\dA-Za-z\*\.\sxX×克gGmlMLLＧ升]+", "", s)  # 剥离前导规格(400g/1*20)
    m = re.match(r"^([一-龥]{2,4})", s)
    return m.group(1) if m else "未知"

def margin_band(retail, cost):
    """毛利率分档(进价用完即弃,只回档)。"""
    if retail and cost and retail > 0:
        rate = (retail - cost) / retail
        if rate < 0:    return "倒挂(<0%)"
        if rate < 0.10: return "0-10%"
        if rate < 0.20: return "10-20%"
        if rate < 0.30: return "20-30%"
        if rate < 0.40: return "30-40%"
        return ">=40%"
    return "未知"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("raw"); ap.add_argument("out")
    ap.add_argument("--category", default="")
    a = ap.parse_args()

    wb = CalamineWorkbook.from_path(a.raw)
    data = wb.get_sheet_by_name(wb.sheet_names[0]).to_python()
    h_i, H = find_header(data)
    rows = data[h_i + 1:]

    c_key  = cidx(H, "货号", "自编码")
    c_name = cidx(H, "品名", "商品名称")
    c_qty  = cidx(H, "数量小计", "销售数量")
    c_amt  = cidx(H, "金额小计", "销售金额")
    c_date = cidx(H, "销售日期")
    c_rtl  = cidx(H, "零售价", "售价")
    c_cost = cidx(H, "进价", "档案进价", "成本价")
    c_spec = cidx(H, "规格")
    c_cat  = cidx(H, "类别名称", "类别")

    agg = defaultdict(lambda: {"name":"","qty":0.0,"amt":0.0,"days":set(),
                               "retail":0.0,"cost":0.0,"spec":"","cat":""})
    for r in rows:
        def g(i): return r[i] if (i is not None and i < len(r)) else None
        name = str(g(c_name) or "").strip()
        if not name or "合计" in name or "总计" in name:
            continue
        raw_key = str(g(c_key) or "").strip()
        # 跳过 ERP 小计/合计行(货号列填'小计',会与日级数据重复计入 → 50%伪垄断)
        if raw_key in ("小计", "合计", "总计", "小  计"):
            continue
        key = raw_key or name                  # 货号缺则用品名兜底
        qty = to_float(g(c_qty)); amt = to_float(g(c_amt))
        d = agg[key]
        d["name"] = d["name"] or name
        d["qty"] += qty; d["amt"] += amt
        if c_date is not None and qty > 0:
            d["days"].add(str(g(c_date)))
        rtl = to_float(g(c_rtl));  cost = to_float(g(c_cost))
        if rtl > 0: d["retail"] = rtl
        if cost > 0: d["cost"] = cost
        d["spec"] = d["spec"] or str(g(c_spec) or "").strip()
        d["cat"]  = d["cat"]  or str(g(c_cat) or "").strip()

    skus = sorted(agg.values(), key=lambda x: x["amt"], reverse=True)
    out_rows = []
    for n, d in enumerate(skus, 1):
        # 零售价:优先列值,缺则用实收单价(销额/销量)
        unit_price = (d["amt"] / d["qty"]) if d["qty"] > 0 else 0.0
        price = d["retail"] if d["retail"] > 0 else unit_price
        # 销量:某些门店ERP销量列错位/为空 → 有零售价时用 销额/价 反推(跨店robust)
        qty_out = d["qty"] if d["qty"] > 0 else (round(d["amt"]/price, 1) if price > 0 else 0.0)
        out_rows.append({
            "SKU序号": f"S{n:03d}",
            "品名": clean_name(d["name"]),
            "品牌_推断": guess_brand(d["name"]),
            "类别": d["cat"] or a.category,
            "单价": round(price, 2),
            "规格": d["spec"],
            "销量": round(qty_out, 1),
            "销额": round(d["amt"], 2),
            "动销天数": len(d["days"]) if c_date is not None else "NA",
            "毛利率档": margin_band(price, d["cost"]),
        })

    with open(a.out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader(); w.writerows(out_rows)

    # 摘要(仅聚合量,无敏感裸值)
    total_amt = sum(d["amt"] for d in skus)
    prices = [r["单价"] for r in out_rows if r["单价"] > 0]
    bands = defaultdict(int)
    for r2 in out_rows: bands[r2["毛利率档"]] += 1
    print(f"[脱敏完成] {a.category or a.raw}")
    print(f"  SKU 数: {len(skus)}  |  价格带: {min(prices) if prices else 0}-{max(prices) if prices else 0}")
    print(f"  销额合计: {round(total_amt,2)}  |  毛利率档分布: {dict(bands)}")
    print(f"  输出: {a.out}  (0条码 0进价 0供应商)")

if __name__ == "__main__":
    main()
