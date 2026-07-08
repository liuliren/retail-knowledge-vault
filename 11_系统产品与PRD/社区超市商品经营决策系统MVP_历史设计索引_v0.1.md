---
id: KB-PRD-DECISIONSYS-001
title: 社区超市商品经营决策系统 MVP · 历史设计索引
status: candidate
fact_layer: inferred
created: 2026-07-07
source: davidliu本地Downloads/Work工作文件夹/3.见自己/3.3工具系统开发 与 1.1.3零售系统模型/PRD
source_type: local_ingest
client_safety: internal_only
summary: MVP设计（数据库/OpenAPI/规则JSON Schema/页面流程图+PRD审计报告）。六哥2026-07-08裁定：未被RetailOS取代，独立保留；RetailOS现有5份文档均为draft级、内容单薄，缺门店画像/周报月报复盘/顾问协同角色/ABCD四层分级等MVP已有能力。
tags: [PRD, 系统设计, MVP, RetailOS前身, draft]
related:
  - "[[RetailOS（门店决策操作系统 · 概念主页）]]"
version: v0.1
---

## 定位说明（核实后修正）

本文档索引的是"社区超市商品经营决策系统"MVP的早期设计草案。六哥最初印象是"应已被RetailOS取代"，AI 核实 `RetailOS.md` + 4份RetailOS产品文档 + v1.0软件PRD后发现：

- RetailOS 现有内容均为 `status: draft`，偏slide-deck级别（粗粒度4层架构+表名列表+5个API端点名+角色列表），**没有真实DDL/OpenAPI规范/JSON Schema规则/页面流程图**（MVP这边这四样都有具体设计产物，只是还在本地Downloads未导入）
- **功能缺口**：RetailOS 缺"门店基础信息管理/门店画像与定位分析""周报/月报复盘"，SKU分层是**三层A/B/C**而非MVP的**四层A/B/C/D**，RBAC角色里没有"顾问"角色（只有Super Admin/HQ Manager/Store Manager/Staff）
- 陈列位配置建议方面 RetailOS 有对应但更粗（"陈列优化引擎"概念，非具体建议产出）

**结论：不能认定为已吸收**，更准确的状态是"RetailOS 是后继/平行方向，但尚未达到 MVP 设计的完整度和落地深度"。

> ✅ **六哥裁定（2026-07-08）**：本 MVP 设计**未被 RetailOS 取代**，独立保留，不降级、不 quarantine。是否将四份设计产物正式导入并入 RetailOS，见下方「待六哥裁决」细项（尚未定案）。

## 系统功能范围（MVP）

- 门店基础信息管理、门店画像与定位分析
- 商品/品类/SKU数据导入
- SKU评分与A/B/C/D分层
- 商品组合建议、陈列位配置建议
- 周报/月报复盘
- 顾问、老板、店长协同使用

## 已有设计产物（原始文件仍在本地Downloads，未导入）

1. **数据库表结构设计**（MVP版）——覆盖上述功能范围的表结构草案
2. **OpenAPI字段级草案**——接口资源对象/字段命名/类型/枚举/返回结构约定
3. **规则配置JSON Schema草案**（Draft 2020-12风格）——支撑规则引擎的参数化配置
4. **页面流程图与页面清单**（V1.0）——页面结构、跳转关系、角色权限差异

## PRD审计报告关键发现（2026年4月·审计对象PRD v2.0 MVP）

审计发现26个问题，其中**9个高级问题直接阻塞开发**，核心是：
- 规则引擎权重未定义
- 模板库对象（DiagSummaryTemplate）缺失，未定义为独立数据对象
- 别名库触发条件来源不明
- 条件跳转逻辑未纳入题目引擎设计（如"选否跳过后续题目"的分支逻辑）
- 登录态失效、多设备同时操作同一草稿等异常处理未定义

**审计官结论**：当时的PRD v2.0"不具备直接进入开发的条件"，需先修复高级问题再排开发。

## 待六哥裁决

- [ ] 是否要把 MVP 四份设计产物（数据库表结构/OpenAPI字段级草案/规则JSON Schema/页面流程图）正式导入并整合进 RetailOS（补齐 RetailOS 现有的门店画像/周报复盘/顾问角色/ABCD四层分级 缺口）
- [ ] 还是维持 RetailOS 现状（更轻量的产品方向），MVP设计彻底作废
- [ ] PRD审计报告的26项审计维度方法论是否要独立提炼为通用"PRD审计checklist"复用工具（不依赖具体是哪个产品）
