---
name: promote
version: v0.1
created: 2026-06-28
author: 六哥 + Claude
description: >
  M-DEC 决策记忆闭环（方法论回补的关键桥梁）。对已知结果的决策：回填
  actual_outcome + lessons → 蒸馏进对应概念页 → 状态 open→closed。
  触发：promote / 决策有结果了 / 回填M-DEC / 方法论回补 / 结项 / 蒸馏决策。
allowed-tools: Bash, Read, Write, Edit
when_to_use: >
  MUST USE 当六哥说：某个决策有结果了 / 回填一下M-DEC / 方法论回补 /
  promote这个决策 / 结项 / 这个实验跑出来了 / 复盘结果写进去 / M-DEC promote。
触发词: [promote, 决策有结果, 回填M-DEC, 方法论回补, 结项, 蒸馏决策, M-DEC闭环]
输出物: 更新后的M-DEC页(closed) + 更新后的概念页(追加验证案例块)
---

# /promote · M-DEC 决策闭环 Skill v0.1

> **一句话**：决策有结果 → 回填 → 蒸馏进方法论 → 关门。这是 M-DEC 缺的那座桥。

---

## 触发场景

- 某个决策的实际结果已可知（实验跑完、周期结束、六哥亲口说"结果出来了"）
- `/review` 复盘时发现某 M-DEC 有 outcome 可填
- 某概念页缺少"实战验证案例"，有对应决策可蒸馏

---

## 输入

| 参数 | 说明 |
|---|---|
| `DEC-ID` 或文件路径 | 要 promote 的 M-DEC 页（如 `M-DEC-010` 或完整路径） |
| `actual_outcome`（可选） | 六哥口述的实际结果；未提供则跳到 Step 2 引导填写 |
| `lessons`（可选） | 六哥口述的教训总结；未提供则跳到 Step 2 引导填写 |

---

## 执行步骤

### Step 1 · 找到 M-DEC 文件

```bash
find "/Users/davidliu/KnowledgeBase/retail-knowledge-vault" \
  -name "*M-DEC*" -o -name "*DEC-*" 2>/dev/null | grep -i "<DEC-ID>"
```

读取全文，确认：
- `status: open`（未关闭）
- `decision:`、`expected_outcome:` 字段已填
- `actual_outcome:` 和 `lessons:` 字段是否为空

### Step 2 · 收集结果信息

如果六哥未在对话中提供，先问：
1. **实际发生了什么？**（actual_outcome：与预期相比）
2. **最重要的教训 1-3 条？**（lessons：可复用的规律性认知）

如果六哥提供了 → 直接用，不重复问。

### Step 3 · 回填 M-DEC 页

用 Edit 工具更新 M-DEC 文件：

**在 frontmatter 中更新**：
```yaml
status: closed
closed_date: YYYY-MM-DD
```

**在正文中补充**（找到 `## 实际结果` 或 `## actual_outcome` 章节，若不存在则追加）：
```markdown
## 实际结果（actual_outcome）
> 填写日期：YYYY-MM-DD

[六哥口述或Agent综合的实际结果，与预期对比]

## 教训（lessons）

1. [教训1：可复用的规律性认知]
2. [教训2]
3. [教训3（如有）]

## Promote 记录
> 本决策已于 YYYY-MM-DD promote，蒸馏进以下概念页：
> - [[概念页名]]（追加"M-DEC验证案例"块）
```

### Step 4 · 蒸馏进概念页

**找到关联的概念页**：
- 从 M-DEC 文件的 `related_pages:` 或 `tags:` 推断
- 或从决策内容推断（如"品类角色调整"决策 → `[[品类管理]]`、`[[SKU角色层]]`）

**在概念页追加验证案例块**（在文件末尾或"实战案例"章节）：

```markdown
## M-DEC 验证案例

### [DEC-ID] · [决策标题] · [YYYY-MM-DD]
- **决策**：[一句话]
- **预期**：[一句话]
- **实际**：[一句话]
- **关键教训**：[最重要的1条]
- **详情**：[[M-DEC-XXX_xxx]]
```

### Step 5 · 输出确认

报告：
1. M-DEC 文件已更新（closed）
2. 蒸馏进了哪些概念页（附路径）
3. 教训摘要（1-3条，六哥确认是否准确）

---

## 输出规范

- M-DEC 文件：`status: open` → `status: closed`，追加 `actual_outcome` + `lessons`
- 概念页：追加 `M-DEC 验证案例` 块（不改写原有内容）
- 不新建文件，只修改现有页面

---

## 注意事项

- **不代替六哥写教训**：Step 2 必须由六哥口述核心认知；Agent 只负责格式化和蒸馏
- **只追加不覆盖**：概念页现有内容不动，只在末尾或案例章节追加
- **一次只 promote 一个 M-DEC**：避免批量 promote 掩盖细节差异
