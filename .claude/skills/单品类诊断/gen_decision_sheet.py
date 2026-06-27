#!/usr/bin/env python3
"""出"六哥决策单"——品类决策母模板的固化工具(机制C·已跑方便食品+巧克力)。
用法: python3 gen_decision_sheet.py <增强SKU表.csv> <品类名> <输出.md>
输入: 单品类诊断 skill 产出的 <品类>_增强SKU表(含 品名/单价/销量/动销天数/角色/受保护/汰换建议)。
输出: 六哥逐行填 留/汰/观 的决策单(client_confidential·≤10秒/款)。
逻辑: 净可汰候选 = 受保护∈('',否) 且 汰换建议含'汰'。绝不替六哥定取舍,只列候选+机器理由。
"""
import csv, sys
def g(r,*names):
    for n in names:
        for k in r:
            if n in k: return r[k]
    return ''
def main(ef, cat, out):
    rows=list(csv.DictReader(open(ef,encoding='utf-8-sig')))
    cand=[r for r in rows if str(g(r,'受保护')).strip() in ('','否') and '汰' in str(g(r,'汰换建议','建议'))]
    L=[f"""---
title: 花厅坊{cat} {len(cand)}款汰换决策单
status: candidate
owner: 六哥
client_safety: client_confidential
summary: {cat}净可汰候选{len(cand)}款·六哥逐行填留/汰/观·品类决策母模板实例
tags: [type/case, 汰换决策, 花厅坊, {cat}, 红线交付]
---

# 🖊 花厅坊{cat} · {len(cand)}款汰换决策单

> 机器筛的净可汰候选(已排受保护款),你每行填一字 **留/汰/观**(≤10秒/款)。填法:Obsidian改表 或 回话"全汰/留第X款"。填完出店长版卡(脱敏·你签)。见 [[品类决策母模板_v0.1]]。

| # | 品名 | 单价 | 近3月销量 | 动销天数 | 角色 | 机器为什么列它为候选 | **你的决策(留/汰/观)** | 备注/换什么 |
|---|---|---|---|---|---|---|---|---|"""]
    for i,r in enumerate(cand,1):
        L.append(f"| {i} | {str(g(r,'品名'))[:22]} | {g(r,'单价')} | {g(r,'销量')} | {g(r,'动销天数')} | {g(r,'角色')} | 动销{g(r,'动销天数')}天(滞)·{g(r,'角色')}角色·销额占比低 |  |  |")
    L.append("\n## 补锚点(可选·你定·具体品牌待选品库)\n- 锚点:________\n## 口诀:汰=动销差+补充角色+无特殊理由 / 留=有引流形象季节价值 / 观=拿不准看一月\n> ⚠️ 受保护款(引流/利润/形象/锁定)不在此列、不动。")
    open(out,"w",encoding="utf-8").write("\n".join(L))
    print(f"✓ {cat}决策单({len(cand)}款净可汰)→ {out}")
if __name__=="__main__":
    if len(sys.argv)!=4: print(__doc__); sys.exit(1)
    main(*sys.argv[1:])
