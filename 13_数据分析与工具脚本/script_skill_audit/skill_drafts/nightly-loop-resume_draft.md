---
name: nightly-loop-resume
status: draft
version: v0.1-draft
created: 2026-07-08
owner: Claude 起草 / 六哥（签字后才生效）
审议轮次: 1
---

# /nightly-loop-resume（草案）

> **⚠️ draft · 未过 skill 上线铁律三件套（触发词字段/SKILL-INDEX行/gitignore白名单）· 不得当可用命令引用。** 触发词字段故意留空。

## 使用场景
夜间/长循环任务收口或次晨接续时："昨晚跑到哪了"——从 git 事实自动生成 LOOP_STATE 骨架，主线程只补判断相（NEXT 三条），替代手写断点文档的机械部分。

## 输入
时间窗（如 "24 hours ago"）；可选 known-dirty 清单（长期未提交路径前缀）。

## 输出
LOOP_STATE 骨架 md（COMPLETED commits / UNCOMMITTED 四类分拣：skill·handoff·known-dirty·待分类 / NEXT 留空）→ 落 Claude输出区，**不直接覆盖 `_当前断点_RESUME.md`**。

## 执行步骤
1. 〔脚本〕`python3 13_数据分析与工具脚本/tool_drafts/nightly_resume_builder_v0.1.py --since <窗> --repo <vault根> [--known-dirty <清单>]`（只跑 git log/status 两条只读命令）。
2. 〔LLM·判断相〕据骨架 + 会话记忆填 NEXT ≤3 条、标风险项。
3. 若需更新正式 RESUME：按 Token-Limited Context Protocol v2.0 压到 ≤300 tokens STATE 格式，**另行**写入并遵守其覆盖规则——这一步是独立动作，不在本 skill 自动做。

## 禁止事项 / 红线
- 不执行 git add/commit/checkout 等任何写 git 动作。
- 骨架含 commit 标题（可能带客户名）→ 仅内部断点用，不得外发、不得进对外交付件。
- 不自动覆盖 RESUME/宪法/任何 stable 件。

## 回滚/暂停机制
纯只读生成；若骨架输出中发现敏感路径异常（如 99_原始素材 出现在待提交区）→ 暂停并把该发现单列报六哥（这本身是 GOV-001 信号）。

## 与现有脚本关系
机械相=tool_drafts/nightly_resume_builder_v0.1.py（mock+真实repo只读实测通过）；与 /handoff、/compact 互补：handoff 管会话交接叙事，本 skill 管 git 事实骨架。

## 何时需六哥裁决
①上线三件套+签字；②known-dirty 清单内容；③是否允许其输出直接进正式 RESUME（当前默认不允许）。
