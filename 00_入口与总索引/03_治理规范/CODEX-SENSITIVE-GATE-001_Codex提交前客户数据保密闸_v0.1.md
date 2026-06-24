---
id: CODEX-SENSITIVE-GATE-001
title: Codex 提交前客户数据保密闸
version: v0.1
status: draft
owner: 六哥
source_type: governance
created: 2026-06-24
updated: 2026-06-24
module: 00_入口与总索引/03_治理规范
client_safety: internal_only
summary: 将 Codex 会话纳入 SENSITIVE-GOV-001 提交前闸；客户明细、派生结论、金矿/完整明细、dry-run 和 execute 结果默认不得进入普通 Git。
tags:
  - 治理规范
  - Codex
  - Git保密
  - 客户隐私
  - SENSITIVE
---

# CODEX-SENSITIVE-GATE-001｜Codex 提交前客户数据保密闸

> 本文件是 [[SENSITIVE-GOV-001_客户数据脱敏与Git保密治理规范_v0.1]] 在 Codex 会话中的执行闸门。目标不是清历史,也不是迁移存量,而是**立即阻断 Codex 后续继续把客户敏感内容提交进普通 Git**。

## 1. 背景
- 2026-06-24 封板记录已确认:并行 Codex 会话曾在本仓提交 `CODEX-Goldmine-*` 与完整明细类内容,与 SENSITIVE-GOV-001 新口径冲突。
- SENSITIVE-GOV-001 已明确:客户原始数据、客户经营判断、客户派生分析结论、客户诊断日志、dry-run / execute 结果默认不进普通 Git。
- 因此 Codex 在 retail-knowledge-vault 内的后续 commit,必须先过本闸门。

## 2. 适用范围
- 适用于 Codex 在 retail-knowledge-vault 内的全部开发、分析、脚本、文档、治理任务。
- 适用于 commit 前的 staged 审核、文件裁决、提交阻断。
- 不适用于历史改写、文件迁移、私有区处置;此类事项另走 SENSITIVE-HISTORY-* / SENSITIVE-PRIVATE-*。

## 3. 固定红线
以下内容默认不得进入普通 Git:
1. 客户原始数据与明细。
2. 客户经营判断与客户派生分析结论。
3. 金矿候选、清库、补货、完整明细、桶明细。
4. dry-run / execute 结果与 review 结果。
5. 客户诊断日志、客户项目执行日志。
6. xls / xlsx / csv / db。
7. `_client_private/` 内任何文件。
8. 未经审查的未知文件。

## 4. 提交前必检命令
每次 Codex 准备 commit 前,必须先执行:
1. `git status --short`
2. `git diff --cached --name-only`
3. `git diff --cached --stat`
4. `git diff --check`

## 5. 敏感关键词
发现下列关键词时,默认按客户敏感内容审查:
- 花厅坊
- 金矿
- 候选
- 清库
- 补货
- 完整明细
- CE桶 / B桶 / D桶
- dry-run
- execute
- 毛利 / 毛利率
- PSD
- 死货
- 动销
- 库龄
- 库存诊断

## 6. 命中后的处理
- 立即停止 commit。
- 不自动脱敏。
- 不自动移动文件。
- 不自动执行 `git rm` / `git rm --cached`。
- 输出只读报告,等待用户裁决。

## 7. 可提交内容
以下内容在复核通过后,可进入普通 Git:
1. 通用工具说明。
2. 方法论与模板。
3. 治理规范与治理元数据。
4. 无客户经营判断的工程记录。
5. 无客户派生结论的执行闸门与状态登记。

## 8. 不可提交内容
以下内容默认不可提交:
1. 客户明细。
2. 客户派生分析结论。
3. dry-run / execute 结果。
4. 客户诊断日志。
5. `_client_private/` 内容。
6. 金矿/清库/补货/完整明细/桶明细。

## 9. 与 SENSITIVE-GOV-001 的关系
- SENSITIVE-GOV-001 定义四区隔离、L0-L4 分级、Git 入库标准。
- 本文件只负责把这些规则前置到 Codex 提交动作之前。
- 如本文件与 SENSITIVE-GOV-001 存在口径冲突,以 SENSITIVE-GOV-001 为上位规则。

## 10. Codex 固定执行条款
> 每次 Codex 准备 commit 前,必须人工判断 staged 中是否含:
> 1. xls/xlsx/csv/db
> 2. 客户名 + 经营数字
> 3. 毛利率 / PSD / 死货 / 金矿 / 动销 / 库龄 / 库存诊断
> 4. 清库 / 补货 / 候选 / 完整明细 / 桶明细
> 5. dry-run / execute 结果
> 6. 客户诊断日志
> 7. `_client_private/` 内文件
> 8. 未审查文件
>
> 若命中任意一项:
> - 停止 commit
> - 不自动脱敏
> - 不自动移动
> - 不自动 `git rm`
> - 输出报告,等待用户裁决

## 11. 本轮接入结论
- Codex 已承认并接入 SENSITIVE-GOV-001。
- 已确认当前 HEAD 仍有 8 个残留金矿/明细治理稿 tracked。
- 这 8 个残留**只登记为后续 `SENSITIVE-PRIVATE-002-C`**,本轮不处理、不迁移、不脱管。
