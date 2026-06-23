---
title: vault Memory 治理体系 v1.0（第 6 大治理支柱 / W20 落地方案）
version: v1.0
status: active
owner: 六哥
source_type: governance
created: 2026-05-09
updated: 2026-05-09
module: 00_入口与总索引/03_治理规范
quadrant: I
client_safety: internal_only
fact_layer:
  observed:
    - "5/9 vault memory 现状：14 条 / .md + frontmatter / 平铺 + 全加载"
    - "5/9 痛点：数量爆炸 / 主题重叠 / 无优先级 / 无生命周期 / 无评分"
  client_told:
    - "5/9 用户：不要简简单单地在 MD 文档里不断增加字段"
    - "5/9 用户：形成简洁、有体系且高效的处理方式"
    - "5/9 用户：Q1-Q4 全选 A（成为第 6 大支柱 / 子目录化 / MD 白盒 / W20 立即落地）"
  inferred:
    - "[推断] W20 全量升级（6 项）/ ~2.5 天工作量"
  pending:
    - "Day 2 frontmatter 全文件升级"
    - "Day 3 双向打通 KB + G10 SOP"
related:
  - "[[CLAUDE.md]] §13.16-20 + §17.11+"
  - "[[工程操作纪律手册_v1.0]]"
  - "[[反幻觉检查清单]] v1.2"
  - "[[G10_Memory治理审计]]（W20 创建占位）"
---

# vault Memory 治理体系 v1.0

> **vault 第 6 大治理支柱**（前 5 大：反幻觉 §13.16-20 / 一致性 §14 / 工程化 §15 / Claude Code 协作 §17.1-10 / 工程操作纪律 §17.11+）。
>
> **触发**：5/9 用户提议探讨 memory 机制升级 / "形成简洁、有体系且高效的处理方式" / Q1-Q4 全选 A。
>
> **重要性**：⭐⭐⭐ vault 顶级运营标准 / 与 [[2026-05-09_滞销与库存挤压判定标准_v1.0]] / [[工程操作纪律手册_v1.0]] 同级。

---

## §1. vault 治理 6 大支柱

```
1. 反幻觉 §13.16-20         数据/内容反幻觉
2. 一致性 §14               概念逻辑一致
3. 工程化 §15               文件/目录/版本工程
4. Claude Code 协作 §17.1-10  vault 内容协作
5. 工程操作纪律 §17.11+     Bash/Git/工具操作
6. Memory 治理 §17.20+      记忆机制治理 ⭐ 5/9 新建
```

---

## §2. 三层架构（vault Memory v2.0）

```
┌──────────────────────────────────────────────────────────┐
│ L1: Hot Memory（当前会话工作记忆）                        │
│   - LLM context window 自动维护                          │
│   - 会话结束消失（除非 promote 到 L2）                   │
│   - 不需 6 哥管理                                         │
├──────────────────────────────────────────────────────────┤
│ L2: Project Memory（vault 项目热记忆）⭐ 当前 .md 系统    │
│   - 跨会话 / 当前热点                                     │
│   - 路径：~/.claude/.../memory/                           │
│   - 升级：分类 + 优先级 + lifecycle + 评分                │
├──────────────────────────────────────────────────────────┤
│ L3: Knowledge Base（vault 长期知识库）                   │
│   - 路径：/Users/davidliu/KnowledgeBase/retail.../        │
│   - memory 与 KB 双向打通                                │
└──────────────────────────────────────────────────────────┘

数据流：
  L1 → L2：会话结束时 promote 重要记忆
  L2 → L3：memory 沉淀为正式 vault 文档（如 §13.20 / §17.11+）
  L3 → L2：vault 实战触发新 memory（如 5/9 cd /tmp 事件）
```

---

## §3. 6 项升级（W20 落地）

### 升级 1：分类子目录化

```
memory/
├── MEMORY.md                ← 索引（升级 2）
├── 00_user/                 ← 用户档案（最高 / 极少改）
├── 01_feedback/             ← 工作纪律 / 反馈
│   ├── P0_红线/             ← 每会话必读
│   ├── P1_高频/             ← 场景相关时加载
│   ├── P2_常规/             ← 按需查阅
│   └── archived/            ← 历史 / 已不适用
├── 02_project/              ← 项目状态（动态衰减快）
│   ├── active/
│   └── archived/
├── 03_reference/            ← 外部资源指针
└── 99_meta/                 ← memory 自治理元数据
    ├── 评分快照_YYYY-MM.md
    └── 生命周期审计_YYYY-MM.md
```

### 升级 2：MEMORY.md 索引升级

```markdown
# vault Memory 索引 v2.0

## P0 红线（每次会话必读）
- [客户家族协同](01_feedback/P0_红线/...) — ⭐⭐⭐ ...
- ...

## P1 高频（场景相关时加载）
- [MVP 优先](01_feedback/P1_高频/...) — last: YYYY-MM-DD / hits: N
- ...

## P2 常规（按需查阅）
- ...

## 项目状态（active）
- [花厅坊战役 #1](02_project/active/...) — W18-W22 / ...
- ...

## 归档候选（30/60/90 天衰减）
- ...
```

