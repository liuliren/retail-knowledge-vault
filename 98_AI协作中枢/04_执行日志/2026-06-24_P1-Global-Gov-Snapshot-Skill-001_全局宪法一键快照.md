---
title: 2026-06-24｜P1-Global-Gov-Snapshot-Skill-001｜创建全局宪法一键快照 Skill
date: 2026-06-24
task_id: P1-Global-Gov-Snapshot-Skill-001
owner: 六哥
agent: Claude
module: 98_AI协作中枢/04_执行日志
summary: 为全局宪法轻量仓加一键快照脚本，只读源、只在本仓 commit、无变化 no-op，补"改了忘提交"漏洞。
tags:
  - 执行日志
  - 治理规范
  - CLAUDE宪法
  - 版本控制
---

# 2026-06-24｜P1-Global-Gov-Snapshot-Skill-001

## 1. 快照脚本路径
`/Users/davidliu/Claude-Global-Governance/snapshot-global-gov.sh`（可执行；脚本留在独立全局仓，不入 retail vault）。

## 2. 脚本功能
1. 安全护栏:仅允许在 `Claude-Global-Governance` 目录、且必须已是 git 仓,否则中止(绝不在 /Users 根 git init)。
2. 只读复制 `/Users/CLAUDE.md`、`/Users/log.md` → `snapshots/`(源缺失则中止/告警)。
3. `git diff` 检测快照变化:无变化 → 打印 `No snapshot changes.` 退出(不产生 commit);有变化 → 追加 `sync-notes.md` + 精确 `git add` + commit + 输出 hash。
4. 全程不 `git add .`,不改源文件。

## 3. 自测结果
| 检查项 | 结果 |
|---|---|
| 未修改原始 /Users/CLAUDE.md | ✅(mtime 未变) |
| 未修改原始 /Users/log.md | ✅(mtime 未变) |
| 只操作轻量仓 | ✅ |
| 未在 /Users 根 git init | ✅ |
| 未使用 git add . | ✅ |
| no-op 或成功 commit | ✅ no-op(源未变,幂等) |

## 4. 全局轻量仓修改文件
- 🆕 `snapshot-global-gov.sh`
- ✏️ `README.md`(新增「4.5 一键快照」节）
- 仓库本地 git 身份已配置(user.name/email),供脚本自动 commit。

## 5. 全局轻量仓 commit
`c7f41e2` · `chore: add global governance snapshot command`。

## 6. 一处有意改进(对原 Prompt）
原 Prompt B 要求 no-op 也记 sync-notes;改为 **no-op 不写 sync-notes、不产生 commit**,避免每次运行污染历史(更符合"少而深")。sync-notes 只记真实快照提交。

## 7. retail vault 记录
`当前任务队列.md` 追加 P1-…-Skill-001;本执行日志。

## 8. 未触碰范围
未改源全局文件;未在 /Users 根 git init;未把 /Users 纳入 Git;未 symlink/hardlink;未批量改宪法;未批量补 summary;未改方法论/M-DEC/RetailOS/M1-M8 正文;未处理真实数据;未 `git add .`。

## 9. 下一步建议
全局治理工具链已稳。按裁决进入 KB-BUILD-001 范式沉淀;summary 随用随补。
