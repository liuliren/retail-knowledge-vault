---
id: SENSITIVE-HISTORY-PLAN-001
title: 未来同步与安全分支策略（轻量版 · 不改写历史）
version: v0.1
status: draft
owner: 六哥
source_type: governance
created: 2026-06-24
updated: 2026-06-24
module: 00_入口与总索引/03_治理规范
client_safety: internal_only
summary: 远端确认 private→不清历史；转为"未来阻断+安全同步"：本地敏感 commit 不 push、A/B 走 public-safe 分支、C/D 本地私有、Claude/Codex 提交前固定检查。
tags:
  - 治理规范
  - Git同步
  - 安全分支
  - 客户隐私
  - SENSITIVE
---

# SENSITIVE-HISTORY-PLAN-001｜未来同步与安全分支策略(轻量版)

> 依据 [[SENSITIVE-GOV-001_客户数据脱敏与Git保密治理规范_v0.1]] + [[2026-06-24_SENSITIVE-HISTORY-AUDIT-001_Git历史客户敏感内容只读审计]]。
> **本文只制定策略,不执行**:不改写历史、不建分支、不改 .gitignore、不 push、不 git rm —— 均为下文标注的待执行项,需逐项授权。

## 0. 决策记录(六哥 2026-06-24)
1. 远端 `liuliren/retail-knowledge-vault` 确认**不会 public**。
2. **暂不执行历史改写**;禁止 filter-repo / BFG / rebase 清史 / 强推。
3. 早期历史中客户敏感内容,按 **private 仓可控风险**处理,不立即清除。
4. 重点从"清历史"→"**未来阻断 + 安全同步**"。
5. 本地 235 个未推送 commit **仍不得直接 push**,先按本方案执行。

## 1. 现状(来自 AUDIT-001)
- `origin/main`(private)已含 8 commit / 77 客户文件 —— 接受为可控,不动。
- 本地 `main` 领先 235 commit,含金矿明细/抽样/诊断 —— **不 push**。
- xls/csv/db 从未入 git。4 个「完整明细/抽样」.md + 14 个 goldmine .py 当前仍 tracked。

## 2. 双轨同步模型(核心)
| 轨 | 内容(四区)| 处置 |
|---|---|---|
| **轨 1 · 可同步** | A 方法论/模板/SOP/agent_rules/字段字典 + B 无客户经营判断的治理元数据 | 可版本化、可推 `public-safe` |
| **轨 2 · 本地私有** | C 客户诊断/经营判断/派生结论/dry-run·execute review + D 原始数据 | 本地私有,**默认不 tracked、永不 push** |

## 3. 推送策略(待执行)
1. **`origin/main` 冻结**:不再把本地 `main` push 到 origin(否则 235 敏感 commit 上传)。现有 77 文件不动(清除=改写历史,出范围)。
2. **`main` = 本地私有工作分支**:含全部历史与客户内容,**默认永不 push**;备份靠本地/外部盘,不靠 origin。
3. **需要备份/共享方法论时** → 走 `public-safe` 分支(§4),只推它。
4. 红线:**任何 push 前必须人工确认目标分支不含 C/D 内容**。
5. **关于逐 commit L2/L3 分类**:因 `main` 永不 push、`public-safe` 由 **A/B 文件快照**构建(非 cherry-pick commit),**逐个分类 235 个 commit 的 L2/L3 对推送决策无影响**,故本方案不做 commit 级分类。仅当未来改走"按 commit 同步"模式时,才需补 commit 级 L2/L3 审计。

## 4. safe-main / public-safe 分支方案(待执行)
- 名称:`public-safe`(curated,仅 A/B)。**别名 `safe-main` / `sync-safe` 视为同义**,本方案统一用 `public-safe`,避免混淆。
- 构建方式:**orphan 分支 + 干净快照**(不 cherry-pick 混杂 commit):
  `git checkout --orphan public-safe` → 清空工作区 → 只复制 A/B 区文件 → 提交为单一干净基线 → 后续仅同步 A/B 增量。
- 用途:方法论/治理规范的可分享版本;真要对外时推到**另建的独立 public 仓**(见 §8),**绝不把本仓设 public**。
- 维护:每次 A/B 有实质更新,手动把对应文件同步进 public-safe 并提交;C/D 永不进入。

## 5. A/B/C/D 四区同步映射(待执行)
| 区 | 示例 | tracked? | 进 main? | 进 public-safe? |
|---|---|---|---|---|
| A 可公开 | 方法论/模板/SOP/agent_rules | ✅ | ✅ | ✅ |
| B 内部治理 | 任务队列/登记表/规范/审计报告(无客户结论) | ✅ | ✅ | 选择性(脱客户引用后) |
| C 客户私有 | 诊断/经营判断/派生结论/明细/抽样/dry-run review | ❌ 默认 gitignored | 本地保留 | ⛔ 永不 |
| D 原始数据 | xls/csv/db/SKU/条码/进价/供应商/会员 | ❌ | ⛔ | ⛔ |

## 6. 客户资料 gitignored 私有区规则(待执行)
- 建本地私有目录(建议)`_client_private/`(根级,整目录 gitignored),客户 C 区内容归此,**只本地、不 tracked、不 push**。
- 现存 tracked 的 C 区文件(4 个「完整明细/抽样」.md + 14 个 goldmine .py)→ 另起任务 `git rm --cached` 迁入私有区(类 Claude执行日志处理,**本方案不执行,仅登记为待办**)。
- .gitignore 追加(待授权,本轮不改):`/_client_private/`、客户诊断聚合日志、dry-run/execute 结果表(已部分落地)。

## 7. Claude / Codex 提交前固定安全条款(即时生效)
> 每次提交前必须:
> 1. `git status --short` + `git diff --cached --name-only/--stat/--check` 核**全量**暂存区;
> 2. 确认无 C/D 内容:客户诊断/经营判断/派生结论(毛利率/PSD/死货/金矿/动销/库龄/明细/抽样)、xls/csv/db、dry-run/execute 结果、客户诊断日志、客户员工姓名;
> 3. **禁止 `git add .`**;只精确 `git add <路径>`;
> 4. **禁止 push `main` 到任何远端**(只允许 push `public-safe`,且推前再核一遍);
> 5. 发现疑似 C/D → **停止并报告**,不自行提交。

## 8. 未来公开/共享升级预案
- **绝不把本仓(`liuliren/retail-knowledge-vault`)设为 public** —— 它的 origin/main 已含 77 客户文件 + 历史敏感。
- 若需公开方法论 → **另建独立全新 public 仓**,只把 `public-safe`(A/B,经脱客户化复核)推过去;新仓从干净 orphan 起步,无本仓历史。
- 公开前过一遍 SENSITIVE-GOV-001 §11 检查清单 + §13 脱敏改写。

## 9. 本方案不做什么(红线)
不改写历史(filter-repo/BFG/rebase/强推);不 push 未审本地 commit;不提交客户敏感文件;不提交 dry-run/execute 结果;不提交客户派生分析结论;不碰 xls/xlsx/csv/db;不 `git add .`;本轮不建分支、不改 .gitignore、不 git rm(均为待授权执行项)。

## 10. 待办登记(各需单独授权)
1. `public-safe` orphan 分支构建。
2. `_client_private/` 私有区建立 + .gitignore 追加。
3. 现存 4 个明细 .md + 14 个 goldmine .py → `git rm --cached` 迁私有区。
4. 升 active 需六哥签字。
