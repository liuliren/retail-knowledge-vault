---
title: Claude Code slash 命令速查
version: v0.1
summary: 18条内置slash命令、触发场景、高频决策树、日常快速翻阅表。
status: review
owner: 六哥
created: 2026-05-04
updated: 2026-05-04
module: 11_系统产品与PRD/Claude Code 官方文档学习包
tags:
  - ClaudeCode
  - slash命令
  - 速查
  - 操作
source_type: reference
confidence: medium
related:
  - "[[README]]"
  - "[[01_上下文与记忆机制总结_v0.1]]"
  - "[[08_token与额度控制规范_v0.1]]"
  - "[[09_Claude_Code使用手册_v0.1]]"
---

# Claude Code slash 命令速查

## 1. 文件定位

按"何时用"组织内置 slash 命令，作为日常高频翻阅件。

## 2. 适用场景

- 不记得某个命令叫什么时
- 培训新人 / 自己复习
- 排查"为什么会话变慢 / token 用得快"

## 3. 命令速查表

来自官方 `commands.md`（仅内置；不含 skill 与第三方）：

| 命令 | 说明 | 何时用 |
|---|---|---|
| `/clear`（别名 `/reset` `/new`） | 开新会话、清上下文，旧会话保留可 `/resume` | 主题切换 |
| `/compact [指令]` | 总结当前会话以释放上下文，可指定保留重点 | 长会话变慢前、新长任务前 |
| `/context` | 当前 context 占用色块图与优化提示 | 怀疑爆窗时 |
| `/usage`（=`/cost`=`/stats`） | 本会话 token、订阅额度条、活跃统计 | 周期性检查 |
| `/config`（=`/settings`） | 主题 / 模型 / 输出风格交互配置 | — |
| `/status` | 状态面板（版本 / 模型 / 账户 / 连接），响应中也能用 | 排错 |
| `/model [model]` | 切模型；带方向键调 effort | 难度切换 |
| `/effort [low\|medium\|high\|xhigh\|max\|auto]` | 调推理深度，立即生效 | 简单任务降到 low 省 token |
| `/init` | 生成 / 改进 CLAUDE.md（已存在则给建议） | 已用过 |
| `/memory` | 列出本会话加载的所有 CLAUDE.md / rules，开关 auto memory | 排查"指令没生效" |
| `/permissions` | 查看 / 管理权限规则 | 加白 / 降扰 |
| `/agents` | 管理 subagent | 配子代理 |
| `/mcp` | 查看 / 禁用 MCP 服务器 | 减 MCP 噪声 |
| `/statusline` | 配置 / 删除状态栏 | — |
| `/add-dir` | 给 Claude 加额外可访问目录 | 跨库工作 |
| `/rewind` | 回滚到上个 checkpoint | 翻车 |
| `/rename` | 重命名当前会话（便于以后 `/resume`） | 长会话清理前 |
| `/resume` | 恢复旧会话 | — |
| `/help` | 帮助 | — |
| `/claude-api [migrate \| managed-agents-onboard]` | 加载 Claude API 参考 / 升级模型 ID | 不适用本 vault |

## 4. 决策树（高频场景）

```
当前会话变慢 / 想省 token？
├── 切主题 → /clear（旧会话保留）
├── 同主题深入 → /compact 关注 X
└── 想看占用 → /context

上下文丢指令？
├── /memory 看加载列表
└── 必要时把口头指令补进 CLAUDE.md

简单 / 复杂任务切换？
├── 简单 → /effort low
├── 高难复盘 → /effort high
└── 切模型 → /model

回滚？
├── 文件改坏 → /rewind 或双击 ESC
└── 会话方向跑偏 → ESC 中断 + 重新提问
```

## 5. 使用纪律（本 vault）

1. 长会话前先 `/rename` 命名，方便 `/resume`
2. 切大主题前 `/clear`；同主题压缩前 `/compact`
3. 简单任务做完 `/effort` 升回默认（避免长期 low 影响后续复杂任务）
4. 怀疑额度异常 → `/usage` 看一眼
5. 给客户演示前 `/status` 检查模型版本

## 6. 待确认事项

- **`/btw`**：官方 `commands.md` 主表中**未直接列出**；可能是 skill / 别名 / 已废弃。**待核验**：在会话内键入 `/` 看下拉，或抓 `interactive-mode.md` 与最近 `whats-new` 验证（见 [[10_待核验问题清单_v0.1]] #1）。

## 7. Sources

- [Commands](https://code.claude.com/docs/en/commands.md)

## 8. 关联上游

- [[README]]
- [[00_官方文档目录索引_v0.1]]

## 9. 关联下游

- [[01_上下文与记忆机制总结_v0.1]]（`/compact` `/clear` `/resume` 机制详解）
- [[08_token与额度控制规范_v0.1]]（`/effort` `/model` `/usage` 在降本中的位置）

## 10. 版本记录

| 版本 | 日期 | 修改内容 | 修改人 |
|---|---|---|---|
| v0.1 | 2026-05-04 | 初次创建：从暂存预览 §6 入库 | 六哥 + Claude |
