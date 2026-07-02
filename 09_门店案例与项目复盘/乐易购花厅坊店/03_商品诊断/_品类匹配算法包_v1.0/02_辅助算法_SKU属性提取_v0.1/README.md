---
title: SKU 属性提取算法 v0.1
version: v0.1
status: active
owner: 六哥
created: 2026-05-04
updated: 2026-05-04
module: 13_数据分析与工具脚本
tags:
  - SKU提取算法
  - 品牌提取
  - 规格提取
  - 软件开发基础素材
  - 工程化资产
  - 跨客户复用
source_type: data
confidence: high
quadrant: III
client_safety: internal_only
related:
  - "[[花厅坊POS清洗脚本_v0.1]]"
  - "[[POS数据清洗与商品标准化规范_v0.1]]"
  - "[[2026-05-04_知识库重构方案_v0.2_完整作战方案]]"
---

# SKU 属性提取算法 v0.1

> **软件开发基础素材** — 后期产品化（PRD / SaaS / 嵌入式工具）的算法核心。
>
> 设计为**纯函数 / 无外部依赖（不调 LLM）/ 单元测试覆盖 / 跨客户复用**。

## 实测准确率（2026-05-04 / 花厅坊 700 SKU 验证）

| 算法 | 完全命中 | 部分命中 | 备注 |
|---|---|---|---|
| **SpecExtractor**（规格）| **93.2%** | +1.5% | 直接生产可用 |
| **BrandExtractor**（品牌）| **99.3%**（with 全品牌库）| | 依赖 KnownBrands；空库时启发式仅 ~17% |
| **BoxPackExtractor**（箱规）| 弱（信息源外置）| | 仅识别 SKU 名内偶尔明示的 N*M / 多数箱规要从采购合同补 |

> 验证方法：`tests/ground_truth_700sku.csv` 全量回归测试 / leave-one-out 严格验证。

## 设计原则

| 原则 | 实现 |
|---|---|
| 纯函数 | 三个 Extractor 类无副作用；输入相同 → 输出相同 |
| 无外部依赖 | 仅用 Python 标准库（re / dataclasses）；不调 LLM；不联网 |
| 单元测试 | 20 个测试覆盖单值/复合/中文/空输入/边界；ground truth 700 SKU 验证 |
| 输出含置信度 | 每个 ExtractResult 含 0.0-1.0 置信度；分级人工 review |
| 增量学习 | BrandExtractor 支持 `add_brand()` — 跨客户跨门店品牌库累积 |
| 可调试 | ExtractResult.method 标签溯源到具体规则；raw_match 留原始匹配文本 |

## 文件结构

```
SKU属性提取算法_v0.1/
├── README.md                          ← 本文件
├── sku_extractor.py                   ← 核心模块（SpecExtractor + BrandExtractor + BoxPackExtractor + 组合）
├── requirements.txt                   ← 无外部依赖（仅标准库）
├── tests/
│   ├── test_sku_extractor.py          ← 20 个单元测试 + ground truth 验证
│   └── ground_truth_700sku.csv        ← 验证基线（花厅坊 700 SKU 金标准）
└── examples/
    ├── basic_usage.py                 ← 5 行入门示例
    └── batch_process.py               ← 批处理（CSV 输入 / 输出补全表）
```

## 快速使用

### 安装

```bash
# 无外部依赖（标准库）
python3 -V  # 需 ≥ 3.10
```

### 基础用法（5 行）

```python
from sku_extractor import SKUAttributeExtractor

# 1. 加载已知品牌库（首次运行可空 / 后续从干净版主数据加载）
known_brands = {"雀巢", "可比克", "Calbee卡乐比", "三湘古镇", "无穷"}

# 2. 实例化
extractor = SKUAttributeExtractor(known_brands)

# 3. 提取
result = extractor.extract("可比克爽口青瓜味薯片55g")
print(result.brand.value)    # "可比克"   (conf=0.95)
print(result.spec.value)     # "55g"      (conf=0.95)
print(result.box_pack.value) # ""         (conf=0.00 / 弱算法)
```

### 批量处理

参见 `examples/batch_process.py` — 支持 CSV → CSV 流水线 + 三层来源标注（原表 / AI 补 / 未知）。

### 运行单元测试

```bash
cd SKU属性提取算法_v0.1
python3 -m unittest discover -s tests -v
```

预期：`Ran 20 tests in 0.02s / OK`

## API 参考

### `SpecExtractor`

```python
class SpecExtractor:
    def extract(sku_name: str) -> ExtractResult
```

支持模式：
- 单值：`100g` / `500ml` / `1.25L` / `70克` / `30片` / `2.5kg`
- 复合：`150g×3` / `3*150g` / `100ml*2`

### `BrandExtractor`

```python
class BrandExtractor:
    def __init__(known_brands: set[str] = None)
    def add_brand(brand: str) -> None
    def extract(sku_name: str) -> ExtractResult
```

