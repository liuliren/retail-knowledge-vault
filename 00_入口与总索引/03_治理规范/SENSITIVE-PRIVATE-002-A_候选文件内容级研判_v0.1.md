---
id: SENSITIVE-PRIVATE-002-A
title: 候选客户明细与 goldmine 脚本内容级研判
version: v0.1
status: draft
owner: 六哥
created: 2026-06-24
module: 00_入口与总索引/03_治理规范
client_safety: internal_only
summary: 只读研判 10 候选+扩查父目录；4 .md 与 8 .py 判客户专用→迁私有区，5 工具判通用→保留；扩查新增 2 个客户专用 pipeline。
tags:
  - 治理规范
  - 客户私有区
  - 内容级研判
  - SENSITIVE
---

# SENSITIVE-PRIVATE-002-A｜候选文件内容级研判

> **纯只读研判**:未迁移、未脱管、未改名、未改正文。本报告只记分类/计数,不回写客户数字/SKU/明细。

## 1. 执行结论
- **4 个完整明细/抽样 .md**:全含 SKU/商品/毛利数值表 → **客户明细(R2–R3),迁私有区**,不可直接工具化。
- **6 个 goldmine .py**:全写死「花厅坊+门店口径+阈值+客户 csv 文件名」→ **客户专用,迁私有区**(算法可未来拆分工具化)。
- **扩查父目录新增 2 个客户专用**:`full_dryrun_90d.py`、`merge_full_90d.py`(写死花厅坊)→ **候选迁私有区**(原 10 清单外)。
- **5 个通用工具**:`ir_calculator/safety_stock/test_retail_tools`(0 花厅坊)+ `abc_classifier`(2 引用)+ `README_测试自检`(1 引用)→ **保留 tracked**,后两者去客户化即可。

## 2. 10 个原候选研判表
| 文件 | tracked | 类型 | 风险 | 客户专用 | 可工具化 | 建议裁决 |
|---|---|---|---|---|---|---|
| B控补货完整明细.md | 是 | 完整明细 | R3 | 是 | 否 | **迁私有区** |
| D清库完整明细.md | 是 | 完整明细 | R3 | 是 | 否 | **迁私有区** |
| 金矿5桶分层抽样.md | 是 | 抽样 | R2–R3 | 是 | 否 | **迁私有区** |
| 金矿候选人工复核抽样.md | 是 | 抽样明细 | R3 | 是 | 否 | **迁私有区** |
| goldmine_bucketB_detail.py | 是 | 脚本 | R2–R3 | 是 | 拆分后可 | **迁私有区** |
| goldmine_bucketCE_detail.py | 是 | 脚本 | R2–R3 | 是 | 拆分后可 | **迁私有区** |
| goldmine_bucketD_detail.py | 是 | 脚本 | R2–R3 | 是 | 拆分后可 | **迁私有区** |
| goldmine_prejudge.py | 是 | 脚本 | R2 | 是 | 拆分后可 | **迁私有区** |
| goldmine_sample_pack.py | 是 | 脚本 | R2 | 是 | 拆分后可 | **迁私有区** |
| goldmine_sample_pack_003.py | 是 | 脚本 | R2 | 是 | 拆分后可 | **迁私有区** |

> 研判依据:4 .md 均含商品/SKU/条码引用 + 毛利/金额数值 + 明细表(7~34 表格行);6 .py 各写死「花厅坊」3~4 处 + 门店口径 + 硬编码阈值 + 客户 csv 文件名。

## 3. 父目录扩查结果(`13_数据分析与工具脚本/花厅坊POS清洗脚本_v0.1/tools/`,13 文件)
| 文件 | 行 | 花厅坊 | 门店 | 硬文件名 | 归类 |
|---|--:|--:|--:|--:|---|
| ir_calculator.py | 25 | 0 | 0 | 0 | 通用 ✅ |
| safety_stock.py | 71 | 0 | 0 | 0 | 通用 ✅ |
| test_retail_tools.py | 256 | 0 | 0 | 0 | 通用(测试)✅ |
| abc_classifier.py | 241 | 2 | 2 | 0 | 核心算法,轻引用 → 保留+去客户化 |
| README_测试自检.md | — | 1 | — | — | 测试文档 → 保留+去客户化 |
| **full_dryrun_90d.py** | 153 | 4 | 1 | 2 | **客户专用(新候选)** |
| **merge_full_90d.py** | 260 | 5 | 1 | 1 | **客户专用(新候选)** |
| goldmine_*.py ×6 | — | 3~4 | 1 | 2~3 | 客户专用(已在原候选)|

## 4. 建议迁私有区清单(12 = 原 10 + 扩查 2)
- 4 .md:B控补货 / D清库 / 金矿5桶抽样 / 金矿候选人工复核抽样。
- 8 .py:goldmine ×6 + **full_dryrun_90d.py + merge_full_90d.py**(新增)。

## 5. 建议工具化保留清单(5)
- 直接保留(0 客户引用):`ir_calculator.py`、`safety_stock.py`、`test_retail_tools.py`。
- 保留 + 去客户化(删少量引用):`abc_classifier.py`(2 处)、`README_测试自检.md`(1 处)。

## 6. 暂不处理 / 需人工裁决
1. **6 goldmine + full_dryrun + merge:迁私有区(默认)还是拆分工具化?** 拆分=把通用分桶/抽样算法去客户化留 A 区 + 客户口径/路径入私有区;成本较高,需你定值不值。
2. **测试依赖风险(关键)**:`test_retail_tools.py`(保留)是否 import goldmine/full_dryrun/merge?若是,迁走会**断测试**——PRIVATE-002-B 执行前必须先验证 import 关系。
3. `full_dryrun_90d.py`、`merge_full_90d.py` 是原 10 清单外的扩查新增,需你确认纳入迁移范围。

## 7. 实际提交文件(本轮)
研判报告(本文)+ 当前任务队列 + SENSITIVE-PRIVATE-002-A 执行日志。**候选文件本身一个未动、未提交。**

## 8. commit hash
见执行日志 / 提交记录。

## 9. 未触碰范围
未 git rm(--cached);未迁移/移动/复制/改名;未改任何候选文件正文;未脱敏写入;未删文件;未改写历史;未 push;未碰 xls/csv/db;未 `git add .`;未提交候选文件 / `_client_private/` 内文件。

## 10. 下一步建议
你裁决三点(§6)后 → **SENSITIVE-PRIVATE-002-B｜客户专用文件脱管迁私有区**:先验证测试 import 依赖,再对确认的 12 个文件 `git rm --cached` + 迁 `_client_private/花厅坊/{details,goldmine,reviews}`,保留本地、不删除。
