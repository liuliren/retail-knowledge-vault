---
title: 数据清洗匹配 retail_clean v0.2
summary: 门店数据清洗+跨文件条码匹配+派生指标(ABC/周转/呆滞)的健壮参数化 python 模块, 库存订货/单品类诊断共用地基
status: draft
client_safety: internal_methodology
fact_layer: observed
---

# retail_clean v0.2 — 数据底座 N1

> 版本: v0.1 清洗+匹配地基 → **v0.2 增派生指标层** (ABC/周转/呆滞/缺货/毛利率), 订货包与诊断 skill 共用同一套口径, 不再各自手撸。

> 把花厅坊/乐易购门店数据的「清洗 + 跨文件匹配」硬化成一个 robust、参数化、可复用的 python 模块。
> 这是 [[社区超市库存订货优化包]] 与 [[单品类诊断]] 共用的**确定性地基**——LLM 不再每次看表猜字段、手撸列序号。

## 1. 文件

| 文件 | 作用 |
|---|---|
| `retail_clean.py` | 核心模块 (函数式, 无副作用)。被诊断/订货 skill import。 |
| `selftest_huachangfang.py` | 自测脚本: 花厅坊·方便食品, 验证与 `run_inv.py` 样板一致 (52 SKU·0 负库存)。 |
| `README.md` | 本文。用法 + 6 类坑处理 + 数据质量边界。 |

## 2. 核心函数清单

