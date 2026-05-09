---
title: vault 商品库 v0.1 主纲（晟果新零售咨询跨客户复用底座）
version: v0.1
status: active
owner: 六哥
created: 2026-05-09
updated: 2026-05-09
module: 13_数据分析与工具脚本/商品库_v0.1
quadrant: I
client_safety: internal_only
related:
  - "[[2026-05-09_商品库立项方案_v1.0]]"
  - "[[字段定义_v1.0]]"
  - "[[05_品类管理与商品规划/商品库索引]]"
  - "[[G11_商品库治理]]"
---

# vault 商品库 v0.1（主存 / 工具属性）

> **战略定位**：晟果新零售咨询专属商品库 / 跨客户复用底座 / Year 2-3 数据飞轮核心壁垒。
>
> **归属（双链）**：13_ 主存（工具属性 / 字段定义 + 数据 + 维护脚本）+ [[05_品类管理与商品规划/商品库索引]] 业务引用。

---

## §1. 三层架构

```
Layer A: 核心 SKU 库（精确 / Year 2 50,000+ 目标）
  → A_core_sku.csv（W26 起步）

Layer B: 品类骨架库（覆盖广 / 长尾兜底）⭐ 起步重点
  → B_category_skeleton.csv（W24 起步）

Layer C: 客户独有 SKU 库（长尾 / 人工标注）
  → C_client_specific/<客户>_SKU.csv（W25 起步）
```

---

## §2. 目录结构

```
13_数据分析与工具脚本/商品库_v0.1/
├── README.md                     ← 本文件（主纲 + 双链入口）
├── 字段定义_v1.0.md              ← 字段字典（single source of truth）
├── B_category_skeleton.csv       ← Layer B（W24 填实）
├── A_core_sku.csv                ← Layer A（W26 填实）
├── C_client_specific/            ← Layer C 客户独有
│   ├── _模板.csv
│   ├── 花厅坊_SKU.csv            （W25 起步）
│   └── （其他客户战役）
├── _maintenance/
│   ├── brand_alias.csv           ← 品牌别名（海天 = HADAY = hisha）
│   ├── package_unit.csv          ← 容量包装标准（330ml = 0.33L）
│   └── update_log.md             ← 变更日志
└── _embedding/                   ← W26+ 升级（sentence-transformers）
    └── （占位）
```

---

## §3. 起步状态（W19 / 5/9 今晚）

| 文件 | 状态 | 数据规模 |
|---|---|---|
| README.md | ✅ 已建 | — |
| 字段定义_v1.0.md | ✅ 已建 | — |
| B_category_skeleton.csv | ⏸ 占位 | 0 SKU（W24 填实 3,000-5,000）|
| A_core_sku.csv | ⏸ 占位 | 0 SKU（W26 填实 1,000-2,000）|
| C_client_specific/_模板.csv | ✅ 已建 | — |
| C_client_specific/花厅坊_SKU.csv | ⏸ 占位 | 0 SKU（W25 填实 7,139）|
| _maintenance/brand_alias.csv | ✅ 已建 | 占位 5 条 |
| _maintenance/package_unit.csv | ✅ 已建 | 占位 5 条 |
| _maintenance/update_log.md | ✅ 已建 | — |

---

## §4. 数据来源（零成本起步 / Q3-A）

| Layer | 来源 | 时点 |
|---|---|---|
| **A 核心** | Open Food Facts（开源）+ 客户反哺 | W26 起步 |
| **B 骨架** | V4.0 大湾区版品类表（308 L4）| W24 起步 |
| **C 客户** | 客户 POS+ERP 数据反向 + 人工标注 | W25 起步（花厅坊）|

**Year 2 升级**：评估采购 GS1 中国会员（~5-10 万元/年）/ 视客户数量决定。

---

## §5. 与 V4.0 品类表的关系

```
V4.0 品类表（308 L4）= 结构 / 骨架 / single source of truth
商品库（A+B+C 三层）= 实例 / 血肉 / V4.0 的实例化

约束：商品库 SKU 必须有 category_l4 FK 指向 V4.0
关系：1 对多（L4 节点 → 多 SKU）

例：
  V4.0 L4 [10103] = 调味品/酱油/生抽
  商品库 SKU：
    sku_id=12345 / 海天生抽 500ml 玻璃瓶 / category_l4=10103
    sku_id=12346 / 海天金标生抽 1.5L / category_l4=10103
    sku_id=12347 / 千禾头道酱油 500ml / category_l4=10103
```

---

## §6. 4 层匹配算法对接（W27+ 立项）

```
商品库 v0.1（本模块 / 基础设施）
    ↓ FK
4 层匹配算法（应用层 / W27+）
    ├── Layer 1 规则层（brand_alias + package_unit）
    ├── Layer 2 模糊匹配（Levenshtein / TF-IDF）
    ├── Layer 3 LLM 语义（embedding / W30+）
    └── Layer 4 人工标注（反哺 Layer C）
    ↓
客户数据清洗模块（前端）
    ↓
诊断 / 分析 / 咨询交付（后端）
```

---

## §7. 治理（G11 月度审计）

详见 [[G11_商品库治理]]：
- 去重（同 SKU 多次反哺）
- 清洗（错别字 / 格式不规范）
- 版本（V4.0 → V4.1 时商品库重新分类）
- 跨客户匿名化（脱敏客户独有 SKU）
- 月度评分（与 G10 Memory 评分类似）

---

## §8. 关联

### 上游

- [[2026-05-09_商品库立项方案_v1.0]]
- [[CLAUDE.md]] §13 反幻觉 + §17.11+ 工程操作纪律

### 横向

- [[字段定义_v1.0]]（同模块 / 字段字典）
- [[05_品类管理与商品规划/商品库索引]]（双链 / 业务属性）
- [[品类表治理决议]] V4.0 大湾区版

### 下游

- [[G11_商品库治理]] SOP（W22+ 立项）
- 4 层匹配算法 v0.1（W27+ 立项）
- 客户数据清洗模块 v0.1（W30+）

---

## §9. 版本记录

| 版本 | 日期 | 变更 |
|---|---|---|
| **v0.1** | **2026-05-09** | **初版 / 主纲建立**：三层架构 + 目录结构 + 起步状态 + 数据来源 + V4.0 关系 + 4 层算法对接 + G11 治理 / W19 提前落地（基础架构 / W22+ 数据填实）|
