---
title: 晟果新零售M-DEC长期记忆系统Schema
version: v0.1
status: candidate
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

# 晟果新零售M-DEC长期记忆系统Schema v0.1（candidate）

> **candidate（2026-06-22 P1-GOV-Batch-011 升级）**。本文件提炼自《零售知识系统 V2 迭代方案》（已归档 [[99_原始素材/战略源料/2026-06-22_进化新思路/README]]），采「最简正确版」：吸收 V2 的**问题意识**，拒绝其**工程复杂度**。**不改 CLAUDE.md、不改任何 M-DEC 正文、不上自动化**。

> **🔖 candidate 状态说明（P1-GOV-Batch-011）**：
> - ✅ **已通过结构审阅**（P1-GOV-Control-010 §B：五原则与 CLAUDE/治理零冲突、四级记忆层与 status 状态机正交不打架、模板可执行）；
> - ⚠ **未完成真实 M-DEC trial**（尚无实跑验证）；
> - ❌ **不具备 active 条件**；
> - **升 active 的两个前置**：① P1-MEM-MDEC-Trial-001（≥1 条真实 M-DEC 跑完 working→episodic→回填全流程）；② 六哥 signoff（CLAUDE §3②）。

## 0. 文件定位
1. 本文件是 M-DEC 长期记忆系统的 **Schema 预览稿**；
2. **不是** CLAUDE.md 替代品（CLAUDE.md 是执行宪法）；
3. **不是** M-DEC 规则正文；
4. **不是**自动化脚本；
5. 用于规范「现场决策**如何进入**知识体系、**如何回填**、**如何晋升**、**如何被取代**」。

## 1. 总判断：采最简正确版
1. V2 是**菜单，不是规格书**；
2. 采纳其**问题意识**（现场决策回流闭环），不照搬工程复杂度；
3. 当前阶段最重要的是**现场判断回流**，不是机器自动化；
4. 知识系统是零售诊断的「**记忆型马具**」，目标是**增强判断**，不是制造新战场（呼应 CLAUDE §1 驭马人层）。

## 2. 与现有治理体系的关系
| 现有文件 / 机制 | 本 Schema 与其关系 |
|---|---|
| [[CLAUDE.md]] v2.2 | CLAUDE.md 是执行宪法；本文件是 M-DEC 记忆规则（执行层细则） |
| [[晟果新零售科学零售Wiki知识体系治理方案_v1.0]] | Wiki 治理方案管**全库治理**；本文件管**决策记忆闭环** |
| 术语口径统一表 | 术语一律以 [[晟果新零售科学零售术语口径统一表_v1.0]] 为准 |
| signoff | 沿用 signoff 作为**人工写入闸门**（CLAUDE §3②） |
| G03_Lint v2 | 后续可检查孤儿决策 / 缺回填 / 缺 provenance / 缺 signoff |
| M-DEC 候选池 | 本文件规范 M-DEC 从 candidate → active 的**晋升路径** |

## 3. 五条设计原则

### 3.1 provenance 取代 confidence score
- **不打** 0.85 这种假精确置信度；
- 所有结论必须**挂来源**；
- 可信度来自**可见证据链**，不来自数字。

### 3.2 supersession 取代 decay
- 决策**不过期，只被取代**；
- 旧判断**保留**（审计价值）；
- 新判断出现时用 `被取代::` 显式连接；
- 保留「当时为什么这么判断」的审计轨迹。

### 3.3 signoff 作为人工写入闸门
- AI 可生成 **draft**；
- 进入 active / 跨店规律层 / 标准动作层**必须 signoff**；
- 没有 signoff，**不得**作为正式规则或客户交付依据。

### 3.4 四级记忆层（中文命名优先，不让英文压过业务语言）
| 记忆层 | 对应 | 说明 |
|---|---|---|
| **现场观察层** | working | 当天看到的问题 / 数据 / 现象 |
| **单店决策层** | episodic | 一次完整 M-DEC 判断 |
| **跨店规律层** | semantic | 多店验证后的经营规律 |
| **标准动作层** | procedural | SOP / 模板 / RetailOS 动作 |

### 3.5 schema 承载 90%，机器后置
- 先用**规则、模板、字段、signoff** 跑通；
- 手动跑过几十轮再谈自动化；
- 未到规模线，**不上向量库 / 图数据库**。

## 4. 实体类型（仅定义 Schema，本轮不建实体文件）
| 实体 | 用途 | 最小字段 |
|---|---|---|
| Store 门店 | 门店上下文 | store_id / 业态 / 面积 / 客群 / 项目状态 |
| Category 品类 | 品类对象 | category_name / L1-L5 / CDT / H-Score |
| SKU | 单品对象 | sku_name / category / H-Score / 脱敏状态 |
| IssueTag 问题标签 | 问题类型 | issue_code / issue_name / severity |
| Decision 决策 | M-DEC 核心 | 现象 / 决策 / 推理 / 来源 / 结果 / 状态 |
| Case 案例 | 项目证据 | project / store / date / output |
| Method KB 方法论 | 跨案例沉淀 | 来源 / 适用条件 / 限制条件 / signoff |

