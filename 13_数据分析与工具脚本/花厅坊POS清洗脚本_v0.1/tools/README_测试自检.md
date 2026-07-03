---
title: Codex 工具测试自检说明（tools/）
status: draft
created: 2026-05-09
updated: 2026-05-09
module: 13_数据分析与工具脚本/花厅坊POS清洗脚本_v0.1
tags:
  - 零售工具
  - 单元测试
  - 自检
summary: clean checkout 后如何自检 P1-3 零售工具（ABC/IR/安全库存/库龄），跑 test_retail_tools 8 用例验证口径一致。
---

# Codex 工具测试自检说明（tools/）

> 本目录为 P1-3 零售工具源码（T-01/02 ABC、T-07 IR、T-09/10 安全库存/库龄）。本文件说明如何在 **clean checkout** 后自检测试。口径来源：[[零售工具注册表_v0.1]] §3.1（active）。

## 1. 测试命令
```bash
cd 13_数据分析与工具脚本/花厅坊POS清洗脚本_v0.1/tools
python3 -m unittest test_retail_tools -v
```
预期：`Ran 8 tests ... OK`。

## 2. 测试覆盖范围（test_retail_tools.py · 8 用例）
| 用例 | 覆盖 |
|---|---|
| test_abc_identity | apply_abc 输出列（销额ABC/毛利ABC/身份/需复核/复核原因）|
| test_nine_grid_full_coverage | 9 格裁决与 §3.1 完全一致 |
| test_no_observation_label | 「观察品」不出现在 9 格输出 |
| test_unknown_combination_not_fallback_observation | 未知组合→invalid_combination（非观察品）|
| test_c_yi_needs_review | C+乙 needs_review=True，其余 8 格 False |
| test_profit_dimension_uses_gross_profit_amount | 毛利维按毛利额贡献分档，非毛利率 |
| test_ir_formula | IR = 12×(1-毛利率)/ITO |
| test_age_grade | 库龄 0-30/30-60/60-90/>90 分级 |

## 3. clean-checkout 依赖
`test_retail_tools.py` 仅 import 同目录三模块（均已入 git）：`abc_classifier.py` / `ir_calculator.py` / `safety_stock.py`。无外部数据依赖，clean checkout 即可跑。

## 4. 禁止事项（铁律）
1. **不得用真实 xls / csv 跑测试**——测试只用内联构造的脱敏小样本（pandas DataFrame）；
2. **dry-run / execute 分离**：本目录测试 = 纯逻辑单测；dry-run runner（`retail_tools_dryrun.py`）与其输出（`_dryrun_preview/*.json`）**不入 git、不在本测试范围**；
3. 真实条码一律脱敏（`{{EAN13_已脱敏}}`），git tracked 文件真实 EAN-13 = 0。

## 5. 当前 execute blocked 原因
- 详见 [[Codex执行前置状态登记表_v0.1]]。
- 简言：**全量真实数据未到位 + dry-run 未审 + 用户 execute signoff 未签** → **当前不允许 execute**。脚本口径（9 格）虽已与 §3.1 一致，但 execute = 写回真实客户数据，须过签字门。

## 版本记录
| v0.1 | 2026-06-22 | CODEX-Tools-Ready-Batch-012：测试命令/覆盖8用例/clean-checkout依赖/禁止用真实数据跑测试/dry-run与execute分离/execute blocked 原因指向前置登记表 |
