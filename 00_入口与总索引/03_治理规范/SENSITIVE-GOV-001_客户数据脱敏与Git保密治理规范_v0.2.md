---
id: P1-GOV-Sensitive-001
title: 客户数据脱敏与 Git 保密治理规范（保密治理唯一口径 SSOT）
version: v0.2
status: superseded
superseded_by: "[[SENSITIVE-GOV-001_客户数据脱敏与Git保密治理规范_v0.3]]"
signoff: 六哥 2026-07-05（S1认可SSOT骨架/S2接受push须过闸+授权措辞/S3授权superseded处置/S4 hook另立工程任务）
审议轮次: 2
审议债: 第2轮批判仅部分完成(限额中断~95%未补跑)·六哥签字生效并知悉此债·补跑如出必修项走v0.3修订
created: 2026-07-02
updated: 2026-07-05
owner: 六哥
module: 00_入口与总索引/03_治理规范
source_type: governance
client_safety: internal_only
fact_layer: observed
summary: 保密治理唯一SSOT收敛稿：一处规定客户数据能否进Git+提交前怎么查+Codex/Claude怎么登记+SignoffLedger留痕+gitignore白名单；GATE/HISTORY-PLAN拟superseded(本轮只写计划)
tags: [保密治理, SSOT, 脱敏, Git红线, 收敛稿]
supersede_plan:
  - "[[CODEX-SENSITIVE-GATE-001_Codex提交前客户数据保密闸_v0.1]]"
  - "[[SENSITIVE-HISTORY-PLAN-001_未来同步与安全分支策略_轻量版_v0.1]]"
related:
  - "[[SENSITIVE-GOV-001_客户数据脱敏与Git保密治理规范_v0.1]]"
  - "[[签字门台账_SignoffLedger_v0.1]]"
  - "[[Codex执行前置状态登记表_v0.1]]"
  - "[[2026-07-03_第2轮批判_SENSITIVE-HISTORY-PLAN-001]]"
  - "[[2026-07-03_第2轮批判_CODEX-SENSITIVE-GATE-001]]"
---

# 客户数据脱敏与 Git 保密治理规范 v0.2 · 保密治理唯一口径（SSOT）

> **定位（收敛裁决 2026-07-03·六哥认可方向）**：本文是**保密治理的唯一真相源（SSOT）**。此前散落三处的保密规则——GOV-001 v0.1、CODEX-SENSITIVE-GATE-001（提交闸）、SENSITIVE-HISTORY-PLAN-001（历史/分支策略）——收敛到本文一处口径。后两者本轮拟 superseded（见 §7，**本轮只写计划、不动原件**）。
> **本稿边界**：只收敛、不扩张；不引入新术语、不建平行治理体系。**✅ 六哥 2026-07-05 签字升 active**（S1-S4 全过·已落 SignoffLedger）；自本日起为保密治理唯一执行依据。审议债：第 2 轮批判 ~95% 未补跑，补跑后如出必修项走 v0.3 修订。

---

## 〇、结论先行

**一句话**：客户真实数据/条码/进价/销售明细/未脱敏客户名/客户派生经营结论**一律不进普通 Git**；把关靠三层——① .gitignore 白名单挡机械件、② 提交前 checklist 挡人工件、③ SignoffLedger 留删除/升级痕迹；执行层最终应落 **pre-commit hook（keys not prompts）**，prompt 固定条款只是第二道防线。

---

## 一、红线：什么绝不进普通 Git（L2+ 一律拦）

| # | 类别 | 判据 | 依据 |
|---|---|---|---|
| R1 | 客户原始数据 | xls/xlsx/csv/db、POS 导出、dry-run/execute 结果表 | v0.1 §7/§6-D |
| R2 | 裸值 | EAN-13 条码、进价、供应商明细、SKU 明细 | retail CLAUDE.md §6-C/D |
| R3 | **未脱敏客户名** | 花厅坊/好家源等可识别真名 + 场景 | P1-GOV-ClientNameAuth-001 |
| R4 | 客户派生经营结论 | "某店死货率偏高""金矿候选数以千计""某品类毛利异常""方案C更适合该店"——**无裸值≠可提交** | v0.1 §8（关键） |
| R5 | 客户诊断/项目执行日志 | 含客户经营判断的聚合日志 | v0.1 §9 |

> **fail-safe**：查不到授权 = 最严格 = 不暴露。无条码/无进价 **不等于**安全（v0.1 §18 反模式①）。

## 二、绿线：什么可以进普通 Git

- 方法论 / 模板 / SOP / 治理规范文档（B 层）；
- 工程执行日志、治理执行日志（非客户诊断类）；
- **已脱敏**的案例（去客户名/门店名/具体数字，改区间或相对描述——脱敏规则见 v0.1 §13）；
- 结构资产 CSV 白名单（A/B/_maintenance 层，见 §五）。

## 三、提交前检查（人工件的闸·10 条 checklist）

沿用 v0.1 §11 十条，**两条最致命红线单列强调**：

