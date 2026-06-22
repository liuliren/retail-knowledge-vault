任务名称：
P1-MEM-Schema-001｜M-DEC长期记忆系统Schema预览稿

本轮目标：
基于《零售知识系统 V2 迭代方案》，提炼为一份适合晟果新零售科学零售知识体系的《M-DEC长期记忆系统Schema》预览稿，并用 1 条现有 M-DEC 做试填样例。只生成预览稿，不修改 CLAUDE.md，不改 M-DEC 正文，不上自动化，不执行全库重构。

最高标准：
把 V2 思想压缩成“最简正确版”。保留 provenance、supersession、signoff、四级记忆层、命名边、M-DEC 回填晋升路径；拒绝 confidence score、decay、自动写入、向量库、图数据库、复杂 hooks。该方案必须服务花厅坊 / 新客户真实交付，而不是新开一个知识工程战场。

当前背景：
1. 当前知识库为“晟果新零售科学零售知识体系”；
2. CLAUDE.md 已升 v2.2；
3. §10 世界级交付标准已 active；
4. §11 卡帕西闭环 wiki 已 target_framework；
5. signoff 已成为 active 签字门；
6. G03_Lint v2 已在 Codex 队列 / 或已产出待审；
7. Wiki治理方案 v1.0 已采用“方案 A：增量统领”；
8. 术语口径统一表预览已完成，正式总体系名为“晟果新零售科学零售知识体系”；
9. M-DEC 是 L4 决策规则层，未验证前只能 candidate；
10. 当前有 M-DEC-010 价格带结构预警、M-DEC-013 单小类长尾结构治理候选等可作为试填样例；
11. 用户明确不希望再开一条庞大新工程，必须最小落地。

用户裁决：
1. 采纳 V2 方案的核心思想，但不照搬 V2 全套工程；
2. 不使用 confidence score；
3. 不使用 decay / 遗忘曲线；
4. 使用 provenance 溯源；
5. 使用 supersession 显式取代；
6. 保留人工 signoff 写入闸门；
7. 暂不上向量库 / 图数据库；
8. 暂不自动写入；
9. 先生成 md 预览稿；
10. 不直接修改 CLAUDE.md；
11. 不直接修改现有 M-DEC 正文；
12. 用 1 条 M-DEC 做试填样例。

本轮允许：
1. 新建一份 M-DEC长期记忆系统Schema 预览稿；
2. 新建或附带一条 M-DEC-010 / M-DEC-013 的试填样例；
3. 追加 Claude执行日志；
4. 如预览稿边界清晰，可 commit；
5. 只提交本轮新建 / 修改文件；
6. 不夹带外部 dirty 文件。

本轮禁止：
1. 不修改 CLAUDE.md；
2. 不改 M-DEC-010 正文；
3. 不改 M-DEC-013 正文；
4. 不批量修改 M-DEC 文件；
5. 不批量修改全库 frontmatter；
6. 不改科学零售总纲；
7. 不改三力总纲；
8. 不改 RetailOS；
9. 不改 M1-M8 正文；
10. 不改 30天商品提效包；
11. 不改 Codex 脚本；
12. 不 execute dry-run；
13. 不上向量库；
14. 不上图数据库；
15. 不设计复杂自动化 hooks；
16. 不新增 confidence score 字段；
17. 不新增 decay / freshness_score / 遗忘曲线字段；
18. 不移动文件；
19. 不删除文件；
20. 不重命名文件；
21. 不碰 xls / csv / docx；
22. 不碰外部 dirty 文件；
23. 不使用 git add .。

---

# A. 生成 Schema 预览稿

建议新建文件路径：
00_入口与总索引/03_治理规范/晟果新零售M-DEC长期记忆系统Schema_预览_v0.1.md

frontmatter 建议：

