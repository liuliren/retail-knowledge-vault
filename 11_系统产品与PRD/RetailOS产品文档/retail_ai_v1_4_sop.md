---
title: AI 零售三脑操作系统 v1.4 SOP
summary: AI 三脑操作系统 v1.4 SOP,实现收件箱驱动的半自动协作(Claude/Codex/Obsidian)。
version: v1.4
status: draft
---

# AI零售三脑操作系统 v1.4 SOP

## 1. 系统概述
本系统由 Claude Code（知识脑）、Codex（执行脑）、Obsidian（记忆层）、SYSTEM_RUNTIME（调度层）组成。

目标：实现收件箱驱动的半自动AI协作系统。

---

## 2. 系统架构
- Claude Code：方法论、分析、文档生成
- Codex：代码、工具、自动化执行
- Obsidian：唯一事实源与状态存储
- SYSTEM_RUNTIME：事件路由与调度

---

## 3. 核心流程
1. 任务写入收件箱
2. Event Router识别任务
3. Dispatcher分发任务
4. Claude/Codex执行
5. 写回Obsidian
6. 更新系统状态

---

## 4. 日常操作流程

### Claude任务
- 读取 Claude收件箱
- 执行方法论/分析
- 输出 Claude输出区
- 写执行日志

### Codex任务
- 读取 Codex收件箱
- 自动创建缺失文件
- 执行代码任务
- 输出 Codex输出区

---

## 5. 错误与自愈机制
- 路径错误 → 自动修复
- 文件缺失 → 自动创建
- 执行失败 → 重试3次
- 最终记录至系统状态

---

## 6. 使用示例

### 示例任务（门店分析）
输入到 Claude收件箱：
“分析花厅坊门店品类结构并生成优化方案”

系统执行：
1. Claude生成分析报告
2. 输出到 Claude输出区
3. 写入执行日志

---

### 示例任务（Codex工具）
输入到 Codex收件箱：
“生成SKU清洗Python脚本”

系统执行：
1. Codex创建脚本文件
2. 执行逻辑验证
3. 输出到 Codex输出区
