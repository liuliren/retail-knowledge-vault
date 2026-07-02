---
title: M-DEC 分类法 · 5 Domain / 12 Category · v1.0
aliases:
  - M-DEC分类法
  - 5D12C
version: v1.0
status: stable
owner: 六哥
created: 2026-06-27
updated: 2026-06-27
module: 01_科学零售方法论/M-DEC
source_type: methodology
confidence: high
signoff: 六哥 2026-06-27
tags:
  - M-DEC
  - 分类法
  - 5D12C
  - 跨战役复用
---

# M-DEC 分类法 · 5D/12C · v1.0

> **单轴原则**：「动作落点杠杆」——这个决策，最终动手改的是哪个经营杠杆？
> 这一个问题的答案，决定 Domain 归属。不因品类复杂而新增 Domain，只在同 Domain 内增加 M-DEC 条数。

---

## 5 Domains · 12 Categories

| Domain | 说明 | Category | 子 Category 名 | 核心判断句 |
|---|---|---|---|---|
| **D1** 品项广度与去留 | 改的是「哪些品/几个品」 | C1.1 | 进场判据 | 新品何时进/按什么标准进 |
| | | C1.2 | 退场/汰换判据 | 老品何时砍/尾部何时清 |
| **D2** 品项结构配比 | 改的是「角色/比例/资源」 | C2.1 | 角色功能分层 | 6 组角色如何划分/谁是主力谁是补充 |
| | | C2.2 | 价格带结构管理 | 价格带何时算过密/断档/漏档 |
| | | C2.3 | 占比与资源配置 | 哪个子类占多少排面/订货量/端架资源 |
| **D3** 位置与陈列 | 改的是「放哪个位/层/区」 | C3.1 | 空间落位与错配诊断 | 商品应落哪个区 / 现状是否与 ABC 错配 |
| | | C3.2 | 陈列重建与执行 SOP | 货架重建步骤/层数确认/区域落位 SOP |
| **D4** 供应与库存保障 | 改的是「怎么补货/备库」 | C4.1 | 补货与安全库存 | 安全库存触发线/补货节奏 |
| | | C4.2 | 供应链节奏管理 | 调改期供应商切换/到货时间节奏 |
| **D5** 诊断与作战执行 | 跨杠杆诊断+落地 | C5.1 | 跨域综合诊断 | 多指标交叉的商品动销诊断框架 |
| | | C5.2 | 调改落地 SOP | 门店多商品同期调改执行步骤 |
| | | C5.3 | 连续战节奏管理 | 夜班连续作战/调改节奏控制 |

**预留 D6**：定价与促销（暂不开门，无现有 M-DEC 落入，待第一条定价决策规则被逼出来再正式开）

---

## 三类 Asset Type

| asset_type | 定义 | 典型 M-DEC |
|---|---|---|
| `judgment_rule` | 量化触发阈值 + 决策规则（「何时算 X」） | M-DEC-010(价格带预警) / M-DEC-009(汰换防误判) |
| `execution_sop` | 分步操作流程（「怎么做」） | M-DEC-005(货架重建) / M-DEC-008(多品调改) |
| `diagnostic_framework` | 多维交叉诊断结构（「怎么看」） | M-DEC-007(动销诊断) / M-DEC-011(ABC错配) |

---

## 当前 M-DEC 全清单（v2026-06-27）

| 编号 | 名称 | Domain | Category | asset_type | status |
|---|---|---|---|---|---|
| M-DEC-001 | 6 组角色拆分判据 | D2 品项结构配比 | C2.1 角色功能分层 | judgment_rule | candidate |
| M-DEC-002 | 大包装区瘦身比例 | D2 品项结构配比 | C2.3 占比与资源配置 | judgment_rule | candidate |
| M-DEC-003 | 调改商品供应链落实节奏 | D4 供应与库存保障 | C4.2 供应链节奏管理 | execution_sop | candidate |
| M-DEC-004 | 夜班连续战节奏 SOP | D5 诊断与作战执行 | C5.3 连续战节奏管理 | execution_sop | pending(stub) |
| M-DEC-005 | 错品类货架重建 SOP | D3 位置与陈列 | C3.2 陈列重建与执行SOP | execution_sop | candidate |
| M-DEC-006 | 陈列层数确认与区域落位 SOP | D3 位置与陈列 | C3.1 空间落位与错配诊断 | execution_sop | candidate |
| M-DEC-007 | 商品动销综合诊断与调整 SOP | D5 诊断与作战执行 | C5.1 跨域综合诊断 | diagnostic_framework | candidate |
| M-DEC-008 | 门店多商品调改 SOP | D5 诊断与作战执行 | C5.2 调改落地SOP | execution_sop | draft |
| M-DEC-009 | 休食老品汰换时间维度防误判 | D1 品项广度与去留 | C1.2 退场/汰换判据 | judgment_rule | candidate |
| M-DEC-010 | 休食小类价格带结构预警 | D2 品项结构配比 | C2.2 价格带结构管理 | judgment_rule | **active** |
| M-DEC-011 | 黄金位×ABC 陈列错配诊断 | D3 位置与陈列 | C3.1 空间落位与错配诊断 | diagnostic_framework | candidate |
| M-DEC-012 | 小类增长率分群与资源再分配 | D2 品项结构配比 | C2.3 占比与资源配置 | diagnostic_framework | candidate |
| M-DEC-013 | 单小类长尾结构治理 | D1 品项广度与去留 | C1.2 退场/汰换判据 | judgment_rule | candidate |

**统计**：13 条 · D1×2 / D2×4 / D3×3 / D4×1 / D5×3 · active×1 / candidate×10 / draft×1 / stub×1

---

## Domain 密度检查（每次新增后更新）

```
D1 品项广度与去留     ██░░ 2 条（C1.1×0 / C1.2×2）← C1.1 进场判据尚无 M-DEC
D2 品项结构配比       ████ 4 条（C2.1×1 / C2.2×1 / C2.3×2）
D3 位置与陈列         ███░ 3 条（C3.1×2 / C3.2×1）
D4 供应与库存保障     █░░░ 1 条（C4.1×0 / C4.2×1）← C4.1 补货安全库存尚无 M-DEC
D5 诊断与作战执行     ███░ 3 条（C5.1×1 / C5.2×1 / C5.3×1·stub）
```

**空缺提示**：C1.1 进场判据、C4.1 补货安全库存 — 花厅坊后续战役中优先补齐。

---

## 使用说明

1. **新增 M-DEC 时**：先过「动作落点杠杆」snap test → 确定 Domain → 选 Category → 选 asset_type → 写 frontmatter 三字段。
2. **跨战役复用时**：按 Domain/Category 过滤，同 Category 下条数最多的说明该杠杆判据最成熟。
3. **升级 active 时**：需六哥签字 + 经过至少 2 个战役场景验证。
4. **不应新增 Domain 的情况**：品类本身复杂（生鲜/烟酒）→ 在现有 Domain 内增加 M-DEC 条数；新的管理维度 → 先看能否归入 D5 跨域诊断。
