---
title: 商品库 embedding 升级计划（W30+ 占位 / 不实施）
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

# 商品库 embedding 升级计划（占位）

> **本文件**：未来规划 / W30+ 评估实施 / **v1.1 不实施**。

---

## §1. 时点

```
W30+ 再评估
触发条件：
  - Layer 1+2 算法（规则 + 模糊匹配）准确度达到 80% 后仍有瓶颈
  - 客户战役 ≥ 2（破晓肇庆开始）
  - 商品库 SKU ≥ 5,000
```

---

## §2. 起步优先

```
✅ 起步优先：本地 sentence-transformers（开源 / 离线）
  - 模型：paraphrase-multilingual-MiniLM-L12-v2（多语 / 中文支持）
  - 或：BGE-M3（北京智源 / 中文最优）
  - 离线运行 / 不依赖云端 API
  - 单次 embedding ~1ms / 万级 SKU 秒级完成

⏸ 后续评估：
  - OpenAI text-embedding-3 / Anthropic claude-3-haiku embedding（云端 / 收费）
  - 仅在本地模型不够时再考虑
```

---

## §3. LLM 角色

```
LLM 只做候选推荐 / 不直接拍板：
  Step 1：embedding cosine 相似度 → top-5 候选
  Step 2：LLM 推理 → final reasoning（输出："推荐 X / 因为 Y"）
  Step 3：< 0.9 confidence 必走人工审核
  Step 4：≥ 0.9 自动入 mapped 层

→ LLM 不能跳过人工审核
→ LLM 不能直接修改商品库（必须经 manual_review）
```

---

## §4. 可追溯要求

```
embedding 结果必须可追溯：
  - 模型版本（如 BGE-M3-v1.5）
  - embedding 生成日期
  - 输入文本（standard_product_name 或 raw_product_name）
  - 向量维度（如 1024）
  - cosine 相似度阈值

存储位置：
  _embedding/ 目录（W30+ 创建）
  ├── model_meta.md           模型版本 + 参数
  ├── embeddings_<date>.npy   numpy 向量文件（按日期分版本）
  └── lookup_index.csv        sku_id ↔ vector_index 映射
```

---

## §5. 升级前提

```
W30+ 升级前必须先完成：
  1. Layer 1+2 算法稳定（规则 + 模糊准确度 > 70%）
  2. 商品库 SKU ≥ 5,000（A + B 合计）
  3. 客户战役 ≥ 2
  4. 6 哥 sign off
  5. 工程操作纪律 §17.11+ 合规（不污染 vault MD 白盒）
```

---

## §5.5. embedding 文件存储策略评估（5/9 W19 后续建议 4 / P2）

### 当前阶段（v1.1）

```
❌ 不纳入 git
原因：
  - .npy 二进制文件不适合 git diff
  - 体积大（万级 SKU 约 100MB+）
  - 可从源 CSV 重建（不是 single source）
```

### W30+ 评估维度（5 项）

| # | 维度 | 阈值 | 影响决策 |
|---|---|---|---|
| 1 | **文件体积** | < 100MB / 单文件 | 大于 → 走外部存储 |
| 2 | **可复现性** | 能否从源 CSV + 模型重建 | 能 → 不必 git / 走本地缓存 |
| 3 | **隐私风险** | 是否含客户独有 SKU 反向推导 | 含 → 必须脱敏后才存 |
| 4 | **查询性能** | embedding 重建耗时 | 长 → 走 SQLite + cache |
| 5 | **是否可从源 CSV 重建** | 模型版本固定 + 输入文本固定 | 能 → 重建优于存档 |

### 存储方案候选（W30+）

```
Option A: 本地缓存（不入 git）
  - .npy 在 _embedding/ 目录 / .gitignore 默认排除（已有 **/*.npy 规则候选）
  - 跨设备走加密备份
  ⭐ 推荐起步

Option B: SQLite + sqlite-vss
  - 与 [[sqlite_upgrade_plan]] 协同
  - 跨客户共享时易管理
  - Year 2+ 评估

Option C: 外部 Vector DB（Chroma / Qdrant）
  - 运维负担重
  - 与 vault MD 白盒哲学冲突
  - 不推荐起步
```

### LLM / embedding 角色限制（重申 §3）

```
⛔ LLM 不直接拍板 / 只做候选推荐
⛔ embedding 结果必须可追溯到商品库 ID + 品类 ID
⛔ < 0.9 confidence 必走人工审核
```

---

## §6. 关联

- [[商品库_v0.1/README]]
- [[2026-05-09_算法多轮测试与v2.1升级报告]]（v2.1 → v0.4 语义增强期）
- [[sqlite_upgrade_plan]]（同期评估 SQLite）

## §7. 版本记录

| 版本 | 日期 | 变更 |
|---|---|---|
| **v0.1** | **2026-05-09** | **占位**：W30+ 评估 / 优先 sentence-transformers 本地 / LLM 仅候选推荐 / 可追溯 / 升级前提 5 项 |
