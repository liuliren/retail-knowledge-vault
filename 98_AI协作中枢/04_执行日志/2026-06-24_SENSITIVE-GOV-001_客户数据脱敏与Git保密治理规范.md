---
title: 2026-06-24｜SENSITIVE-GOV-001｜客户数据脱敏与 Git 保密治理规范落盘
date: 2026-06-24
task_id: SENSITIVE-GOV-001
owner: 六哥
agent: Claude
module: 98_AI协作中枢/04_执行日志
summary: 把客户数据脱敏/经营判断保护/Git 同步边界沉淀为正式治理规范；只新增文档，不改业务正文、不改 .gitignore、不处理历史。
tags:
  - 执行日志
  - 治理规范
  - 客户数据脱敏
  - Git保密
---

# 2026-06-24｜SENSITIVE-GOV-001｜客户数据脱敏与 Git 保密治理规范落盘

## 1. 依据
GIT-HYGIENE-001/002 + SENSITIVE-REVIEW-001 形成的口径:客户原始数据/经营判断/派生结论/诊断日志/dry-run·execute 结果默认不进普通 Git;普通 Git 只管方法论/模板/治理规则/无经营判断的工程记录。

## 2. 文档落点
`00_入口与总索引/03_治理规范/SENSITIVE-GOV-001_客户数据脱敏与Git保密治理规范_v0.1.md`(status=draft)。查重:无同名/近名规范。

## 3. 规范核心
18 节:定义 → 为何治理 → 四区隔离(A/B/C/D)→ L0–L4 分级 → 入库判断标准 → 允许/禁止清单 → **派生结论受控(无裸值≠可提交)** → AI 日志治理 → .gitignore 建议(只入文档)→ 提交前检查清单 → 裁决表模板 → 脱敏改写规则 → 历史残留原则(禁未授权 filter-repo)→ Claude/Codex 固定执行条款 → 事件对应 → 最小流程 → 反模式。

## 4. 本轮未触碰范围
未改 .gitignore(建议规则只写进文档);未改业务正文 / M-DEC / RetailOS / M1-M8;未处理 xls/csv/db;未移动客户文件;未执行任何历史改写(filter-repo/BFG/rebase/强推);未提交金矿review/治理债务队列/Claude执行日志;未 `git add .`;未批量扫描全库。

## 5. 下一步
SENSITIVE-HISTORY-AUDIT-001(只读评估历史残留)、ID-DEDUP-001(个人 vault KB-BUILD-001 改 ID);债务队列与金矿review 各自脱敏/裁决任务;本规范升 active 待签字。
