---
title: Claude 双宪法边界声明
version: v0.1
status: active
owner: 六哥
created: 2026-06-24
updated: 2026-06-24
module: 00_入口与总索引/03_治理规范
task_id: P1-CLAUDE-Constitution-Boundary-001
summary: 裁定 /Users/CLAUDE.md(全局宪法)与 retail CLAUDE.md(项目宪法)的作用域、优先级与冲突裁决，止住双规则漂移。
tags:
  - 治理规范
  - CLAUDE宪法
  - 边界声明
  - agent_rules
source_type: governance
confidence: high
signoff:
  approved_by: 六哥
  approved_at: 2026-06-24
  approval_basis: P1-CLAUDE-Boundary-Active-Versioning-002
  approval_scope: 确认 /Users/CLAUDE.md 与 retail CLAUDE.md 的作用域、优先级、冲突裁决与红线继承规则；不代表重写任一宪法；不代表批量修改 summary 或业务正文。
  approval_status: approved
---

# Claude 双宪法边界声明（P1-CLAUDE-Constitution-Boundary-001）

## 0. 结论先行

1. **`/Users/CLAUDE.md` = 全局宪法**：管 Claude 在六哥**所有工作区**的通用行为红线;**`retail-knowledge-vault/CLAUDE.md` v2.2 = 项目宪法**:只在 retail vault 内生效。
2. **优先级**:`全局红线 > 项目红线 > 项目执行细则 > 单次 Prompt`。单次 Prompt **只能收窄、不能放宽**安全/Git/真实数据/execute/敏感红线。
3. **冲突裁决**:涉**安全/Git/真实数据/敏感/execute** → 取**更严者**(通常全局);涉 **retail 内部结构/命名/summary/query只读/agent_rules** → **retail 优先**;**无法判断 → 停下报告,不自行扩权**。
4. 本声明**不重写、不合并、不删除**任一宪法,只补边界、优先级、裁决。

---

## 1. 定位

| 文件 | 角色 | 一句话 |
|---|---|---|
| `/Users/CLAUDE.md`(v1.0) | **全局宪法** | Claude 在所有 vault 的通用价值观、协作契约与红线(主体性/批判陪练/隐私红线/keys-not-prompts) |
| `retail-knowledge-vault/CLAUDE.md`(v2.2) | **项目宪法** | retail vault 的知识工程治理(A–E 权限/G01–G11 回路/世界级交付标准/卡帕西闭环/数据红线) |
| 单次任务 Prompt | **任务边界** | 本轮允许/禁止文件、输出结构;只能在更严方向收窄 |

> 个人 vault(`David-Liu-Vault`)受**全局宪法 + 其自身 AGENTS.md/CLAUDE.md** 管辖,不受 retail 项目宪法约束(双库正交,见 retail §9)。

---

## 2. 优先级链(写死)

```
全局红线  >  项目红线  >  项目执行细则  >  单次 Prompt
```

1. 全局红线**不可**被项目规则覆盖。
2. 项目红线**不可**被单次 Prompt 覆盖。
3. 单次 Prompt **只能向更严方向收窄**权限。
4. 单次 Prompt **不得放宽**真实数据 / Git / execute / 敏感信息红线。

---

## 3. 管辖范围

| 规则来源 | 管辖范围 |
|---|---|
| `/Users/CLAUDE.md` | Claude 全局行为、所有 vault 通用红线(隐私、删除、对外发布、keys-not-prompts、批判陪练、写作铁律) |
| retail `CLAUDE.md` | retail vault 内:A–E 权限、raw/wiki/agent_rules、G01–G11 回路、summary、M-DEC、世界级交付标准、数据红线、git 纪律 |
| 单次 Prompt | 本轮任务边界、允许/禁止文件、输出结构 |

---

## 4. 冲突裁决规则

按冲突**类型**分流:

1. **安全 / Git / 真实数据 / 敏感信息 / execute 写回** → **更严者优先**(通常是全局或更严的一方)。
2. **retail vault 内部结构 / 命名 / summary / query 只读 / agent_rules** → **retail CLAUDE.md 优先**。
3. **单次 Prompt 与任一宪法冲突** → 取**更严格者**。
4. **无法判断** → **停止并报告**,不自行解释扩权。

---

## 5. 关键发现:全局 §4/§5 目录 schema 属"愿景态",非约束红线

> ⚠️ 本轮比对发现的最大歧义,必须显式处理:

`/Users/CLAUDE.md` §4「启动结构」与 §5「知识页规范」描述的 `10_sources/`、`30_wiki/(retail|build|growth|media)`、`50_private/`、`00_meta/` 等路径,**在磁盘上不存在**——既不匹配 retail vault(用 `00_入口与总索引`…`99_原始素材`),也不完全匹配个人 vault(用 `00_总控`…`80_个人资料_敏感`)。

