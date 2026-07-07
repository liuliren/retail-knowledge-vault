---
title: Skill资产盘点表（Phase-Y·Y2）
summary: retail vault .claude/skills/ 19个skill + SKILL-INDEX 盘点：作用/状态/过时判断/升级需求。
version: v0.1
status: draft
owner: Claude（Phase-Y 盘点）/ 六哥（裁决）
created: 2026-07-08
source_type: audit_note
client_safety: internal_only
---

# Skill 资产盘点表 draft（2026-07-08 · Phase-Y Y2）

> 方法：读 SKILL-INDEX.md 全文 + 各 SKILL.md frontmatter+前20行；`.claude/agents/`、`.claude/commands/` 均不存在。retail 局部共 **19 个 skill 目录 + 1 个 SKILL-INDEX**；根层另有 report-export/read-floorplan/lint-kb/lint-privacy/lint-coverage/process-inbox/zero-scheduler/ingest（canonical）等（不在本表深评）。
> 上线铁律三件套 = ①frontmatter `触发词:` ②SKILL-INDEX 加行 ③.gitignore 白名单。

| 名称 | 路径 | 类型 | 作用 | 状态 | 过时? | 需升级? | 下一步 |
|---|---|---|---|---|---|---|---|
| trio | skills/trio | 数据分析 | 三件套一条龙（trio_engine 后端） | active·生产 | 否 | 小：花厅坊默认路径硬编码 | 参数化门店路径 |
| abcz | skills/abcz | 数据分析 | ABCZ分层（小类内签字口径） | active·生产 | 否 | 注意：A≤70/B≤90 自标"draft标准待审议" | 阈值走三轮审议 |
| movement | skills/movement | 数据分析 | 动销率 | active·生产 | 否 | 否 | 保持 |
| priceband | skills/priceband | 数据分析 | 价格带+毛利双轨 | active·生产 | 否 | 否 | 保持 |
| posclean | skills/posclean | 数据分析 | POS清洗（pos_clean 后端·七坑防护）——**最成熟工具链入口** | active·生产 | 否 | 否 | 保持 |
| diagnose | skills/diagnose | 交付引擎 | 端到端单品类诊断（v0.3·机制A相位分工） | active·生产 | 否 | 中：与脱敏测试链路脚本关系需厘清 | 双入口消歧 |
| mdcard | skills/mdcard | 交付引擎 | 图卡体系 v1.1（六哥07-03/07-04两次签字） | active·签字 | 否 | 否 | 保持 |
| fixloop | skills/fixloop | 治理回路 | 审计→修复→验收闭环（07-07 刚升 active·签字·三件套3/3过） | active·新 | 否 | 观察期 | 第二次实跑后回填经验 |
| critique | skills/critique | 治理回路 | 批判审议/魔鬼代言人（标准第2轮） | **candidate**（status字段明示） | 否 | 是：待六哥签字转 active | 签字门 |
| promote | skills/promote | 治理回路 | M-DEC 闭环回填+蒸馏 | active | 否 | **是：纯人工流程，无机械 checker 支撑**——本 Phase 新脚本 mdec_promote_checker 即补此位 | 接 tool_drafts 脚本（六哥裁决后） |
| ingest（retail局部版） | skills/ingest | 进料 | 【已废弃】指针防误用，canonical 在根层 | **deprecated** | 是（有意保留） | 否 | 不能动（删除需六哥D档签字） |
| scan | skills/scan | 进料 | 每日语料巡检分流器（ingest/deep-read 上游） | active | 否 | 小：定时挂载状态未验证 | 核实 launchd |
| deep-read | skills/deep-read | 进料 | 逐字精读引擎（零售老刘321篇 canonical 工程） | active | 否 | 否 | 保持 |
| draft | skills/draft | 媒体 | 媒体稿起草 v0.3（07-07 更新） | active | 否 | 否 | 保持 |
| publish | skills/publish | 媒体 | 公众号发布准备 v0.4（frontmatter v0.4 但正文标题仍写 v0.2） | active | 否 | 小：版本号内部漂移 | 正文版本号对齐（A档） |
| review | skills/review | 复盘 | 周/月复盘（写 life-vault + retail 战役档案） | active | 否 | 注意跨库写入合规（两库正交） | 保持 |
| merge | skills/merge | 文档治理 | 双文档冲突裁定 | active | 否 | 否 | 保持 |
| compact | skills/compact | 会话治理 | 压缩治理 | active | 否 | 否 | 保持 |
| handoff | skills/handoff | 会话治理 | 交接文档+新会话prompt | active | 否 | **是：与 RESUME/LOOP_STATE 半人工**——nightly_resume_builder 可为其供料 | 接 tool_drafts 脚本（六哥裁决后） |

## 三个结构性发现

1. **skill 生命周期字段不统一**：仅 critique/fixloop/mdcard 等少数有 `status:`/`signoff:` 字段；trio/abcz/movement/priceband/posclean 五个生产 skill frontmatter 连 version 都没有——与"标准审议铁律"的 draft/stable 判别要求脱节。
2. **治理回路 skill（promote/handoff/fixloop）全靠 LLM 手工执行，零脚本支撑**；数据分析 skill 全有脚本后端。本 Phase 4 个新脚本正是补治理侧机械相。
3. **废弃管理是健康样板**：retail 局部 ingest 用"指针防误用"而非删除，符合 D 档红线；但 SKILL-INDEX 未标 deprecated 状态列，建议 INDEX 增加状态标记（A档小改，待裁决）。
