---
title: 2026-06-24｜SENSITIVE-PRIVATE-003｜goldmine配置文件归属裁决
date: 2026-06-24
task_id: SENSITIVE-PRIVATE-003
owner: Codex
agent: Codex
module: 98_AI协作中枢/04_执行日志
summary: 裁决 goldmine 配置说明、配置加载器与配置模板的长期归属；保留治理说明 tracked，配置代码与模板移私有区。
tags:
  - 执行日志
  - 配置治理
  - 客户私有区
  - SENSITIVE
---

# 2026-06-24｜SENSITIVE-PRIVATE-003｜goldmine配置文件归属裁决

## 1. 裁决对象
1. `goldmine客户配置模板_SENSITIVE-PRIVATE-003_v0.1.md`
2. `tools/client_config.py`
3. `tools/client_config_template_goldmine.yaml`

## 2. 裁决结论
- `goldmine客户配置模板...md`：治理说明文档，可继续 tracked。
- `client_config.py`：不含真实客户值，但属于客户配置框架临时件，含私有路径约定与客户配置读取逻辑，**本轮移私有区**。
- `client_config_template_goldmine.yaml`：纯占位模板，但包含客户字段、输出前缀与 goldmine 阈值参数，**本轮移私有区**。

## 3. 原则
- 当前阶段，普通 Git 仅保留治理说明，不保留客户配置代码/模板。
- 若未来要把配置框架恢复为 tracked，须另开 `SENSITIVE-PRIVATE-004`，先做去客户化抽象再复审。

## 4. 实际处理
- `git rm --cached -- client_config.py`
- `git rm --cached -- client_config_template_goldmine.yaml`
- 移至 `_client_private/花厅坊/goldmine/`
- 治理说明文档继续 tracked，并补充收口口径。

## 5. 未触碰范围
- 未改真实客户配置。
- 未触碰 `_client_private/` 既有私有文件正文。
- 未 push、未改写历史、未删文件。

## 6. 下一步
- `SENSITIVE-PRIVATE-003` 收口完成。
- 整条 Codex 客户数据 Git 保密治理链可进入最终总复核。
