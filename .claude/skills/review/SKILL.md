---
name: review
version: v0.1
created: 2026-06-28
author: 六哥 + Claude
description: >
  周/月复盘引擎。从 logs+decisions+outputs 合成复盘稿，强制对照 2026 三目标
  与花厅坊交付窗口，产出复盘稿 + 3 项下期优先级 + parking lot。
  触发：/review week | /review month | 周复盘 | 月复盘 | 总结一下这周。
allowed-tools: Bash, Read, Write, Edit
when_to_use: >
  MUST USE 当六哥说：周复盘 / 月复盘 / 总结这周 / review week / review month /
  这周干了什么 / 回顾一下 / 帮我复盘 / 周总结 / 月总结。
触发词: [review, 周复盘, 月复盘, 总结这周, 帮我复盘, 周总结, 月总结]
输出物: 复盘稿(.md 写入 life-vault) + 零售线进展摘要(写入 retail 对应战役档案)
---

# /review · 周月复盘引擎 Skill v0.1

> **一句话**：从三个数据源（完成记录 + 决策记录 + 对外输出）合成一张复盘稿，强制对照 2026 三目标，不逃避、不粉饰。

---

## 输入

```
/review week     周复盘（当前周）
/review month    月复盘（当前月）
/review W27      指定周次
```

---

## 执行步骤

### Step 1 · 确定时间范围

- `week` → 当前北京时间的自然周（周一~周日）
- `month` → 当前月
- 指定周次 → 该周的日期范围

### Step 2 · 采集三类数据

**① 完成记录（从 RESUME + 日志）**
```bash
# 读当前断点（RESUME 为 STATE-MACHINE 格式，读 STATE 相关字段）
RESUME="/Users/davidliu/KnowledgeBase/retail-knowledge-vault/98_AI协作中枢/00_总控/_当前断点_RESUME.md"
cat "$RESUME" | grep -A 80 -E "STATE|task:|next_action|open_loops|hot_files|Parking"

# 读 life-vault 本周日志（如存在）
find "/Users/davidliu/KnowledgeBase/life-vault" -name "2026-W*.md" | head -3
```

**② 决策记录（M-DEC 活跃状态）**
```bash
find "/Users/davidliu/KnowledgeBase/retail-knowledge-vault" \
  -name "M-DEC-*" -newer /tmp/week_start 2>/dev/null | head -10
# 或直接搜 status:open 的 M-DEC
grep -rl "status: open" "/Users/davidliu/KnowledgeBase/retail-knowledge-vault/16_客户与战役档案" 2>/dev/null
```

**③ 对外输出（新建/发布的交付件）**
```bash
find "/Users/davidliu/KnowledgeBase/retail-knowledge-vault/98_AI协作中枢/01_Claude_Code/Claude输出区" \
  -name "*.md" -newer /tmp/week_start 2>/dev/null | wc -l
```

### Step 3 · 对照 2026 三目标（强制执行）

每次复盘必须回答以下三个数字，即使无法精确量化也要给出定性判断：

| 目标 | 全年 | 本期进展 | 累计进度 |
|---|---|---|---|
| 营收 | 30万 | 本期新增？元 | 当前：元 |
| 完整客户交付 | 5个 | 本期新增/推进？ | 当前：个 |
| 诊断/品类调整服务 | 30次 | 本期完成？次 | 当前：次 |

**花厅坊窗口**：计算距 8/31 交付红线剩余天数，评估当前节奏是否达标。

### Step 4 · 起草复盘稿

**结构**（严格按此顺序，不加废话）：

```markdown
# [W27 / 2026-06] 复盘

> 复盘时间：YYYY-MM-DD | 花厅坊倒计时：X天

## 对照 2026 三目标
（见上方表格，直接填数字）

## 本期完成（客观事实，不评价）
- 事项1
- 事项2
...

## 卡住/未完成（诚实列出）
- 事项1（原因：X）

## 学到的（最重要1-3条，必须是可复用规律，不是感想）
1.
2.
3.

## 能量状态（一句话，T2层不展开）
[状态评估]

## 下一期 3 件撬动任务
1. [最重要，直接与三目标挂钩]
2.
3.

## Parking（本期降优先级但不丢的事）
- ...
```

### Step 5 · 写入文件

**复盘稿** → `life-vault/10_life/weekly/2026-WXX.md`（周复盘）
或 `life-vault/10_life/monthly/2026-MM.md`（月复盘）

**零售线进展摘要**（仅记录交付相关）→ 追加到
`retail-knowledge-vault/09_门店案例与项目复盘/乐易购花厅坊店/` 对应周期记录

### Step 6 · 更新 RESUME 断点

在 RESUME 的"下一步指针"更新为复盘确定的 3 件撬动任务。

---

## 输出物

1. `life-vault/10_life/weekly/2026-WXX.md` — 完整复盘稿（T2层）
2. RESUME 断点更新（下一步指针）
3. 对话中直接输出**执行摘要**（3目标进度 + 3件下期任务）供六哥即时确认

---

## 铁律

- **三目标必须对照**：不允许"回顾了这周工作"但不对照营收/客户/诊断数字
- **禁止粉饰**：卡住的事必须诚实列出，不以"推进中"代替具体问题
- **3件下期任务必须与三目标直接挂钩**：不接受"继续推进"类虚词
- **停在签字门**：3件任务输出后，等六哥确认再写入 RESUME
