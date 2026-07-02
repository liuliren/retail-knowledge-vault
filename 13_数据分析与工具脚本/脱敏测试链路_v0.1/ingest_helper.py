#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ⚠️ DEPRECATED · 台账写入职责已废弃（2026-06-30 · ingest v1.4）
# 根层 _内容消化台账.md 是唯一权威台账，由 Claude 在 ingest Step 1 显式写入。
# 本脚本最多可作结构提取辅助（标题/来源/标签/路由建议），不得作为台账写入依据。
# 原有坑：台账硬编码写入旧 retail 台账（批01实证）。
"""
/ingest skill helper — 编译层自动化的确定性部分(L1 raw → 结构化字段 + 台账登记)。
LLM 只在进料时跑一次编译(摘要/分类/链接);本脚本做机械活,不调 LLM。

输入: 一个 Clipping(.md, L1 raw)
输出: ① 打印结构化字段(供 LLM 编译概念页) ② 追加台账一行(消化执行层)
裸值不涉及(clip 是公开外部内容,A 层)。
"""
import sys, re, os, argparse

# Clippings 子目录 → 域 + 建议目标库/目录(路由)
DOMAIN = [
  (("零售老刘","门店经营","商品研究","零售标杆","零售趋势"),
     ("retail", "14_外部案例与行业研究/零售老刘体系")),
  (("AI 应用","AI 趋势","AI-全栈工程师学习-艾逗笔","Claude"),
     ("build/AI", "→主库 David-Liu-Vault/30_研究领域 或 claude库")),
  (("一人公司","营销自媒体"),
     ("growth/media", "→主库 David-Liu-Vault/30_研究领域 或 retail media")),
]
def route(path):
    for keys,(dom,tgt) in DOMAIN:
        if any(k in path for k in keys): return dom,tgt
    return "未分类","(需人工指定)"

def parse_fm(text):
    m=re.match(r"^---\n(.*?)\n---", text, re.S)
    fm={}
    if m:
        for line in m.group(1).splitlines():
            mm=re.match(r"^(\w+):\s*(.*)$", line)
            if mm: fm[mm.group(1)]=mm.group(2).strip().strip('"')
    return fm

def digest(text):
    # 取 ## Why 段,否则 description/序言首句
    m=re.search(r"##\s*Why\s*\n(.+?)(?:\n##|\n---|\Z)", text, re.S)
    if m: return re.sub(r"\s+"," ",m.group(1)).strip()[:300]
    m=re.search(r"序言[：:](.+?)(?:\n|。)", text)
    if m: return m.group(1).strip()[:300]
    return ""

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("clip")
    ap.add_argument("--ledger", default="00_入口与总索引/05_审计与档案/内容消化台账_v0.1.md")
    ap.add_argument("--note", default="", help="编译后概念页相对路径(LLM写完回填)")
    ap.add_argument("--date", default="2026-06-25")
    a=ap.parse_args()
    text=open(a.clip,encoding="utf-8").read()
    fm=parse_fm(text); dom,tgt=route(a.clip)
    title=fm.get("title", os.path.basename(a.clip).replace(".md",""))
    print(f"=== /ingest 结构化字段 ===")
    print(f"  标题: {title}")
    print(f"  来源: {fm.get('source','')[:80]}")
    print(f"  created: {fm.get('created','')}  tags: {fm.get('tags','')}")
    print(f"  域(路由): {dom}  →建议落: {tgt}")
    print(f"  消化摘要(原文Why/序言): {digest(text)}")
    print(f"\n  下一步(LLM编译): 写≤150词summary+3-7标签+wikilink关联 → 概念页落 {tgt}")
    # 台账登记
    led=a.ledger
    if not os.path.exists(led):
        os.makedirs(os.path.dirname(led), exist_ok=True)
        open(led,"w",encoding="utf-8").write(
          "---\ntitle: 内容消化台账 v0.1\nstatus: live\nowner: 六哥\n"
          "module: 00_入口与总索引/05_审计与档案\nclient_safety: internal_only\n"
          "summary: /ingest skill 的消化执行层:记录每篇clip→编译进哪个概念页的状态。\n"
          "tags: [台账, 内容消化, ingest]\n---\n\n# 内容消化台账 v0.1\n\n"
          "> 每 /ingest 一篇 clip 追加一行。L1 raw→L2/L3 编译的执行账本。\n\n"
          "| 日期 | clip | 域 | 状态 | 编译进 |\n|---|---|---|:--:|---|\n")
    note=a.note or "(待回填)"
    with open(led,"a",encoding="utf-8") as f:
        f.write(f"| {a.date} | {title[:30]} | {dom} | compiled | {note} |\n")
    print(f"\n  ✅ 台账已登记: {led}")

if __name__=="__main__": main()
