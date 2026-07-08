---
title: 跨会话 ingest 收口方案
version: v0.1
status: executed
owner: 六哥
created: 2026-07-08
executed_date: 2026-07-08
module: 00_入口与总索引/05_审计与档案
source_type: governance_plan
client_safety: internal_only
fact_layer: observed
summary: D-08跨会话ingest债的收口方案:核查同批/挂MOC/登台账/quarantine与删除判据;不处理文件本体
审议轮次: 1
related:
  - "[[2026-07-07_未决项清单_v0.1]]"
---

# 跨会话 ingest 收口方案 · draft（不处理文件本体）

## 1. 债务现状（截至 2026-07-08 夜）
已确认的并行会话产物（均 untracked/未登记/未挂链）：
1. `01_/KB-CONCEPT-PRODMIX-001_商品配置模型_v0.1.md`（D-08 首发·来源核查已做：local_ingest 指纹）
2. `05_/KB-CAT-HSMATRIX-001_HS矩阵选品工具_v0.1.md`
3. `11_/社区超市商品经营决策系统MVP_历史设计索引_v0.1.md`
4. `12_/00_战略层/六哥零售圈_社群冷启动方案与竞品情报_v0.1.md`
5. `14_/SRC-20260707_即时零售行业深度报告_招商证券_v0.1.md`
6. `12_/01_选题库.md`（modified）
⚠️ 清单动态增长中——收口前须重新 git status 定版。

## 2. 同批核查步骤
① 让并行会话自报产物清单+任务上下文（首选，最准）；② 若无法自报：`git status --porcelain` 取全部 untracked/modified → 逐个查 frontmatter `source:`/`source_type:` 指纹归批；③ PRODMIX 的源路径显示原目录有 `1/01｜ 1/02｜…` 编号，rg "零售系统模型" 查兄弟文件是否已落。

## 3. 收口路径（每文件三选一）
| 路径 | 适用 | 动作 |
|---|---|---|
| **A 补收口** | 内容质量合格+确是六哥想要的 ingest | 挂对应 MOC → 登内容消化台账 → 按主题 commit |
| **B quarantine** | 来源不明/质量存疑/待六哥想 | 移入 `98_AI协作中枢/01_Claude_Code/Claude输出区/_quarantine_跨会话/`（输出区 gitignored 天然隔离）；不删 |
| **C 删除** | 确认误生成/重复 | **D 档六哥签字** → 删 → 落台账 |

## 4. 判据
- 挂 MOC 判据：KB-* 页 → 科学零售知识树对应分支；SRC-* → 14_ 精读索引；产品/社群方案 → 变现 MOC
- 登台账判据：`source_type: local_ingest/clip_ingest` 必登内容消化台账（ingest 闭环三步之一）
- quarantine 时限：≤7 天必须转 A 或 C（防第二个滞留区）

## 5. 何时执行
建议与次日裁决 #6 合并：明早六哥先问并行会话拿清单 → 本方案按批走 A/B/C → 一次 commit 收口。**本方案文件本身不动任何债务文件。**

## 6. 执行记录（2026-07-08 收口）
六批全部走 **A 补收口**（含 #3，六哥裁定「未被 RetailOS 取代，独立保留」，非 quarantine/删除）：
1. KB-CONCEPT-PRODMIX-001 → 挂 [[科学零售知识树_MOC]] + 登台账
2. KB-CAT-HSMATRIX-001 → 挂 [[科学零售知识树_MOC]] + 登台账
3. 社区超市商品经营决策系统MVP历史设计索引 → 六哥裁定未被取代 → 更新正文裁定说明 + 挂 [[RetailOS（门店决策操作系统 · 概念主页）]] 前身条目 + 登台账
4. 六哥零售圈_社群冷启动方案与竞品情报 → 挂 [[晟果新零售变现体系总控_MOC]] L6 + 登台账
5. SRC-20260707_即时零售行业深度报告 → 挂 [[精读卡索引_v1.0]] 新增券商研报节 + 登台账
6. `12_/01_选题库.md`（+22行追加）→ 随批一并 commit，非独立路由
D-08 收口完成，RESUME 遗留项相应清除。