1. `git status --short` → `git diff --cached --name-only` → `--stat` → `--check`；
2. staged 是否含 xls/xlsx/csv/db；
3. staged 是否含**客户名 + 经营数字**；
4. staged 是否含毛利率/PSD/死货/金矿/动销/库存诊断；
5. staged 是否含 dry-run/execute 结果 / 客户诊断日志；
6. **🔴 禁止 `git add .`**（必须精确 `git add <file>`）；
7. **🔴 禁止未经六哥明确授权 `git push`**（历史含敏感时 push=扩散；main 推送前须过本 checklist）——本条系收敛 HISTORY-PLAN-001 §7.4"push 管控"，并修正其"main 永不 push"已被 2026-07-02 P1-0 裁决取代的过时表述：**push 不是禁止，是须过闸 + 授权**。

## 四、登记与留痕（谁做了什么，有账可查）

| 机制 | 职能 | 位置 |
|---|---|---|
| **SignoffLedger** | 删除/升级/对外发布/脱敏的签字留痕（`YYYY-MM-DD｜文件｜原态→新态｜六哥｜理由`） | 03_治理规范/签字门台账 |
| **Codex 执行前置状态登记表** | Codex 数据管线执行状态登记（**含客户项目状态者按 §9 应移出 tracked 或脱敏**） | 03_治理规范/（待评估 git 状态） |
| **本 SSOT** | 保密口径唯一来源，其他保密文件降为指针或 superseded | 本文 |

## 五、.gitignore 白名单如何生效（机械件的闸）

- 默认全局忽略 `**/*.{xls,xlsx,csv,db,ppt,key,pdf,dwg}`；
- **仅显式白名单放行结构资产**：商品库 A_*/B_*/_maintenance/*.csv（模式级·2026-07-03 修审计#8 已落地 commit a6435d2）；
- **客户数据保持默认忽略 fail-safe**：C_client_specific/*_raw.csv、*_mapped.csv 永不放行；
- 白名单增删 = 改保密边界 = 须过本 SSOT 口径复核。

## 六、执行层：keys not prompts（本轮只标注方向，不建 hook）

> 全局宪法 §7"权限护栏铁律"：对 Agent 说"别提交"只是建议,不是安全设置。保密的第一道防线**必须**落在权限/机械层。

- **现状**：`.git/hooks` 为空——当前保密全靠 prompt 固定条款（v0.1 §15）+ 人工 checklist = **纯第二道防线**，无第一道。
- **指定执行层（拟建·非本轮）**：pre-commit hook 实现机械判据（扩展名/路径/客户名正则的**审查触发**，不做关键词硬停——GATE-001 实测关键词硬闸误报率 71.7%，硬停仅限客观判据如扩展名/路径）。
- **本轮不写 hook**（六哥裁：不扩大范围）；仅在此登记为"保密治理的唯一执行层落点",另立工程任务时从本 SSOT 派生。

## 七、被收敛文件的 superseded 计划（本轮只写计划·不动原件）

| 文件 | 拟处置 | 理由（第2轮批判） | 本轮动作 |
|---|---|---|---|
| CODEX-SENSITIVE-GATE-001 | **superseded → 机械判据并入本 SSOT §六执行层 + §三 checklist** | 关键词硬闸误报 71.7%、漏禁 add./禁 push 两红线、零 hook 执行层 | **不改原件**，仅登记拟并入项 |
| SENSITIVE-HISTORY-PLAN-001 | **superseded → §8 公开预案并入本 SSOT（另节·拟建）；过时红线作废** | 两核心红线（禁 filter-repo/强推、main 永不 push）已被 P1-0 签字裁决推翻，60% 条款已死 | **不改原件**，仅登记 |
| GOV-001 v0.1 | 本 SSOT 签字升 active 后 → v0.1 标 superseded_by v0.2 | 自身 §8/§13 曾含未脱敏客户示例（已于 00f3d57 脱敏） | 保留待签 |

> **执行顺序（签字后）**：六哥签字升本 SSOT active → 落 SignoffLedger → 再逐一给 GATE/HISTORY-PLAN/v0.1 改 status（D 档·各自签字留痕）。**本轮到此为止。**

## 八、承接 v0.1 的完整细则（不重复，指针引用）

L0–L4 五级敏感分级（v0.1 §4）、四区隔离模型（§3）、文件裁决表模板（§12）、脱敏改写规则（§13）、历史残留处理原则（§14）、反模式清单（§18）——**细则仍以 v0.1 为准**，本 SSOT 签字后整体承接，v0.1 转 superseded_by。

---

## 待六哥裁决点

- **S1**：认不认可本收敛稿作为保密治理 SSOT 骨架？
- **S2**：§三第 7 条"push 须过闸+授权"（取代 HISTORY-PLAN"main 永不 push"）措辞是否可接受？
- **S3**：签字升 active 后，是否授权我逐一处置 GATE/HISTORY-PLAN/v0.1 的 superseded（D 档，各自留痕）？
- **S4**：pre-commit hook 是否另立工程任务（本轮不做，仅登记落点）？

*v0.2 · 2026-07-05 六哥签字升 active（落 SignoffLedger）· 已进 03_治理规范 tracked · 审议债：轮2批判~95%未补跑，随 v0.3 修订清偿 · 判断相不下放，SSOT 升级签字权在六哥*
