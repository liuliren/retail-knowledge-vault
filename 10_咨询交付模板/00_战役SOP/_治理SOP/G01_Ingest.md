---
title: G01_Ingest（原始素材进库 SOP）
version: v0.1
status: draft
owner: 六哥
created: 2026-05-04
updated: 2026-05-04
module: 10_咨询交付模板/00_战役SOP/_治理SOP
tags:
  - 治理SOP
  - Ingest
  - G01
  - Karpathy
  - 占位
source_type: template
confidence: pending
quadrant: III
client_safety: internal_only
related:
  - "[[CLAUDE.md]]"
  - "[[00_战役SOP/README]]"
  - "[[_治理SOP/G02_Query]]"
  - "[[_治理SOP/G03_Lint]]"
  - "[[2026-05-04_知识库重构方案_v0.2_完整作战方案]]"
---

# G01_Ingest（原始素材进库 SOP）

> ⚠️ **占位状态（Phase 0 D4）**：本 SOP 是 [[CLAUDE.md]] §18.1 已锁的 Ingest 流程的 SOP 落地。仅 §0 + §1 + §C 骨架；§A/§B/§D/§E/§F/§G/§H/§I 待 Phase 1 第一次真正 Ingest（花厅坊首访资料）走通后回流。**禁止假装填满**。

---

## §0 SOP 元数据

| 字段 | 值 |
|---|---|
| SOP id | G01 |
| 类型 | 治理 SOP（"知识进库"一等公民操作） |
| 触发 | 新原始源（客户照片 / POS / 访谈录音 / 行业研究 / v0.x 增量包）进入 vault |
| 上游 | 真实世界产出（人 / 客户 / 现场 / 外部） |
| 下游 | [[_治理SOP/G02_Query]]（被调用）/ wiki 综合主页（被吸收）|
| 调用 wiki 模块 | [[90_素材暂存与待整理]] / [[CLAUDE.md]] §18.1 |
| 关联仪表 | [[Vault健康仪表]]（待 Ingest 14 天 WIP / 待核验项总数）|
| 默认 quadrant | III（外延复制：进库流程必须模板化） |
| 默认 client_safety | internal_only（90_ Raw 层默认不外传，含敏感客户信息禁止 commit） |
| 失败代价 | 素材"堆在抽屉"无人吸收 → 战役无依据 → 反幻觉机制失效 |

---

## 1. 战役定位

vault 与 Claude Code 协作的**第一个一等公民操作**——"知识进库"。本 SOP 把 [[CLAUDE.md]] §18.1 的简明流程落地为可执行步骤。

**核心约束**：
- 原始素材**不可变**（进入后不修改原文）
- 14 天 WIP 上限（90_/99_待Ingest/ 内素材超期必处理）
- 含敏感客户信息**不入版本控制**

---

## §A 入场条件 (Entry Criteria)

> ⬜ 待充实

骨架方向：素材已离线收集完毕 / 来源 + 日期 + 采集人可标 / 已判断分类（客户素材 / 行业研究 / 临时灵感）。

---

## §B 关键里程碑 (Milestones)

> ⬜ 待充实

骨架方向：M1 落入 90_/99_待Ingest/（含元数据三件套）/ M2 LLM 提取并写入对应 wiki 综合主页 / M3 14 天内闭环（或归档 / 或重启）。

---

## §C 必产出物与 DoD (Deliverables & Definition of Done)

骨架占位（按 [[CLAUDE.md]] §18.1 五步流程）：

| 步骤 | DoD 方向（待充实） |
|---|---|
| S1 落 90_/99_待Ingest/ | 文件名含日期前缀 + 来源代号 + 简述 |
| S2 标元数据 | 日期 / 来源 / 采集人 / client_safety 默认值（见 §0） |
| S3 判断分类 | 客户素材（→ 90_/00_客户原始材料/<客户代号>/）/ 行业研究（→ 90_/01_行业研究原始资料/）/ v0.x 增量包（→ 90_/02_v0.x增量交付包/）/ 临时灵感（→ 90_/03_临时灵感/）|
| S4 LLM 提取并写入 wiki 综合主页 | 综合主页**主动更新**（不是被动等召唤）/ 标依据链接回 90_ 原始 |
| S5 14 天 WIP 限制 | 超期素材必须处理（吸收 / 归档 / 重启）|

---

## §D 风险红线 (Risk Lines)

> ⬜ 待充实

骨架方向：禁止修改原文 / 禁止合并冲突信息（必须标注，参 §13.11）/ 禁止把含真实客户敏感信息的素材 commit / 禁止"堆而不吸"。

---

## §E 人决策点 (Human Judgment Gates)

> ⬜ 待充实

骨架方向：DP1 分类边界判断（客户素材 vs 行业研究的灰区）/ DP2 综合主页是否合并（同一概念的多源材料是否进同一页）/ DP3 14 天到期处理（吸收 / 归档 / 重启）。

---

## §F 出场条件 (Exit Criteria)

> ⬜ 待充实

骨架方向：综合主页已更新 + 双链可追溯 + 90_/99_待Ingest/ 文件已迁出。

---

## §G 责任分工 (RACI)

> ⬜ 待充实

骨架方向：人主导分类 + Claude 主写综合主页 + PM 监督 14 天 WIP。

---

## §H 客户可见性 (client_safety)

- 90_ Raw 层：默认 internal_only（含真实客户敏感信息绝不外传）
- 综合主页（wiki 层）：按文件 frontmatter 标注

---

## §I 已知陷阱

> ⬜ 待第一次真正 Ingest 后补充

---

## §J 关联

- **上游**：人 / 客户 / 现场 / 外部
- **下游**：[[_治理SOP/G02_Query]] / wiki 综合主页
- **关联**：[[CLAUDE.md]] §18.1 / [[90_素材暂存与待整理]]（D5 重定位 Raw Sources）
