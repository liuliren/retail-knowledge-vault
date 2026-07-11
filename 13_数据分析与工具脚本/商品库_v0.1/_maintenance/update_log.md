---
title: 商品库变更日志
summary: 商品库变更日志台账，追踪版本迭代、字段升级、新增文件、数据修正。
status: draft
created: 2026-05-09
updated: 2026-05-09
module: 13_数据分析与工具脚本/商品库_v0.1
tags:
  - 商品库
  - 变更日志
  - 台账
---

# 商品库变更日志

| 日期 | 版本 | 变更类型 | 变更内容 | 操作人 | 原因 / 来源 |
|---|---|---|---|---|---|
| 2026-05-09 | v0.1 | 初版 | 基础架构（README + 字段定义 + 5 CSV 占位 + brand_alias 5 + package_unit 10）| 6 哥+Claude | W19 提前落地 |
| 2026-05-09 | v1.1 | 内完善 | 8 项升级（采纳 ChatGPT 4 控制点 + 4 其他建议）：(1) 字段 P0/P1/P2 分级 / (2) 经营属性三层归属 / (3) keyword_rule 13+ 列 / (4) G11 错误处理 7 项 / (5) raw+mapped 双层 / (6) 4 文件套（README/字段字典/使用规则/维护 SOP）/ (7) _future/ 占位 / (8) 一句话定位 + 5 角色 + 闭环 8 步 | 6 哥+Claude | ChatGPT 8 项升级采纳 |
| 2026-05-09 | v1.1 | 文件重命名 | 字段定义_v1.0.md → 01_字段字典.md / A_core_sku.csv → A_core_sku_seed.csv / _模板.csv → _客户SKU模板.csv | Claude | v1.1 命名规范 |
| 2026-05-09 | v1.1 | 文件拆分 | 花厅坊_SKU.csv → 花厅坊_SKU_raw.csv + 花厅坊_SKU_mapped.csv（双层）| Claude | raw 不覆盖 / mapped 工作流 |
| 2026-05-09 | v1.1 | 新增文件 | 02_商品库使用规则.md / 03_商品库维护SOP.md / _future/embedding_plan.md / _future/sqlite_upgrade_plan.md / _maintenance/keyword_rule.csv | Claude | 4 文件套 + 治理升级 |
| 2026-05-09 | v1.1 | 样例填充 | B/A/raw/mapped 各 3-5 样例（共 ~25 行 / 不大规模填充）| Claude | v1.1 边界 |
| 2026-05-09 | v1.1 | CSV 跟踪修正 | .gitignore 加 6 条精确白名单 / 结构层 CSV 上 git / raw/mapped 仍忽略 | Claude | dc8cf98 commit |
| 2026-05-09 | v1.1 后续建议入库 | 文档治理 | CSV 跟踪修正后 6 条建议分级入库（P0×2 / P1×2 / P2×2）：补充客户数据 git 安全边界（README §4.1 / 02 §3.4-3.5）+ 跨设备同步规则（03 §7）+ embedding 文件评估项（embedding_plan §5.5）+ _anonymized/ Year 2+ 预留（sqlite_upgrade_plan §5.5）+ G11 v0.3 候选检查项（G11 §6.5）。**不启动 W23+ 数据接入 / 不导入真实客户数据** | 6 哥+Claude | W19 后续建议入库 |
| 2026-07-08 | v1.1 → dormant | 状态冻结 | 六哥裁决冻结：两个月零实质使用、B_category_skeleton.csv 未随 V6.0 迁移（仍 v4_skeleton）、全库无脚本/skill 实际读取本目录。status 改 dormant，README §6 加不符声明警示，设第3客户签约后的重启触发条件 | 六哥+Claude（99_归档补课精读工程发现） | 2026-07-08 夜间精读全量签字清单 P0-1 |