---
title: 晟果新零售M-DEC长期记忆系统Schema
version: v0.1
status: draft
owner: 六哥
created: 2026-06-22
updated: 2026-06-22
source_type: governance_schema
permission_level: internal_methodology
client_safety: internal_only
module: M-DEC长期记忆系统
related:
  - "[[CLAUDE.md]]"
  - "[[晟果新零售科学零售Wiki知识体系治理方案_v1.0]]"
  - "[[晟果新零售科学零售术语口径统一表_预览_v0.1]]"
tags: [M-DEC, 长期记忆, schema, provenance, supersession, signoff, 科学零售]
---

正文建议结构：

# 晟果新零售M-DEC长期记忆系统Schema v0.1 预览稿

## 0. 文件定位

说明：
1. 本文件是 M-DEC 长期记忆系统的 Schema 预览稿；
2. 它不是 CLAUDE.md 替代品；
3. 它不是 M-DEC 规则正文；
4. 它不是自动化脚本；
5. 它用于规范“现场决策如何进入知识体系、如何回填、如何晋升、如何被取代”。

## 1. 总判断：采最简正确版

必须写清：
1. V2 是菜单，不是规格书；
2. 我们采纳问题意识，不照搬工程复杂度；
3. 当前阶段最重要的是现场判断回流，不是机器自动化；
4. 知识系统是零售诊断的“记忆型马具”，目标是增强判断，而不是制造新战场。

## 2. 与现有治理体系的关系

必须说明：

| 现有文件 / 机制 | 本 Schema 与其关系 |
|---|---|
| CLAUDE.md v2.2 | CLAUDE.md 是执行宪法，本文件是 M-DEC 记忆规则 |
| Wiki治理方案 v1.0 | Wiki治理方案管全库治理，本文件管决策记忆闭环 |
| 术语口径统一表 | 术语以口径表为准 |
| signoff | 本文件沿用 signoff 作为人工写入闸门 |
| G03_Lint v2 | 后续可检查孤儿决策、缺回填、缺 provenance、缺 signoff |
| M-DEC 候选池 | 本文件规范 M-DEC 从 candidate 到 active 的晋升路径 |

## 3. 五条设计原则

必须包含：

### 3.1 provenance 取代 confidence score

要求：
- 不打 0.85 这种假精确置信度；
- 所有结论必须挂来源；
- 可信度来自可见证据链。

### 3.2 supersession 取代 decay

要求：
- 决策不过期，只被取代；
- 旧判断保留；
- 新判断出现时用“被取代::”显式连接；
- 保留当时为什么这么判断的审计轨迹。

### 3.3 signoff 作为人工写入闸门

要求：
- AI 可生成 draft；
- 进入 active / semantic / procedural 层必须 signoff；
- 没有 signoff，不得作为正式规则或客户交付依据。

### 3.4 四级记忆层

使用中文命名，不要让英文术语压过业务语言：

| 记忆层 | 对应 | 说明 |
|---|---|---|
| 现场观察层 | working | 当天看到的问题 / 数据 / 现象 |
| 单店决策层 | episodic | 一次完整 M-DEC 判断 |
| 跨店规律层 | semantic | 多店验证后的经营规律 |
| 标准动作层 | procedural | SOP / 模板 / RetailOS 动作 |

### 3.5 schema 承载 90%，机器后置

要求：
- 先用规则、模板、字段、signoff 跑通；
- 等手动跑过几十轮再自动化；
- 未到规模线，不上向量库 / 图数据库。

## 4. 实体类型

建议定义：

| 实体 | 用途 | 最小字段 |
|---|---|---|
| Store 门店 | 记录门店上下文 | store_id / 业态 / 面积 / 客群 / 项目状态 |
| Category 品类 | 记录品类对象 | category_name / L1-L5 / CDT / H-Score |
| SKU | 记录单品对象 | sku_name / category / H-Score / 脱敏状态 |
| IssueTag 问题标签 | 记录问题类型 | issue_code / issue_name / severity |
| Decision 决策 | M-DEC 核心 | 现象 / 决策 / 推理 / 来源 / 结果 / 状态 |
| Case 案例 | 项目证据 | project / store / date / output |
| Method KB 方法论 | 跨案例沉淀 | 来源 / 适用条件 / 限制条件 / signoff |

