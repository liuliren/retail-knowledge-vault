---
title: Subagents 使用规范
version: v0.1
summary: Subagent与fork区分、何时用、文件位置、工具白名单、本vault配置建议。
status: review
owner: 六哥
created: 2026-05-04
updated: 2026-05-04
module: 11_系统产品与PRD/Claude Code 官方文档学习包
tags:
  - ClaudeCode
  - subagents
  - 子代理
  - 上下文隔离
  - 降本
source_type: reference
confidence: medium
related:
  - "[[README]]"
  - "[[01_上下文与记忆机制总结_v0.1]]"
  - "[[08_token与额度控制规范_v0.1]]"
  - "[[09_Claude_Code使用手册_v0.1]]"
---

# Subagents 使用规范

## 1. 文件定位

判断"什么任务该交给 subagent / 什么不该"，并给出本 vault 的初步配置方向（不实施，仅记录）。

## 2. 适用场景

- 准备把"扫 vault 全量""跨多门店比对""读长 Excel"等任务委派出去
- 遇到主会话 context 已经吃紧
- 想做受控审查（限 Read/Grep，禁 Write）
- 复盘"上一周哪些任务该用 subagent 但没用"

## 3. 核心机制

### 3.1 何时用

- **一次性高吞吐"读多写少"工作**（扫 vault、跨多门店比对、处理长 Excel / POS 导出）
- **重复出现的同类副任务**（每周做"陈列规则一致性扫描"）→ 写成 named subagent
- **想限制工具集**（只给 Read/Grep，禁 Write）做受控审查

### 3.2 何时不用

- 信息少、上下文小、回合短的任务（spawn 本身有冷启动成本）
- 需要主会话**已有的对话上下文** → 用 **fork**（继承历史），不是 named subagent
- 多代理需互相通信、并行 → 用 **agent teams**（注意约 7× token），本阶段不开

### 3.3 文件位置 / 关键 frontmatter

- `.claude/agents/*.md`（项目）
- `~/.claude/agents/*.md`（用户）
- CLI `--agents` JSON（一次性，不入盘）

字段（部分；**待核验**：完整字段表对照官方 sub-agents 完整文档逐项校验，见 [[10_待核验问题清单_v0.1]]）：

| 字段 | 作用 |
|---|---|
| `name` | 子代理名 |
| `description` | 决定 Claude 是否自动派发——写得宽 = 容易被滥用 |
| `tools` | 工具白名单（受控审查时只放 Read/Grep） |
| `model` | 推荐 Haiku 控本 |
| `memory` | `project` / `local` / `user` 三种持久记忆位置 |
| `initialPrompt` | 启动时自动提交的第一轮 |

### 3.4 风险

- 子代理本身要加载 CLAUDE.md / MCP / skill 列表，越多越贵
- 内置 subagent 的 `description` 决定是否被自动派发，写得宽会被滥用
- `agent-memory/` 与主会话 auto memory 是**两套**目录，注意区分

### 3.5 fork vs named subagent

- **fork**：继承当前会话的全部历史与系统提示，做"分身"——同一上下文跑多条路径。
- **named subagent**：完全独立 context，从零开始，只回主会话一个总结。

## 4. 操作规则（本 vault，建议方向，不实施）

1. 第一个 named subagent 候选：**陈列规则一致性扫描器**——周期性扫 `06_陈列规划与DisplayMap/` 与各门店 `09_门店案例与项目复盘/<店>/05_陈列整改/`，模型用 Haiku，工具限 `Read` `Grep` `Glob`。
2. 第二个候选：**反幻觉巡检员**——按 `[[反幻觉检查清单]]` 扫真实门店相关结论，标出"未注明依据""推断当事实"等问题。
3. 主会话遇到大批量 vault 扫描，优先 `Agent` 调度 Explore 子代理（已内置）而不是自己 grep。
4. **不要**为单文件、短任务建 subagent——成本高于收益。
5. **不要**开 agent teams。

## 5. 待确认事项

- subagent 完整 frontmatter 字段表（见 [[10_待核验问题清单_v0.1]] #6）
- agent-memory（subagent 持久记忆）与主 auto memory 的协作边界（同上 #6）

## 6. Sources

- [Sub-agents](https://code.claude.com/docs/en/sub-agents.md)
- [Costs - Agent team token costs](https://code.claude.com/docs/en/costs.md)

## 7. 关联上游

- [[README]]
- [[01_上下文与记忆机制总结_v0.1]]

## 8. 关联下游

- [[08_token与额度控制规范_v0.1]]
- [[09_Claude_Code使用手册_v0.1]]

## 9. 版本记录

| 版本 | 日期 | 修改内容 | 修改人 |
|---|---|---|---|
| v0.1 | 2026-05-04 | 初次创建：从暂存预览 §7 入库 | 六哥 + Claude |
