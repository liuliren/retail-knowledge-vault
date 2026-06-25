#!/usr/bin/env bash
# 单品类诊断 orchestrator: raw.xls → 脱敏 → 自检 → 分析 → 打印指标(供agent写诊断卡)
# 用法: diagnose.sh <raw.xls绝对路径> <品类名>
# 裸值只流过脚本,不进 Agent 上下文(keys-not-prompts)。
set -euo pipefail
RAW="${1:?需raw.xls路径}"; CAT="${2:?需品类名}"
ROOT="/Users/davidliu/KnowledgeBase/retail-knowledge-vault"
PIPE="$ROOT/13_数据分析与工具脚本/脱敏测试链路_v0.1"
OUTDIR="$ROOT/09_门店案例与项目复盘/乐易购花厅坊店/03_商品诊断/01_清洗输出/_疯狂测试脱敏"
mkdir -p "$OUTDIR"
CSV="$OUTDIR/${CAT}_脱敏SKU表_v0.1.csv"

echo "===== [1/3] 脱敏 ====="
python3 "$PIPE/sanitize.py" "$RAW" "$CSV" --category "$CAT"

echo "===== [2/3] 脱敏自检(0条码残留) ====="
python3 - "$CSV" <<'PY'
import csv,re,sys
leak=sum(1 for row in csv.reader(open(sys.argv[1],encoding="utf-8-sig"))
         for c in row if re.fullmatch(r"\d{8,}", str(c).strip()))
print(f"条码残留 {leak} 处 " + ("✅ 干净" if leak==0 else "❌ 需修·停止"))
sys.exit(0 if leak==0 else 1)
PY

echo "===== [3/4] 分层失真分析 ====="
python3 "$PIPE/analyze.py" "$CSV"

echo "===== [4/4] 角色闸 + ABCZ + 汰换建议 ====="
ENR="$OUTDIR/${CAT}_增强SKU表_v0.1.csv"
python3 "$PIPE/enrich.py" "$CSV" "$ENR"
echo ""
echo ">>> 脱敏表: $CSV"
echo ">>> 增强表(角色/ABCZ/汰换): $ENR"
echo ">>> 下一步: Agent 据指标+增强表写 5 段诊断卡(含净可汰清单) + make-pdf 渲染至 output/"
