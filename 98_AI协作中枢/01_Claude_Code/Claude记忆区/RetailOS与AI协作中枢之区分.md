---
name: retailos-ai
title: RetailOS与AI协作中枢之区分
summary: RetailOS为真实门店决策系统(A-G)，与Obsidian+Claude+Codex协作中枢并非一回事。
description: RetailOS 是真实门店决策业务系统，与 Obsidian+Claude+Codex 的 AI 协作中枢是两回事，勿混淆
metadata: 
  node_type: memory
  type: project
  originSessionId: 7ec6868c-e751-4c25-8d6f-0e1d036b31f3
---

**RetailOS** = 真实的**零售门店决策操作系统**（业务产品），架构为 A-G 六层：
- v1.0 减法层（库存/SKU结构/价格带/陈列/ABC裁决/误判/门店SOP），封装为店员可照做的 5 步 SOP；
- v1.1 三项补深（E毛利交叉ABC / A库存升级 / B商品角色）；
- v2.0 加法层 = 选品/引进层（4 闸：真需求/有位置/算得过来PSD+毛利/供得上）。
- 验证基础：花厅坊 T03 饼干 + G4-A 麦片货架 + 沙埔大道店跨店。M-DEC 编号 + Cluster 治理严格，A-G 不擅扩、编号待六哥分配。

**AI 协作中枢 / SYSTEM_RUNTIME** = `98_AI协作中枢/` 下 Obsidian + Claude Code + Codex 三脑**协作管道**（收件箱/分发器/输出区/执行日志），是工程协作基础设施，**不是业务系统**。

**Why**：本会话曾把"零售决策系统"误判为 AI 协作中枢，做了一份打错靶子的报告，David 更正后才对准。两者名字都像"系统"，极易混。

**How to apply**：用户说"零售决策系统/门店系统/RetailOS"时，默认指**业务系统 RetailOS**（在 `09_…花厅坊/03_商品诊断/` 与 `10_咨询交付模板/`），不是协作中枢。涉及 RetailOS 改动须尊重 M-DEC/Cluster 治理。相关：[[客户管理水平约束-花厅坊]]。
