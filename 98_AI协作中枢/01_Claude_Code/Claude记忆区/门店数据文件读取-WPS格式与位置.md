---
name: wps
description: 花厅坊门店 .xls 多为 CDFV2/WPS 格式需 python-calamine 读；供应商/销售原始表在 99_原始素材，清洗合并表在 01_清洗输出
metadata: 
  node_type: memory
  type: reference
  originSessionId: 7ec6868c-e751-4c25-8d6f-0e1d036b31f3
---

**位置**（花厅坊 `09_…乐易购花厅坊店/`）：
- 原始 POS/档案/供应商导出表 → `99_原始素材/01_门店数据材料/` 与 `00_客户原始材料/`（只读，勿改）；
- Codex 清洗后的合并表 → `03_商品诊断/01_清洗输出/`（商品档案_合并版 / 销售统计汇总_合并版含主供应商列 / 库存即时快照 等）；
- 清洗脚本 → `13_数据分析与工具脚本/花厅坊POS清洗脚本` + `…/03_商品诊断/_品类匹配算法包`。

**格式坑**：很多门店 `.xls` 是 **CDFV2（WPS/金山）格式**，`xlrd` 报 `Expected BOF record; found b'\x01\x02...'`，本机 **LibreOffice 未装**。
**解法**：`python3 -m pip install python-calamine`，再 `pandas.read_excel(f, engine='calamine')` 可读。普通 .xls 用 xlrd、.xlsx 用 openpyxl。

**已知关键表**：`20260510_商品档案表_包含供应商信息.xls`（6854SKU/货号→供应商/进货价/采购周期/100%覆盖）；`供应商销售汇总_90天.xls`（主供应商+进货金额+类别）。读真实门店数据只做结构化分析，进价/采购额绝对值不入 md。相关：[[客户管理水平约束-花厅坊]]。
