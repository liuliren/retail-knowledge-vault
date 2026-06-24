---
title: 2026-06-24｜SENSITIVE-HISTORY-PLAN-001｜未来同步与安全分支策略(轻量版)
date: 2026-06-24
task_id: SENSITIVE-HISTORY-PLAN-001
owner: 六哥
agent: Claude
module: 98_AI协作中枢/04_执行日志
summary: 远端 private→不清史，制定未来阻断+安全同步轻量策略；只落盘策略，不改写历史/不建分支/不改 .gitignore/不 push。
tags:
  - 执行日志
  - 治理规范
  - Git同步
  - 客户隐私
---

# 2026-06-24｜SENSITIVE-HISTORY-PLAN-001(轻量版)

## 1. 决策
远端确认 private → 暂不清历史(早期 77 文件按可控风险接受);转"未来阻断 + 安全同步"。

## 2. 落盘内容
`03_治理规范/SENSITIVE-HISTORY-PLAN-001_未来同步与安全分支策略_轻量版_v0.1.md`(status=draft):
- 双轨模型:轨1 A/B 可同步 / 轨2 C/D 本地私有;
- 推送策略:origin/main 冻结、main 永不 push、需要时走 public-safe;
- public-safe orphan 分支构建方案;
- A/B/C/D 四区同步映射表;
- `_client_private/` gitignored 私有区规则;
- Claude/Codex 提交前固定安全条款(即时生效);
- 公开升级预案:绝不设本仓 public,另建干净独立仓推 public-safe。

## 3. 只制定不执行
本轮未建分支、未改 .gitignore、未 git rm、未 push、未改写历史。待办(各需单独授权):public-safe 分支构建 / `_client_private/` 建立 + .gitignore 追加 / 4 明细 .md + 14 goldmine .py 迁私有区。

## 4. 未触碰范围
未 filter-repo/BFG/rebase/reset/强推;未 push;未 git rm(--cached);未改 .gitignore;未改业务正文;未脱敏写入;未碰 xls/csv/db;未 `git add .`。

## 5. 下一步
升 active 待签字;之后按待办逐项授权执行(建议先 `_client_private/` + 4+14 文件迁移,再 public-safe)。
