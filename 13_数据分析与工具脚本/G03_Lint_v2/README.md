---
title: G03_Lint v2 知识库自动体检脚本
summary: Vault 自动体检脚本，扫描断链、孤儿、陈旧、权限等六查指标。
version: v0.1
status: active
owner: Codex
created: 2026-06-22
updated: 2026-06-22
module: 13_数据分析与工具脚本
tags:
  - G03_Lint
  - 知识库体检
  - Codex
source_type: tool
confidence: high
client_safety: internal_only
signoff: Codex dry-run implementation
---

# G03_Lint v2 知识库自动体检脚本

## 用途

一条命令扫描本 Obsidian Vault 的 Markdown 文件，输出六查体检仪表盘：

1. 断链查
2. 孤儿查
3. 状态查
4. Schema 查
5. 敏感查
6. 版本查

脚本只读取 Markdown 文件，不读取 Excel/CSV，不修改被扫描文件。

## 运行

```bash
cd /Users/davidliu/KnowledgeBase/retail-knowledge-vault
python3 13_数据分析与工具脚本/G03_Lint_v2/lint_v2.py
```

默认输出：

```text
00_入口与总索引/05_审计与档案/lint_仪表盘_最新.md
```

可选参数：

```bash
python3 13_数据分析与工具脚本/G03_Lint_v2/lint_v2.py --output /tmp/lint.md
python3 13_数据分析与工具脚本/G03_Lint_v2/lint_v2.py \
  --output /tmp/lint.md \
  --json-output /tmp/lint.json
```

JSON 输出使用 `schema_version: "1"`，只包含指标、阻断类型和文件路径，不包含正文或敏感命中值。

## 安全边界

- 只扫描 `.md` 文件。
- 默认排除 `99_归档`、`Clippings`、`.git`。
- 排除 `13_数据分析与工具脚本/知识库自动化_v1/runtime`，防止机器产物反向污染体检指标。
- 敏感命中只输出文件、类型、计数和掩码，不输出条码真值。
- 输出仪表盘可覆盖，其他文件不改。
- 核心知识检查 `summary`；status 规范枚举为 `draft/candidate/active/deprecated/archived`，仅报告、不自动改写。

## 测试

```bash
cd /Users/davidliu/KnowledgeBase/retail-knowledge-vault/13_数据分析与工具脚本/G03_Lint_v2
python3 -m unittest discover -s tests -v
```
