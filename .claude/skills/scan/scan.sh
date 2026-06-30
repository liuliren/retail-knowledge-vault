#!/usr/bin/env bash
# 语料巡检 scan.sh — 找出自上次巡检以来新增/改动的语料 .md（纯只读检测，不改任何内容文件）
# 用法:
#   scan.sh            列出自上次 marker 以来新增/改动的 .md（首次无 marker → 列最近7天）
#   scan.sh --stamp    打时间戳（巡检处理完后调用，标记"本批已巡检"）
#   scan.sh --since 3  忽略 marker，强制列最近 N 天改动
set -euo pipefail

VAULT="/Users/davidliu/KnowledgeBase/retail-knowledge-vault"
MARKER_DIR="$VAULT/98_AI协作中枢/04_执行日志"
MARKER="$MARKER_DIR/_语料巡检_last_marker"
# 监视目录（新语料落点）。要扩展就加路径。
WATCH=(
  "$VAULT/Clippings"
  "$VAULT/90_素材暂存与待整理"
)

mkdir -p "$MARKER_DIR"

if [[ "${1:-}" == "--stamp" ]]; then
  touch "$MARKER"
  echo "✅ marker 已更新: $(date '+%Y-%m-%d %H:%M:%S')"
  exit 0
fi

FINDARGS=()
if [[ "${1:-}" == "--since" ]]; then
  FINDARGS=(-mtime "-${2:-7}")
  echo "# 强制列最近 ${2:-7} 天改动"
elif [[ -f "$MARKER" ]]; then
  FINDARGS=(-newer "$MARKER")
  echo "# 自上次巡检($(date -r "$MARKER" '+%Y-%m-%d %H:%M'))以来的新增/改动:"
else
  FINDARGS=(-mtime -7)
  echo "# [首次巡检] 无 marker → 列最近 7 天改动:"
fi

count=0
for d in "${WATCH[@]}"; do
  [[ -d "$d" ]] || continue
  while IFS= read -r f; do
    echo "$f"
    count=$((count+1))
  done < <(find "$d" -type f -name '*.md' "${FINDARGS[@]}" 2>/dev/null | sort)
done

echo "# ---- 共 $count 个新语料文件 ----" >&2