策略：已知品牌库匹配（最长匹配，conf=0.95）→ 启发式英中混合（conf=0.6）→ 启发式纯中文（conf=0.4）。

### `BoxPackExtractor`

```python
class BoxPackExtractor:
    def extract(sku_name: str, spec: str = "") -> ExtractResult
```

弱算法 — 仅匹配 SKU 名内明示的 `N*M` / `N×M` 模式。多数箱规需从采购合同 / 经销商资料补充。

### `SKUAttributeExtractor`（组合）

```python
class SKUAttributeExtractor:
    def __init__(known_brands: set[str] = None)
    def add_brand(brand: str) -> None
    def extract(sku_name: str) -> SKUAttributes  # 含 brand / spec / box_pack 三个 ExtractResult
```

### `ExtractResult` 数据类

```python
@dataclass(frozen=True)
class ExtractResult:
    value: str              # 提取值（空 = 未识别）
    confidence: float       # 0.0-1.0
    method: str             # 方法标签（known_brand_match / rule_single / rule_composite / heuristic_*）
    raw_match: str = ""     # 原始匹配文本

    def __bool__(self) -> bool:
        return bool(self.value) and self.confidence >= 0.5
```

## 跨客户复用方法

**晟果商品主数据骨架库 v0.x 的合并逻辑**（参 [[2026-05-04_知识库重构方案_v0.2_完整作战方案]] §0.1）：

```python
# 第 1 家店：花厅坊（700 SKU 已沉淀 168 品牌）
extractor = SKUAttributeExtractor(known_brands=load_brands("花厅坊"))

# 第 2 家店：客户 A → 加载共享库 + 学习新品牌
extractor.add_brand("新品牌X")
extractor.add_brand("新品牌Y")
save_brands("共享库_v0.2", extractor.brand_extractor.known_brands)
# 客户 A 命中率应该 ≥85%（重合 SKU 直接命中）

# 第 3 家店：~95% 命中率（增量学习累积）
```

**护城河形态**：每多服务一家店，共享品牌库越厚 → 第 N 家店清洗成本指数下降。

## 局限与改进方向

| 局限 | 影响 | 改进方向 |
|---|---|---|
| 品牌算法依赖 KnownBrands | 空库时仅 17% 命中 | Phase 2 加 LLM 辅助层（Haiku 提取 + 人 review）|
| 箱规算法弱 | 命中率 <10% | 接入采购合同 / 经销商资料外部源 |
| 仅支持中文 + 简单英文 | 进口品 / 韩日品仍弱 | Phase 2 加多语言 NLP |
| 无主品牌 / 子品牌区分 | "Aji 小龙虾" → 提取 "Aji"，但有些场景需要子品牌 | Phase 2 加品牌层级体系 |
| 不识别"商品分类"（如薯片 / 巧克力）| 不在本算法范围 | 由 ERP 类别字典 / D04 / D05 单独处理 |

## 局限明示（反幻觉硬约束 [[CLAUDE.md]] §13）

1. **算法准确率以 700 SKU 为验证基线** — 跨业态跨地区可能下降，第二家店启动时必须重测
2. **置信度 0.5 以上才作为提取结果** — 0.4 启发式纯中文不算"识别"（见 `__bool__`）
3. **不修改原始数据** — 算法只输出建议，原始字段保留（参 [[CLAUDE.md]] §13.11 / Raw 4 条铁律）

## 关联

### 关联上游
- [[POS数据清洗与商品标准化规范_v0.1]]（SOP 上游）
- [[花厅坊POS清洗脚本_v0.1]] / config.py（消费方）

### 关联下游
- 商品主数据骨架库 v0.x（Phase 2 起跨客户共享库）
- 11_系统产品与PRD（Phase 3 产品化）
- `.claude/skills/数据清洗/` 镜像（Phase 2 W21，参 `_镜像图` §2.2）

### 关联案例
- 花厅坊战役 #1（首套实战 + ground truth）
- `09_/03_商品诊断/01_清洗输出/品牌主数据_干净版_v0.1.csv`（金标准）

## 版本记录

- **v0.1**（2026-05-04 / Phase 1 启动前夜）— 首版。规格 93.2% / 品牌 99.3%（with known_brands）/ 20 单元测试 ✅ / 工程化模块 + ground truth + examples + README。

## 待充实（Phase 2 / Phase 3）

- ⬜ LLM 辅助层（品牌算法在空库 / 启发式失败时的兜底）
- ⬜ 多语言扩展（韩日 / 进口品）
- ⬜ 主品牌 / 子品牌层级体系
- ⬜ 跨客户共享品牌库版本控制
- ⬜ FastAPI 服务化（产品化前置）
- ⬜ 增量学习的"品牌冲突检测"（同 SKU 名在不同客户提取出不同品牌时如何裁决）
