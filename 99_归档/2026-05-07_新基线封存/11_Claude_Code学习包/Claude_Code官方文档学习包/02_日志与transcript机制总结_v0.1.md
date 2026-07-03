---
title: 日志与 transcript 机制总结
version: v0.1
summary: 会话全明文落盘位置与隐私护栏、/rewind回滚依赖、月度复盘蒸馏机制建议。
status: review
owner: 六哥
created: 2026-05-04
updated: 2026-05-04
module: 11_系统产品与PRD/Claude Code 官方文档学习包
tags:
  - ClaudeCode
  - transcript
  - 日志
  - 复盘
  - 隐私
  - 文件快照
source_type: reference
confidence: medium
related:
  - "[[README]]"
  - "[[01_上下文与记忆机制总结_v0.1]]"
  - "[[09_Claude_Code使用手册_v0.1]]"
---

# 日志与 transcript 机制总结

## 1. 文件定位

说清楚 Claude Code 在本机会写哪些数据、写到哪里、可不可以拿来复盘、有没有隐私风险。

## 2. 适用场景

- 月度复盘脚本（蒸馏 transcript 提取高频问题、翻车案例）
- 排查"我之前是怎么让 Claude 改 X 的"
- 评估是否要把 transcript 入版本控制（默认：不入）
- 评估对外输出材料前的脱敏

## 3. 核心内容

### 3.1 落盘位置（基于 `~/.claude/`）

| 路径 | 内容 |
|---|---|
| `projects/<project>/<session>.jsonl` | 完整会话 transcript：每条消息 / 工具调用 / 工具结果 |
| `projects/<project>/<session>/tool-results/` | 大块工具输出（WebFetch、长 grep 等） |
| `projects/<project>/memory/MEMORY.md` + 主题文件 | 该项目 auto memory |
| `file-history/<session>/` | 改动文件的预改快照（用于 `/rewind` 回滚） |
| `history.jsonl` | 你输入过的所有提示，含时间戳与项目路径（上箭头召回用） |

`<project>` 由 git 仓库路径派生；同一仓库的 worktree 与子目录共享一个 auto memory 目录。**待核验**：非 git 仓库（如本 vault）时具体派生规则、跨 worktree 的实测一致性（见 [[10_待核验问题清单_v0.1]] #4）。

### 3.2 重要属性

- **全部明文**：markdown / jsonl，**任何过工具的内容都会落盘**——文件内容、命令输出、粘贴文本均在内
- **机器本地**：不跨机器、不上云
- **hooks 可读**：hook 上下文中能拿到 `transcript_path`（用于审计或自动复盘提取）
- **statusLine 可见**：`session_id`、`transcript_path` 同样在 stdin JSON 里

### 3.3 与 `/rewind` 的关系

`file-history/<session>/` 保留改动前快照，配合 `/rewind`（双击 ESC）可回滚文件改动。**待核验**：纯 markdown 写入是否完整入快照（见 [[10_待核验问题清单_v0.1]] #5）。

## 4. 已确认事实

以上 3.1–3.3 直接来自官方 claude-directory.md。

## 5. 操作规则（本 vault）

1. **transcript 不入版本控制**——含粘贴的客户数据、命令输出，禁止 git add。
2. **复盘机制建议（待授权后实施）**：
   - 每月 1 次扫 `~/.claude/projects/*/[*.jsonl]`
   - 蒸馏出：高频问题 / 翻车次数 / 平均上下文使用率 / 常用 slash 命令分布
   - 写入 `15_刻意练习与成长/月度复盘/`，**只留统计与去标识案例，不留原始 jsonl**
3. **对外材料**（视频号、客户报告、案例）发布前，**禁止**直接复制 transcript 片段——必须先脱敏。
4. **大改 vault 结构前**，确认当前会话有 checkpoint（即 `file-history/<session>/` 在写入），失败时优先 `/rewind` 回退。

## 6. 隐私与安全红线

- 不要把 `~/.claude/projects/*/[*.jsonl]` 同步到云盘 / iCloud Drive 默认目录。
- 不要在 hook 中把 `transcript_path` 整个发给外部 HTTP 服务。
- 给客户演示时关闭 statusLine 中的 `session_id` 显示（避免被截图记录）。

## 7. 待确认事项

- 见 §3.1 / §3.3 内嵌的两条"待核验"。

## 8. Sources

- [.claude Directory](https://code.claude.com/docs/en/claude-directory.md)
- [Hooks Reference](https://code.claude.com/docs/en/hooks.md)（用于 `transcript_path` 字段说明）
- [Status Line](https://code.claude.com/docs/en/statusline.md)（同上）

## 9. 关联上游

- [[README]]
- [[01_上下文与记忆机制总结_v0.1]]

## 10. 关联下游

- [[15_刻意练习与成长/README]]（未来月度复盘机制将引用本文件）

## 11. 版本记录

| 版本 | 日期 | 修改内容 | 修改人 |
|---|---|---|---|
| v0.1 | 2026-05-04 | 初次创建：从暂存预览 §5 入库 | 六哥 + Claude |
