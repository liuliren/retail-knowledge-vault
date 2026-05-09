---
title: statusLine 使用规范
version: v0.1
status: review
owner: 六哥
created: 2026-05-04
updated: 2026-05-04
module: 11_系统产品与PRD/Claude Code 官方文档学习包
tags:
  - ClaudeCode
  - statusLine
  - 监控
  - 额度可视化
source_type: reference
confidence: medium
related:
  - "[[README]]"
  - "[[08_token与额度控制规范_v0.1]]"
  - "[[09_Claude_Code使用手册_v0.1]]"
---

# statusLine 使用规范

## 1. 文件定位

把 statusLine 的输入字段、适合展示什么、性能边界一次说清，作为本 vault 配置 statusLine 的依据（实际配置需单独授权）。

## 2. 适用场景

- 想"一眼看到上下文使用率与 5 小时额度"
- 多 worktree / 多会话切换时分辨当前在哪
- 老板演示前确认模型与 effort 设置

## 3. 核心机制

### 3.1 工作方式

Claude Code 把 JSON 通过 stdin 传给你的脚本，脚本输出文本，Claude Code 显示这一行（或多行）。

- 配置位置：`~/.claude/settings.json` 或 `.claude/settings.json` 的 `statusLine` 字段
- 触发：事件驱动；空闲时不会刷新
- 时间型字段需开 `refreshInterval`（最小 1s）

### 3.2 输入字段（官方 schema 节选）

`cwd` / `session_id` / `session_name` / `transcript_path` / `model.{id,display_name}` / `workspace.{current_dir,project_dir,git_worktree,added_dirs}` / `version` / `output_style.name` / `cost.{total_cost_usd,total_duration_ms,total_lines_added/removed}` / `context_window.{used_percentage,remaining_percentage,current_usage,context_window_size}` / `effort.level` / `thinking.enabled` / `rate_limits.{five_hour,seven_day}.{used_percentage,resets_at}` / `vim.mode` / `agent`

### 3.3 适合展示

- `model.display_name`
- `context_window.used_percentage`（**最关键**）
- `rate_limits.five_hour.used_percentage`
- `workspace.git_worktree`（如未来引入 worktree）
- `cost.total_cost_usd`（注意：订阅用户仅供参考）

### 3.4 边界

- 脚本卡住 → 拖累 UI
- `refreshInterval` 最小 1s；缺省只在事件触发时跑（主会话空闲时不刷新）
- **不要在 statusLine 里做网络调用 / 写文件**

## 4. 操作规则（本 vault，建议方向，不实施）

建议初版状态栏内容（一行版）：

```
[Opus | effort=high] | ctx 18% | 5h 23% | dir=retail-knowledge-vault
```

字段映射：
- `model.display_name` + `effort.level`
- `context_window.used_percentage`
- `rate_limits.five_hour.used_percentage`
- `workspace.current_dir` 末段

**注意**：当前贴的是**示意**，配置文件、jq 脚本、actual 路径需在实施时按官方 statusline.md 完整 schema 与你的环境逐字段验证。

### 隐私

- 客户演示 / 录屏前**关掉** `session_id` 显示（见 [[02_日志与transcript机制总结_v0.1]] §6）
- `cost.total_cost_usd` 对订阅用户是估值，不是账单

## 5. 待确认事项

- 本 vault 实际可用字段在当前 Claude Code 版本下的完整可用性（需 `claude --version` 后逐字段实测）

## 6. Sources

- [Status Line](https://code.claude.com/docs/en/statusline.md)

## 7. 关联上游

- [[README]]

## 8. 关联下游

- [[08_token与额度控制规范_v0.1]]（statusLine 是降本反馈回路的关键监控点）
- [[02_日志与transcript机制总结_v0.1]]（隐私字段交叉引用）

## 9. 版本记录

| 版本 | 日期 | 修改内容 | 修改人 |
|---|---|---|---|
| v0.1 | 2026-05-04 | 初次创建：从暂存预览 §9 入库 | 六哥 + Claude |
