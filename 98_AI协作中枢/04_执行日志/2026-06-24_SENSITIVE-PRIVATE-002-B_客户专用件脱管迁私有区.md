---
title: 2026-06-24｜SENSITIVE-PRIVATE-002-B｜客户专用明细与 goldmine 脚本脱管迁私有区
date: 2026-06-24
task_id: SENSITIVE-PRIVATE-002-B
owner: 六哥
agent: Claude
module: 98_AI协作中枢/04_执行日志
summary: 前置闸确认测试不依赖迁走脚本；整迁 12 客户专用件到 _client_private/花厅坊/，git rm --cached + mv，本地零丢失，未改正文/未push。
tags:
  - 执行日志
  - 客户私有区
  - git脱管
  - SENSITIVE
---

# 2026-06-24｜SENSITIVE-PRIVATE-002-B｜客户专用件脱管迁私有区

## 1. 前置 import 依赖闸（只读，已过）
`test_retail_tools.py` 的 import:`unittest / pandas / abc_classifier / ir_calculator / safety_stock`。
**不 import 任何将迁走的 8 个脚本(goldmine ×6 + full_dryrun_90d + merge_full_90d)→ 迁移不断测试。** 未修测试、未改 import。

## 2. 实际迁移文件清单(12,整迁,不拆分)
| 原路径 | → 私有区 |
|---|---|
| `03_治理规范/花厅坊90天B控补货完整明细说明…md` | `_client_private/花厅坊/details/` |
| `03_治理规范/花厅坊90天D清库完整明细说明…md` | `…/details/` |
| `03_治理规范/花厅坊90天金矿5桶分层抽样说明…md` | `…/reviews/` |
| `03_治理规范/花厅坊90天金矿候选人工复核抽样说明…md` | `…/reviews/` |
| `…/tools/goldmine_bucketB_detail.py` | `…/goldmine/` |
| `…/tools/goldmine_bucketCE_detail.py` | `…/goldmine/` |
| `…/tools/goldmine_bucketD_detail.py` | `…/goldmine/` |
| `…/tools/goldmine_prejudge.py` | `…/goldmine/` |
| `…/tools/goldmine_sample_pack.py` | `…/goldmine/` |
| `…/tools/goldmine_sample_pack_003.py` | `…/goldmine/` |
| `…/tools/full_dryrun_90d.py` | `…/goldmine/` |
| `…/tools/merge_full_90d.py` | `…/goldmine/` |

## 3. 操作方式
每件:`git rm --cached --quiet -- <原路径>`(移出索引)→ `mv <原路径> _client_private/花厅坊/<子目录>/`(迁入 gitignored 私有区)。**未删除本地内容**。

## 4. 落位核验
私有区:details 2 / reviews 2 / goldmine 8 = 12 ✅;原 `tools/` 残留 goldmine/full/merge .py = 0 ✅;`_client_private/` 已 gitignored。

## 5. 未触碰范围
未删文件;未改任何迁移件正文/代码;未脱敏改写;未修测试;未改 import;未改写历史;未 push;未碰 xls/csv/db;未 `git add .`;未提交 `_client_private/` 内任何文件。

## 6. 测试依赖未决
本轮迁移**不影响** test_retail_tools.py(无依赖)。若未来有其它 runner/脚本 import 迁走模块,另起 **TEST-IMPACT-001** 修复(本轮不修)。

## 7. 下一步
TOOL-GENERALIZE-001(把可复用 goldmine 算法去客户化为通用工具,另建,不在私有区改);保留件 abc_classifier/README 的去客户化(轻引用)可并入。
