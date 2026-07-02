---
title: SKILL-INDEX（技能目录·≤200tokens·启动必读）
updated: 2026-06-30
---

# Skill Index

| Skill | 触发词（说出即自动调用） |
|---|---|
| `/ingest` | ingest、进料、读这篇、消化这个、编译这个 |
| `/scan` | scan、语料巡检、扫新语料、今天有什么新输入、检查新clip |
| `/deep-read` | deep-read、深度精读、续读、接着读、精读下一批、读零售老刘 |
| `/promote` | promote、蒸馏、提炼决策、回填lessons |
| `/draft` | draft、起草、帮我写、写篇文章、出稿、公众号稿、视频号、小红书 |
| `/publish` | publish、发文、配图上传、准备发布、走发布流程 |
| `/diagnose` | diagnose、诊断、测X类、出诊断卡、category diagnosis |
| `/review` | review、周复盘、月复盘、总结这周、帮我复盘 |
| `/compact` | compact、压缩上下文、该compact了、context太长了 |
| `/handoff` | handoff、交接、新会话prompt、整理上下文 |
| `/merge` | merge、两个文件对比、文档合并、去重、副本裁定 |
| `weekly_data.sh` | 生成周报数据、采集本周数据、周报采集、手动跑周报 |

**自动调用规则**：用户说出触发词 → 无需打 `/`，直接加载并执行对应 skill。

---

## Skill 上线铁律（新 skill 必过三项·缺一不得使用）

1. **frontmatter 有 `触发词:` 字段** — 供本索引拉取，格式：`触发词: [词A, 词B, ...]`
2. **本文件已追加对应行** — 名称 + 触发词，≤1 行
3. **`.gitignore` 已加白名单** — 如需 git 追踪则必加；本地专用 skill 可豁免

> 未过三项 = 未完成，不得在 CLAUDE.md 或其他 skill 中引用为可用命令。
