---
title: pre-flight check checklist v1.0（操作前自检 / L1 操作契约）
version: v1.0
status: active
signoff:
  approved_by: 六哥
  approved_at: 2026-06-22
  approval_basis: "P0-GOV-Signature-Batch-002：首批高确定性 active 治理基础件签字补齐"
  approval_scope: "确认当前 active 状态；不代表重新审定全文，不改变正文方法论口径"
  approval_status: approved
owner: 六哥
created: 2026-05-09
updated: 2026-05-09
module: 00_入口与总索引/03_治理规范
quadrant: I
client_safety: internal_only
related:
  - "[[工程操作纪律手册_v1.0]]"
  - "[[工程操作错误案例库]]"
  - "[[反幻觉检查清单]] v1.2"
---

# pre-flight check checklist v1.0

> **目的**：vault 工程操作纪律 4 层治理底盘的 **L1 操作契约** / 每次重要操作前的自检清单。
>
> **使用方式**：高风险操作（git / Bash / Edit / Write / 数据分析）前 / 按场景过对应 checklist / 不通过不执行。

---

## §1. 通用 pre-flight check（每次 Bash 命令前）

### 1.1 cwd 验证（5/9 触发）

- [ ] cwd 是否在 vault？（`pwd` 应输出 `/Users/davidliu/KnowledgeBase/retail-knowledge-vault`）
- [ ] 上一次命令是否包含 `cd <other>` 切走 cwd？
- [ ] 是否需要用 `git -C <repo>` 显式指定？

### 1.2 命令副作用评估

- [ ] 命令是否破坏性？（rm -rf / git reset --hard / git push --force）→ 用户确认
- [ ] 命令是否影响其他文件 / 目录？
- [ ] 命令失败是否会污染 cwd / state？

### 1.3 工具选择

- [ ] 是否优先用 dedicated tools？（Read 而非 cat / Edit 而非 sed）
- [ ] 是否多个独立操作应并行？

---

## §2. Git 操作 pre-flight

### 2.1 commit 前

- [ ] `git status` 看清当前状态
- [ ] `git diff` 验证修改是否符合预期
- [ ] 是否有 `.env` / 敏感文件被 staged？
- [ ] 是否优先 `git add <specific>` 而非 `git add -A`？
- [ ] commit message 第 1 行 ≤ 72 字符？格式 `chore/feat/fix/docs/refactor: 简明动词`？

### 2.2 push 前

- [ ] 用户是否明确要求 push？（默认不 push）
- [ ] 是否 push 到 main/master？（force push 必须用户明确）
- [ ] 是否包含 hook bypass（`--no-verify`）？（默认不允许）

### 2.3 不破坏性操作

- [ ] `git reset --hard` / `git branch -D` / `git clean -f` / `git checkout --` 是否用户明确？
- [ ] 是否有更安全的替代（如 `git stash` / `git revert`）？

---

## §3. 文件操作 pre-flight（Read / Edit / Write）

### 3.1 Edit 前

- [ ] 是否已 Read 该文件？（系统强制）
- [ ] old_string 是否唯一？（避免 multiple matches 错误）
- [ ] 缩进是否精确（含 tab 后内容）？
- [ ] 修改范围是否在用户指定的任务包内？

### 3.2 Write 前

- [ ] 是否新文件？（已有文件应用 Edit）
- [ ] 是否用户明确要求新建？（绝不擅自创建 .md / README）
- [ ] 路径是否符合 [[文件命名规范]]？
- [ ] frontmatter 是否完整（含 fact_layer / quadrant / etc）？

### 3.3 大范围修改前

- [ ] 是否列拟修改清单 + 等待用户确认？
- [ ] 是否单一任务包内？（不顺手扩写）

---

## §4. 数据分析 pre-flight（与 §13.20 协同）

### 4.1 数据来源

- [ ] 是否记录文件名 + sheet + 行号 + 时段 + 字段定义？
- [ ] frontmatter `data_source` + `fact_layer` 是否完整？
- [ ] 时段定义是否精确？（不 "30 天" / 写明 4/8-5/8 / 31 天）

### 4.2 数学验证

- [ ] 数字之间是否数学闭合？
- [ ] 不一致时是否列 ≥ 3 种解释 + 数学验证？
- [ ] 是否标 [推断]？是否让用户 confirm？

### 4.3 字段定义

- [ ] 报表字段语义是否追溯？（如"客流"实际可能是"客单数"）
- [ ] 行数 vs 实际数据行（去 header / 去小计）是否区分？

详见 [[反幻觉检查清单]] §M v1.2

---

## §5. 进程与执行 pre-flight

### 5.1 长任务

- [ ] 任务预计 ≥ 30 秒？→ `run_in_background: true`
- [ ] 是否避免 sleep 轮询？（用 Monitor / 系统通知）
- [ ] timeout 是否合理？（默认 2 min / 长任务自定义）

### 5.2 失败处理

- [ ] 失败 ≥ 3 次是否停止？（不死循环）
- [ ] 是否排查根因（不简单重试）？

---

## §6. 工具调用 pre-flight

### 6.1 工具选择

- [ ] Read / Edit / Write 优先于 Bash？
- [ ] 多个独立操作是否并行？
- [ ] 跨域研究是否用 subagent？（保护主 context）

### 6.2 Subagent

- [ ] 任务是否真需要 subagent？（不滥用）
- [ ] 任务上下文是否完整传递？（subagent 不知道当前会话）

---

## §7. 自我修订 / 错误纠正 pre-flight

### 7.1 用户订正

- [ ] 是否优先用户最新订正？（不"我记得用户最早说过 X"）
- [ ] 旧版表述是否 audit-log 留存（不删 / 标 ❌）？
- [ ] 是否更新 feedback memory（跨会话不再犯）？

### 7.2 错误案例沉淀

- [ ] 是否沉淀至 [[工程操作错误案例库]] / [[数据一致性追溯案例库]]？
- [ ] 5 段固定结构（触发 / 错误做法 / 根因 / 修复 / 教训）是否完整？

---

## §8. 高风险场景一键 checklist

### A. 跨外部目录数据分析

```
□ §1.1 cwd 验证（必须 pwd）
□ §1.2 命令副作用评估（不 cd / 用脚本内 chdir）
□ §4.1-4.3 数据来源 / 数学验证 / 字段定义
□ §6.1 工具选择（Read 文件而非 cat）
```

### B. git commit + push

```
□ §1.1 cwd 验证
□ §2.1 commit 前 5 项
□ §2.2 push 前 3 项
□ §2.3 不破坏性 2 项
```

### C. 大范围 vault 修改

```
□ §3.3 大范围修改前 2 项
□ §1.3 工具选择（Edit 优先）
□ §7.1 用户订正优先
```

---

## §9. 与现有 checklist 的关系

```
[[反幻觉检查清单]] v1.2 §A-§M（13 段）= vault 内容反幻觉
本 pre-flight checklist v1.0 = vault 工程操作纪律
两者协同 / 形成 vault 端到端 checklist 闭环
```

---

## §10. 版本记录

| 版本 | 日期 | 变更 |
|---|---|---|
| **v1.0** | **2026-05-09** | **初版 / vault 第 5 大支柱 L1 操作契约**：8 大场景 + 高风险一键 checklist 3 个 + 与反幻觉 checklist 协同。触发：5/9 cd /tmp 事件 + 6 大类规则需要操作前自检载体 |
