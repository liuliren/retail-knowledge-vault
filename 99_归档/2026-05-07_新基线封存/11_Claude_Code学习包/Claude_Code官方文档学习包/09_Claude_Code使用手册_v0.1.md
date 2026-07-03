---
title: Claude Code 使用手册（综合）
version: v0.1
summary: 分散机制收敛成日常决策树：五原则、15大主题、6高频决策树、操作禁忌。
status: review
owner: 六哥
created: 2026-05-04
updated: 2026-05-04
module: 11_系统产品与PRD/Claude Code 官方文档学习包
tags:
  - ClaudeCode
  - 使用手册
  - 综合
  - 三个月生存战
  - 操作SOP
source_type: reference
confidence: medium
related:
  - "[[README]]"
  - "[[01_上下文与记忆机制总结_v0.1]]"
  - "[[03_slash命令速查_v0.1]]"
  - "[[04_subagents使用规范_v0.1]]"
  - "[[07_权限与安全红线_v0.1]]"
  - "[[08_token与额度控制规范_v0.1]]"
  - "[[10_待核验问题清单_v0.1]]"
---

# Claude Code 使用手册（综合）

> 三个月生存战的主操作手册。把分散在 01–08 的机制收敛成"日常怎么用"的决策树。

## 1. 文件定位

把"我现在要用 Claude Code 做 X，我应该怎么开/怎么用/怎么收"这件事讲清。

层级关系：
- 本手册 = 操作汇总（决策与流程）
- 01–08 = 各机制的事实与边界
- 10 = 待核验事项（手册中所有"待核验"标记都能回到 10 找到）

## 2. 适用场景

- 日常工作前 5 分钟扫一眼
- 培训新人 / 团队对齐
- 排查"为什么今天用得这么贵"

## 3. 三个月生存战的"五个原则"

1. **每个会话有边界**——明确这一会话要解决的一件事，做完即收
2. **省 token 不掉质量**——通过纪律省，而不是降标准省
3. **委派优于自做**——能交给 subagent / skill / CLI 工具的，不让主会话扛
4. **可观测优于猜**——statusLine + `/usage` + `/context` 三件套先开
5. **可回滚优于完美**——大改前 plan，改前可 `/rewind`，写前可 `/compact`

## 4. 与本知识库工作流最相关的 TOP 15 主题

按"知识库长期维护 + 三个月生存战 + 额度可控"打分，从高到低：

| # | 主题 | 解决什么 | 详见 |
|---|---|---|---|
| 1 | Memory（CLAUDE.md + auto memory） | 跨会话稳定指令 | [[01_上下文与记忆机制总结_v0.1]] |
| 2 | Context window / `/compact` | 上下文管理 | [[01_上下文与记忆机制总结_v0.1]] |
| 3 | Slash commands | 会话内控制 | [[03_slash命令速查_v0.1]] |
| 4 | Permissions | 拦截危险操作 | [[07_权限与安全红线_v0.1]] |
| 5 | Hooks | 自动化与防护（**默认不开**） | [[05_hooks使用规范_v0.1]] |
| 6 | Sub-agents | 隔离上下文、降本 | [[04_subagents使用规范_v0.1]] |
| 7 | Costs / token reduction | 控成本 | [[08_token与额度控制规范_v0.1]] |
| 8 | Status line | 一眼看 token / cost / branch | [[06_statusLine使用规范_v0.1]] |
| 9 | `.claude/` 目录结构 | 知道东西在哪 | [[02_日志与transcript机制总结_v0.1]] |
| 10 | Logs / transcript | 复盘原料 | [[02_日志与transcript机制总结_v0.1]] |
| 11 | Permission modes（plan） | 大改前先看路径 | [[07_权限与安全红线_v0.1]] |
| 12 | `/init` / `/memory` | 维护 CLAUDE.md | [[03_slash命令速查_v0.1]] |
| 13 | Skills（vs CLAUDE.md） | 减小常驻上下文 | [[01_上下文与记忆机制总结_v0.1]] |
| 14 | `.claude/rules/` 路径范围 | 大库分模块加载 | [[01_上下文与记忆机制总结_v0.1]] |
| 15 | Checkpointing / `/rewind` | 翻车回滚 | [[02_日志与transcript机制总结_v0.1]]（**待核验**：纯 markdown 是否完整入快照） |

## 5. 标准会话流程（默认 SOP）

### 5.1 开会话

```
1. 决定本会话目标（一句话）
2. /status —— 确认模型与 effort
3. 简单任务 → /effort low；复杂 → /effort medium 或 high
4. 多文件扫库的活 → 先想能不能交 Explore subagent
```

### 5.2 工作中

```
1. statusLine 实时看 ctx % + 5h %
2. 长任务前 /compact 关注 X
3. 每读一批文件，问自己"这个还能不能交 subagent"
4. 大改 vault 前 → 进 plan 模式（Shift+Tab）→ 看路径 → 退出再做
```

