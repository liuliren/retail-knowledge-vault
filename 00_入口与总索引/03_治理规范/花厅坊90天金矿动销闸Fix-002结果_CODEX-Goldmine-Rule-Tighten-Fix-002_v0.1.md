---
title: 花厅坊90天 金矿动销闸 Fix-002 结果 CODEX-Goldmine-Rule-Tighten-Fix-002
version: v0.1
status: draft
owner: 六哥
created: 2026-06-24
updated: 2026-06-24
module: 00_入口与总索引/03_治理规范
client_safety: internal_only
source_type: reference
related:
  - "[[花厅坊90天三闸金矿候选review_CODEX-Full-DryRun-Review-002_v0.1]]"
  - "[[花厅坊90天金矿收窄分布_CODEX-Goldmine-Rule-Tighten-Fix-001_v0.1]]"
  - "[[零售工具注册表_v0.1]]"
---

# 花厅坊90天 金矿动销闸 Fix-002 结果 v0.1

> 据 Review-002 结论 C,动销闸改销量优先、库龄降级为风险标签。**纯统计·零逐 SKU/真实条码/进价/供应商裸名;结果表不入 git;无正式裁决。**

## 1. 执行结论
- ✅ 动销闸代码改完:`recently_sold=90天销量≥4`(去库龄一票否决);新增 `old_inventory_risk=库龄>90`(标签,**不排除金矿**);dead_stock 只由销量<4 触发。**31 单测全过**;9 格/invalid 0/观察品 0/保 P75 不变。
- 🎯 **金矿候选 16 → 1,121**(占 eligible-C 15.0%)——从 Fix-001 的过度过滤恢复到合理待复核池。

## 2. 核心规则变更
| 项 | Fix-001 | Fix-002 |
|---|---|---|
| recently_sold | 销量≥4 **且** 库龄≤90 | **销量≥4**(仅销量)|
| 库龄>90 | 一票否决金矿 | **old_inventory_risk 标签,不排除** |
| dead_stock_review_pool | 销量<4 或 库龄>90 | **仅 eligible+成本可信+销量<4** |
| goldmine_candidate | 含库龄≤90 | **去库龄,加老库存风险标注** |

## 3. Fix-001 → Fix-002 对比
| 指标 | Fix-001 | Fix-002 |
|---|--:|--:|
| 总行 | 10,232 | 10,232 |
| eligible | 8,599 | 8,599 |
| cost_unreliable | 825 | 825 |
| client_specific_excluded(生鲜)| 808 | 808 |
| cost_missing_review_pool | 825 | 825 |
| **dead_stock_review_pool** | **8,089** | **2,394** |
| recently_sold(销量≥4)| 未单列 | 7,003 |
| old_inventory_risk(库龄>90)| 未单列 | 9,117 |
| **金矿候选** | **16** | **1,121** |
| └ 含老库存风险 | — | 1,104 |
| └ 新货(库龄≤90)| 16 | 17 |
| invalid / 观察品 | 0 / 0 | 0 / 0 |

## 4. 结果判断
1. ✅ **金矿恢复合理**:16→1,121(eligible-C 15.0%),不再被库龄误杀;
2. ✅ **dead_stock 回归本义**:8,089→**2,394**,正好等于 Review-002 测出的「销量<4 真动销不足 2,394」——证明 dead_stock 现**只由销量触发**,库龄不再误伤;
3. ✅ **old_inventory_risk 成功作标签**:9,117 库龄>90 中,有动销(销量≥4)的进金矿候选并标风险(1,104),无动销的归 dead_stock;
4. ✅ 无异常膨胀(总行/9格/scope/成本池/生鲜池均稳定);
5. **金矿 1,121 = 待复核池**(非正式裁决):其中 **1,104 带老库存风险**(低销高毛利率但库存老,需判清库/缩面/补货)、**17 新货**(库龄≤90,最干净)。

## 5. 保留逻辑核验
| 项 | 结果 |
|---|:--:|
| 原 ABC 九宫格不变 | ✅(apply_abc 未动)|
| P75 保留 / P85 未启用 | ✅ |
| data_quality_scope_filter(客户配置驱动)| ✅ |
| 生鲜=client_specific_excluded(非永久硬排)| ✅ |
| cost_reliable / cost_missing_review_pool | ✅ |
| 新品/缺货/促销/数据异常排除 | ✅ |

## 6. 红线/边界
条码全脱敏 ✅;真实进价/供应商裸名未入 md ✅;结果表 gitignored 未入 git ✅;未改 §3.1.x 正文/未真实写回/未出正式裁决 ✅。

## 7. 是否进 Execute-Approval
**否**。Fix-002 后是「待复核金矿候选池(1,121)」,非正式裁决。**下一步 CODEX-Full-DryRun-Review-003**(审 1,121 池结构 + 老库存风险 1,104 子集如何处置 + 是否抽样)→ 再议写回。

## 版本记录
| v0.1 | 2026-06-24 | Fix-002:动销闸改销量优先(recently_sold=销量≥4)+库龄降级old_inventory_risk标签(不排除金矿);dead_stock只由销量<4触发。31测试过;9格/invalid0/观察品0/P75不变。**金矿16→1121(老库存1104/新货17),dead_stock8089→2394(=Review-002真动销不足数)**。待复核池非裁决,下一步Review-003。结果表未入git |
