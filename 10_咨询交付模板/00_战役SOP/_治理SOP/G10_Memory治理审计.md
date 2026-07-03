---
title: G10 Memory 治理审计 SOP v0.1（vault 第 6 大支柱月度审计）
summary: Memory治理月度审计，评分衰减、生命周期转换、token预算控制≤5K。
version: v0.1
status: active
owner: 六哥
created: 2026-05-09
updated: 2026-05-09
module: 10_咨询交付模板/00_战役SOP/_治理SOP
quadrant: III
client_safety: internal_only
related:
  - "[[Memory治理体系_v1.0]]"
  - "[[评分衰减算法说明_v1.0]]"
  - "[[G07_vault月度审计]]"
  - "[[G09_工程操作纪律审计]]"
---

# G10 Memory 治理审计 SOP v0.1

> **本 SOP**：vault 第 6 大治理支柱（Memory 治理）的月度审计 / 与 G07 内容审计 / G08 数据治理 / G09 工程操作纪律审计协同。
>
> **触发**：每月 1 日（人工触发）/ 6 哥每月固定 30 分钟执行。
>
> **目标**：memory 体系健康（评分衰减合理 / lifecycle 自动转换 / 同主题不分散 / token 预算 ≤ 5K）。

---

## §1. SOP 总流程（5 步 / 共 30 分钟）

```
Step 1（5 min）：扫 memory 文件总数 + 子目录分布（vs 上月）
Step 2（10 min）：评分快照生成（99_meta/评分快照_YYYY-MM.md）
Step 3（5 min）：lifecycle 自动转换（dormant / archived_candidate）
Step 4（5 min）：双向打通 KB 抽样验证（5 关键文件 § memory 触发记录）
Step 5（5 min）：沉淀 [[Vault健康仪表]] + 月度报告
```

---

## §2. 评分快照生成（Step 2）

```python
# 月度审计算法（自动化候选 / W22+ 实施）
for memory in all_memory_files:
    days_since = (today - memory.last_accessed).days
    decay = exp(-days_since / 30)
    priority_w = {'P0': 1.0, 'P1': 0.7, 'P2': 0.4, 'P3': 0.1}[memory.priority]
    memory.decay_score = memory.hit_count * decay * priority_w
    
    # lifecycle 自动转换
    if memory.decay_score < 0.1 and memory.priority in ('P2', 'P3'):
        memory.lifecycle = 'dormant'
    if memory.decay_score < 0.05 and days_since > 90:
        memory.lifecycle = 'archived_candidate'

# 输出至 99_meta/评分快照_YYYY-MM.md
```

---

## §3. 月度报告模板

```markdown
## Memory 治理月度审计 总结（YYYY-MM-DD）

1. memory 总数：__ / 子目录分布：P0_红线 __ / P1_高频 __ / P2_常规 __ / archived __
2. 评分平均：__ / vs 上月 ±__
3. lifecycle 转换：
   - dormant 新增 __
   - archived_candidate __（待 6 哥 confirm）
4. 双向打通 KB 抽样：__ / 5 关键文件 §memory 触发记录是否更新
5. 同主题分散检测：__ 候选合并案例
6. token 预算估算：__ K tokens（目标 ≤ 5K）
7. P0 升级候选：__（P1 score > 0.5 + 高频引用）
8. P3 永久归档候选：__ / 6 哥 confirm 后 mv 99_archived_old/
9. 与 G07/G08/G09 协同：...
10. 下月计划：...
```

---

## §4. 与 G07 / G08 / G09 协同

```
G07 vault 月度审计     业务内容层（70 文件 / 6 维评分）
G08 vault 数据治理     数据契约层（每次数据进库）
G09 工程操作纪律审计   工程操作层（每月 / 6 大类规则）
G10 Memory 治理审计    记忆层（每月 / 评分衰减 / 双向打通）⭐ 本 SOP

四 SOP 协同 = vault 完整治理审计闭环：
  内容 (G07) × 数据 (G08) × 操作 (G09) × 记忆 (G10)
```

---

## §5. 落地节奏

| 月份 | 审计重点 | 输出 |
|---|---|---|
| **2026-06**（W22 收尾后第 1 月）| 首次月度审计 + lifecycle 转换 | `2026-06_memory月度审计_v1.0.md` |
| **2026-07** | dormant / archived_candidate sign off | `2026-07_memory月度审计_v1.1.md` |
| **2026-08+** | 跨业态可复用度评估（其他客户战役 memory）| 持续 |

---

## §6. 验收标准（v0.1 升 v1.0 条件）

- ☐ 至少 1 次完整月度审计（W22 后 / 6/9）
- ☐ 评分快照模板实战 ≥ 1 次
- ☐ lifecycle 转换至少 1 次（dormant / archived_candidate）
- ☐ 双向打通 KB 5 关键文件覆盖
- ☐ token 预算 ≤ 5K（vs W20 起步 ~10K+）
- ☐ 6 哥 sign off 至少 1 次

---

## §7. 关联

- [[Memory治理体系_v1.0]]
- [[评分衰减算法说明_v1.0]]
- [[G07_vault月度审计]]
- [[G08_vault数据治理]]
- [[G09_工程操作纪律审计]]

## §8. 版本记录

| 版本 | 日期 | 变更 |
|---|---|---|
| **v0.1** | **2026-05-09** | **初版**：5 步流程 + 评分算法 + 月度报告模板 + 与 G07/G08/G09 协同 / 待 6 月首次月度审计后升 v1.0 |
