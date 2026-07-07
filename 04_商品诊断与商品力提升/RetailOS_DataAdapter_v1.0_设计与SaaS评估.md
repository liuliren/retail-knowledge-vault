---
id: KB-ADAPTER-001
title: RetailOS Data Adapter v1.0 · 设计 + SaaS就绪评估
version: v1.0
status: candidate
owner: 六哥
source_type: engineering_design
created: 2026-06-25
module: 04_商品诊断与商品力提升
client_safety: internal_only
aliases: [Data Adapter, ERP标准化层, RetailOS v2.1架构]
summary: 攻SaaS化第一阻碍=跨店ERP结构不统一。建adapter.py:任意门店ERP→统一13字段schema+质量评分(0-100)+A/B/C分级+异常检测。2店真实验证:花厅坊88/A、沙埔大道64/B(自动检出列错位并反推)。SaaS就绪=NO但阻碍已破(schema混乱→自动归一)。剩余:L3/L4分类映射/生鲜未验/Display→Sales净证。含架构v2.1五层。
tags: [Data Adapter, ERP标准化, SaaS评估, 架构v2.1, candidate]
---

# RetailOS Data Adapter v1.0 · 设计 + SaaS 就绪评估

> **唯一目标**:消除跨店复制的工程瓶颈——ERP/POS 数据结构不统一。
> **方法论纪律**:不改 SKU角色/ABCZ/品类理论;**纯工程·数据标准化**。
> **底层逻辑(六哥洞察)**:把"LLM 看每店表猜字段"沉淀成确定性适配器 → 运行时 LLM 依赖趋近 0。
> **不是空设计**:`adapter.py` 已在 2 店真实数据跑通(见 §4 实证)。

## 结论先行
1. **阻碍已破**:同一 `adapter.py` 把花厅坊(日级/小计行/无零售价)与沙埔大道(SKU级/列错位)**自动归一为同一 13 字段 schema**,无需每店手改。
2. **质量可分级**:花厅坊 88/A、沙埔大道 64/B —— 数据可用性自动评分,SaaS 接入可据此 gate。
3. **SaaS 就绪 = 尚未(NO),但从"不可能"变"工程可达"**:剩 3 阻塞(L3/L4分类映射 / 生鲜未验 / Display→Sales净证)。

---

## TASK 1 — ERP 统一数据模型

### ① 标准 Schema(13 字段·所有门店归一到此)
`store_id · sku_id · product_name · l3_category · l4_category · price · cost_price(脱敏置空) · margin_band · sales_qty_30d · sales_value_30d · inventory_qty · shelf_position · promo_flag`

> 脱敏:`sku_id`=序号(非裸条码);`cost_price` 置空,只留 `margin_band`(§7);供应商 drop。

### ② Schema 适配规则
- **字段映射**:`CAND` 候选表(标准字段→跨店源名并集)。**新店只需加候选名即兼容**,不改引擎。
- **字段错位修正**:表头自动定位(扫含"品名+销量/销额"的行);列错位→值域反推(销量空但有价→`销量=销额/价`,沙埔大道实证)。
- **多版本 ERP 兼容**:小计/合计行(货号∈{小计/合计/总计})自动剔除;日级表按 sku_id 聚合到 SKU 级。

### ③ 门店差异容忍机制(字段分级)
| 级别 | 字段 | 缺失处理 |
|------|------|---------|
| **必须存在** | product_name + (price 或 sales_value) | 缺→数据不可用,拒绝 |
| **可推断** | price(←销额/销量)、sales_qty(←销额/价)、l3(←类别) | 缺→反推,标记 |
| **允许缺失降级** | cost_price→毛利未知 / inventory→周转NA / shelf / promo | 缺→置空降级,不崩 |

---

## TASK 2 — 跨店数据适配器引擎（adapter.py）
`13_数据分析与工具脚本/脱敏测试链路_v0.1/adapter.py`,含:
- **field mapping engine**:CAND 声明式映射 + 表头自动定位。
- **schema validation**:字段覆盖体检(price/qty/cost/inv/cat/date 有无)。
- **anomaly detection**:进价>售价(price↔cost错置)、毛利倒挂、负库存、SKU重复编码、销量列错位。
- **auto-normalization**:聚合/反推/脱敏/小计剔除 → 标准 schema csv。

用法:`python3 adapter.py <店ERP.xls> <STD输出.csv> --store <店代号>`

