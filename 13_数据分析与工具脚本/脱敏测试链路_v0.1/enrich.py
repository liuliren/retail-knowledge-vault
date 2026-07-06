#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
脱敏测试链路 v0.1 — 增强端:角色闸自动标记 + ABCZ 评分 + 汰换建议。
输入: 脱敏SKU表csv。输出: 增强csv(+ABCZ/评分/角色/受保护/汰换建议) + 摘要。
对接: [[SKU角色层与目的品保护机制_v0.1.6]](五角色+GBA锁定+目的品保护)
      [[单品管理]] §7.3(ABCZ·本批仅用可得维度,缺周转/库存则标注)。

⚠️ 诚实边界: 脱敏表无 库存/周转/关联/供应/适配 列 → ABCZ 用可得维度
   (销额/毛利率档/动销/价格带)简化计算,缺失维度不臆造。进价不准→毛利率档仅参考。
"""
import sys, csv, re, os
from collections import defaultdict

SEASON_KW = re.compile(r"礼盒|礼袋|大礼|年货|中秋|春节|端午|粽|月饼|节庆|心语|心型|礼")
MARGIN_SCORE = {"倒挂(<0%)":0,"0-10%":20,"10-20%":40,"20-30%":60,"30-40%":80,">=40%":100,"未知":50}

def brand_family(b):
    m = re.match(r"^([一-龥]{2})", str(b).strip()); return m.group(1) if m else "未知"

def pctl_rank(val, sorted_vals):
    """val 在升序序列中的分位(0-1)。"""
    if not sorted_vals: return 0.0
    lo = sum(1 for x in sorted_vals if x < val)
    return lo/len(sorted_vals)

def main():
    src, out = sys.argv[1], sys.argv[2]
    rows = list(csv.DictReader(open(src, encoding="utf-8-sig")))
    n = len(rows)
    amt = [float(r["销额"] or 0) for r in rows]
    price = [float(r["单价"] or 0) for r in rows]
    qty = [float(r["销量"] or 0) for r in rows]
    total = sum(amt) or 1
    amt_sorted, qty_sorted, price_sorted = sorted(amt), sorted(qty), sorted(price)
    p50_price = price_sorted[len(price_sorted)//2] if price_sorted else 0
    p85_price = price_sorted[int(0.85*(len(price_sorted)-1))] if price_sorted else 0
    # 品牌族销额 → top3(GBA锁定判据)
    bfam = defaultdict(float)
    for r in rows: bfam[brand_family(r["品牌_推断"])] += float(r["销额"] or 0)
    top3_fam = {b for b,_ in sorted(bfam.items(), key=lambda x:-x[1])[:3] if b!="未知"}

    # ABCZ: 按销额降序累计
    order = sorted(rows, key=lambda r: float(r["销额"] or 0), reverse=True)
    cum = 0.0; abcz = {}
    cut_d = total*0.99
    for i, r in enumerate(order):
        cum += float(r["销额"] or 0)
        share = cum/total
        if share <= 0.70: g="A"
        elif share <= 0.90: g="B"
        elif share <= 0.99: g="C"
        else: g="D"
        abcz[id(r)] = g

    enriched = []
    cnt = defaultdict(int); role_cnt = defaultdict(int)
    protected_n = cullable_n = 0; cull_amt = 0.0
    for r in rows:
        a = float(r["销额"] or 0); p = float(r["单价"] or 0); q = float(r["销量"] or 0)
        days = r.get("动销天数","NA")
        d = int(float(days)) if str(days) not in ("NA","") else None
        g = abcz[id(r)]
        # 综合评分(可得维度)
        score = round(100*(0.4*pctl_rank(a,amt_sorted) + 0.25*pctl_rank(q,qty_sorted)
                           + 0.1*0.5) + 0.25*MARGIN_SCORE.get(r["毛利率档"],50), 1)
        fam = brand_family(r["品牌_推断"])
        # 角色(优先级:季节>锁定>形象>引流>利润>补充)
        if SEASON_KW.search(r["品名"]): role="季节/礼赠"
        elif g=="A" and fam in top3_fam: role="锁定目的品"
        elif p>0 and p>=p85_price: role="形象"
        elif q>0 and pctl_rank(q,qty_sorted)>=0.85 and p<=p50_price: role="引流"
        elif r["毛利率档"] in (">=40%","30-40%") and g in ("A","B"): role="利润"
        else: role="补充"
        protected = role in ("季节/礼赠","锁定目的品","形象","引流")
        cullable = (g=="D") or (d is not None and d<=3 and score<35)
        if protected: advice = f"保({role})"; protected_n += 1
        elif cullable: advice = "汰"; cullable_n += 1; cull_amt += a
        else: advice = "留"
        cnt[g]+=1; role_cnt[role]+=1
        e = dict(r); e.update({"ABCZ":g, "综合评分":score, "角色":role,
                               "受保护":"是" if protected else "", "汰换建议":advice})
        enriched.append(e)

    fields = list(rows[0].keys()) + ["ABCZ","综合评分","角色","受保护","汰换建议"]
    with open(out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(enriched)

    print(f"[增强完成] {os.path.basename(src)} → {os.path.basename(out)}")
    print(f"  ABCZ: A={cnt['A']} B={cnt['B']} C={cnt['C']} D={cnt['D']}")
    print(f"  角色: {dict(role_cnt)}")
    print(f"  受保护(不可单独淘汰): {protected_n} 款")
    print(f"  净可汰候选: {cullable_n} 款 (销额{cull_amt:.0f}/{cull_amt/total*100:.0f}%) — 仍需店长现场核")
    print(f"  ⚠️ ABCZ 缺 周转/库存/关联/供应/适配 维度;进价不准→毛利档仅参考")

if __name__ == "__main__":
    main()
