---
title: Token 与额度控制规范
version: v0.1
status: review
owner: 六哥
created: 2026-05-04
updated: 2026-05-04
module: 11_系统产品与PRD/Claude Code 官方文档学习包
tags:
  - ClaudeCode
  - token
  - 额度
  - 降本
  - 三个月生存战
source_type: reference
confidence: medium
related:
  - "[[README]]"
  - "[[01_上下文与记忆机制总结_v0.1]]"
  - "[[03_slash命令速查_v0.1]]"
  - "[[04_subagents使用规范_v0.1]]"
  - "[[06_statusLine使用规范_v0.1]]"
  - "[[09_Claude_Code使用手册_v0.1]]"
---

# Token 与额度控制规范

> 三个月生存战的核心 SOP 之一。

## 1. 文件定位

把"每天怎么用 Claude Code 才不爆额度"做成一份可遵守的纪律，11 条要点 + 监控反馈回路。

## 2. 适用场景

- 每天开始工作前快速过一遍
- 发现额度异常时排查
- 培训新人时

## 3. 核心规范（11 条）

### A. 会话纪律

1. **切主题先 `/clear`**（`/rename` 后再清，便于 `/resume`）
2. **长任务前先 `/compact 关注 X`**，把当前对话浓缩
3. **简单任务 `/effort low`**；高难复盘 `/effort high`，做完降回来
4. **所有"扫 vault 全量""跨多门店比对""读长 Excel"任务 → subagent**

### B. 模型分层

5. **主会话**：Sonnet 兜底；架构 / 方法论体系级思考用 Opus
6. **子代理**：Haiku 优先（在 frontmatter `model: haiku`）

### C. 上下文优化

7. **CLAUDE.md 控制在 200 行内**（当前 567 行强烈建议拆 `.claude/rules/`，需单独授权后实施）：
   - `rules/陈列.md`（`paths: ["06_陈列规划与DisplayMap/**"]`）
   - `rules/商品诊断.md`（`paths: ["04_商品诊断与商品力提升/**","09_门店案例与项目复盘/**/03_商品诊断/**"]`）
   - `rules/方法论.md`（`paths: ["01_科学零售方法论/**"]`）
   - `rules/反幻觉与逻辑一致性.md`（无 paths，全局加载）
8. **重型 SOP**（DisplayMap 检查、52 周 MD 模板、商品诊断流程）→ skill 而非 CLAUDE.md，按需加载
9. **关闭未用的 MCP server**（`/mcp`）；CLI 优于 MCP server（`gh`、`bq`、`gcloud`）

### D. 思考 token

10. 默认 thinking on；简单任务 `/effort low`；脚本 / 批量场景考虑 `MAX_THINKING_TOKENS=8000`

### E. 工具产出过滤

（本阶段不开）后续可加 PreToolUse hook 把 `npm test` / 大日志只留失败行——见 [[05_hooks使用规范_v0.1]]

### F. 监控

11. **statusLine 显示 `context_window.used_percentage` + `rate_limits.five_hour.used_percentage`**；每次会话结束 `/usage` 一眼

## 4. 反馈回路

```
工作中 → statusLine 实时看 ctx % 与 5h %
       ↓
ctx > 70% → /compact
ctx > 90% → /clear（必要时 /rename + /resume）
5h > 80% → 当天主任务收尾，停一停
       ↓
会话结束 → /usage 看结算
       ↓
每周 → 蒸馏哪些任务花得不值（应该委派给 subagent 的）
       ↓
每月 → 见 [[02_日志与transcript机制总结_v0.1]] §5 复盘机制
```

## 5. 反模式（不要做）

- 凡事都让主会话从头扫 vault（应交 subagent / skill）
- CLAUDE.md 越写越长（应拆 `.claude/rules/`）
- 全程开 `/effort high`（多数任务 medium 足够）
- 同一会话从早跑到晚不 `/compact`
- 客户演示用 Opus + max effort（演示用 Sonnet + medium 即可）
- 把 `/usage` 当账单（订阅用户的美元数仅供参考）

## 6. 待确认事项

- 订阅用户（Pro/Max）的 `/usage` 美元数与实际计费关系（见 [[10_待核验问题清单_v0.1]] #2）
- `MAX_THINKING_TOKENS` 在订阅用户与 API 用户间的行为是否一致（**待核验**：抓 `model-config.md` 与 `costs.md` 完整版）

## 7. Sources

- [Costs](https://code.claude.com/docs/en/costs.md)
- [Commands - /effort, /usage, /compact, /clear](https://code.claude.com/docs/en/commands.md)
- [Context Window](https://code.claude.com/docs/en/context-window.md)

## 8. 关联上游

- [[README]]
- [[01_上下文与记忆机制总结_v0.1]]

## 9. 关联下游

- [[03_slash命令速查_v0.1]]
- [[04_subagents使用规范_v0.1]]
- [[06_statusLine使用规范_v0.1]]
- [[09_Claude_Code使用手册_v0.1]]

## 10. 版本记录

| 版本 | 日期 | 修改内容 | 修改人 |
|---|---|---|---|
| v0.1 | 2026-05-04 | 初次创建：从暂存预览 §11 入库 | 六哥 + Claude |