## 5. 命名边规则（Obsidian 可用）
```
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
1. 同一现象在不同门店重复出现，**不视为重复，而是新证据**；
2. 去重按 **provenance 身份**，不按文字相似度；
3. 真冲突进入**待审**，不自动合并；
4. 不要求每条都有全部命名边，但 `来源::` **必须优先**。

## 6. M-DEC 最小记录模板（30 秒可口述）
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
配套 frontmatter 建议：
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
> 本轮**只定义模板，不改现有 M-DEC 文件**。

## 7. M-DEC 晋升路径
1. 现场观察层 → 单店决策层；
2. 单店决策层 → **回填结果**；
3. 多个独立场景验证 → 跨店规律层；
4. 跨店规律层 → 标准动作层；
5. 进入 active / 标准动作层**必须 signoff**。

**默认门槛**：≥3 个独立场景验证且结果方向一致。
**例外通道**：强证据 + 用户 signoff 可提前晋升，但**必须写明例外理由**。
**禁止**：① 仅凭 AI 总结晋升；② 仅凭一次门店判断晋升 active；③ 为凑数制造伪 M-DEC。

## 8. 回填机制
1. 没有结果回填的决策，**只是记录，不是记忆**；
2. 回填周期建议 **2–4 周**；
3. 周复盘时检查 `result_status: pending`；
4. G03_Lint v2 后续可检查缺回填决策；
5. **回填失败也要记录**——失败也是知识。

## 9. supersession 规则
```yaml
decision_status: superseded
superseded_by: "[[新决策文件]]"
superseded_reason: "价格带变化 / 客群变化 / 数据口径修正 / 竞争变化 / 用户签字修正"
superseded_at: 2026-06-22
```
要求：① 不删旧决策；② 不用 decay；③ 不用「过期」模糊处理；④ 旧判断保留审计价值。

## 10. provenance 规则
每条正式结论**至少一个来源**。来源类型：① 门店案例；② 现场观察；③ 脱敏数据摘要；④ 周复盘；⑤ 客户反馈；⑥ 外部研究；⑦ 已签 M-DEC。
禁止：① 无来源 AI 判断写成 active；② 用 confidence score 替代来源；③ 引用真实条码 / 真实敏感数据。

## 11. lint 检查建议（后续 G03_Lint v2）
| 检查项 | 规则 |
|---|---|
| 缺 provenance | active / candidate M-DEC 必须有来源 |
| 缺 signoff | active 必须有 signoff |
| 缺回填 | result_status=pending 超 4 周提醒 |
| 孤儿决策 | 无入链 / 无索引 / 无 MOC |
| superseded 缺新链接 | 标 superseded 但无 superseded_by |
| 条码红线 | git tracked 文件真实 EAN-13 = 0 |

## 12. 30 天试运行（不设过高指标）
- **第 1 周**：用模板记录 1–2 条花厅坊真实决策；
- **第 2–3 周**：回填至少 1 条结果；检查能否从决策追到来源；
- **第 4 周**：选 1 条最稳定记录，判断是否具晋升潜力；不强求晋升；**重点看管道是否不断流**。

## 13. 禁止事项
1. 不上 confidence score；2. 不上 decay；3. 不让 AI 自动写入 active；4. 不提前上向量库；5. 不提前上图数据库；6. 不为孤儿归零破坏案例留痕；7. 不让知识系统抢花厅坊主线注意力；8. 不批量改现有 M-DEC；9. 不把 draft 当 active；10. 不用真实条码入 git。

---

## 附：试填样例（仅示例·不改原 M-DEC 文件）

> **声明**：以下为 Schema 试填**样例**，**不修改** [[M-DEC-013]] 原文、**不改变其 status**，以**脱敏/抽象**方式表达，无真实条码/真实销售额。

### 试填样例：M-DEC-013 单小类长尾结构治理候选
- **记忆层**：单店决策层 → 跨店规律层候选
- **现象**：单一小类内 SKU 数偏多但贡献集中度低，长尾 SKU（销额 C 段）占架面比例过高，挤占核心品排面（脱敏：占比为抽象区间，非真实数值）。
- **决策**：对该小类执行长尾结构治理——按双维 ABC + 商品角色闸筛出「双低且非目的品」候选汰换，腾出排面给核心引擎与利润品。
- **推理**：长尾 SKU 拉低小类周转与坪效；先过角色闸保护目的品/引流品，再过误判 4 问，避免误杀利润品（销额 C+毛利甲）。
- `来源::`
  - [[T03饼干脱敏实跑]]
  - [[T01膨化脱敏实跑]]
  - [[T05果干脱敏实跑]]
- **结果**：待后续复盘回填（result_status: pending）
- **状态**：candidate
- **是否可晋升**：暂不可——需**第二客户 / 第二门店**独立验证（当前仅花厅坊单店三小类，属同店多小类，非跨店独立场景）。
- `signoff`：未签 active，仅作候选样例。

> 说明：该样例命中本 Schema 多条规则——`来源::` 优先（3 条脱敏实跑作 provenance）、晋升门槛未达（需跨店≥3 独立场景）、回填待办（result_status: pending）、未 signoff 故不可作正式规则。

## 版本记录
| v0.1 | 2026-06-22 | P1-MEM-Schema-001：基于《零售知识系统V2迭代方案》提炼M-DEC长期记忆系统Schema预览稿；provenance取代confidence score / supersession取代decay / signoff人工闸门 / 四级记忆层 / 实体类型 / 命名边 / 回填与晋升路径；附M-DEC-013试填样例；未改CLAUDE.md / 未改M-DEC正文 / 未引入自动化·向量库·图数据库 |
