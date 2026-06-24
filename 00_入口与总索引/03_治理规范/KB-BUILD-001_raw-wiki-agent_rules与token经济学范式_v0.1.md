---
id: KB-BUILD-001
title: raw / wiki / agent_rules 与 token 经济学范式
version: v0.1
status: draft
owner: 六哥
created: 2026-06-24
module: 00_入口与总索引/03_治理规范
task_id: KB-BUILD-001
summary: AI 协作知识库的三层构建范式——raw 保真、wiki 可读、agent_rules 可执行，配 summary 首轮检索与 query 只读，降 token、防漂移。
tags:
  - KB-BUILD
  - 知识工程
  - agent_rules
  - token经济学
  - LLM-Wiki
source_type: build
confidence: high
related:
  - "[[Claude双宪法边界声明_P1-CLAUDE-Constitution-Boundary-001_v0.1]]"
---

# KB-BUILD-001｜raw / wiki / agent_rules 与 token 经济学范式

## 1. 一句话定义

KB-BUILD-001 是一套面向 AI 协作知识库的**三层构建范式**:**raw 保真、wiki 可读、agent_rules 可执行**,并通过 **summary 首轮检索**与 **query 只读**机制,降低 token 消耗和规则漂移。

## 2. 问题背景(它解决什么)

传统知识库的 6 个常见病:① 原始材料、人工解读、机器规则**混在一起**;② AI 每次检索都读长正文;③ query/retrieve 易被误用成写入;④ 规则散落在 Prompt 里,无稳定执行层;⑤ 项目规则与全局规则**冲突**;⑥ 批量整理看似高效,实则制造低质摘要与治理噪声。

## 3. 三层结构(核心)

| 层 | 定位 | 典型内容 | 写入规则 | token 作用 |
|---|---|---|---|---|
| **raw** | 原始材料层 | 原文、截图、导出、访谈、未加工素材 | **物理只读** | 保真,不反复读 |
| **wiki** | 人类知识层 | 结构化解释、方法论、案例、复盘 | 人工整理 | 供人理解 |
| **agent_rules** | 机器规则层 | 可执行规则、字段规范、lint、SOP、边界 | 高压缩、可执行 | 供 AI 快速执行 |

> 三层各司其职:raw 不解释、wiki 不执行、agent_rules 不叙事。混层 = 反模式(见 §13)。

## 4. raw 物理只读

1. raw **不承载解释**;2. raw **不被 agent 自动改写**;3. raw 是**证据源**,不是执行层;4. 价值在**保真与可追溯**;5. **不频繁塞进上下文**。

> raw 的核心价值不是让 AI 每次重读,而是让知识库有可追溯的源头。

落地:本库 `99_原始素材`/客户 xls 已 `chmod a-w` + `.no-ingest`(见双宪法边界声明 §8、§7 数据红线)。

## 5. wiki 人类可读层

1. 人工理解层;2. 可含解释、案例、结构化表达;3. **不等于** agent 执行规则;4. 服务人类阅读与项目复盘;5. **重要页必带 `summary:`**。

## 6. agent_rules 机器执行层

要**短、硬、可检查**——不写散文、不堆背景。应含:`must / must not`、字段规范、lint 规则、签字门、Git 红线、数据红线、执行 SOP。**这是 token 经济学的关键层**(规则越短越硬,AI 执行越省、越稳)。

> 本库的 agent_rules 即 `CLAUDE.md`(项目宪法)+ `/Users/CLAUDE.md`(全局宪法)+ `AI互通总规则` + 本类治理页。

## 7. summary 首轮检索字段

1. **低成本首轮检索字段**,不是正文替代;2. **必须读正文后写,不得套话**;3. 目标是帮 agent 判断"要不要深入正文";4. **不一次性批量补全**——高频页先补 / `/ingest` 时补 / 日常编辑补 / lint 缺失按需补。

样板(本轮已回填):
- 品质管理 → `经营控制链的校验层，判断金额结果与数量动作是否真实、健康、可持续，防"数字好看但不健康"。`
- 52周MD → `围绕一年52周，把商品/品类/促销/陈列/复盘节奏周期化管理的年度商品运营节奏方法。`

## 8. query 只读编译层铁律