### 升级 3：lifecycle 字段（frontmatter 扩展）

```yaml
priority: P0 / P1 / P2 / P3
lifecycle: active / dormant / archived
last_accessed: 2026-05-09
hit_count: 12
decay_score: 0.85
vault_links:
  - "[[CLAUDE.md]] §X"
expires: 2027-05-09  # 强制 review 节点
```

### 升级 4：评分与衰减

```python
def relevance_score(m):
    days_since = (today - m.last_accessed).days
    decay = exp(-days_since / 30)  # 30 天衰减一半
    priority_w = {'P0': 1.0, 'P1': 0.7, 'P2': 0.4, 'P3': 0.1}[m.priority]
    score = m.hit_count * decay * priority_w
    
    # 自动 lifecycle 转换
    if score < 0.1 and m.priority in ('P2', 'P3'):
        m.lifecycle = 'dormant'  # 30+ 天未用
    if score < 0.05 and days_since > 90:
        m.lifecycle = 'archived'  # 候选归档
    return score
```

### 升级 5：双向打通 KB

```
memory 文件 frontmatter `vault_links: [[...]]`
         ↕
vault KB 关键文件 §"memory 触发记录"段（新增）
```

### 升级 6：检索机制

```
会话启动时 LLM 自动加载：
  - P0 全部（5 条 / ~3K tokens）
  - MEMORY.md 索引（14 条 / ~1K tokens）
  - keyword match 相关 P1（3-5 条 / ~2K tokens）
  
会话中按需 retrieve：
  - 用户提关键词 → 自动 retrieve P2/P3
  - LLM 标识"参考 memory: [[X]]"用法

总 token 预算：~5K（vs 当前全加载 ~10K+）
```

---

## §4. W20 落地节奏（5/16-5/22 / 6 哥 + Claude）

| Day | 内容 | 工作量 |
|---|---|---|
| **Day 1（W20-1 / 5/16）** | 升级 1+2：子目录化 + MEMORY.md 索引升级 | 0.5 天 |
| **Day 2（W20-2 / 5/17）** | 升级 3：14 文件 frontmatter 加新字段 | 0.5 天 |
| **Day 3（W20-3 / 5/18）** | 升级 4：评分与衰减规则（手动维护起步）| 0.5 天 |
| **Day 4（W20-4 / 5/19）** | 升级 5：双向打通 KB（关键 5-8 文件加 §"memory 触发记录"）| 0.5 天 |
| **Day 5（W20-5 / 5/20）** | 升级 6：检索机制设计文档 + G10 SOP 落地 | 0.5 天 |
| **W20 总工作量** | — | **2.5 天** |

---

## §5. 4 层治理底盘（与 §13.16-20 / §17.11+ 协同）

| 层 | 内容 | 落地 |
|---|---|---|
| **L1 操作契约** | memory 写入前 frontmatter 必填检查 | pre-flight checklist 加 §11 Memory 操作 |
| **L2 规则集** | 6 项升级（本手册）| 本文件 §3 |
| **L3 自动检查** | lint 脚本扫 frontmatter 字段 / decay 自动算 | W22+ 实施 |
| **L4 Constitutional 自检** | 月度 G10 审计 + Memory 错误案例库 | [[G10_Memory治理审计]] / [[Memory错误案例库]] W21+ |

---

## §6. 与 vault 其他治理协同

```
§13.20 数据治理       「数据维度」反幻觉
§17.11+ 工程操作纪律  「工程操作维度」反幻觉
§17.20+ Memory 治理   「记忆维度」反幻觉 ⭐ 新

共同根因：「细节差异叠加 = 系统性错误」
共同方法：4 层治理底盘
共同纪律：错误必沉淀案例库 / 跨业态可复用
```

---

## §7. W20 验收标准（v1.0 升 v1.1 条件）

- ☐ 6 项升级 W20 全部落地
- ☐ memory 子目录化完整 + 14 文件全部 mv 到对应位置
- ☐ MEMORY.md 索引升级完成（按 P0/P1/P2 + 项目状态 + 归档候选 5 段分组）
- ☐ 14 文件 frontmatter 全部加 priority / lifecycle / hit_count / vault_links / expires
- ☐ 5-8 关键 KB 文件加 §"memory 触发记录"段
- ☐ G10 Memory 治理审计 SOP v0.1 落地
- ☐ CLAUDE.md §17.20+ Memory 治理写入

---

## §8. 关联

- [[CLAUDE.md]] §13.16-20 + §17.11+
- [[工程操作纪律手册_v1.0]]
- [[2026-05-09_vault全量审计与数据审计1月期机制_v1.0]]
- [[反幻觉检查清单]] v1.2
- [[数据一致性追溯案例库]]
- [[工程操作错误案例库]]
- [[G10_Memory治理审计]]（W20 Day 5 创建）

## §9. 版本记录

| 版本 | 日期 | 变更 |
|---|---|---|
| **v1.0** | **2026-05-09** | **初版 / vault 第 6 大治理支柱建立**：三层架构 + 6 项升级 + W20 落地节奏 + 4 层治理底盘 + 与现有体系协同。触发：5/9 用户提议 + Q1-Q4 全选 A |
