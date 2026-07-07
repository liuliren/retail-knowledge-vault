---
title: Skill缺口评估报告（Phase-Y·Y4）
summary: 基于Y2实测证据的Skill资产10问逐答：生命周期字段、治理skill缺机械相、三件套合规、废弃管理。
version: v0.1
status: draft
owner: Claude（Phase-Y）/ 六哥（裁决）
created: 2026-07-08
source_type: audit_note
client_safety: internal_only
---

# Skill 缺口评估报告 draft（Y4 · 任务书10问逐答）

**Q1 Skill 版图覆盖与空白？**
19 个 retail 局部 skill 覆盖：数据分析（5）、交付（2）、治理回路（3）、进料（3）、媒体（2）、复盘（1）、文档/会话治理（3）。**空白**：①M-DEC promote 复核无独立审查流程（promote skill 是执行者自查）；②夜间/断点恢复无 skill（handoff 偏会话交接，不管跨夜 LOOP_STATE）；③品类POS清洗（category_pos_cleaner）尚无 skill 入口。本 Phase 3 个 skill 草案对位这三格。

**Q2 上线铁律三件套合规率？**
触发词字段：19/19 有（含 deprecated 件）。SKILL-INDEX 行：fixloop 07-07 已加，未见漏网。gitignore 白名单未逐一核验（不改 gitignore，仅提示 /lint 应加此查项）。总体合规，但**三件套核验目前靠人肉**——可脚本化（Y5 路线图 T-09）。

**Q3 生命周期字段（status/signoff/version）覆盖率？**
低。有 status 字段：critique(candidate)/fixloop(active)/mdcard(active+signoff)/ingest(deprecated) 等约 5 个；trio/abcz/movement/priceband/posclean 五个生产 skill **无 version 无 status 无 signoff**。frontmatter_status_checker（本 Phase 新脚本）可扫出全量清单，补齐是 A/B 档批量小修。

**Q4 skill 与脚本后端的绑定健康度？**
数据分析 5 skill 全部"skill=口径卡+一行命令，脚本=机械相"，是正确形态。治理 3 skill（promote/fixloop/handoff）纯 prompt 流程零脚本支撑——LLM 每次重新推理检查项，漂移风险高。这是最大结构性缺口（对应 Y6 新脚本 2/4 号件）。

**Q5 有无过时/僵尸 skill？**
仅 retail 局部 ingest（deprecated·有意保留防误用，处理正确）。G03_Lint_双链巡检（脚本侧）对应的旧 lint 思路已被 lint-kb（根层）+lint_v2 取代。无其他僵尸。SKILL-INDEX 无状态列，deprecated/candidate 在目录里不可见——建议 INDEX 加状态标记。

**Q6 触发词冲突/歧义？**
未见硬冲突。潜在歧义：根层与 retail 双层 skill 体系（review、compact、ingest 均有同名或近名），依赖 scoped 机制裁决；SKILL-INDEX 已用"根层另有"段落声明，可接受。"清洗数据"（posclean）与未来 category-pos-cleaning skill 触发词需错开（草案已用"品类清洗/品类映射"区隔）。

**Q7 skill 文档密度是否失衡？**
是。diagnose/deep-read/fixloop 是重文档（含相位分工表、项目章程）；trio/abcz 等轻文档（20行内）。轻重与使用频率匹配，失衡可接受；唯 promote 作为"M-DEC 缺的那座桥"文档单薄且无检查表——升级候选。

**Q8 signoff 门是否被 skill 正确内置？**
好：draft（停在等签字）、diagnose（升active/发客户须签字）、deep-read（回填停签字门）、scan（停在签字门）、fixloop（D档才停）均显式写门。critique 自身仍是 candidate 未签字——用"未签字的skill去审别人的标准"存在自指尴尬，建议优先补签。

**Q9 与 Phase-Z（品类表/category_pos_cleaner）的接口？**
当前零 skill 接口：category_pos_cleaner v0.1-0.3 只能手工调。品类表 v3 诊断列（business_role 透传）已为 skill 化预留。草案 category-pos-cleaning-review_draft.md 定义"跑脚本→读质量报告→人工复核→六哥签字"回路，签字前不可上真实数据。

**Q10 最该新增/升级什么 skill？**
新增（本 Phase 已出草案×3）：mdec-promote-review（配 checker 脚本）、nightly-loop-resume（配 resume builder）、category-pos-cleaning-review（配 cleaner v0.3）。升级：①critique 补签字；②五个数据分析 skill 补 frontmatter 生命周期字段；③promote 挂 checker 脚本为机械相。均待六哥裁决，草案不构成生效依据。
