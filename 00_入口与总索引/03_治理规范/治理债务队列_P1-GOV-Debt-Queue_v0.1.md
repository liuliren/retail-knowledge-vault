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
| 3 | G03_Lint v2 规则 | **11 查已实现**（8 + 语义 3）| —— | 语义规则已落地，后续按需增强口径 | P3 |
| 3a | provenance warning | **0**（基线干净）| 优先目录均有来源信号 | 常态监控；新件保持有来源 | P3 |
| 3b | supersession warning | **0** | superseded 件均带 superseded_by | 常态监控 | P3 |
| 3c | failed 记录 warning | **0** | 暂无 failed/侥幸状态文件 | 现场回填出现 failed 时须留因 | P3 |
| 4 | M-DEC Schema trial（0B）| 预演完成 | 捕获路径未充分验证（需新现场决策）| 花厅坊新现场决策补验 → 0C 三问 → v0.2 | P1 |
| 5 | Codex execute 数据线 | **review已做·结论B暂缓** | 候选泛化(P75机械捞top quartile) + 写回未签 | 抽样复核→大概率P85+动销二级闸→重跑→再review→approval | P0 |
| 5b | 金矿候选泛化(P75辨别力) | **剔生鲜后复跑·待人工复核** | 剔后候选1168(20.5%C行);死货34%成最强污染 | 六哥看剔生鲜版100条→大概率加「近90天动销」二级闸砍死货 | P1 |
| 5c | 生鲜剔除(内购无成本) | ✅落地·**口径已修正** | —— | 按生鲜档案剔808行;**§3.1.3降级:客户级数据质量排除非通用永久规则** | 完成 |
| 5g | 数据质量范围筛选机制 | ✅**代码同步** | 生鲜808=client_specific_excluded客户配置;eligible84% | 完成(Fix-001,单测验证非硬编码) | P2 |
| 5d | 成本可信闸(成本缺失) | ✅**代码同步** | cost_missing_review_pool=825 | 完成(Fix-001) | P2 |
| 5e | 近90天动销闸(死货) | ✅Fix-002修正 | —— | 完成 | P2 |
| 5h | 金矿池处置(老库存1104) | **5桶明细全出** | 待采购+现场据明细执行 | A17/B529/C161/D228/E186明细齐(gitignored);执行由现场定 | P2 |
| 5f | P85 是否上 | **暂不上(已记)** | 保P75,留v0.3备选 | 两闸重跑review后再议 | P2 |
| 5a | 金矿口径(方法+代码) | ✅**已闭环** | —— | §3.1.1签字+代码同步(金矿候选1686/占C行19.9%);仅余review/写回 | 完成 |
| 6 | 饼干货盘敏感核查 | 暂缓 | 含真实货盘，挂链前需核敏感 | 核敏感→脱敏达标挂链/否则豁免 | P2 |
| 7 | 第二客户验证（M-DEC-013 等）| 等待 | 同店三小类=共因，缺独立场景 | 第二客户/门店独立复现 → 升 active | P1 |
| 8 | source_type 缺失 | 部分清理 | lint 缺字段 183（含 source_type 等）| 随签字批/编辑顺手补 | P2 |
| 9 | provenance / supersession lint | **已实现**（Batch-Rules-002）| —— | 弱检测落地，基线全 0 | P3 |
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

## 5. 累计签字进度（信息）
- active 无签字：247 → **230**（Batch-002 签 10 + Batch-003 签 6 + Single-004 签 1 = 17）。

## 版本记录
| v0.1 | 2026-06-23 | P1-GOV-G03Lint-Batch-014：建治理债务队列(10 队列+优先级+阻塞依赖图)。本轮 lint 加 candidate越权/execute前置 2 检测+3 预备规则；中确定性 3 件补 source_type。只排程不执行 |
| v0.1(Rules-002) | 2026-06-23 | P1-GOV-G03Lint-Rules-002：provenance/supersession/failed 三语义弱检测**已实现**，lint 11 查；基线全 0；更新队列 #3/#9 为已实现；补累计签字 17/active无签字 230 |
