#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
脱敏测试链路 v0.1 — 分析端:在脱敏SKU表上跑 品牌密度/价格带/集中度/复杂度判级。
输入: 脱敏SKU表 csv(sanitize.py 产物)。输出: 结构化指标(stdout JSON-ish + 表)。
对接: 复杂类分层引擎 + 失真库(品牌遮蔽型)+ 多品类压力测试。
"""
import sys, csv, glob, os, re
from collections import defaultdict

def brand_family(b):
    """品牌族:取品牌_推断前2个中文,合并'德芙桶装/德芙黑'→德芙。"""
    m = re.match(r"^([一-龥]{2})", str(b).strip())
    return m.group(1) if m else "未知"

def pctl(xs, q):
    if not xs: return 0
    xs = sorted(xs); i = int(q*(len(xs)-1))
    return xs[i]

def analyze(path):
    rows = list(csv.DictReader(open(path, encoding="utf-8-sig")))
    n = len(rows)
    amt = [float(r["销额"] or 0) for r in rows]
    price = [float(r["单价"] or 0) for r in rows]
    total = sum(amt) or 1
    # 集中度(按销额降序,sanitize已排序)
    cum = 0; cr5 = sum(amt[:5])/total; cr10 = sum(amt[:10])/total; top1 = amt[0]/total if amt else 0
    # 长尾:销额后50% SKU 的销额占比
    half = n//2
    tail_share = sum(amt[half:])/total
    # 品牌密度
    bfam = defaultdict(float)
    for r in rows: bfam[brand_family(r["品牌_推断"])] += float(r["销额"] or 0)
    bsorted = sorted(bfam.items(), key=lambda x:-x[1])
    top_brand, top_brand_amt = bsorted[0]
    top_brand_share = top_brand_amt/total
    top3_brand_share = sum(v for _,v in bsorted[:3])/total
    hhi = sum((v/total)**2 for v in bfam.values())  # 品牌赫芬达尔
    # 价格带
    p25,p50,p75,pmax,pmin = pctl(price,.25),pctl(price,.5),pctl(price,.75),max(price),min([p for p in price if p>0] or [0])
    span = pmax/pmin if pmin>0 else 0
    # 动销
    days = [r["动销天数"] for r in rows if r["动销天数"] not in ("NA","")]
    low_move = None
    if days:
        dvals = [int(float(d)) for d in days]
        low_move = sum(1 for d in dvals if d<=3)/len(dvals)
    return dict(cat=os.path.basename(path).split("_")[0], n=n, total=round(total),
                top1=top1, cr5=cr5, cr10=cr10, tail_share=tail_share,
                top_brand=top_brand, top_brand_share=top_brand_share,
                top3_brand_share=top3_brand_share, brand_n=len(bfam), hhi=hhi,
                pmin=pmin,p25=p25,p50=p50,p75=p75,pmax=pmax,span=span, low_move=low_move,
                brands=bsorted[:5])

def classify(m):
    """按引擎判级:价格带分裂 + 品牌密度 → 复杂度 + 失真型预判。"""
    # 复杂度
    split = m["span"]>=10 and m["p75"]>m["p25"]*2.5   # 价格带多档成群
    brand_dense = m["top_brand_share"]>=0.30 or m["hhi"]>=0.15
    if split and brand_dense: cx="高复杂(价格带分裂+品牌密度)"
    elif split: cx="高复杂(价格带分裂)"
    elif brand_dense: cx="中复杂(品牌密度型)"
    else: cx="中复杂/简单"
    layer = "L4(按品牌族/价格带分档)" if (split or brand_dense) else "L3"
    # 失真型预判
    flaws=[]
    if brand_dense: flaws.append(f"品牌遮蔽型(top品牌'{m['top_brand']}'占{m['top_brand_share']*100:.0f}%)")
    if split: flaws.append(f"价格带遮蔽型(跨度{m['span']:.0f}x,中位{m['p50']}掩盖{m['pmin']}-{m['pmax']})")
    if m["top1"]>=0.25: flaws.append(f"批发异常/单SKU垄断(top1占{m['top1']*100:.0f}%)")
    if m["low_move"] and m["low_move"]>=0.4: flaws.append(f"长尾低动销({m['low_move']*100:.0f}%的SKU动销≤3天)")
    return cx, layer, flaws

if __name__=="__main__":
    d=sys.argv[1]
    for p in sorted(glob.glob(os.path.join(d,"*_脱敏SKU表_v0.1.csv"))):
        m=analyze(p); cx,layer,flaws=classify(m)
        print(f"\n{'='*60}\n【{m['cat']}】 SKU={m['n']}  销额={m['total']}  品牌族数={m['brand_n']}")
        print(f"  价格带: {m['pmin']}-{m['pmax']} (跨度{m['span']:.0f}x, p25/p50/p75={m['p25']}/{m['p50']}/{m['p75']})")
        print(f"  集中度: top1SKU={m['top1']*100:.0f}%  CR5={m['cr5']*100:.0f}%  CR10={m['cr10']*100:.0f}%  后50%SKU销额={m['tail_share']*100:.0f}%")
        print(f"  品牌密度: top品牌'{m['top_brand']}'={m['top_brand_share']*100:.0f}%  top3={m['top3_brand_share']*100:.0f}%  HHI={m['hhi']:.3f}")
        if m['low_move'] is not None: print(f"  动销: {m['low_move']*100:.0f}% 的SKU动销≤3天")
        print(f"  top5品牌族: {[(b,round(v)) for b,v in m['brands']]}")
        print(f"  → 复杂度判级: {cx}")
        print(f"  → 推荐分层: {layer}")
        print(f"  → 失真型预判: {flaws if flaws else '无显著失真'}")
