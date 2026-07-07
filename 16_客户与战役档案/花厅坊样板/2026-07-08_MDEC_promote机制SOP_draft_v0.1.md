---
title: M-DEC promote 机制 SOP
version: v0.1
status: draft
owner: 六哥
created: 2026-07-08
module: 16_客户与战役档案/花厅坊样板
source_type: sop_draft
client_safety: internal_only
fact_layer: inferred
summary: 从M-DEC-010首例迁入蒸馏的promote操作SOP草案;含触发/评分/copy规则/SSOT/签字门/回滚;未过三轮审议不得引用为执行依据
审议轮次: 1
related:
  - "[[2026-07-08_MDEC010_首例迁入终审包_draft_v0.1]]"
  - "[[04_商品诊断与商品力提升/中层决策库/README]]"
---

# M-DEC promote 机制 SOP · draft v0.1

> **法理声明**：本 SOP 含"必须/不得"字样即触发标准审议铁律——当前为 draft·审议轮次1，**未过三轮审议+六哥签字前不得被引用为执行依据**。首例（M-DEC-010）按终审包个案放行，不依赖本 SOP 生效。

## 1. promote 触发条件（满足全部）
① 卡 status=active 且有六哥签字；② actual_outcome 已知（有实跑证据文件）；③ ≥2 个独立案例或 ≥2 门店验证（宪法 §11.3 口径）；④ 六哥明示启动（不自动触发）。

## 2. promote 就绪度评分（4 项检查表）
| 项 | 通过标准 |
|---|---|
| 状态与签字 | active + frontmatter signoff 在 |
| 证据 | 实跑证据文件存在且被卡内 fact_layer 引用 |
| 蒸馏去向 | 目标方法论页已选定（active 页优先） |
| 命名合规 | M-DEC-NNN 命名符合中层决策库 README 体系 |
4/4 → 出预审单；<4 → 出差距清单（参照 009/011/012 模板）。

## 3. copy vs move 规则
**默认 copy**（首例裁决确立）：战役档案完整性 > 目录整洁。move 仅当六哥明示且原目录留指针页。

## 4. SSOT 归属规则
copy 后 **04_ 中层决策库版 = 唯一权威版**；16_ 原卡冻结为战役历史件、不再更新。04_ 版 frontmatter 必带 `promoted_from` + `promote_date` 两字段（消歧三件套之二，第三件是原卡指针块）。

## 5. 原卡指针规则
文末追加引用块，签字前用**候选措辞**（"已获准作为…候选；迁入完成并签字后…"），签字后可改为完成式。指针必须含指向 04_ 版的全路径 wikilink。

## 6. 中层决策库命名规则
沿用原卡文件名（M-DEC-NNN_主题_vX.Y.md），不改名不重编号；同名双卡靠目录+promoted_from+指针三重消歧。

## 7. 方法论登记行规则
向对应方法论页 §实战登记表**只追加一行**：时点/场景/验证结论/证据/反写动作五列；**不改理论正文、不把卡内临界值抽象为通用规则**（写明"口径以卡内校准为准"）。

## 8. SignoffLedger 规则
每例 promote 落一行：日期/事项/动作/签字人/理由。签字前可先落"终审签字待落"行，签字后补终审行。

## 9. fact_layer 要求
04_ 版 fact_layer 与原卡**逐字一致**；promote 过程不得把 inferred 升 observed、不得删 pending。

## 10. pending 项保留规则
卡内 pending 如实随卡迁移，**清除 pending 需独立证据+六哥确认**，promote 本身不是清除理由。

## 11. 禁止事项
不自动 promote / 不代签 / 不在一次 promote 里迁多卡 / 不顺手改卡正文 / 不动中层决策库 README（改 README=机制变更须签字）/ 不把候选卡（_候选后缀）直接迁入。

## 12. 六哥签字门
四处 diff（04_ 新建/原卡指针/方法论登记行/台账行）→ 终审包一次呈批 → 签字 → commit。任何一处被否 → 全组撤回工作区修改。

## 13. 回滚机制
签字前：`git restore` 三处已跟踪文件 + 删除 04_ untracked 副本，零残留。签字后发现问题：不删 04_ 版（已是 SSOT），走 errata 勘误模式旁注，台账补记。

## 14. lint 检查建议（给 G03 v3 的输入）
① promoted_from 指向的原卡必须存在且含指针块；② 同名双卡若缺 promoted_from 字段 → 报双权威；③ 原卡在 promote 后若再被修改 → 报"历史件复活"。

## 15. 最小首例迁入流程（实测于 M-DEC-010）
预审单 → 六哥三项裁决（迁入/指针/蒸馏去向）→ dry-run 报告 → 六哥四项裁决（SSOT/措辞/新建/登记行）→ 工作区落 4 处 diff → 终审包 → 签字 → 单主题 commit → 台账终审行。**全程 8 步、2 个裁决点、1 个签字点。**
