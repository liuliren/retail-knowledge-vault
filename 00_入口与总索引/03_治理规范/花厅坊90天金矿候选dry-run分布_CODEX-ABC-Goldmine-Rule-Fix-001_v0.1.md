---
title: 花厅坊90天 金矿候选 dry-run 分布 CODEX-ABC-Goldmine-Rule-Fix-001
version: v0.1
status: draft
owner: 六哥
created: 2026-06-23
updated: 2026-06-23
module: 00_入口与总索引/03_治理规范
client_safety: internal_only
source_type: reference
related:
  - "[[花厅坊90天full_dryrun审阅_CODEX-Full-DryRun-Execute-001_v0.1]]"
  - "[[ABC九宫格利润金矿口径方法论评审_P0-ABC-Goldmine-Method-Review-001_v0.1]]"
  - "[[零售工具注册表_v0.1]]"
---

# 花厅坊90天 金矿候选 dry-run 分布 v0.1

> §3.1.1 C 行毛利率闸代码同步后重跑（六哥签字授权 CODEX-ABC-Goldmine-Rule-Fix-001）。
> **纯统计·零逐 SKU 明细·零真实条码/进价/供应商裸名。结果表不入 git。不含正式裁决/诊断结论。**

## 0. 执行结论
- ✅ 代码同步 §3.1.1：abc_classifier 新增 `assign_gross_margin_rate_tier` + `assign_goldmine`；dry-run runner 接入；**17 单测全过**。
- ✅ 重跑全店 10,232 SKU：**9 格标签不变**、invalid=0、观察品=0、条码全脱敏。
- 🎯 **金矿闸生效**：捞出 **1,686 个低销高毛利率金矿候选**（占 C 行 19.9%）——这些原本全落「双低」、被毛利额贡献维掩盖。

## 1. 九宫格分布（不变·验证未破坏）
| 身份 | 计数 | 占比 |
|---|--:|--:|
| 双低 | 8,478 | 82.9% |
| 流量补充·控利 | 1,365 | 13.3% |
| 常规品 | 163 | 1.6% |
| 核心引擎 | 160 | 1.6% |
| 流量品 | 66 | 0.6% |
| invalid_combination | 0 | ✅ |
| 观察品（已废止） | 0 | ✅ |
> 与上一轮一致 → 金矿闸**叠加而非替换**，9 格裁决未被破坏。

## 2. 毛利率分层 gross_margin_rate_tier
| tier | 计数 | 占比 |
|---|--:|--:|
| mid | 4,317 | 42.2% |
| high | 2,737 | 26.7% |
| low | 2,586 | 25.3% |
| unavailable | 592 | 5.8% |
> 优先小类 P75/P25；小类样本<20 降全店分位；毛利率缺失=unavailable。

## 3. 金矿候选 goldmine_candidate
- **金矿候选数 = 1,686**；**占 C 行(8,478) = 19.9%**。
- 含义：销额 C（低销）+ 毛利率 high（小类/全店 P75）+ 非缺货 + 非新品。**= 复核字段，非最终裁决**。

### 3.1 C 行金矿排除原因分布（计数）
| 原因 | 计数 |
|---|--:|
| 金矿候选(命中) | 1,686 |
| 毛利率未达阈值 | 5,638 |
| 毛利率不可用/数据异常 | 592 |
| 缺货排除 | 408 |
| 新品保护排除 | 154 |
> C 行合计 8,478 = 1,686 + 5,638 + 592 + 408 + 154 ✅。
> ⚠ **促销字段缺失**：金矿候选 reason 统一标「促销字段缺失需人工复核」——促销异常未能自动排除，复核时须人工判。

## 4. 模块覆盖（不变）
| 模块 | 可算 | blocked/降级 |
|---|--:|---|
| ABC 九宫格 | 100% | 0 |
| 毛利率分层 | 94.2% | unavailable 592(5.8%) |
| 金矿闸 | C 行全判 | 促销 unavailable(记 reason) |
| IR | 64.4% | ITO 缺 3,348 |
| 库龄分级 | 99.8% | 缺 21 |

## 5. 质量检查
| 检查项 | 结果 |
|---|---|
| 输入/输出 SKU 数 | 10,232 / 10,232（一致）|
| 原 9 格标签不变 | ✅ |
| invalid_combination=0 | ✅ |
| 观察品=0 | ✅ |
| gross_margin_rate_tier 生成 | ✅ |
| goldmine_candidate 生成 | ✅(1,686) |
| goldmine_reason 生成 | ✅ |
| 金矿候选占 C 行 | 19.9% |
| 促销缺失进 reason | ✅ |
| 真实 EAN-13 入 md | 否 |
| 真实进价入 md | 否 |
| 供应商裸名入 md | 否 |
| 结果表入 git | 否（gitignored）|
| 单测 | 17 passed |
| 可进入 review | ✅（管线层）|

## 6. 是否进入 review / approval
- **管线层 ✅**：金矿闸跑通、9 格未破坏、字段齐、脱敏达标、单测全过。
- **可进 CODEX-Full-DryRun-Review-001**（更细审阅金矿候选合理性）。
- **真实写回仍暂缓**：需 review 后 CODEX-Execute-Approval-001 **另签字**。
- 复核要点：① 1,686 金矿候选需人工抽样验「是否真高毛利率值得保护」；② 促销异常无字段,复核时人工判;③ unavailable 592 需查毛利率为何缺。

## 版本记录
| v0.1 | 2026-06-23 | CODEX-ABC-Goldmine-Rule-Fix-001：代码同步§3.1.1(abc_classifier加毛利率分层+金矿闸,runner接入,17单测过),重跑10232 SKU。9格不变/invalid0/观察品0/条码脱敏。金矿候选1686(占C行19.9%);tier high2737/mid4317/low2586/unavailable592;排除分布(未达阈值5638/不可用592/缺货408/新品154)。促销缺失记reason。结果表未入git。可进review,写回仍暂缓 |
