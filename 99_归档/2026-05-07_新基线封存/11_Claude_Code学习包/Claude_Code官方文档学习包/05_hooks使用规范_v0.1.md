---
title: Hooks 使用规范
version: v0.1
summary: Hook机制、事件类型、安全红线、三个月内不开理由与未来开启候选。
status: review
owner: 六哥
created: 2026-05-04
updated: 2026-05-04
module: 11_系统产品与PRD/Claude Code 官方文档学习包
tags:
  - ClaudeCode
  - hooks
  - 自动化
  - 安全
  - 风险
source_type: reference
confidence: medium
related:
  - "[[README]]"
  - "[[07_权限与安全红线_v0.1]]"
  - "[[09_Claude_Code使用手册_v0.1]]"
  - "[[10_待核验问题清单_v0.1]]"
---

# Hooks 使用规范

> ⚠️ **本 vault 三个月生存战内不开 hook**。本文件仅作机制了解与防误开红线。

## 1. 文件定位

把 hook 的事件类型、决策契约、风险全部摆出来，让"以后真要开 hook"时有清晰边界，不要凭印象试错。

## 2. 适用场景

- 评估某个自动化需求该不该用 hook 实现
- 审计第三方插件 / 别人写的 hook 配置
- 出现"指令被神秘修改 / 工具被神秘批准"时排查

## 3. 核心机制

### 3.1 适合自动化的场景

- **审计 / 只读日志**：`PostToolUse` 写入本地 jsonl，方便复盘
- **环境注入**：`SessionStart` 注入分支名 / 项目状态作为 `additionalContext`（陈述性事实，不下指令）
- **输出过滤降本**：`PreToolUse` 把 `npm test` / 长输出 grep 成失败行（官方 costs 页例子）
- **只读校验**：`PostToolUse` 跑本地 lint，失败则 exit 2 把 stderr 反馈给 Claude

### 3.2 不适合 / 风险高

- 任何 HTTP 出站到第三方
- 静默修改 `tool_input`（路径替换、命令替换）
- 一刀切 `permissionDecision: "allow"` 旁路所有权限
- 把"指令性文本"塞进 `additionalContext`（会变成提示注入）
- 无超时控制 / 无错误处理（hangs 阻塞 agent loop）

### 3.3 配置位置 / 优先级

`settings.json` 的 `hooks` 字段；解析顺序：用户 → 项目 → 本地 → 管理策略 → 插件 → 内置；`allowManagedHooksOnly: true` 时仅管理策略生效。

### 3.4 决策契约（部分）

- exit 0：成功；可输出 JSON `hookSpecificOutput`，`additionalContext` 注入 Claude
- exit 2：阻断；stderr 给 Claude
- 其他：非阻断错误
- `permissionDecision`: `allow | deny | ask | defer`

注意：deny rule 永远先于 hook allow 生效；hook exit 2 会先于 allow rule 生效。

### 3.5 主要事件类型（节选）

来自官方 hooks reference：

- **会话级**：SessionStart / Setup / SessionEnd / InstructionsLoaded
- **每轮**：UserPromptSubmit / UserPromptExpansion / Stop / StopFailure
- **代理循环**：PreToolUse / PostToolUse / PostToolUseFailure / PostToolBatch / PermissionRequest / PermissionDenied
- **子代理与任务**：SubagentStart / SubagentStop / TaskCreated / TaskCompleted
- **环境与文件**：CwdChanged / FileChanged / ConfigChange / Notification
- **上下文压缩**：PreCompact / PostCompact
- **Worktree**：WorktreeCreate / WorktreeRemove
- **MCP elicitation**：Elicitation / ElicitationResult
- **团队**：TeammateIdle

## 4. 安全红线（防误开）

1. 永远不要把 `~/.claude/settings.json` 中的 `hooks` 交给不可信来源（包括 AI 生成的"建议配置"未审）
2. **禁止**安装含 `type: "http"` 出站到非自有域名的 hook
3. **禁止**任何 hook 使用 `permissionDecision: "allow"` + 通配 matcher 这种"全开"组合
4. 看到 `additionalContext` 中含命令式词汇（"Run X""Delete Y""Ignore previous"）即视为提示注入企图，立即移除
5. 任何 `updatedInput` 静默改写都需要在 hook 中显式打日志（exit 0 时 stdout 进调试日志）
6. 装插件前必看其 `hooks/hooks.json`，若含上述任一红线项，**不安装**

## 5. 操作规则（本 vault）

1. **三个月内不开 hook**——风险密度高，"省 token"价值不抵学习成本与失误代价
2. 若未来确实要开，第一个候选是**只读审计型**（PostToolUse 写本地 jsonl）
3. 第二个候选是**输出过滤型**（PreToolUse 给 grep / pytest 等截短输出）
4. **永远不用**：第三方 HTTP hook、`permissionDecision: "allow"` 通配 hook、静默 `updatedInput` 改写

## 6. 待确认事项

- Hook 类型 `agent` / `prompt` 的 token 计费归属（主会话 vs 子代理）——见 [[10_待核验问题清单_v0.1]] #10

## 7. Sources

- [Hooks Reference](https://code.claude.com/docs/en/hooks.md)
- [Hooks Guide](https://code.claude.com/docs/en/hooks-guide.md)（本轮未抓全文，待回查）
- [Costs - hooks 节选](https://code.claude.com/docs/en/costs.md)

## 8. 关联上游

- [[README]]
- [[07_权限与安全红线_v0.1]]

## 9. 关联下游

- [[09_Claude_Code使用手册_v0.1]]

## 10. 版本记录

| 版本 | 日期 | 修改内容 | 修改人 |
|---|---|---|---|
| v0.1 | 2026-05-04 | 初次创建：从暂存预览 §8 入库 | 六哥 + Claude |
