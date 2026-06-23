---
title: 治理债务队列 P1-GOV-Debt-Queue
version: v0.1
status: draft
owner: 六哥
created: 2026-06-23
updated: 2026-06-23
module: 00_入口与总索引/03_治理规范
client_safety: internal_only
source_type: reference
related:
  - "[[治理总控待决任务表_P1-GOV-Control-010_v0.1]]"
  - "[[Codex执行前置状态登记表_v0.1]]"
  - "[[下一批active签字候选审计表_P0-GOV-Signature-Batch-002_v0.1]]"
---

# 治理债务队列 v0.1（P1-GOV-Debt-Queue）

> 汇总当前所有治理债务，统一排程。**本表只登记/排程，不执行。** 数据源：lint 仪表盘（2026-06-23）+ 各审计/登记表。

## 1. 债务队列总表
| # | 队列 | 当前状态 | 阻塞原因 | 下一步 | 优先级 |
|:--:|---|---|---|---|:--:|
| 1 | active signoff 剩余批次 | 237 无签字（247→237）| 需逐批审计，不批量刷 | 续审高/中确定性，每批≤10 | P1 |
| 2 | 中确定性 6 件 Batch-003 | 字段补齐就绪 | 3 件已补 source_type；4 件字段完整 | 微核后 P0-GOV-Signature-Batch-003 签 | P1 |
| 3 | G03_Lint v2 规则 | 8 查已实现 + 3 预备 | provenance/supersession/failed 为语义/跨文件，未实现 | 跑稳低风险后再实现语义规则 | P2 |
| 4 | M-DEC Schema trial（0B）| 预演完成 | 捕获路径未充分验证（需新现场决策）| 花厅坊新现场决策补验 → 0C 三问 → v0.2 | P1 |
| 5 | Codex execute 数据线 | blocked | 全量真实数据未到 + dry-run 未审 + 未签字 | 按现场导出清单导数据 → full dry-run | P0 |
| 6 | 饼干货盘敏感核查 | 暂缓 | 含真实货盘，挂链前需核敏感 | 核敏感→脱敏达标挂链/否则豁免 | P2 |
| 7 | 第二客户验证（M-DEC-013 等）| 等待 | 同店三小类=共因，缺独立场景 | 第二客户/门店独立复现 → 升 active | P1 |
| 8 | source_type 缺失 | 部分清理 | lint 缺字段 183（含 source_type 等）| 随签字批/编辑顺手补 | P2 |
| 9 | provenance / supersession lint | 预备登记 | 语义/跨文件状态机复杂 | 设计已登记，待 §3 之后实现 | P2 |
| 10 | 真实 EAN-13 红线持续监控 | 绿（红线=0）| —— | lint 每轮扫，新数据接入时保持 0 | P1 常态 |

## 2. 本轮（Batch-014）进展
- lint 加 2 低风险检测（candidate 越权 approved / execute 前置存在性）→ 已实现并跑通；
- lint 最新：active无签字 **237**、candidate越权 **0**、execute前置 **存在·已声明阻断**、红线 **0**、孤儿 **11**；
- 中确定性 3 件补 source_type（Memory治理/工程错误案例库/数据一致性案例库）→ Batch-003 就绪。

## 3. 阻塞依赖图（execute 总闸门）
```
§3.1 active ✅ → abc_classifier 9格 ✅ → 测试自洽 ✅
                                          ↓
                        全量真实数据 ❌(待导出) → full dry-run ❌ → 用户签字 ❌ → execute
```
> execute 仍关闭；卡点纯在数据线（#5）。

## 4. 纪律
- 本表只排程，不执行；
- 签字/execute/改脚本各有独立闸门，按 [[高效批处理任务规范_v1.0]] 合批纪律推进；
- 每完成一批回本表更新状态。

## 版本记录
| v0.1 | 2026-06-23 | P1-GOV-G03Lint-Batch-014：建治理债务队列(10 队列+优先级+阻塞依赖图)。本轮 lint 加 candidate越权/execute前置 2 检测+3 预备规则；中确定性 3 件补 source_type。只排程不执行 |