**裁定**:全局宪法 **§4/§5 视为"愿景/初始设想",非生效红线**,**禁止任何 Agent 据此创建 `10_sources/`、`30_wiki/` 等新目录或据此判路径**。各 vault 的**实际目录结构以该 vault 自身的 CLAUDE.md/AGENTS.md 为准**。全局宪法中**生效**的是 §0–§3(主体性/原则/协作契约)、§7(隐私红线/keys-not-prompts)、§8(迭代纪律)等**原则与红线**层。

---

## 6. 隐私分层对照(T0–T3 ↔ A–E):互补,非冲突

两套词汇服务不同对象,**共享同一条客户红线**,不构成矛盾:

| 全局 T 层(隐私/个人) | retail A–E(工作数据分级) | 共同红线 |
|---|---|---|
| T0 公开 | E 对外简报 `client_shareable` | 0 术语 0 条码,脱敏后才出 |
| T1 专业可委托 | A 外部资料 / B 方法论 / C 客户项目(脱敏) | 杠杆主战场 |
| T2 私人 | C `client_confidential` / D `raw_sensitive` | 客户原始数据**只读冻结、不进 wiki、不上云** |
| T3 关系封存 | （仅个人 vault） | 默认不读,本地优先 |

**裁定**:retail vault 内用 **A–E**;个人/全局隐私用 **T0–T3**;两者在"客户机密铁律 + keys-not-prompts"上**完全一致**,以更严者执行。**不引入第三套分层。**

---

## 7. Git 与数据红线(向下继承)

全局未写 git 细则 → **retail 的 git 红线即为该 vault 的生效红线**,且任何 Prompt 不得放宽:

1. **禁止 `git add .`**;只 add 本轮明确产出的文件。
2. 真实 `xls / csv / db` **不入 Git**。
3. `dry-run / execute` 结果表**不入 Git**。
4. 真实条码 / 进价 / 供应商裸名**不进 tracked markdown**。
5. 运行态文件留在 **gitignored** 目录。

> 注:`KnowledgeBase/` 根**非** git 仓;`retail-knowledge-vault/` **是**独立 git 仓;`/Users/CLAUDE.md` 在所有仓之外(不受版本控制)。

---

## 8. raw / wiki / agent_rules 分层(retail 生效)

| 层 | 定位 | 写入规则 |
|---|---|---|
| **raw**（`99_原始素材`/xls/大文档） | 原始材料 | **物理只读**(`chmod a-w` + `.no-ingest`),进库即冻结 |
| **wiki**（方法论/概念页/MOC） | 人类可读知识 | 可人工整理、可重编译 |
| **agent_rules**（CLAUDE.md/AI互通总规则/本声明） | 机器执行规则 | 高压缩、可执行、少 token |

---

## 9. query 只读 + summary（retail 生效)

1. **query / search / retrieve 默认只读**:检索动作**不得触发写入**;默认只读编译层,raw 非授权不读入(retail §7 G02 编译层优先铁律)。
2. **summary**:低成本首轮检索字段,**不是正文替代**;**必须读正文后写,不得套话**(retail §7 G01 / §10.2)。

---

## 10. 维护机制

1. **全局宪法变更** = 单独任务,记 `/Users/log.md`。
2. **项目宪法变更** = 记 retail `98_AI协作中枢/00_总控/当前任务队列.md`。
3. **本边界声明变更** = 必须有 commit。
4. **不允许**在普通内容任务中顺手改宪法。
5. **不允许**一次批量重写两份宪法。

---

## 11. 本轮识别的冲突点清册

| 冲突类型 | 是否真冲突 | 说明 | 裁决 |
|---|---|---|---|
| 权限边界(T0–T3 vs A–E) | 否(词汇分轨) | 服务不同对象,共享客户红线 | §6 对照表,各管各域 |
| 目录 schema(§4/§5 vs 实际) | **是(歧义)** | 全局 §4/§5 路径磁盘不存在 | §5:全局 §4/§5 降为愿景态,非红线 |
| 操作回路命名(/ingest vs G01) | 否 | 同概念别名 | slash 命令 = G 系列的用户侧别名 |
| Git 规则 | 否(全局缺位) | 全局未写 | retail git 红线生效,不得放宽 |
| summary 字段 | 否 | 仅 retail 有 | retail 生效 |
| execute/dry-run 签字门 | 否 | 仅 retail 有 | retail 生效 |
| 真实数据红线 | 否(一致) | 两处都冻结只读 | 更严者执行 |
| vault 作用域 | **是(定位歧义)** | 全局文件内容像项目 schema | §1/§3:按作用域分,§5 纠正 |
| 自动开发边界 | 否 | retail §5 更严 | 更严者执行 |

---

## 12. 开放问题 / 下一步

1. 全局 `/Users/CLAUDE.md` §4/§5 是否择期**重写为真实结构或删除**?(本轮只声明其非红线,未改其正文 —— 需另起全局宪法专项任务 + 六哥签字)
2. 个人 vault `David-Liu-Vault` 是否需要一份与本声明对齐的"个人 vault 项目宪法"?
3. 本声明升 `active` 需六哥签字(retail §3①/§10.2 状态机)。
