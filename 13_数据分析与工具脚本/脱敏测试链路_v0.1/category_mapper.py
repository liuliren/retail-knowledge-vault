#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RetailOS L3/L4 品类映射自动化 — SaaS 第二阻碍攻关。

问题: adapter 已归一字段,但"SKU 属哪个 L3/L4"仍需每店品类表(人工)。
解法(沉淀进代码降 LLM 依赖): 声明式 关键词→L3 映射表 + 复杂类标记。
   - 有类目列的店:源类目→标准L3(同义归一)
   - 无类目列的店:品名关键词→推断L3(沙埔大道实证)
   - L4=决策层构造(决策组),数据层只标"复杂类需L4",不臆造L4内容。

新品类只需在 L3_KEYWORDS 加一行 → 自动认(M-DEC回路用于工具:越跑越全)。
输入: adapter 标准schema csv。输出: 补 l3_category(+L4 needed标记) + 覆盖率 + 未映射清单。
"""
import sys, csv, re, os
from collections import defaultdict

# ── 标准 L3 + 关键词(品名命中即归类·优先级从上到下) ──
L3_KEYWORDS = [
  ("巧克力",   ["巧克力","巧克","黑巧","松露","费列罗","德芙","明治","瑞士莲","士力架","M&M","脆香米"]),
  ("糖果果冻", ["软糖","橡皮糖","棒棒糖","奶糖","硬糖","果冻","布丁","口香糖","益达","绿箭","旺仔","喜糖","糖"]),
  ("饼干糕点", ["饼干","曲奇","威化","夹心","蛋卷","蛋黄派","面包","蛋糕","桃酥","沙琪玛","华夫","糕"]),
  ("膨化薯片", ["薯片","薯条","薯愿","虾条","锅巴","雪饼","仙贝","米果","爆米花","乐事","膨化"]),
  ("坚果炒货", ["瓜子","花生","腰果","核桃","开心果","巴旦木","夏威夷","栗","坚果","炒货","洽洽","每日坚果"]),
  ("肉脯卤味", ["肉脯","猪肉脯","牛肉","鸭","凤爪","鸡爪","鸡翅","鸡米","卤","酱","火腿","香肠","肉干",
               "素牛","豆干","鱼","海味","风干肉","手撕","牛板筋","鸭脖","鸭掌","卤蛋","郡肝"]),
  ("即食蔬菜", ["海苔","紫菜","笋","魔芋","海带","拌饭","萝卜","梅菜","榨菜","蕨根","藕"]),
  ("果干蜜饯", ["葡萄干","芒果干","话梅","梅","蜜饯","果干","西梅","柠檬干","菠萝干","溜溜"]),
  ("冲调",     ["麦片","燕麦","冲调","咖啡","奶粉","豆浆粉","芝麻糊","藕粉","代餐"]),
  ("方便速食", ["方便面","桶面","泡面","螺蛳粉","自热","米线","臭宝","统一","粉丝"]),
  ("乳品饮料", ["牛奶","酸奶","乳","优酪","优之良品","蒙牛","伊利","燕塘","益力","饮料","可乐","矿泉","气泡水"]),
  ("酒水",     ["啤酒","白酒","红酒","清酒","米酒","洋酒","威士忌","果酒"]),
]
# 复杂类(需 L4 决策组分层) — 来自复杂类分层引擎验证
COMPLEX_L3 = {"巧克力","酒水","冲调","果干蜜饯"}  # 品牌密度/价格带分裂型

# 源类目同义归一(有类目列时)
SYN = {"巧克力":"巧克力","糖果":"糖果果冻","果冻":"糖果果冻","饼干":"饼干糕点","糕点":"饼干糕点",
       "膨化":"膨化薯片","薯片":"膨化薯片","坚果":"坚果炒货","炒货":"坚果炒货","肉脯":"肉脯卤味",
       "卤味":"肉脯卤味","果干":"果干蜜饯","蜜饯":"果干蜜饯","冲调":"冲调","方便":"方便速食",
       "乳":"乳品饮料","饮料":"乳品饮料","酒":"酒水","酒水":"酒水"}

def infer_l3(name, src_cat):
    # 1. 源类目优先(同义归一)
    if src_cat:
        for k,v in SYN.items():
            if k in src_cat: return v, "源类目"
    # 2. 品名关键词推断
    nm=str(name)
    for l3, kws in L3_KEYWORDS:
        if any(kw in nm for kw in kws): return l3, "品名推断"
    return "", "未映射"

def main():
    src, out = sys.argv[1], sys.argv[2]
    rows=list(csv.DictReader(open(src,encoding="utf-8-sig")))
    src_method=defaultdict(int); l3_dist=defaultdict(int); unmapped=[]
    for r in rows:
        l3,method = infer_l3(r.get("product_name",""), r.get("l3_category",""))
        r["l3_category"]=l3
        r["l4_category"]= "需L4决策组" if l3 in COMPLEX_L3 else ""
        src_method[method]+=1; l3_dist[l3 or "(未映射)"]+=1
        if not l3: unmapped.append(r.get("product_name","")[:18])
    with open(out,"w",newline="",encoding="utf-8-sig") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    n=len(rows); mapped=n-src_method["未映射"]
    print(f"[L3映射] {os.path.basename(src)}  SKU={n}")
    print(f"  覆盖率: {mapped}/{n} = {mapped/n*100:.0f}%  (来源: {dict(src_method)})")
    print(f"  L3分布: {dict(sorted(l3_dist.items(), key=lambda x:-x[1]))}")
    print(f"  复杂类(需L4): {[l for l in l3_dist if l in COMPLEX_L3]}")
    print(f"  未映射 {len(unmapped)} 款样本: {unmapped[:8]}")

if __name__=="__main__": main()