| 函数 | 签名 | 职责 |
|---|---|---|
| `read_wps_xls` | `(path, sheet=0)` | 坑①: 用 calamine 读 WPS/CDFV2 .xls (兼容 .xlsx), 返回原始矩阵。 |
| `locate_header` | `(rows, field_candidates=None, header_keywords=None, scan_rows=30, min_fields=2)` | 坑②: 扫描定位表头行 + 建 `{字段:列序号}` 映射; 跨相邻行补全被拆散的合并表头。 |
| `clean_barcode` | `(x)` | 坑③: 去尾 `.0`、展开科学计数, 归一 join key。 |
| `is_barcode` / `to_num` | `(x, min_len=8)` / `(x)` | 条码判定 / 安全数值转换 (空返 None, 区别真实 0)。 |
| `parse_rows` | `(rows, header_idx, colmap, require_barcode=True)` | 矩阵→`{标准字段:值}` 记录 list, 数值列转 float, 滤汇总行。 |
| `drop_anomalies` | `(records, rules=None)` | 坑④: 规则化剔除 (负库存/价≤0/空货号品名), **返回剔除行数+原因**。 |
| `aggregate_sales_by_barcode` | `(sales_records)` | 明细按条码聚合销量/销额/**动销天数**。 |
| `join_by_barcode` | `(sales, inventory, archive=None, base="inventory")` | 坑⑥: 以条码为主键三表合一, 返回统一记录 + join 统计。 |
| `clean_store_file` | `(path, source_type, sheet=0, drop_rules=None, field_candidates=None, require_barcode=True)` | 高层封装: 读→定位→解析→剔除, 一步出干净记录 + meta。 |

`source_type` ∈ `{"inventory","sales","archive"}`, 各自有默认字段候选表 (`INVENTORY_FIELDS` / `SALES_FIELDS` / `ARCHIVE_FIELDS`)。

### 2.1 v0.2 派生指标层 (订货/诊断共用口径, 阈值参数化)

| 函数 | 签名 | 职责 |
|---|---|---|
| `compute_period_days` | `(sales_records, default=None)` | 由明细日期跨度推算统计天数 (花厅坊方便食品自动得 94, 与样板一致)。 |
| `compute_abc` | `(records, value_key="period_value", a_cut=0.7, b_cut=0.9)` | 累计占比 ABC 分层 (默认按库存期间销售额, 同 run_inv 口径)。 |
| `enrich_turnover` | `(records, period_days, asof_date=None, stale_gap_days=30, slow_dos=90)` | 补 日均动销/DOS/毛利率/呆滞/慢周转/缺货疑似 (进价依赖项仅参考)。 |
| `summarize` | `(records)` | 出聚合诊断口径 (ABC 分布/呆滞款数+积压/慢周转/缺货/积压成本), 无裸值。 |
| `build_dataset` | `(inventory_path, sales_path, archive_path=None, base, period_days=None, asof_date=None, ...)` | **端到端单入口**: 清洗三源→聚合→join→ABC+周转派生→汇总, skill 实际调用方式。 |

```python
# 订货包 / 单品类诊断 skill 的单一入口 —— 一行出全量诊断记录
from datetime import date
records, report = rc.build_dataset(
    inventory_path="库存积压报表_xxx.xls",
    sales_path="xxx_商品明细.xls",
    archive_path=None,                 # 可选第三源
    base="inventory", asof_date=date(2026, 5, 8))
# report["summary"] → {有效SKU, ABC, 呆滞款数, 呆滞积压成本, 慢周转款数, 缺货疑似款数, ...}
# records 每条含: abc / daily_velocity / dos / margin_rate / is_stale / is_slow / is_stockout_suspect
```

## 3. 用法

```python
import retail_clean as rc

# 单文件清洗 (参数化: 任意品类/门店, 不写死)
inv,  inv_meta  = rc.clean_store_file("库存积压报表_xxx.xls", "inventory")
sales, _        = rc.clean_store_file("xxx_商品明细.xls",     "sales")
sales_agg       = rc.aggregate_sales_by_barcode(sales)

# 跨文件匹配 (条码主键, 以库存定义 SKU 全集)
merged, stats = rc.join_by_barcode(sales=sales_agg, inventory=inv, base="inventory")
# merged: [{barcode, name, l3_category, supplier, price, inventory,
#           last_buy_date, sale_qty, sale_value, active_days,
#           cost_ref, backlog_cost, cost_reliability='仅参考'}, ...]
# stats : {全集SKU数, 命中_sales, join率_sales, ...} → 数据边界声明直接用
```

**扩展点 (新店/新报表零改码)**: 表头名变了, 只需在 `field_candidates` 加候选名:
```python
rc.clean_store_file(path, "inventory",
    field_candidates={**rc.INVENTORY_FIELDS, "inventory": ["当前库存","即时库存","结存"]})
```

**自定义剔除规则**:
```python
rc.drop_anomalies(records, rules={"drop_negative_inventory": True,
                                  "drop_nonpositive_price": False})
```

## 4. 6 类坑的处理说明

| # | 坑 | 处理 |
|---|---|---|
| ① | **WPS/CDFV2 .xls** pandas 常失败 | `read_wps_xls` 用 `python-calamine`。同时兼容 .xlsx。 |
| ② | **多行/合并表头 + 空列打乱列位** (库存表头在 r3、明细在 r6, 真实列被空列错位) | `locate_header` 扫前 30 行按关键词命中数选表头行, 再**按表头名**(非 idx)定位每列; 对仍缺的字段跨相邻 ±2 行补全 (治 `行号` 被拆到下一行)。 |
| ③ | **条码读成浮点** `6901234567890.0` (合成示例) | `clean_barcode` 去尾 `.0`、展开科学计数 → join key 一致化。 |
| ④ | **负库存/异常剔除** | `drop_anomalies` 规则化: 剔 当前库存<0 (生鲜重灾区)、零售价≤0、空货号/品名; **记录每类剔除行数与原因** → 直接喂数据边界声明。 |
| ⑤ | **进价不准** (花厅坊已知坑) | join 输出对进价依赖字段 (margin/backlog/turnover) 标 `cost_reliability='仅参考'`; 见 [[花厅坊数据质量坑]]。 |
| ⑥ | **跨文件匹配** | `join_by_barcode` 以条码为主键: 明细给销量/动销天数, 库存给当前库存/进货日期, 档案给类目/供应商; 类目/供应商按 档案>库存>明细 优先回填, 任一源可缺。 |

## 5. 已知数据质量边界

1. **进价不准** → 毛利率、库存积压成本 (backlog_cost)、周转天数 (DOS) 全部 `仅参考`, 不可作签字结论的唯一依据。
2. **明细缺零售价列** → `price` 由库存/档案补; 若都缺, 可用 销额÷销量 反推 (调用方决定)。
3. **archive join 率因源而异** — 花厅坊 方便食品 的类目+供应商已在库存+明细内, 现有 `联营/百货` 档案与该品类 **SKU 全集不重叠** (实测交集 0, 条码格式两侧均为干净 13 位, 非 key bug), 故档案为可选第三源。匹配真实档案需选与目标品类同 SKU 域的档案表。
4. **join 率 = 数据现实, 非缺陷** — 自测中 明细 join 率 60% (52 款库存里 31 款期间有销, 21 款呆滞/零动销), 与 `run_inv.py` 样板一致。

## 6. 自测结果 (基线对齐)

`python3 selftest_huachangfang.py` (需在 vault 根目录运行):

```
库存积压报表: 表头r3, 原始54行→解析52→有效52, 剔除: 无
商品销售明细: 表头r6, 明细2236行→聚合167条码
跨文件匹配  : 全集52, 命中明细31 (join率60%), cost_reliability='仅参考'
派生指标层  : 统计天数94(明细跨度自动算) ABC=A11/B10/C31 呆滞17款≈812元 慢周转48款 缺货0
build_dataset单入口: 与分步结果完全一致
全量基线对齐 run_inv.py (9 项断言全 ✅):
  有效SKU 52  负库存 0  ABC 11/10/31  呆滞17款·812元  慢周转48款  缺货0
```

v0.2 不只复现样板的 52 SKU·0 负库存, 而是**逐项复现 run_inv.py 全量诊断口径** (ABC/呆滞/慢周转/缺货), 证明派生层可安全替代各 skill 的自撸算法。

## 7. 铁律 (CLAUDE.md §6/§7)

- 只读门店原始数据 (`raw_sensitive`), 不改不删原文件。
- 客户裸值 (条码/进价) 不堆进上下文、不打印裸值 (自测输出条码掩码、不打印进价)。
- 输出客户明细 CSV 须落 `_client_private/` 或本目录 (本目录 `*.csv` 已 gitignore), 不入 git。
