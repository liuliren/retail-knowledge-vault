---
title: POS清洗库 v0.1
summary: POS原始导出三合一清洗CLI(probe体检/sales销售明细/archive档案);七坑防护内置;花厅坊15.2万行0偏差首验
version: v0.1
status: candidate
created: 2026-07-02
owner: 六哥
module: 13_数据分析与工具脚本
---

# POS清洗库 v0.1

`pos_clean.py` 单文件 CLI，「POS 原始导出 → 标准表」的权威入口，/posclean skill 的执行层。

## 三个子命令

| 子命令 | 作用 | 输出 |
|---|---|---|
| `probe` | 目录体检：真伪格式(OLE魔数)/行数/截断/期间线索 | 控制台报告 |
| `sales` | 打印式销售报表(34列「商品-分部汇总」)→ 标准明细 master | `sales_master.csv` + 逐表对账 |
| `archive` | 商品档案表(两种版式自动识别)→ SKU 注册表 | `sku_registry.csv` + 停购维护率预警 |

## 七坑防护（花厅坊 2026-07-02 实测沉淀）

假xls检测 / 非标OLE(calamine引擎) / 打印报表行级过滤 / 65536截断报警 / 无表头位置映射 / 逐表对账(>0.5%报警) / 中文路径NFD安全。

## 工具链关系（不重叠）

```
POS原始导出 → [本库 probe→sales/archive] → 标准表 → [/trio 三件套引擎] → 分析结果
                                        ↘ [数据清洗匹配_v0.1] 字段级硬化 → 商品库_v0.1
花厅坊POS清洗脚本_v0.1 = 早期专用管道(dryrun/execute),保留;新数据一律走本库
```

## 纪律

- 先 probe 后清洗；任何 🔴 不带病进管道
- 原始只读；输出落客户工作区不入 git；列映射变更=口径变更须六哥确认
