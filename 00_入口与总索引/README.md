---
title: 00_入口与总索引 — vault 主入口（Karpathy main page 风格 / v2.0）
version: v2.0
status: active
quadrant: I
owner: 六哥
created: 2026-05-01
updated: 2026-05-07
module: 00_入口与总索引
tags:
  - 主入口
  - Karpathy_main_page
  - 6子目录导航
  - LLM_friendly
source_type: reference
confidence: high
client_safety: internal_only
related:
  - "[[CLAUDE.md]]"
  - "[[科学零售wiki入口]]"
  - "[[2026-05-07_vault升级方案_v2.0]]"
  - "[[2026-05-07_McKinsey审计报告_v1.0]]"
---

# 🧭 00_入口与总索引（vault 主入口 v2.0）

> **本目录**：vault 的导航台 + 总控台 + 治理中心 + 作战指挥台。
> **设计**：Karpathy main page 风格（参 [[科学零售wiki入口]]）+ McKinsey 5 层信息架构 + Anthropic Constitutional 自检
> **进入路径**：每次 session 启动 → 本目录 → 6 子目录或 [[科学零售wiki入口]] → 具体节点

---

## ⭐ 主 Wiki 入口（Karpathy LLM 知识图谱中心）

> **首选**：[[科学零售wiki入口]] — 全 vault 主导航 hub / 80+ 双链 / 5 大支柱 + 6 大标准 / 三力骨架 / 战役档案 + 6 表 v1.0 + 主方法论 13 / 工具与交付 / 治理 / 反向回写机制 / Quick Reference

---

## 📁 6 子目录导航

```
00_入口与总索引/
├── README.md                ← 本文件（vault 主入口 v2.0）
├── _wiki入口/                ← Karpathy 风格 LLM 主导航
│   └── 科学零售wiki入口.md   ← 全 vault hub
├── 01_战略层/                ← Strategy（晟果独有）
├── 02_方法论索引/             ← Methodology
├── 03_治理规范/               ← Governance
├── 04_作战指挥/               ← Operations
└── 05_审计与档案/             ← Audit & Archive
```

### 1. `_wiki入口/`（Karpathy 风格 LLM hub）

- [[科学零售wiki入口]] ⭐ — vault 主导航 hub

### 2. `01_战略层/`（Strategy）

- [[科学零售知识地图]] — 三力骨架 + 经营控制链 主图
- [[品牌资产手册_v0.1]] — 销售包内核 / 对外品牌色调
- [[三回归仪表]] — 战略对齐 / 反假忙碌

### 3. `02_方法论索引/`（Methodology）

- [[知识库总索引]] — 全库文件入口
- [[核心概念主定义索引]] — 防止概念冲突
- [[标签体系说明]] — 标签分类规范

### 4. `03_治理规范/`（Governance）

- [[知识库治理规范]] — 治理总则
- [[文档工程化标准]] — Markdown + frontmatter 规范
- [[文件命名规范]] — 命名规则与版本号
- [[反幻觉检查清单]] — 15 条反幻觉规则
- [[逻辑一致性检查清单]] — 跨文件一致性
- [[变更影响检查清单]] — 修改前必查
- [[知识库测试用例]] — 规则验证

### 5. `04_作战指挥/`（Operations）

- [[战役指挥板]] — 全战役调度 + 健康灯
- [[当前重点项目看板]] — 当前重点项目
- [[Vault健康仪表]] — 12 维度健康度
- [[常用模板入口]] — 快速跳转

### 6. `05_审计与档案/`（Audit & Archive）

- [[2026-05-07_McKinsey审计报告_v1.0]] — McKinsey 5 module 审计
- [[2026-05-07_封存断链清单_v1.0]] — 封存映射 + 断链 SOP
- [[2026-05-07_vault战略重构方案_v1.0]] — Phase 1 重构方案
- [[2026-05-07_vault升级方案_v2.0]] — 6 大标准 + 反哺机制 + Karpathy
- [[版本更新记录]] — 历史变更

---

## 🚀 Session 启动三件套（≤ 30 秒定位）

```
Step 1: 读 memory（自检三件套）
  - [[user_六哥]]
  - [[feedback_engineering_standards_5_pillars]] / [[feedback_anthropic_claude_alignment]]（顶层 6 大标准）
  - [[feedback_mvp_first_validate_in_practice]]（MVP 优先）
  - [[project_花厅坊战役]]（战役状态指针）

Step 2: 读 vault 仪表
  - [[战役指挥板]] / [[当前重点项目看板]] / [[Vault健康仪表]] / [[三回归仪表]]

Step 3: [[科学零售wiki入口]] → 跳到具体节点
```