注意：
不要在本轮建立这些实体文件，只定义 Schema。

## 5. 命名边规则

定义 Obsidian 可用的命名边：

```text
来源:: [[案例/门店/数据摘要]]
诊断出:: [[IssueTag]]
触发:: [[决策]]
导致:: [[结果]]
被取代:: [[新决策]]
晋升为:: [[方法论/规则/SOP]]
适用于:: [[业态/品类/场景]]
限制于:: [[适用边界]]
```

要求：
1. 同一现象在不同门店重复出现，不视为重复，而是新证据；
2. 去重按 provenance 身份，不按文字相似度；
3. 真冲突进入待审，不自动合并；
4. 不要求每条记录都有全部命名边，但来源:: 必须优先。

## 6. M-DEC 最小记录模板

给出 30 秒可口述模板：

```markdown
## [日期] 决策｜[门店]｜[一句话标题]

- 现象：
- 决策：
- 推理：
- 来源:: [[门店]] / [[IssueTag]] / [[现场记录]]
- 结果：
- 状态：live
- 回填日期：
- signoff：
```

同时给出 frontmatter 建议：

```yaml
title:
version: v0.1
status: draft
source_type: m_dec_episode
client_safety: internal_only
store:
category:
issue_tags:
decision_status: live
result_status: pending
```

注意：
本轮只定义模板，不改现有 M-DEC 文件。

## 7. M-DEC 晋升路径

必须写清：

1. 现场观察层 → 单店决策层；
2. 单店决策层 → 回填结果；
3. 多个独立场景验证 → 跨店规律层；
4. 跨店规律层 → 标准动作层；
5. 进入 active / procedural 必须 signoff。

默认门槛：
≥3 个独立场景验证且结果方向一致。

例外通道：
强证据 + 用户 signoff 可提前晋升，但必须写明例外理由。

禁止：
- 不得仅凭 AI 总结晋升；
- 不得仅凭一次门店判断晋升 active；
- 不得为了凑数制造伪 M-DEC。

## 8. 回填机制

必须说明：
1. 没有结果回填的决策，只是记录，不是记忆；
2. 回填周期建议 2–4 周；
3. 周复盘时检查 result_status: pending；
4. G03_Lint v2 后续可检查缺回填决策；
5. 回填失败也要记录，因为失败也是知识。

## 9. supersession 规则

给出格式：

```yaml
decision_status: superseded
superseded_by: "[[新决策文件]]"
superseded_reason: "价格带变化 / 客群变化 / 数据口径修正 / 竞争变化 / 用户签字修正"
superseded_at: 2026-06-22
```

要求：
1. 不删除旧决策；
2. 不用 decay；
3. 不用“过期”模糊处理；
4. 旧判断保留审计价值。

## 10. provenance 规则

要求：
每条正式结论至少有一个来源。

来源类型：
1. 门店案例；
2. 现场观察；
3. 脱敏数据摘要；
4. 周复盘；
5. 客户反馈；
6. 外部研究；
7. 已签 M-DEC。

禁止：
1. 不得把无来源 AI 判断写成 active；
2. 不得用 confidence score 替代来源；
3. 不得引用真实条码 / 真实敏感数据。

## 11. lint 检查建议

列出后续 G03_Lint v2 可检查项：

| 检查项 | 规则 |
|---|---|
| 缺 provenance | active / candidate M-DEC 必须有来源 |
| 缺 signoff | active 必须有 signoff |
| 缺回填 | result_status=pending 超 4 周提醒 |
| 孤儿决策 | 无入链 / 无索引 / 无 MOC |
| superseded 缺新链接 | 标 superseded 但无 superseded_by |
| 条码红线 | git tracked 文件真实 EAN-13 = 0 |

## 12. 30 天试运行

压缩原方案，不要设过高指标。

建议写：

第 1 周：
- 用模板记录 1–2 条花厅坊真实决策；

第 2–3 周：
- 回填至少 1 条结果；
- 检查是否能从决策追到来源；

