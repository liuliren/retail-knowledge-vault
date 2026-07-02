---
title: G03 Lint 双链巡检脚本 v0.1（每周一仪式 / Karpathy LLM wiki maintainer）
version: v0.1
status: active
quadrant: III
owner: 六哥
created: 2026-05-07
updated: 2026-05-07
module: 13_数据分析与工具脚本
tags:
  - G03_Lint
  - 双链巡检
  - 每周仪式
  - LLM_maintainer
  - Karpathy_wiki
source_type: data
confidence: high
client_safety: internal_only
---

# G03 Lint 双链巡检脚本 v0.1

> **本脚本**：vault 治理 SOP G03 Lint 的自动化实现 / 每周一仪式（30 分钟内跑完）/ Anthropic Constitutional AI 自检机制。
>
> **设计哲学**：[[feedback_anthropic_claude_alignment]] §6 LLM as maintainer — Claude（我）承担 90% 维护负担 / 用户专注实战。

## 1. 8 维度扫描

| # | 维度 | 触发红灯条件 |
|---|---|---|
| 1 | 悬空双链 | `wiki-link` 指向不存在的文件（>5 即红）|
| 2 | 命名漂移 | 文件名 vs 文件内 title 不一致 |
| 3 | quadrant 完整 | frontmatter 缺 quadrant（>5 即红）|
| 4 | v0.x 老化 | v0.x 文件 > 30 天未升级 |
| 5 | 99_待 Ingest 超期 | 90_素材内文件 > 14 天未处置 |
| 6 | 客户验证日志 24h | 客户接触后 24h 内无日志（红线）|
| 7 | 双链密度 | 文件 `wiki-link` < 5（II/III 象限）|
| 8 | 反幻觉红线 | "推断当事实"模式扫（语义检测）|

## 2. 使用方式

```bash
# 每周一早晨 / 跑 30 min 内
cd 13_数据分析与工具脚本/G03_Lint_双链巡检脚本_v0.1/
python3 lint.py

# 输出 → reports/2026-05-W19_lint_report.md
# 自动 update [[Vault健康仪表]] 8 维度数据
```

## 3. 设计原则（Anthropic Constitutional）

- ✅ **自动 enforce** / 不靠人工 review
- ✅ **报告驱动** / 不直接修改文件（除非 user 授权）
- ✅ **可追溯** / 每次扫描有时间戳 + SHA256
- ✅ **non-destructive** / 仅读 / 不写 vault 内容（仅写仪表）

## 4. 关联

- [[CLAUDE.md]] §18.3 G03 Lint SOP 定位
- [[feedback_anthropic_claude_alignment]] §6 LLM as maintainer
- [[Vault健康仪表]]（输出目标）
- [[2026-05-07_vault升级方案_v2.0]] §6 Phase 4

## 5. 待充实

- [ ] lint.py 实现（当前仅 README 占位 / Phase 4 完整实施）
- [ ] reports/ 目录建（每周一份报告）
- [ ] Vault 健康仪表自动 update hook
- [ ] 待 5/13 战役收口后 W20 启动首次 lint