---

## 🎖️ 6 大标准基线（vault 工程化品质塔）

| 支柱 | 解决 | vault 落地 |
|---|---|---|
| **McKinsey** | 顶级咨询品质 | [[2026-05-07_McKinsey审计报告_v1.0]] / Issue tree / Pyramid |
| **IBM** | 企业工程化 | frontmatter 12 字段 / [[文档工程化标准]] / SHA256 校验 |
| **Oracle** | 数据架构 | 6 表 PK/FK / 单源真相 / ACID / snapshot 冻结 |
| **Apple** | 用户中心 + 工艺 | [[feedback_mvp_first_validate_in_practice]] / Excel freeze pane |
| **Tesla** | 工业化迭代 | v0.x → v1.0 / SKU 算法 v0.1 实战 / OTA |
| **Anthropic** ⭐ | AI 协作哲学 | HHH / Constitutional 自检 / Karpathy 自然涌现 / LLM as maintainer |

每次重大工作 6 维自检（参 [[feedback_engineering_standards_5_pillars]] + [[feedback_anthropic_claude_alignment]]）。

---

## 🔁 反向回写机制（实战 → wiki 涌现）

```
客户接触（5/6 二访 / 5/8 方便速食 / 等）
   ↓ T+24h（§21 硬约束）
客户验证日志（15_/客户验证日志/）
   ↓ T+48h
主方法论 §"实战登记"段（13/13 已建 100% / Phase 3 5/7 完成）
   ↓ T+1w
M-DEC 候选 v0.1 → v0.5（16_/花厅坊样板/）
   ↓ G06 战后复盘
M-DEC v1.0（mv 04_/中层决策库/）
   ↓ 跨战役 #2 验证
CLAUDE.md §6 顶层固化
```

---

## 📊 vault 当前健康度（2026-05-07）

| 维度 | 状态 |
|---|---|
| 一级目录完整性 | 19/19 ✅ |
| frontmatter quadrant 完整 | 95%（5/7 cleanup 52 文件）|
| 6 表 v1.0 lock | ✅ |
| 历史封存 | 970M 已封存 |
| 客户验证日志数 | 1（首条 / 5/6 老板访谈）|
| 战役 docs sync | 10/10 ✅ |
| Karpathy main wiki | ✅（5/7 v1.0）|
| 主方法论 §实战登记 | 13/13 ✅ 100% |
| 6 大标准 memory | 6/6 ✅ |

详见 [[Vault健康仪表]] v0.5 / [[2026-05-07_McKinsey审计报告_v1.0]]。

---

## 📅 关键时点（W18-W22）

| 时点 | 节点 |
|---|---|
| 5/8 | 基础数据搭建日 + 方便速食组数据核查 + 客户验证日志补建 |
| 5/9 | 数据装载 + sign off 准备 |
| 5/10 | 休食区其它品类调改启动 |
| 5/16 | M1.7 全量数据装载完成 |
| 5/23 | M2 一周效果验证 |
| 5/30 | M3 14 天深度复盘 + G05 阶段门 + M-DEC v0.5 |
| 6/03 | M4 花厅坊样板对外可讲 |
| 6/30 | M5 第一个新客户签约（不变 / 库存去化 ≤ 30,000 元）|

---

## 🎯 vault 当前不做（[[战役指挥板]] §三月四不做）

1. 不做与三大优先级无关的事（花厅坊样板 / 销售签约 / 治理基线）
2. 不做"系统化"诱惑（不做 SaaS / PRD / 平台化产品）
3. 不做超出当前战役范围的研究
4. 不做"为了完整而完整"的方法论（v0.x 无客户验证 = 未验证）

---

## 📝 版本记录

| 版本 | 日期 | 变更 |
|---|---|---|
| v1.0 | 2026-05-01 | 初版（基础目录说明）|
| **v2.0** | **2026-05-07** | **Karpathy main page 风格升级**：① 显式链入 [[科学零售wiki入口]] / 6 子目录 ⭐ / ② 6 大标准（M+I+O+A+T+Anthropic）/ ③ 反向回写机制图 / ④ Session 启动三件套 / ⑤ vault 健康度 / ⑥ 关键时点 / ⑦ 当前不做（治理纪律）/ ⑧ frontmatter 升 quadrant: I + 关联 v2.0 升级方案 |
