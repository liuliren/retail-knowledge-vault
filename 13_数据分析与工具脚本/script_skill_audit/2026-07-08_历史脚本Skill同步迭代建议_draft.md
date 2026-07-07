---
title: 历史脚本Skill同步迭代建议（Phase-Y·Y9）
summary: 补README/补测试/旧skill加红线/接RESUME/Phase-Z打通/归档候选/不能动名单/批次安排。
version: v0.1
status: draft
owner: Claude（Phase-Y）/ 六哥（裁决）
created: 2026-07-08
source_type: audit_note
client_safety: internal_only
---

# 历史脚本/Skill 同步迭代建议 draft（Y9）

## 1. 补 README 名单（文档-代码同步·B档批量可做）
- `G03_Lint_v2/README.md`：六查→实做13查同步；`updated` 字段更新（**最高优先**，红线件文档漂移）
- `category_pos_cleaner/README_draft.md`：v0.3 收敛机制补写后转正命名
- `tool_drafts/`：4 个新脚本共用一页 README（v0.2 时补）
- publish skill 正文版本号 v0.2→v0.4 对齐（A档一行改）

## 2. 补测试名单（按风险排序）
1. **lint_v2 敏感正则专项测试**（红线检测零回归=Y3 最大缺口）→ 路线图 T-05
2. pos_clean 断言级用例（现仅导入级）：七坑各一条 mock 用例
3. sanitize.py 输出零裸值断言（T-09）
4. mdcard 最小渲染冒烟测试
5. build_master mock 集成测试

## 3. 旧 skill 加红线/补字段名单（A/B档小修，改前列清单给六哥）
- trio/abcz/movement/priceband/posclean 五件：补 version/status/signoff frontmatter 字段
- abcz：A≤70/B≤90 阈值"draft标准待审议"提示已在 skill 内，建议同步进 trio_engine 文件头
- critique：candidate→active 需六哥签字（自指风险：未签字skill在审别人的标准）
- SKILL-INDEX：建议加状态标记（deprecated/candidate 可见化）

## 4. 接 RESUME/断点体系名单
- nightly_resume_builder（本 Phase 新件）→ 与 /handoff、compact 治理对接（见 skill 草案，签字后）
- scan skill：核实 launchd 定时是否真在跑，结果记 RESUME
- 知识库自动化_v1：核实 run_daily.sh 挂载状态（同上）

## 5. 与 Phase-Z 打通项
- category_pos_cleaner v0.3 ⇄ 品类表迭代实验 v3 诊断列透传（已预留）
- frontmatter_status_checker 可先对 05_品类管理与商品规划/ 试跑（只读），为品类底座件的 status 消债供弹药
- 品类表反哺建议（quality_report 第三章）→ V6.0 修订提案流程（六哥裁决门）
- category-pos-cleaning-review skill 草案 = Phase-Z 的 skill 化出口

## 6. 归档候选（C档·移动不可逆·须六哥列清单确认后才动）
| 候选 | 理由 | 前置动作（A档可先做） |
|---|---|---|
| 花厅坊POS清洗脚本_v0.1/ | 入口已被 POS清洗库+三件套取代 | 先在其 README 顶部加"入口已转移"指针 |
| G03_Lint_双链巡检脚本_v0.1/ | 仅README无代码，已被 lint_v2 取代 | 同上加指针 |
| 数据清洗匹配_v0.1/selftest_huachangfang.py | 依赖真实数据不可移植 | 待 mock 自测替代后 |
| 知识库自动化_v1/ | 待核实定时挂载；若已停=整包归档候选 | 先核实，不预判 |

## 7. 不能动名单（红线）
- `.claude/skills/` 全部正式件（含 deprecated ingest 指针——删除需D档签字）
- `.claude/hooks/pre-commit-gov001.sh`（只可出建议 diff：补 rar/7z/gzip/sqlite 魔数）
- `pos_schema.py`（口径SSOT，改=改口径=签字）、trio_engine/pos_clean 生产主干
- .gitignore / CI / 一切 active·stable 正文；99_原始素材 与客户 raw（只 ls 不读）

## 8. 批次安排建议
- **批次1（今晚可收）**：本 Phase 产物定稿 + lint_v2 README 同步稿（草案给六哥）+ publish 版本号一行修
- **批次2（本周）**：T-05 敏感正则测试 + 五个数据 skill frontmatter 补齐（B档清单报告）+ 归档候选前置指针
- **批次3（Phase-Z 合流）**：category-pos-cleaning-review 三件套上线审议 + 真实数据签字门
- **批次4（低优）**：T-07/T-08 checker、知识库自动化_v1 处置裁决
