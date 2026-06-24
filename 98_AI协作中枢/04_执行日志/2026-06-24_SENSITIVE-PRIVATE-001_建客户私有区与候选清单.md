---
title: 2026-06-24｜SENSITIVE-PRIVATE-001｜建立客户私有区 + 客户明细候选文件清单
date: 2026-06-24
task_id: SENSITIVE-PRIVATE-001
owner: 六哥
agent: Claude
module: 98_AI协作中枢/04_执行日志
summary: 阶段A建 _client_private/ 私有区+gitignore；阶段B只读列候选——纠正为 4 .md + 6 .py = 10（非18）；不迁移不脱管。
tags:
  - 执行日志
  - 客户私有区
  - gitignore
  - SENSITIVE
---

# 2026-06-24｜SENSITIVE-PRIVATE-001｜建客户私有区 + 候选清单

## 阶段 A（已执行）
1. 建目录:`_client_private/花厅坊/{goldmine,reviews,details}` + 本地 `README.md`（已 gitignored，不 tracked）。
2. `.gitignore` 追加规则 `_client_private/`（依据 SENSITIVE-GOV-001 + PLAN-001 + 本任务）。
3. 治理目录留 tracked 指针 `00_入口与总索引/03_治理规范/_client_private_README说明_v0.1.md`。
4. 校验:`git check-ignore _client_private/README.md` 命中 ✅；其内文件永不进 git。

## 阶段 B（只读清单，未迁移/未脱管）

### ⚠️ 纠正 PLAN-001/AUDIT-001 计数失误
原记"14 goldmine .py / 共 18"有误：`grep -ic goldmine` 把 4 个文件名含 "CODEX-Goldmine-" 的 .md 也算进去了。**精确过滤 `goldmine.*\.py$` 后,goldmine .py 实为 6 个。真实候选 = 4 .md + 6 .py = 10 个文件。**

### 候选① 完整明细/抽样 .md（4，均 tracked，路径 `00_入口与总索引/03_治理规范/`）
| 文件 | tracked | 风险 | 类型 | 建议 |
|---|---|---|---|---|
| 花厅坊90天B控补货完整明细说明_CODEX-Goldmine-Bucket-B-Detail-001_v0.1.md | 是 | R2–R3 | 完整明细 | 待 P-002 脱管迁移 |
| 花厅坊90天D清库完整明细说明_CODEX-Goldmine-Bucket-D-Detail-001_v0.1.md | 是 | R2–R3 | 完整明细 | 待 P-002 脱管迁移 |
| 花厅坊90天金矿5桶分层抽样说明_CODEX-Goldmine-Sample-Pack-003_v0.1.md | 是 | R2 | 抽样 | 待 P-002 脱管迁移 |
| 花厅坊90天金矿候选人工复核抽样说明_CODEX-Goldmine-Sample-Pack-001_v0.1.md | 是 | R2 | 抽样 | 待 P-002 脱管迁移 |

### 候选② goldmine .py（6，均 tracked，路径 `13_数据分析与工具脚本/花厅坊POS清洗脚本_v0.1/tools/`）
| 文件 | tracked | 风险 | 类型 | 建议 |
|---|---|---|---|---|
| goldmine_bucketB_detail.py | 是 | R2–R3 | goldmine 脚本 | 待裁决（脚本可能含客户阈值/明细逻辑）|
| goldmine_bucketCE_detail.py | 是 | R2–R3 | goldmine 脚本 | 待裁决 |
| goldmine_bucketD_detail.py | 是 | R2–R3 | goldmine 脚本 | 待裁决 |
| goldmine_prejudge.py | 是 | R2 | goldmine 脚本 | 待裁决 |
| goldmine_sample_pack.py | 是 | R2 | goldmine 脚本 | 待裁决 |
| goldmine_sample_pack_003.py | 是 | R2 | goldmine 脚本 | 待裁决 |

> 需用户裁决:① 6 个 .py 是"通用脚本（去客户数据后可留 A 区）"还是"客户专用（迁私有区）"——需内容级判断;② 整个 `花厅坊POS清洗脚本_v0.1/tools/` 父目录是否也客户专用（本轮未扩查，仅就 goldmine 6 个列候选）。

## 未触碰范围
未 git rm(--cached);未迁移/移动/复制候选文件;未改候选文件正文;未删除任何文件;未改写历史;未 push;未碰 xls/csv/db;未 `git add .`;未提交 `_client_private/` 内任何文件。

## 下一步
六哥确认 10 个候选清单准确 → 发起 **SENSITIVE-PRIVATE-002**（脱管迁移）。其中 6 个 .py 需先裁决"通用 vs 客户专用"。
