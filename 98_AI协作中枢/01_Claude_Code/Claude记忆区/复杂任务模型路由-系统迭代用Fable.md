---
name: complex-task-model-routing-fable
description: 系统迭代/架构设计等复杂判断类任务派代理时须显式指定Fable模型,不依赖默认继承
metadata:
  node_type: memory
  type: feedback
---

**六哥 2026-07-07 令**："系统迭代等复杂任务,要调用fable等最优模型处理。"

**Why**：五层模型调度(retail CLAUDE.md §7)已定义 L3=Fable主线程 专司判断相/编排/审计合成,L2=Sonnet代理专司机械+轻判断——但用 Agent 工具派子代理时,若不显式传 `model` 参数,子代理走的是其自身 agent 定义的默认模型(如通用 general-purpose 类型未必锁定继承主线程档位),存在"复杂任务被静默降级到较低档模型执行"的风险。六哥这句话是把"判断相不下放"的护城河纪律,落实到"调用 Agent 工具时的具体参数"这一操作细节。

**How to apply**：派工涉及架构设计/口径统一/四模块骨架/跨文件结构判断这类"系统迭代"性质的复杂任务时,Agent 工具调用**显式传 `model: "fable"`**,不留给默认继承;纯机械/批量/格式转换类任务(如 lint 消债批量改行、checker 脚本跑批)可保持默认(对应 L1/L2 档位),无需强制升档。
