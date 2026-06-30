---
description: Generate a structured handoff document and resume prompt before /compact or /clear. Use when compact recommends compact/clear, when the user asks for a "handoff", "交接", "新会话 prompt", "session summary", or when explicitly asked to prepare for a fresh Claude Code session.
allowed-tools: Bash(git status:*), Bash(git log:*), Bash(git diff:*), Bash(ls:*), Read, Write
---

# Project Handoff

你是当前项目的 Claude Code 会话交接生成助手。

你的任务是：在用户决定 `/compact` 或 `/clear` 前 / **生成一份结构化 handoff 文档** + **可粘贴的新会话启动 prompt**。

## 触发场景

- compact skill 建议 compact / clear
- 用户主动要求"handoff" / "交接" / "新会话 prompt" / "整理上下文"
- 长会话（≥ 4h / ≥ 8 commits / 任务阶段完整收口）
- 跨业务模块切换（数据底座 → 治理 / 业务 → 工具）

## 强制前置检查（不可跳）

运行：

```bash
git status --short
git log --oneline -15
git diff --check
```

**必须满足 / 否则停止**：

```
✅ 工作区 clean（或仅 1-3 个已复查 / 等用户拍板 commit）
✅ 0 真实数据 xls / xlsx / rar / csv 在 staged
✅ 0 空白错误（diff --check 通过）
```

否则：先输出工作区异常报告 / 等用户处理 / 不生成 handoff。

## 强制边界（与 compact §强制边界 完全一致）

```
❌ 不清洗真实数据
❌ 不生成 SKU 清单
❌ 不输出商品名 / 品牌名 / 条码 / 销售金额 / 销量明细
❌ 不生成方便速食 v0.6 结论
❌ 不启动调改
❌ 不提交 xls / xlsx / rar / csv / 真实经营数据
❌ 不修改已完成 BUS-DATA / BUS-TOOL / 命名规范文件
❌ 不自动 commit
❌ 不自动执行 /compact 或 /clear
```

## handoff 文档结构（必须包含）

文件路径：

```
13_数据分析与工具脚本/_claude_context/handoff_YYYYMMDD_HHMMSS.md
```

或用户指定路径。

frontmatter：

```yaml
---
title: 会话交接 YYYY-MM-DD HH:MM
version: v0.1
status: handoff
quadrant: governance
project: <战役名 或 cross_client>
phase: handoff
source_type: session_handoff
created: YYYY-MM-DD
updated: YYYY-MM-DD
session_topic: <主题>
session_duration: <小时>
session_commits: <数量>
session_main_outputs:
  - <主要产出 1>
  - <主要产出 2>
tags:
  - 会话交接
  - context_handoff
  - claude_code_session
---
```

正文 8 段：

### §1 会话基本信息

- 起止时间
- 主题
- commit 数 + commit hash 范围
- 主要任务

### §2 当前 vault 治理状态

- HEAD commit hash
- 工作区状态（clean / dirty）
- 关键已落地（BUS-DATA / GOV-AUDIT / BUS-TOOL / 治理 / 业务 命名清单 + commit hash）
- 关键文件路径（5-10 个 / 不超 15 个）

### §3 强制边界（务必复制到新会话）

完整复制 compact §强制边界。

### §4 关键 fact_layer.client_told（反幻觉）

- 4/25 调改 = 4/25 晚上（六哥 5/10 confirm）
- 供应商 + 进价系统可导出（生鲜进价未入系统）
- 0206% = 方便食品独立大类（020601 = 方便面 / 等同方便速食原口径**待 5/13 启明 confirm**）
- 5/10 已收 16 文件 / 含方便食品 30 天 + 日均销售 + 库存积压（仅 020601 子集）+ 主商品档案 + 等
- 5/8 已收 / 方便食品销量排行 90 天（aggregate / 0206%）

### §5 当前阶段定位

- 战役（如花厅坊样板战役 #1 / W18-W22 / 5/30 G05）
- 数据底座主线（如 BUS-DATA-001~007C 已闭环 / 008 暂不满足）
- 工具链（如 BUS-TOOL-001 xls→xlsx 已可用）
- 治理状态（如 vault v3.0 设计稿 v0.5 / 命名规范三件套 / GOV-AUDIT-001 v0.1）

### §6 关键缺口与待确认

5-10 项关键缺口（用 优先级 + 触发日 + 责任侧 标注）：

```
🔴 P0 库存（完整方便食品 / 5/12 启明）
🔴 P0 0206% 口径（5/13 启明现场 confirm）
🔴 P0 sign off 5 件 + ⑥⑦（5/13-5/15 启明）
🟡 P1 数据质量等级（A-E 评定规则 / W21）
🟡 P1 M-DEC alias（140 处短码 / W21）
...
```

### §7 下一步候选（按优先级 / 不自动执行）

- 立即（5/12-5/13）
- W21（治理 + 数据）
- W22+（5/30 G05 后）

### §8 新会话启动 prompt（可直接粘贴）

```text
我是 6 哥 / 晟果新零售咨询 / 乐易购花厅坊店项目。

先读以下交接文档快速进入状态：
- [[13_数据分析与工具脚本/_claude_context/handoff_<timestamp>]]

当前 HEAD = <commit hash>
工作区 clean。

强制边界（必读 §3）：
- 不清洗真实数据 / 不出 SKU 清单 / 不出 v0.6 结论
- 不启动调改 / 不提交 xls / xlsx / rar / csv / 真实经营数据
- 不改既有 BUS-DATA / BUS-TOOL / 命名规范文件 / 不自动 commit

当前任务：<具体任务名 / 或"等待指令">

特别注意（fact_layer.client_told）：
- 4/25 调改 = 4/25 晚上
- 0206% = 方便食品（待 5/13 启明 confirm 等同方便速食原口径）
- 启明 sign off 5+2 = 7 件待 5/13-5/15
```

## 不执行 / 不替代

- ❌ 不替代 compact（决策何时 compact）
- ❌ 不自动 /compact 或 /clear（用户主动）
- ❌ 不替代用户最终选择
- ❌ 不修改既有项目文件

## 输出后建议

```
1. 用户 review handoff 文档
2. 用户决定 /compact / /clear / 继续
3. 若 /clear / 用户用 §8 prompt 启动新会话
4. 若 /compact / 用户继续当前会话 / handoff 作 audit-log
```

## 版本

| 版本 | 日期 | 说明 |
|---|---|---|
| v1.0 | 2026-05-10 W20-Day1 | 初版 / TOOLING-CTX-002 / 与 compact 协同 |
