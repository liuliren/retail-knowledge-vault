---
name: mdec-promote-review
status: draft
version: v0.1-draft
created: 2026-07-08
owner: Claude 起草 / 六哥（签字后才生效）
审议轮次: 1
---

# /mdec-promote-review（草案）

> **⚠️ draft · 未过 skill 上线铁律三件套（触发词字段/SKILL-INDEX行/gitignore白名单）· 不得当可用命令引用。** 触发词字段故意留空，防误触发。

## 使用场景
六哥或主线程说"这批 M-DEC 卡能不能 promote / 做 promote 前审查"时：在 /promote（执行回填蒸馏）之前，先做一轮**独立的机械+判断双相审查**，把不就绪的卡拦在门外。

## 输入
一个或多个 M-DEC 卡路径（或中台决策库目录）。

## 输出
promote 就绪度审查表（每卡：4项机械检查结果 + 消歧三件套痕迹 + 审查意见 candidate/暂缓/退回），落 Claude输出区。

## 执行步骤
1. 〔脚本·机械相〕对每卡跑 `13_数据分析与工具脚本/tool_drafts/mdec_promote_checker_v0.1.py <卡> --vault <vault根>`（只读）。
2. 〔LLM·判断相〕对机械全过的卡，读正文核实：actual_outcome 是否真有结果证据、lessons 是否可蒸馏、目标概念页是否明确。
3. 汇总审查表，逐卡给意见；**不执行任何回填/状态变更**。
4. 递交六哥；六哥点头的卡才进 /promote 流程。

## 禁止事项 / 红线
- 不改任何 M-DEC 卡、概念页、status 字段（本 skill 纯审查）。
- 不得因机械检查通过就自行调用 /promote——promote 的蒸馏与关门是判断相+签字动作。
- 不读 99_原始素材/ 与客户 raw。

## 回滚/暂停机制
纯只读无回滚需求；审查中发现卡内含客户裸值等红线问题→立即暂停该卡审查并单列报六哥。

## 与现有脚本关系
机械相=tool_drafts/mdec_promote_checker_v0.1.py（本 Phase mock 测试通过）；与 /promote skill 是"审查→执行"上下游，不取代。

## 何时需六哥裁决
①本 skill 上线（三件套+签字）；②任一卡的 promote/退回终裁；③checker 就绪度4项口径若要改动。
