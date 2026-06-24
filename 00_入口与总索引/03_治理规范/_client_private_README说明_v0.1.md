---
id: SENSITIVE-PRIVATE-001-README
title: 客户私有区 _client_private 说明（tracked 指针）
version: v0.1
status: draft
owner: 六哥
source_type: reference
created: 2026-06-24
module: 00_入口与总索引/03_治理规范
client_safety: internal_only
summary: 指向 gitignored 的 _client_private/ 客户私有区；该目录本身不进 git，此说明留在治理目录作可追溯指针。
tags:
  - 治理规范
  - 客户私有区
  - gitignore
  - SENSITIVE
---

# 客户私有区 `_client_private/` 说明

> 本文是 **tracked 指针**（`_client_private/` 整目录已 gitignored，其内文件不进 git，故说明放此）。

## 定位
`_client_private/`（库根）= 客户 **C/D 区**内容的本地私有区。依据 [[SENSITIVE-GOV-001_客户数据脱敏与Git保密治理规范_v0.1]] §3 + [[SENSITIVE-HISTORY-PLAN-001_未来同步与安全分支策略_轻量版_v0.1]] §6。

## 规则
1. 存放:客户诊断/经营判断/派生结论/完整明细/抽样/dry-run·execute review/原始数据。
2. **整目录 gitignored**:`.gitignore` 规则 `_client_private/`；其内文件**永不进普通 git**。
3. **禁止** `git add -f` 强加其内文件入 git。
4. **禁止 push**；**禁止**放入任何公开分支（含未来 public-safe）。
5. 可本地保留 + 外盘备份。
6. 客户案例要沉淀为方法论 → 先**去客户化脱敏**（SENSITIVE-GOV-001 §13）再放 A/B 区。

## 建议结构
```
_client_private/
└── 花厅坊/
    ├── goldmine/   金矿候选/分桶/抽样脚本与说明
    ├── reviews/    dry-run / execute review
    └── details/    清库/补货/诊断完整明细
```

## 关联
SENSITIVE-PRIVATE-001（建私有区 + ignore，本轮）；SENSITIVE-PRIVATE-002（客户明细/goldmine 文件脱管迁移,下一轮,待授权）。
