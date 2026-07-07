---
title: 中层决策库 README 增补建议稿
version: v0.1
status: draft
owner: 六哥
created: 2026-07-08
module: 04_商品诊断与商品力提升/中层决策库
source_type: readme_proposal
client_safety: internal_only
fact_layer: inferred
summary: README增补建议(不改README本体):目录结构/命名/状态规则/SSOT/迁入流程五节增补文本,六哥签字后由主线程合入
审议轮次: 1
related:
  - "[[04_商品诊断与商品力提升/中层决策库/README]]"
  - "[[2026-07-08_中层决策库promote机制_draft_v0.1]]"
---

# README 增补建议稿（不改 README 本体·签字后合入）

> 现 README（v0.1·active·2026-05-05）只有编号体系与定位，缺"怎么进库"。以下为建议**追加**的五节文本，六哥签字后由主线程原文合入 README（届时 README 升 v0.2 并落台账）。

## 建议增补一：目录结构
```
中层决策库/
├── README.md                 # 本文件（编号体系+准入规则权威）
├── M-DEC-NNN_主题_vX.Y.md     # 已迁入的权威版判断卡（status 必为 active）
└── 2026-*_*_draft_*.md       # 机制草案/候选池等治理件（draft，不是卡）
```
判断卡与治理件靠命名区分：卡=M-DEC 前缀；治理件=日期前缀。

## 建议增补二：命名规范（承 README §既有体系）
迁入卡沿用原文件名不改名不重编号；同名双卡（16_ 历史件 vs 本库权威版）靠 `promoted_from`/`promote_date` 字段+原卡指针块消歧。

## 建议增补三：状态规则
本库判断卡 status **只允许 active 或 deprecated**——draft/candidate 卡不得存放于此（暂存去 16_ 战役档案）。违规入库=lint 红线（建议 G03 v3 增查）。

## 建议增补四：SSOT 规则
卡一经迁入，本库版=唯一权威版；16_ 原卡冻结为历史件。卡内容更新只发生在本库版，且更新须走版本记录+必要时重签。

## 建议增补五：迁入流程（指针）
八步流程见 [[2026-07-08_中层决策库promote机制_draft_v0.1]]（该机制过三轮审议前，每例迁入按个案终审包呈批）。

## 待六哥裁决
- [ ] 五节是否合入 README（合入=改 active 治理件，D 档签字+台账）
- [ ] 状态规则"只允许 active/deprecated"是否过严（备选：允许 candidate 挂"试运行区"子目录）