---

## TASK 3 — 失真控制（数据质量评分 + 分级）
| 检出项 | 实现 |
|--------|------|
| price↔cost 错置 | 进价>售价×1.5 → 计数告警 |
| 类目错位/缺失 | 无类目列 → 扣分 + L3 留空(不臆造) |
| SKU 重复编码 | 去重计数 |
| 销售归因/列错位 | 销量列空→反推 + 标记 |
| 毛利倒挂(进价不准) | margin<0 计数,>2% 扣分 |

**数据质量评分 0-100**:满分扣(缺类目-10/缺库存-10/缺日期-8/列错位-8/倒挂率×系数/重复-5)。
**可用性分级**:A≥80 / B 60-79 / C<60。**SaaS 接入 gate:C 级需人工补数据才入库。**

---

## TASK 4 — SaaS 化关键判断

### RetailOS 能进入 SaaS 阶段吗? → **NO(尚未),但唯一工程瓶颈已破**

| 能力 | 状态 |
|------|------|
| 多店接入能力 | 🟡 ~70%:schema 自动归一✓;**L3/L4 分类映射仍需每店品类表**(未自动) |
| 自动分析能力 | ✅ 有(adapter→analyze→enrich→诊断卡 全链) |
| 低人工依赖能力 | 🟡 改善:数据读取的每店手改已消除;剩 L3/L4 映射 + 异常复核 |

### 当前阻塞点（≤3）
1. ~~**L3/L4 品类映射未自动化**~~ → 🟢 **已攻(2026-06-25)**:`category_mapper.py` 声明式关键词→L3 映射 + 复杂类标 L4。实证:花厅坊 89%、沙埔大道(无类目)纯品名推断 67%;补关键词即升(自我进化)。**L4=决策层构造,数据层只标"复杂类需L4"不臆造。** 剩:未映射尾部需扩词表(渐进)。
2. **生鲜未验** —— 占社区超市 40-50% 销额,无条码/称重/损耗,adapter 的 sku_id 基础不成立。
3. **Display→Sales 净证未完成** —— 执行层闭环未验。

> **结论**:adapter v1.0 把 SaaS 化从"数据结构混乱不可能"推进到"schema 已统一、质量可分级、接入可 gate"。**这是 SaaS 地基,不是 SaaS 成品。**

---

## TASK 5 — 系统架构 RetailOS v2.1（五层）
```
┌─ Execution Layer   门店调改清单(店长照做)        ← 诊断卡⑤ / DisplayMap调整
├─ Visualization     DisplayMap + 诊断卡(make-pdf)  ← report-export
├─ Decision Layer    角色闸 + ABCZ + M-DEC + 六哥签字 ← enrich.py + 护城河10%
├─ Computation       复杂度/失真/集中度 + 角色/ABCZ   ← analyze.py + enrich.py
└─ Data Layer ★NEW   ERP Adapter(归一+质量分级)      ← adapter.py(本设计)
```
**v2.1 的增量 = Data Layer(★)**:此前各 skill 直接吃花厅坊定制格式;现在底部多了**统一 Data Layer**,上面 4 层不变即可接任意门店。**这是 v2.0→v2.1 的唯一结构升级,也正是 SaaS 化必须先垫的地基。**

---

## §4 实证（2 店真实·非空设计）
| 店 | ERP 结构 | 质量分 | 级 | 关键 |
|----|---------|:--:|:--:|------|
| 花厅坊休闲 | 日级+小计行+无零售价 | **88** | A | 字段全,仅进价不准 |
| 沙埔大道休闲 | SKU级+列错位+无类目 | **64** | B | **自动检出列错位并反推销量** |

> 同一引擎、零改、两套截然不同的 ERP → 同一 13 字段 schema。**适配器有效。**

## 自我进化机制（受治理）
新店接入 → adapter 跑 → 遇新 schema 怪癖 → 把候选名/规则**固化进 CAND/规则(代码)**,非固化进对话 → 下次自动认。**越跑越不需要 LLM**(M-DEC 回路用于工具层)。

## 关联
[[RetailOS_v2.0_Scale评估报告_v0.1]] · [[13_数据分析与工具脚本/脱敏测试链路_v0.1/README|脱敏测试链路_v0.1]] · [[Skills路线图_v0.1]] · `/单品类诊断` · [[复杂类分层计算引擎_v1.0]]