第 4 周：
- 选 1 条最稳定记录，判断是否具备晋升潜力；
- 不强求晋升方法论；
- 重点看管道是否不断流。

## 13. 禁止事项

必须列出：

1. 不上 confidence score；
2. 不上 decay；
3. 不让 AI 自动写入 active；
4. 不提前上向量库；
5. 不提前上图数据库；
6. 不为追求孤儿归零破坏案例留痕；
7. 不让知识系统抢花厅坊主线注意力；
8. 不批量改现有 M-DEC；
9. 不把 draft 当 active；
10. 不用真实条码入 git。

## 14. 版本记录

记录：
v0.1：基于《零售知识系统 V2 迭代方案》提炼为 M-DEC 长期记忆系统 Schema 预览稿，未修改 CLAUDE.md，未改现有 M-DEC 正文。

---

# B. 试填样例

在同一文件末尾或新建附录中，选一条做“示例”，建议优先：

- M-DEC-010 休食小类价格带结构预警；
或
- M-DEC-013 单小类长尾结构治理候选。

要求：
1. 明确只是“试填样例”；
2. 不修改原 M-DEC 文件；
3. 不改变原 M-DEC status；
4. 不写真实条码；
5. 不写真实敏感销售额；
6. 以脱敏 / 抽象方式表达。

样例格式：

```markdown
## 试填样例：M-DEC-013 单小类长尾结构治理候选

- 记忆层：单店决策层 → 跨店规律层候选
- 现象：
- 决策：
- 推理：
- 来源::
  - [[T03饼干脱敏实跑]]
  - [[T01膨化脱敏实跑]]
  - [[T05果干脱敏实跑]]
- 结果：待后续复盘回填
- 状态：candidate
- 是否可晋升：暂不可，需第二客户 / 第二门店验证
- signoff：未签 active，仅作为候选样例
```

---

# C. 执行日志

追加 Claude执行日志：

标题：
2026-06-22｜P1-MEM-Schema-001｜M-DEC长期记忆系统Schema预览稿

记录：
- 新建 Schema 预览稿；
- 吸收 provenance / supersession / signoff / 四级记忆层 / 命名边；
- 未修改 CLAUDE.md；
- 未修改 M-DEC 正文；
- 未上自动化；
- 未执行全库重构；
- 下一步建议试运行 1 条真实 M-DEC。

---

# D. git diff 与 commit

完成后运行：

git status --short
git diff --stat

只允许 add 本轮新建的 Schema 预览稿和 Claude执行日志。

禁止：
git add .

commit message：

docs: 新增M-DEC长期记忆系统Schema预览稿

commit body：
- 基于零售知识系统 V2 迭代方案提炼 M-DEC 长期记忆系统 Schema；
- 明确 provenance 取代 confidence score；
- 明确 supersession 取代 decay；
- 明确 signoff 为人工写入闸门；
- 定义四级记忆层、实体类型、命名边、回填与晋升路径；
- 附 M-DEC 试填样例；
- 未修改 CLAUDE.md；
- 未修改现有 M-DEC 正文；
- 未引入自动化、向量库或图数据库。

---

# E. 完成后输出报告

# P1-MEM-Schema-001 完成报告

## 1. 执行结论

## 2. 新建文件路径

## 3. Schema 核心内容摘要

## 4. 试填样例结果

## 5. 未触碰范围

## 6. git diff 摘要

## 7. commit hash 与 message

## 8. 风险与未决问题

## 9. 下一步建议

下一步候选：
1. P1-MEM-Schema-Review-001｜人工审阅 Schema 预览稿
2. P1-MEM-MDEC-Trial-001｜用 1 条真实 M-DEC 跑完整 working→episodic→回填流程
3. P1-MEM-G03Lint-Rules-001｜把缺 provenance / 缺回填 / superseded 缺链接纳入 G03_Lint
4. P1-MEM-Index-Link-001｜将 Schema 文件挂入 Wiki治理方案 / MOC / 主定义索引