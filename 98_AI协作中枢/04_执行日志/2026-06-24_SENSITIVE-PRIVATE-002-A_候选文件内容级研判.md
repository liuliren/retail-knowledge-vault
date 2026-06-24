---
title: 2026-06-24｜SENSITIVE-PRIVATE-002-A｜候选客户明细与 goldmine 脚本内容级研判
date: 2026-06-24
task_id: SENSITIVE-PRIVATE-002-A
owner: 六哥
agent: Claude
module: 98_AI协作中枢/04_执行日志
summary: 只读研判 10 候选+扩查父目录；4 .md+8 .py 判客户专用迁私有区，5 工具保留；扩查新增 2 个客户专用 pipeline；不迁移不脱管。
tags:
  - 执行日志
  - 客户私有区
  - 内容级研判
  - SENSITIVE
---

# 2026-06-24｜SENSITIVE-PRIVATE-002-A｜候选文件内容级研判

## 1. 方法
只读内容级信号探测(写死「花厅坊」/门店口径/硬编码阈值/硬编码客户 csv 文件名/明细表行/SKU·商品引用),不回显敏感正文。

## 2. 结论
- **迁私有区(12)**:4 完整明细/抽样 .md + 6 goldmine .py + 扩查新增 2 pipeline(`full_dryrun_90d.py`/`merge_full_90d.py`)。
- **保留工具资产(5)**:`ir_calculator.py`/`safety_stock.py`/`test_retail_tools.py`(0 客户引用)+ `abc_classifier.py`/`README_测试自检.md`(轻引用,去客户化即可)。

## 3. 三个待裁决
1. 6 goldmine + 2 pipeline:**整迁私有区 vs 拆分工具化**?
2. **测试 import 依赖**:`test_retail_tools.py` 是否依赖将迁走的脚本?迁前必验,否则断测试。
3. `full_dryrun_90d.py`/`merge_full_90d.py` 为原 10 清单**扩查新增**,需确认纳入迁移。

## 4. 未触碰范围
未 git rm(--cached);未迁移/移动/复制/改名;未改候选正文;未脱敏写入;未删文件;未改写历史;未 push;未碰 xls/csv/db;未 `git add .`;未提交候选文件 / `_client_private/` 内文件。

## 5. 下一步
裁决三点后 → **SENSITIVE-PRIVATE-002-B**(脱管迁移):先验 import 依赖,再对确认文件 `git rm --cached` + 迁 `_client_private/花厅坊/`,保留本地。