### 5.3 收会话

```
1. /usage —— 看本会话花费
2. 长 / 重要会话 → /rename 命名
3. 切主题 → /clear（旧会话保留可 /resume）
4. 同主题深入 → /compact，继续
```

## 6. 高频决策树

### 6.1 "上下文要爆了"

```
ctx 0–60% → 继续干
ctx 60–80% → 准备 /compact 关注当前主题
ctx 80–95% → 立即 /compact
ctx > 95% → /clear（先 /rename 再清，必要时 /resume 找回）
```

### 6.2 "额度要爆了（5 小时窗口）"

```
5h < 50% → 正常
5h 50–80% → 把 effort 降到 medium / low；考虑模型从 Opus → Sonnet
5h > 80% → 当天主任务收尾，停一停
```

### 6.3 "Claude 一直不听指令"

```
1. /memory 看加载列表
   ├── 缺关键文件 → 检查 CLAUDE.md / .claude/rules 路径
   ├── 文件加载了但内容自相矛盾 → 拆/改 CLAUDE.md
   └── 都对 → 把口头指令补进 CLAUDE.md（口头指令 /compact 后会丢）
2. 简化指令的措辞（"用 2 空格缩进"优于"格式化代码"）
```

### 6.4 "改坏了想回滚"

```
文件改坏 → /rewind 或双击 ESC（前提是 file-history 写入正常，待核验）
会话方向跑偏 → ESC 中断 → 重新提问
切错主题 → /resume 找旧会话
```

### 6.5 "要做高吞吐扫库"

```
是否信息少、回合短？
├── 是 → 主会话直接做
└── 否 → 委派
    ├── 一次性 → Explore 子代理（内置）
    ├── 重复 → 写个 .claude/agents/<name>.md（用 Haiku）
    └── 需主会话历史 → fork（不是 named subagent）
```

### 6.6 "要不要开 hook"

```
本阶段：默认不开
要开的话先问：
1. 能不能用 skill / subagent / 手动命令替代？能 → 不开
2. 要不要发 HTTP 出站？要 → 不开
3. 要不要静默改 tool_input？要 → 不开
4. 装第三方插件含 hook？看其 hooks.json 含上述任一 → 不装
```

## 7. 操作禁忌（与本 vault 治理对齐）

1. 编造门店数据 / 商品数据（[[反幻觉检查清单]]）
2. 把暂存素材直接当成正式结论
3. 让 Claude 删除重要项目资料（应 `Edit(/99_归档/**)` deny）
4. 在客户演示时显示 `session_id` / `transcript_path`
5. 把含敏感信息的 `*.jsonl` 同步到云盘
6. 用 Opus + max effort 做"周报""今日总结"等简单任务
7. 把"指令"放进 hook 的 `additionalContext`（=提示注入）
8. 用通配符在 Bash 规则里限 URL（不可靠）
9. 用 `bypassPermissions` 模式做日常工作

## 8. 与 vault 其他规则的对齐

- 反幻觉：本手册任何"操作建议"必须在 01–08 中能找到机制依据
- 逻辑一致性：与 [[知识库治理规范]] / [[文档工程化标准]] 不冲突
- 可执行性：每条规则都说明"什么时候做 / 怎么做"，不只是"应该 X"

## 9. 待确认事项

本文件作为综合手册，所有"待核验"项汇总在 [[10_待核验问题清单_v0.1]]，读者请直接以该清单为准。

## 10. Sources

本文件是 01–08 的汇总，主源包括：

- [Memory](https://code.claude.com/docs/en/memory.md)
- [Context Window](https://code.claude.com/docs/en/context-window.md)
- [Commands](https://code.claude.com/docs/en/commands.md)
- [Sub-agents](https://code.claude.com/docs/en/sub-agents.md)
- [Hooks Reference](https://code.claude.com/docs/en/hooks.md)
- [Status Line](https://code.claude.com/docs/en/statusline.md)
- [Permissions](https://code.claude.com/docs/en/permissions.md)
- [Costs](https://code.claude.com/docs/en/costs.md)
- [.claude Directory](https://code.claude.com/docs/en/claude-directory.md)
- [Best Practices](https://code.claude.com/docs/en/best-practices.md)（本轮未抓全文，待回查）

## 11. 关联上游

- [[README]]
- [[00_官方文档目录索引_v0.1]]

## 12. 关联下游

- 本包内 01–08 全部主题文件
- [[10_待核验问题清单_v0.1]]
- 未来在 `00_入口与总索引/` 派生的"Claude Code 操作速查卡"

## 13. 版本记录

| 版本 | 日期 | 修改内容 | 修改人 |
|---|---|---|---|
| v0.1 | 2026-05-04 | 初次创建：综合 01–08 主题，建立决策树与会话 SOP | 六哥 + Claude |
