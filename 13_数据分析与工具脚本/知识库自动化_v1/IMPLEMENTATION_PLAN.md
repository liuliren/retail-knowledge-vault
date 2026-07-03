---
title: Knowledge Vault Automation Implementation Plan
status: draft
created: 2026-06-01
updated: 2026-06-01
module: 13_数据分析与工具脚本/知识库自动化_v1
tags:
  - 知识库自动化
  - 实施计划
  - G03_Lint
---

# Knowledge Vault Automation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为晟果新零售知识库建立可持续运行的资产台账、增量检测、质量门、运行日志和安全调度执行层。

**Architecture:** 新模块只读取 Vault 文件元数据与 Markdown，不读取 Office/数据库正文，不进入 `_client_private/`。所有机器产物写入模块自己的 `runtime/`，现有 G03 Lint 作为质量引擎由流水线调用；人工知识正文、客户数据和 Git 状态均不自动修改。

**Tech Stack:** Python 3.10+ 标准库、`unittest`、现有 G03 Lint v2、macOS launchd 配置模板。

---

### Task 1: 资产模型与安全扫描契约

**Files:**
- Create: `13_数据分析与工具脚本/知识库自动化_v1/tests/test_inventory.py`
- Create: `13_数据分析与工具脚本/知识库自动化_v1/kb_automation/models.py`
- Create: `13_数据分析与工具脚本/知识库自动化_v1/kb_automation/frontmatter.py`
- Create: `13_数据分析与工具脚本/知识库自动化_v1/kb_automation/inventory.py`

- [x] **Step 1: 写失败测试**

覆盖：排除 `_client_private/.git/runtime`、非 Markdown 只读元数据、Markdown frontmatter、SHA256、父级入口、敏感扩展分类。

- [x] **Step 2: 运行测试确认 RED**

Run: `python3 -m unittest tests.test_inventory -v`

Expected: FAIL，原因是 `kb_automation.inventory` 尚不存在。

- [x] **Step 3: 实现最小扫描器**

输出每个资产的相对路径、类型、大小、修改时间、哈希、frontmatter 摘要、父级入口和风险标签；不得输出 Markdown 正文。

- [x] **Step 4: 运行测试确认 GREEN**

Run: `python3 -m unittest tests.test_inventory -v`

Expected: 全部 PASS。

### Task 2: 快照与增量差异

**Files:**
- Create: `13_数据分析与工具脚本/知识库自动化_v1/tests/test_snapshot.py`
- Create: `13_数据分析与工具脚本/知识库自动化_v1/kb_automation/snapshot.py`

- [x] **Step 1: 写失败测试**

覆盖新增、修改、删除、未变化四类资产，以及首次运行无基线场景。

- [x] **Step 2: 运行测试确认 RED**

Run: `python3 -m unittest tests.test_snapshot -v`

Expected: FAIL，原因是快照差异模块尚不存在。

- [x] **Step 3: 实现确定性 JSON 快照与差异**

快照按路径排序；差异仅保存路径、变化类型和元数据，不保存正文。

- [x] **Step 4: 运行测试确认 GREEN**

Run: `python3 -m unittest tests.test_snapshot -v`

Expected: 全部 PASS。

### Task 3: 安全流水线与运行锁

**Files:**
- Create: `13_数据分析与工具脚本/知识库自动化_v1/tests/test_pipeline.py`
- Create: `13_数据分析与工具脚本/知识库自动化_v1/kb_automation/pipeline.py`
- Create: `13_数据分析与工具脚本/知识库自动化_v1/kb_automation/cli.py`
- Create: `13_数据分析与工具脚本/知识库自动化_v1/run.py`

- [x] **Step 1: 写失败测试**

覆盖专用 runtime 写入、并发锁、失败日志、G03 非零退出阻断、成功运行状态。

- [x] **Step 2: 运行测试确认 RED**

Run: `python3 -m unittest tests.test_pipeline -v`

Expected: FAIL，原因是流水线尚不存在。

- [x] **Step 3: 实现流水线**

顺序：扫描资产 → 生成差异 → 调用 G03 → 写仪表盘 → 原子替换 latest 快照 → 追加 JSONL 运行日志。

- [x] **Step 4: 运行测试确认 GREEN**

Run: `python3 -m unittest tests.test_pipeline -v`

Expected: 全部 PASS。

### Task 4: 可观测仪表与裁决队列

**Files:**
- Create: `13_数据分析与工具脚本/知识库自动化_v1/tests/test_dashboard.py`
- Create: `13_数据分析与工具脚本/知识库自动化_v1/kb_automation/dashboard.py`

- [x] **Step 1: 写失败测试**

覆盖摘要指标、增量清单、敏感阻断、AI 输出 aging、建议裁决和不回显正文。

- [x] **Step 2: 运行测试确认 RED**

Run: `python3 -m unittest tests.test_dashboard -v`

Expected: FAIL，原因是仪表模块尚不存在。

- [x] **Step 3: 实现机器仪表**

仅输出聚合指标和路径；AI 输出超过 7 天进入 `hold/review` 建议队列，不自动移动。

- [x] **Step 4: 运行测试确认 GREEN**

Run: `python3 -m unittest tests.test_dashboard -v`

Expected: 全部 PASS。

### Task 5: 调度、文档与全链验证

**Files:**
- Create: `13_数据分析与工具脚本/知识库自动化_v1/tests/test_scheduler.py`
- Create: `13_数据分析与工具脚本/知识库自动化_v1/kb_automation/scheduler.py`
- Create: `13_数据分析与工具脚本/知识库自动化_v1/README.md`
- Create: `13_数据分析与工具脚本/知识库自动化_v1/run_daily.sh`
- Modify: `.gitignore`

- [x] **Step 1: 写失败测试**

覆盖 launchd 模板路径、每日运行参数、日志路径和不自动加载约束。

- [x] **Step 2: 运行测试确认 RED**

Run: `python3 -m unittest tests.test_scheduler -v`

Expected: FAIL，原因是调度模块尚不存在。

- [x] **Step 3: 实现调度配置生成器和运行说明**

只生成 plist 预览；不执行 `launchctl bootstrap`。`runtime/` 加入 `.gitignore`。

- [x] **Step 4: 全链验证**

Run:

```bash
python3 -m unittest discover -s tests -v
python3 run.py run --vault ../../..
python3 run.py status --vault ../../..
git diff --check
```

Expected: 单测全通过；流水线生成 runtime 产物；状态命令返回最近运行结果；无空白错误。

### Task 6: 第二阶段扩展

**Files:**
- Modify: `13_数据分析与工具脚本/G03_Lint_v2/lint_v2.py`
- Create: `13_数据分析与工具脚本/G03_Lint_v2/tests/`
- Modify: `98_AI协作中枢/00_总控/系统状态.md`

- [x] **Step 1: 为 G03 增加结构化 JSON 输出测试**
- [x] **Step 2: 为 Git staged 保密闸增加自动阻断测试**
- [x] **Step 3: 接入正式系统状态，但不覆盖人工业务正文**
- [x] **Step 4: 经用户预览后安装并加载 launchd**

> 进度：Task 1-6 已于 2026-06-24 完成。调度已加载，每日 09:00 运行；首次 kickstart 退出码 0。
