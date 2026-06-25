#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RetailOS Data Adapter v1.0 — 跨店 ERP/POS → 统一标准 schema(SaaS化第一阻碍攻关)。

设计目标(六哥洞察):把"LLM看每个店的表猜字段"沉淀成"声明式适配器自动归一"
→ 跨店复制时运行时 LLM 依赖趋近 0(确定性代码=0 token)。

输入: 任意门店 ERP/POS 导出(.xls/.xlsx,calamine 读)
输出: 标准 schema csv + 数据质量评分(0-100)+ 可用性分级(A/B/C)+ 异常清单

脱敏铁律(CLAUDE.md §7): 货号(条码)→ sku_id 序号;进价裸值→ margin_band 即弃;供应商 drop。
依赖: python-calamine
"""
import sys, csv, re, os, argparse
from collections import defaultdict

# ── 统一标准 schema(prompt TASK1 ①) ──
STD_SCHEMA = ["store_id","sku_id","product_name","l3_category","l4_category",
              "price","cost_price","margin_band","sales_qty_30d","sales_value_30d",
              "inventory_qty","shelf_position","promo_flag"]

# 字段分级(prompt TASK1 ③)
MUST   = {"product_name","price_or_value"}          # 缺则不可用
INFER  = {"price","sales_qty_30d","l3_category"}     # 可推断
DEGRADE= {"cost_price","inventory_qty","shelf_position","promo_flag"}  # 缺则降级

# 源字段候选(跨店并集·新店加候选即兼容,prompt TASK1 ②)
CAND = {
  "sku_id":       ["货号","自编码","条码","商品条码"],
  "product_name": ["品名","商品名称"],
  "category":     ["类别名称","类别","商品类别","课别"],
  "price":        ["零售价","售价","零售单价"],
  "cost_price":   ["进价","档案进价","成本价","加权成本"],
  "sales_qty":    ["数量小计","销售数量","销量"],
  "sales_value":  ["金额小计","销售金额","销额"],
  "inventory":    ["库存","当前库存","库存即时快照","库存数量"],
  "date":         ["销售日期"],
}
SUBTOTAL = {"小计","合计","总计","小  计"}
MARGIN_BAND = lambda r,c: ("未知" if not(r and c and r>0) else
    "倒挂" if (r-c)/r<0 else "0-10%" if (r-c)/r<.1 else "10-20%" if (r-c)/r<.2
    else "20-30%" if (r-c)/r<.3 else "30-40%" if (r-c)/r<.4 else ">=40%")

def to_f(v):
    try: return float(v) if v not in (None,"") else 0.0
    except (ValueError,TypeError): return 0.0
def is_barcode(s): s=str(s).strip(); return s.isdigit() and len(s)>=8
def clean_name(s): return "(未命名SKU)" if is_barcode(s) else str(s).strip()
def brand(s):
    s=str(s).strip()
    if is_barcode(s) or not s: return "未知"
    s=re.sub(r"^[\dA-Za-z\*\.\sxX×克gG升mlML]+","",s)
    m=re.match(r"^([一-龥]{2,4})",s); return m.group(1) if m else "未知"

def find_header(rows, n=30):
    for i,row in enumerate(rows[:n]):
        cells=[str(c).strip() for c in row]
        has_name=any(x in cells for x in CAND["product_name"])
        has_val =any(x in cells for x in CAND["sales_qty"]+CAND["sales_value"])
        if has_name and has_val: return i, cells
    raise RuntimeError("未找到表头(需含品名+销量/销额)")

def colidx(H, key):
    for nm in CAND[key]:
        if nm in H: return H.index(nm)
    return None

def adapt(path, store_id):
    from python_calamine import CalamineWorkbook
    wb=CalamineWorkbook.from_path(path)
    data=wb.get_sheet_by_name(wb.sheet_names[0]).to_python()
    hi,H=find_header(data); rows=data[hi+1:]
    idx={k:colidx(H,k) for k in CAND}
    anomalies=defaultdict(int); notes=[]

    # 聚合
    agg=defaultdict(lambda:{"name":"","cat":"","qty":0.,"val":0.,"price":0.,"cost":0.,"inv":0.,"days":set()})
    for r in rows:
        g=lambda k: r[idx[k]] if (idx[k] is not None and idx[k]<len(r)) else None
        name=str(g("product_name") or "").strip()
        if not name or "合计" in name or "总计" in name: continue
        rawk=str(g("sku_id") or "").strip()
        if rawk in SUBTOTAL: continue
        key=rawk or name
        d=agg[key]; d["name"]=d["name"] or name
        d["cat"]=d["cat"] or str(g("category") or "").strip()
        d["qty"]+=to_f(g("sales_qty")); d["val"]+=to_f(g("sales_value"))
        p=to_f(g("price")); c=to_f(g("cost_price")); inv=to_f(g("inventory"))
        if p>0: d["price"]=p
        if c>0: d["cost"]=c
        if inv: d["inv"]=inv
        if idx["date"] is not None and to_f(g("sales_qty"))>0: d["days"].add(str(g("date")))

    # 字段覆盖体检
    has_price_col = idx["price"] is not None
    has_qty_vals  = any(d["qty"]>0 for d in agg.values())
    has_cost      = idx["cost_price"] is not None and any(d["cost"]>0 for d in agg.values())
    has_inv       = idx["inventory"] is not None and any(d["inv"]>0 for d in agg.values())
    has_cat       = idx["category"] is not None
    has_date      = idx["date"] is not None

    # 列错位/降级检测(prompt TASK3)
    if not has_qty_vals:
        anomalies["销量列缺失/错位→用销额÷价反推"]=1; notes.append("qty_inferred")

    out=[]; dup=set()
    for n,(k,d) in enumerate(sorted(agg.items(), key=lambda x:-x[1]["val"]),1):
        if k in dup: anomalies["SKU重复编码"]+=1
        dup.add(k)
        unit = d["val"]/d["qty"] if d["qty"]>0 else 0.
        price = d["price"] if d["price"]>0 else unit
        qty   = d["qty"] if d["qty"]>0 else (round(d["val"]/price,1) if price>0 else 0.)
        # price↔cost 错置检测
        if d["cost"]>0 and price>0 and d["cost"]>price*1.5: anomalies["进价>售价(疑price↔cost错置/进价不准)"]+=1
        band=MARGIN_BAND(price,d["cost"])
        if band=="倒挂": anomalies["毛利倒挂"]+=1
        if has_inv and d["inv"]<0: anomalies["负库存"]+=1
        out.append({
          "store_id":store_id, "sku_id":f"S{n:04d}", "product_name":clean_name(d["name"]),
          "l3_category":d["cat"], "l4_category":"",            # L4 需决策层补,适配层不臆造
          "price":round(price,2), "cost_price":"",             # 脱敏:不输出裸进价
          "margin_band":band, "sales_qty_30d":round(qty,1), "sales_value_30d":round(d["val"],2),
          "inventory_qty": (round(d["inv"]) if has_inv else ""),
          "shelf_position":"", "promo_flag":"",
        })

    # 数据质量评分(prompt TASK3)
    score=100; deduct=[]
    if not has_cat:  score-=10; deduct.append("缺类目(-10)")
    if not has_cost: score-=5;  deduct.append("缺进价→毛利降级(-5)")
    if not has_inv:  score-=10; deduct.append("缺库存→周转NA(-10)")
    if not has_date: score-=8;  deduct.append("缺销售日期→动销NA(-8)")
    if "qty_inferred" in notes: score-=8; deduct.append("销量列错位/反推(-8)")
    tot=len(out) or 1
    daoge=anomalies.get("毛利倒挂",0)/tot
    if daoge>0.02: score-=min(15,round(daoge*100*0.5)); deduct.append(f"毛利倒挂{daoge*100:.0f}%(进价不准)")
    if anomalies.get("SKU重复编码",0): score-=5; deduct.append("SKU重复编码(-5)")
    score=max(0,min(100,score))
    grade="A" if score>=80 else "B" if score>=60 else "C"
    return out, dict(anomalies), score, grade, deduct, {
        "price":has_price_col,"qty":has_qty_vals,"cost":has_cost,"inv":has_inv,"cat":has_cat,"date":has_date}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("raw"); ap.add_argument("out")
    ap.add_argument("--store", required=True); a=ap.parse_args()
    out,anom,score,grade,deduct,cov=adapt(a.raw,a.store)
    with open(a.out,"w",newline="",encoding="utf-8-sig") as f:
        w=csv.DictWriter(f,fieldnames=STD_SCHEMA); w.writeheader(); w.writerows(out)
    # 条码残留自检
    leak=sum(1 for r in out for v in r.values() if re.fullmatch(r"\d{8,}",str(v).strip()))
    print(f"[Adapter] store={a.store}  SKU={len(out)}  → {os.path.basename(a.out)}")
    print(f"  字段覆盖: {cov}")
    print(f"  数据质量评分: {score}/100  分级: {grade}")
    print(f"  扣分: {deduct}")
    print(f"  异常: {anom}")
    print(f"  脱敏自检: 条码残留 {leak} 处 " + ("✅" if leak==0 else "❌"))

if __name__=="__main__": main()
