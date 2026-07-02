---
title: 晟果新零售知识库自动化执行层
version: v0.1
status: draft
owner: Codex
created: 2026-06-24
updated: 2026-06-24
module: 13_数据分析与工具脚本
source_type: tool
client_safety: internal_only
summary: 资产台账、增量质量门、运行日志和安全调度入口
related:
  - "[[2026-06-24_知识库全量资产与自动化成熟度审计_v0.1]]"
  - "[[13_数据分析与工具脚本/G03_Lint_v2/README|G03 Lint v2]]"
---

# 晟果新零售知识库自动化执行层 v0.1

## 定位

本模块把现有知识治理规则转化为可重复运行的执行链：

`资产扫描 → 快照差异 → G03 质量门 → 决策队列 → 仪表盘 → 运行日志`

它不修改知识正文，不移动或删除文件，不读取 Office/数据库正文，不进入 `_client_private/`。

## 机器产物

全部写入本目录的 `runtime/`，该目录不进入 Git：

- `inventory_latest.json`：最近一次通过质量门的资产基线。
- `inventory_candidate.json`：质量门阻断时保留的候选快照。
- `delta_latest.json`：相对成功基线的新增、修改、删除清单。
- `g03_latest.md`：本次 G03 检查报告。
- `g03_latest.json`：版本化 G03 结构化指标与路径清单。
- `staged_gate_latest.json`：SENSITIVE-GOV 提交前自动闸结果。
- `task_registry_latest.json`：收件箱与当前任务队列的统一任务注册表。
- `dashboard_latest.md`：自动化运行仪表。
- `system_status_latest.md`：独立机器系统状态，不覆盖人工状态文件。
- `runs.jsonl`：不可覆盖的运行日志。
- `pipeline.lock`：并发运行锁，正常退出后自动清理。

## 使用

```bash
cd /Users/davidliu/KnowledgeBase/retail-knowledge-vault/13_数据分析与工具脚本/知识库自动化_v1

# 只做资产计数，不写 runtime
python3 run.py scan --vault ../..

# 跑完整流水线
python3 run.py run --vault ../..

# 查看最近一次运行状态
python3 run.py status --vault ../..

# 生成每日 09:00 launchd 配置预览，不安装
python3 run.py scheduler-preview --vault ../.. --hour 9 --minute 0

# 校验、安装并立即验证每日调度
python3 run.py scheduler-install --vault ../.. --hour 9 --minute 0
```

## 质量门

- G03 `redline > 0`：阻断，不更新成功基线。
- candidate 越权签字：阻断，不更新成功基线。
- staged 命中客户数据、派生经营结论、敏感扩展或 `_client_private/`：阻断。
- 运行异常：记录 `failed`，不更新成功基线。
- 正常运行：原子替换 `inventory_latest.json`。

## 测试

```bash
python3 -m unittest discover -s tests -v
```

## 调度边界

当前 LaunchAgent：

- Label：`com.shengguo.retail-knowledge-vault.automation`
- 时间：每日 09:00（本机时区）
- 配置：`~/Library/LaunchAgents/com.shengguo.retail-knowledge-vault.automation.plist`
- 行为：只运行本模块，不 commit、不 push、不移动文件。

安装命令会原子写入 plist，先执行 `plutil -lint`，再执行 `launchctl bootstrap` 和 `kickstart`。