1. query/search/retrieve **默认只读**;2. 查询动作**不得触发写入**;3. 检索层与写入层**分离**;4. 写入必须进入**明确任务**;5. 防 agent "找资料时顺手改文件";6. 这是知识库工程化稳定性的基础(见 retail §7 G02)。

## 9. token 经济学(为什么省)

| 机制 | 省 token 的方式 |
|---|---|
| raw 只读 | 不反复读原始长材料 |
| summary | 先用短摘要筛选,再决定是否翻正文 |
| wiki | 人类整理后减少上下文噪声 |
| agent_rules | 执行规则短、硬、可复用 |
| query 只读 | 避免检索时产生无关写入与返工 |
| lint | 用机器检查代替人工通读 |
| 双宪法边界 | 减少规则冲突与解释成本 |

> ⚠️ **谨慎表达,不写死"必省 70–90%"**:在高频检索与多 agent 协作场景,这套结构**有机会显著降低**上下文读取量;具体比例取决于**文档粒度、summary 质量、agent 执行纪律**三者。

## 10. 双宪法边界(防漂移)

1. `/Users/CLAUDE.md` = 全局宪法;2. retail `CLAUDE.md` = 项目宪法;3. 单次 Prompt = 任务边界;4. 优先级:**全局红线 > 项目红线 > 项目细则 > 单次 Prompt**;5. 单次 Prompt **只能收窄、不能放宽**红线;6. **冲突无法判断时,停止并报告**。详见 [[Claude双宪法边界声明_P1-CLAUDE-Constitution-Boundary-001_v0.1]]。

## 11. 版本控制与快照

1. 全局宪法**不应裸奔**(无版本史不可回滚);2. **不在 `/Users` 根 git init**;3. 用**独立轻量仓** `/Users/davidliu/Claude-Global-Governance/`;4. 快照脚本 `snapshot-global-gov.sh`;5. **只快照不改源**;6. **有变化才 commit**;7. **no-op 不污染历史**。

## 12. 适用场景

Obsidian 知识库 · Claude Code 本地知识库治理 · Codex 自动开发 · 多 agent 协作 · 长期项目记忆 · 零售知识库/方法论库 · 客户数据治理项目。

## 13. 反模式(必避)

① 把 raw 当 wiki 写;② 把 wiki 当 agent_rules 执行;③ 把 Prompt 当永久规则;④ query 时顺手写入;⑤ 为检索体验**一次性批量补低质 summary**;⑥ 把**单个客户特例外推为通用规则**;⑦ 在 `/Users` 根 git init;⑧ 用 `git add .`;⑨ 真实数据/dry-run 结果入 Git;⑩ 把 AI 结果**直接写回真实业务系统**。

## 14. 最小执行流程

1. **raw 收集**:只读保真;2. **wiki 提炼**:写人能读懂的结构化解释;3. **summary**:高频页补低成本摘要;4. **agent_rules**:稳定规则压缩成机器可执行规范;5. **lint**:查缺字段/越权/断链/红线;6. **query**:只读检索;7. **写入**:单独任务、明确边界、精确 `git add`;8. **快照**:全局规则变更后跑 `snapshot-global-gov`。

## 15. 与晟果新零售知识库的关系

1. KB-BUILD-001 是**知识库建设范式**,**不是零售业务方法论**;2. 它支撑:科学零售方法论、M-DEC、RetailOS、花厅坊数据线、Codex 自动开发;3. **不替代业务判断**;4. 服务于"**少 token、不掉工程质量**"。

---

## 关联与开放问题

- **ID 去重(待裁决)**:个人 vault `David-Liu-Vault/30_研究领域/LLM-Wiki第二大脑构建模式.md` 早前被标 `id: KB-BUILD-001`,与本页**撞 ID**。按双宪法边界(retail = build/方法论 SSOT),**本页为权威 KB-BUILD-001**;个人 vault 那页应降为"应用实例"并改 ID(如 `KB-PKM-001`)或仅 wikilink 指回本页。本轮未改个人 vault,留六哥裁决。
- 关联源:[[Claude双宪法边界声明_P1-CLAUDE-Constitution-Boundary-001_v0.1]]、retail `CLAUDE.md` §7/§10.2、Karpathy LLM Wiki、Asteri_eth(@Asteri_eth)raw/Wiki/agent_rules 范式(SRC-20260624)。
- 升 `active` 需六哥签字(retail §3①/§10.2 状态机)。
