#!/usr/bin/env bash
# weekly_data.sh — 周报数据采集器 v1.1
# 每周日 07:00 北京时间自动运行，输出结构化周报数据文件供 /review 读取
# 手动运行: bash weekly_data.sh

VAULT="/Users/davidliu/KnowledgeBase/retail-knowledge-vault"
OUTPUT_DIR="$VAULT/98_AI协作中枢/05_周报系统/数据存档"
mkdir -p "$OUTPUT_DIR"

WEEK=$(TZ="Asia/Shanghai" date "+%Y-W%V")
TODAY=$(TZ="Asia/Shanghai" date "+%Y-%m-%d")
OUTPUT="$OUTPUT_DIR/_周报数据_${WEEK}.md"

# 花厅坊倒计时（macOS date -j）
DEADLINE_TS=$(date -j -f "%Y-%m-%d" "2026-08-31" "+%s" 2>/dev/null || echo 0)
NOW_TS=$(date "+%s")
DAYS_LEFT=$(( (DEADLINE_TS - NOW_TS) / 86400 ))

# Git 统计（过去7天）
cd "$VAULT" 2>/dev/null || true
COMMITS_7D=$(git log --oneline --since="7 days ago" 2>/dev/null | wc -l | tr -d ' ')
COMMIT_LIST=$(git log --since="7 days ago" --format="- %s" 2>/dev/null | head -20 || echo "（无记录）")
FILES_MD=$(git log --since="7 days ago" --name-only --format="" 2>/dev/null | grep "\.md$" | sort -u | wc -l | tr -d ' ')

# 方法论页状态统计
ACTIVE_COUNT=$(grep -rl "^status: active" "$VAULT/01_科学零售方法论/" 2>/dev/null | wc -l | tr -d ' ')
CANDIDATE_COUNT=$(grep -rl "^status: candidate" "$VAULT/01_科学零售方法论/" 2>/dev/null | wc -l | tr -d ' ')

# Skill 数量
SKILL_COUNT=$(ls -d "$VAULT/.claude/skills/"*/ 2>/dev/null | wc -l | tr -d ' ')

# open loops from RESUME
RESUME="$VAULT/98_AI协作中枢/00_总控/_当前断点_RESUME.md"
OPEN_LOOPS=""
if [ -f "$RESUME" ]; then
  OPEN_LOOPS=$(awk '/^open_loops:/{f=1;next} f && /^[^ ]/{exit} f && /^  -/{sub(/^  - /,"- ");print}' "$RESUME" | head -10)
fi
[ -z "$OPEN_LOOPS" ] && OPEN_LOOPS="（未读到 open_loops）"

# 写入输出文件
{
cat << HEADER
---
title: 周报数据 ${WEEK}
generated: ${TODAY}
type: weekly-data-brief
for_skill: /review
---

# 周报原始数据 · ${WEEK}

> 由 weekly_data.sh v1.1 自动生成 · /review 读取此文件作为数据底座

---

## 仪表盘

| 指标 | 数值 |
|---|---|
| 花厅坊倒计时 | **${DAYS_LEFT} 天**（截止 8/31） |
| 本周 git 提交 | ${COMMITS_7D} 次 |
| 本周修改 md 页面 | ${FILES_MD} 个 |
| 方法论页 active | ${ACTIVE_COUNT} 个 |
| 方法论页 candidate | ${CANDIDATE_COUNT} 个 |
| Skills 总数 | ${SKILL_COUNT} 个 |

---

## 本周 Git 提交记录

HEADER

echo "$COMMIT_LIST"

cat << MID

---

## 当前 Open Loops（来自 RESUME）

MID

echo "$OPEN_LOOPS"

cat << FOOTER

---

## 2026 三目标进度（六哥填写后 /review 可用）

| 目标 | 全年 | 本期新增 | 累计 |
|---|---|---|---|
| 营收 | 30万 | 元 | 元 |
| 完整客户交付 | 5个 | 个 | 个 |
| 诊断/品类调整 | 30次 | 次 | 次 |

---

## 本周客户动态（六哥填写）

- 喻总：
- 花厅坊：
- 其他：

---

> 下一步：触发 /review week，AI 读取本文件生成复盘稿
FOOTER
} > "$OUTPUT"

echo "[weekly_data] ✅ 周报数据已生成: $OUTPUT"
echo "[weekly_data] 花厅坊: ${DAYS_LEFT}天 | 提交: ${COMMITS_7D}次 | active页: ${ACTIVE_COUNT}个"
