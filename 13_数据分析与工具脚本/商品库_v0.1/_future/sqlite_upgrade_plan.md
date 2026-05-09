---
title: 商品库 SQLite 升级计划（Year 2+ 占位 / 不实施）
version: v0.1
status: draft
owner: 六哥
created: 2026-05-09
updated: 2026-05-09
module: 13_数据分析与工具脚本/商品库_v0.1/_future
quadrant: I
client_safety: internal_only
related:
  - "[[商品库_v0.1/README]]"
---

# 商品库 SQLite 升级计划（占位）

> **本文件**：未来规划 / Year 2+ 评估实施 / **v1.1 坚持 CSV + Markdown 白盒**。

---

## §1. 当前阶段坚持 CSV + Markdown 白盒

```
当前（v1.1 - v1.0 全周期）：
  存储：CSV（数据）+ Markdown（说明 / 字段定义）
  读取：Python pandas / openpyxl
  写入：Excel / 文本编辑器 / 脚本
  审计：git history / Markdown 表格

理由：
  ✅ vault MD 白盒哲学（与 IBM Audit Trail / Apple Minimalism 一致）
  ✅ 无运维负担（不要数据库服务）
  ✅ 6 哥 / 顾问 / 客户都能看 / 都能改
  ✅ 跨设备同步友好（git）
  ✅ 与 vault 6 大治理支柱协同
```

---

## §2. SQLite 升级触发条件（Year 2+）

```
任一条件触发评估升级：

条件 1：SKU 数量超过 50,000
  - CSV 读写慢（pandas 大文件性能）
  - 内存占用 > 500MB
  - 查询时间 > 1 秒

条件 2：查询性能成为瓶颈
  - 跨表 JOIN 频繁（A × B × C × keyword_rule）
  - 复杂筛选（按品牌 + 规格 + 包装多维过滤）
  - 实时查询需求（如咨询会议中实时查）

条件 3：跨客户映射关系复杂化
  - 客户 ≥ 5 / 累积 mapped 数据 > 10 万行
  - 跨客户去重 / 反哺逻辑复杂化
  - 需要事务保证（同时改 A + 多个 mapped）

条件 4：需要更严格 FK 和索引
  - matched_sku_id / matched_skeleton_id / category_l4_code 等 FK 完整性强保证
  - 索引加速频繁查询字段
  - 触发器（如 mapped 修正自动 update raw 反向）
```

---

## §3. 升级方案（W30+ 评估）

```
Option A: SQLite（推荐起步）
  ✅ 嵌入式（无服务）/ 单文件 / 跨平台
  ✅ 支持 SQL / FK / 索引 / 触发器
  ✅ Python sqlite3 内置库
  ✅ 仍可与 CSV 互转（备份用）
  ⏸ 不支持向量（需扩展 sqlite-vss）

Option B: DuckDB（数据分析友好）
  ✅ 内存 + 磁盘混合 / 性能强
  ✅ 直接读 CSV / Parquet
  ✅ SQL 兼容性好
  ⏸ 工业化运维案例少

Option C: PostgreSQL（重型）
  ✅ 功能最强 / FK / 触发器 / 全文搜索 / pgvector
  ❌ 运维负担重 / 不适合早期 vault

→ 起步推荐 SQLite（轻量 + 嵌入式 + git 友好）
→ 后期视需求评估 DuckDB / PostgreSQL
```

---

## §4. 升级路径（不破坏 vault 白盒）

```
Step 1：保留 CSV 作为 source of truth（git 跟踪）
Step 2：SQLite 作为查询引擎（从 CSV 自动生成 / 不入 git）
Step 3：每次 CSV 变更 → 自动重建 SQLite
Step 4：Markdown 文档不变 / 仍是 single source

→ 不抛弃 CSV / 不抛弃 Markdown / SQLite 仅作为性能补充
```

---

## §5. 升级前提

```
Year 2+ 升级前必须先完成：
  1. 商品库 SKU ≥ 50,000（A + B + C 合计）
  2. 客户战役 ≥ 5
  3. CSV 性能确实成为瓶颈（实测）
  4. 6 哥 sign off
  5. 工程操作纪律 §17.11+ 合规
  6. 与 vault 6 大治理支柱协同评估
```

---

## §6. 关联

- [[商品库_v0.1/README]]
- [[embedding_plan]]（同期评估 / 协同升级）
- [[CLAUDE.md]] §15 工程化标准

## §7. 版本记录

| 版本 | 日期 | 变更 |
|---|---|---|
| **v0.1** | **2026-05-09** | **占位**：当前坚持 CSV + Markdown 白盒 / Year 2+ 评估 / SQLite 起步推荐 / 升级路径不破坏白盒 / 升级前提 6 项 |
