---
title: 花厅坊90天 金矿收窄分布（scope+成本闸+动销闸）CODEX-Goldmine-Rule-Tighten-Fix-001
version: v0.1
status: draft
owner: 六哥
created: 2026-06-24
updated: 2026-06-24
module: 00_入口与总索引/03_治理规范
client_safety: internal_only
source_type: reference
related:
  - "[[金矿候选二级闸与成本异常排除评审_P0-ABC-Goldmine-Rule-Tighten-001_v0.1]]"
  - "[[花厅坊90天full_dryrun_review_CODEX-Full-DryRun-Review-001_v0.1]]"
  - "[[零售工具注册表_v0.1]]"
---

# 花厅坊90天 金矿收窄分布 v0.1（§3.1.2 + §3.1.3 代码同步重跑）

> 代码同步 §3.1.2(成本闸+动销闸)+ §3.1.3(数据质量范围筛选)后重跑。**纯统计·零逐 SKU 明细/真实条码/进价/供应商裸名;结果表不入 git;无正式裁决。**

## 0. 执行结论
- ✅ 三闸代码同步:abc_classifier 加 scope/cost/recently/pool 函数 + assign_goldmine 三闸;**27 单测全过**;9 格不变、invalid=0、观察品=0、条码全脱敏。
- ✅ **生鲜=客户级 scope 标记(client_specific_excluded),非硬编码品类永久排除**——同样"水果"在成本可靠客户下仍 eligible(单测验证)。
- 🎯 **金矿候选 1,686 → 16**(占 eligible-C 行 0.2%)——三闸把噪声清到一个可人工逐条复核的极小池。

## 1. 数据质量范围 data_quality_scope_status
| status | 计数 | 占比 |
|---|--:|--:|
| eligible | 8,599 | 84.0% |
| cost_unreliable | 825 | 8.1% |
| client_specific_excluded(生鲜·花厅坊配置) | 808 | 7.9% |
> 仅 eligible(8,599)进金矿判断。生鲜 808 = 当前客户数据质量配置排除(非通用)。

## 2. 金矿候选 + 复核池
| 项 | 计数 |
|---|--:|
| **金矿候选 goldmine_candidate** | **16**(占 eligible-C 7,453 的 0.2%)|
| dead_stock_review_pool | 8,089 |
| cost_missing_review_pool | 825 |
| client_specific_excluded(生鲜) | 808 |
| none(其它) | 510 |

## 3. 阶段对比
| 阶段 | 分析行 | C行/eligible-C | 金矿候选 | 主污染 | 说明 |
|---|--:|--:|--:|---|---|
| 初始 P75 | 10,232 | C 8,478 | 1,686 | 数据异常35% | 未 scope 筛选 |
| 剔生鲜(drop·历史) | 9,424 | C 5,708 | 1,168 | 死货34% | 生鲜 drop |
| **§3.1.2+§3.1.3** | 10,232 | eligible-C 7,453 | **16** | 死货(dead_stock 8,089) | scope+成本闸+动销闸 |

## 4. 关键发现
1. **三闸有效**:金矿从 1,686 收到 **16**——成本闸去 825 伪高毛利、生鲜 scope 去 808、**动销/库龄闸去绝大多数(dead_stock 8,089)**。
2. **死货池 8,089 = 店内重滞结构性问题**:店内 9,117 SKU 库龄>90(89% 重滞)→ 库龄≤90 闸成主切刀。这本身是花厅坊一个重大经营信号(海量老库存),非闸错。
3. ⚠ **动销闸口径限制**:`recently_sold` 当前用 **库龄≤90 代理「近 90 天动销」**(最近销售日期仅 24% 覆盖,用库龄兜底)。库龄=进货/建档 recency,非销售 recency → 可能把「老库存但近期仍有零星销售」的真小众好货也判进死货。**Review-002 可议**:是否改用最近销售日期/放宽库龄阈值(如≤180)。

## 5. 质量检查
| 项 | 结果 |
|---|---|
| 输入/输出 SKU | 10,232 / 10,232(一致,无膨胀)|
| 原 9 格标签 | 不变 ✅ |
| invalid_combination / 观察品 | 0 / 0 ✅ |
| 新字段生成 | scope_status/reason/client_specific_exclusion/cost_reliable/recently_sold/exclusion_pool/两池 ✅ |
| 保留 P75 / 误用 P85 | 是 / 否 ✅ |
| 硬编码生鲜永久排除? | **否**(客户配置驱动,单测验证)✅ |
| 真实条码/进价/供应商入 md | 否 ✅ |
| 结果表入 git | 否(gitignored)✅ |
| 单测 | 27 passed ✅ |

## 6. 是否进 Review-002
- **管线层 ✅**:三闸跑通、生鲜客户配置化、字段齐、脱敏达标、27 测试过。
- **可进 CODEX-Full-DryRun-Review-002**:重点审 ① 16 候选是否真金矿(可逐条);② 死货闸是否过严(库龄代理动销的口径问题);③ 是否放宽库龄/改用销售日期。
- **真实写回仍暂缓**(需 Review-002 + Execute-Approval 签字)。

## 版本记录
| v0.1 | 2026-06-24 | CODEX-Goldmine-Rule-Tighten-Fix-001：代码同步§3.1.2+§3.1.3(scope filter+成本闸+动销闸,27测试过);生鲜=client_specific_excluded客户配置非硬编码;金矿1686→16;scope eligible84%/cost_unreliable8.1%/生鲜7.9%;池dead_stock8089/cost_missing825。⚠动销闸用库龄≤90代理(店89%重滞致候选极少),Review-002议口径。结果表未入git |
