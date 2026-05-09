# 商品库变更日志

| 日期 | 版本 | 变更类型 | 变更内容 | 操作人 | 原因 / 来源 |
|---|---|---|---|---|---|
| 2026-05-09 | v0.1 | 初版 | 基础架构（README + 字段定义 + 5 CSV 占位 + brand_alias 5 + package_unit 10）| 6 哥+Claude | W19 提前落地 |
| 2026-05-09 | v1.1 | 内完善 | 8 项升级（采纳 ChatGPT 4 控制点 + 4 其他建议）：(1) 字段 P0/P1/P2 分级 / (2) 经营属性三层归属 / (3) keyword_rule 13+ 列 / (4) G11 错误处理 7 项 / (5) raw+mapped 双层 / (6) 4 文件套（README/字段字典/使用规则/维护 SOP）/ (7) _future/ 占位 / (8) 一句话定位 + 5 角色 + 闭环 8 步 | 6 哥+Claude | ChatGPT 8 项升级采纳 |
| 2026-05-09 | v1.1 | 文件重命名 | 字段定义_v1.0.md → 01_字段字典.md / A_core_sku.csv → A_core_sku_seed.csv / _模板.csv → _客户SKU模板.csv | Claude | v1.1 命名规范 |
| 2026-05-09 | v1.1 | 文件拆分 | 花厅坊_SKU.csv → 花厅坊_SKU_raw.csv + 花厅坊_SKU_mapped.csv（双层）| Claude | raw 不覆盖 / mapped 工作流 |
| 2026-05-09 | v1.1 | 新增文件 | 02_商品库使用规则.md / 03_商品库维护SOP.md / _future/embedding_plan.md / _future/sqlite_upgrade_plan.md / _maintenance/keyword_rule.csv | Claude | 4 文件套 + 治理升级 |
| 2026-05-09 | v1.1 | 样例填充 | B/A/raw/mapped 各 3-5 样例（共 ~25 行 / 不大规模填充）| Claude | v1.1 边界 |
