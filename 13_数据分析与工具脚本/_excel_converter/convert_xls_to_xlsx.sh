#!/usr/bin/env bash
# =============================================================================
# convert_xls_to_xlsx.sh - 批量 xls → xlsx 转换工具 v0.1
# =============================================================================
# 用途：客户 POS 系统老式 .xls 文件批量转 .xlsx（LibreOffice soffice headless）
# 默认输出 /tmp / 不入 vault / 不入 git
# 不修改原始文件 / 不清洗数据 / 不生成结论
#
# 使用：
#   bash convert_xls_to_xlsx.sh <输入目录> [输出目录]
#
# 例：
#   bash convert_xls_to_xlsx.sh \
#     "/path/to/xls_dir" \
#     "/tmp/_xls_convert_20260510"
# =============================================================================

set -u  # 严格变量 / 但保留对失败文件的容错处理（不用 -e）

# --- 1. 参数检查 ---
if [ "$#" -lt 1 ]; then
  echo "❌ 用法: $0 <输入目录> [输出目录]"
  echo ""
  echo "  参数 1（必填）：输入目录（含 .xls 的文件夹）"
  echo "  参数 2（可选）：输出目录 / 默认 /tmp/_xls_convert_<timestamp>/"
  echo ""
  echo "  例: $0 \"/path/to/xls_dir\""
  echo "      $0 \"/path/to/xls_dir\" \"/tmp/_xls_convert_20260510\""
  exit 1
fi

INPUT_DIR="$1"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="${2:-/tmp/_xls_convert_${TIMESTAMP}}"

# --- 2. 输入目录检查 ---
if [ ! -d "$INPUT_DIR" ]; then
  echo "❌ 输入目录不存在: $INPUT_DIR"
  exit 1
fi

# --- 3. 自动查找 soffice ---
SOFFICE=""
SOFFICE_CANDIDATES=(
  "/opt/homebrew/bin/soffice"
  "/usr/local/bin/soffice"
  "/Applications/LibreOffice.app/Contents/MacOS/soffice"
)

for cand in "${SOFFICE_CANDIDATES[@]}"; do
  if [ -x "$cand" ]; then
    SOFFICE="$cand"
    break
  fi
done

# 如以上路径都没找到 / 试 PATH
if [ -z "$SOFFICE" ]; then
  if command -v soffice >/dev/null 2>&1; then
    SOFFICE="$(command -v soffice)"
  fi
fi

if [ -z "$SOFFICE" ]; then
  echo "❌ 未找到 LibreOffice soffice"
  echo "   请安装：brew install --cask libreoffice"
  echo "   或下载：https://www.libreoffice.org/"
  exit 1
fi

echo "✅ soffice 找到: $SOFFICE"

# --- 4. 创建输出目录 ---
mkdir -p "$OUTPUT_DIR"
echo "📂 输入: $INPUT_DIR"
echo "📂 输出: $OUTPUT_DIR"
echo ""

# --- 5. 找 .xls 文件（不含 .xlsx）---
SHOPT_BAK=$(shopt -p nullglob nocaseglob 2>/dev/null || true)
shopt -s nullglob nocaseglob

XLS_FILES=()
for f in "$INPUT_DIR"/*.xls; do
  # *.xls glob 不匹配 *.xlsx / nullglob 下空目录返回空 / 仅取真实文件
  [ -f "$f" ] && XLS_FILES+=("$f")
done

eval "$SHOPT_BAK"

XLS_COUNT=${#XLS_FILES[@]}

if [ "$XLS_COUNT" -eq 0 ]; then
  echo "⚠️  未在输入目录找到 .xls 文件: $INPUT_DIR"
  exit 0
fi

echo "📋 找到 $XLS_COUNT 个 .xls 文件"
echo ""

# --- 6. 批量转换 ---
LOG_FILE="$OUTPUT_DIR/_convert_log.txt"
{
  echo "=== xls→xlsx 批量转换日志 ==="
  echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
  echo "输入: $INPUT_DIR"
  echo "输出: $OUTPUT_DIR"
  echo "soffice: $SOFFICE"
  echo "文件数: $XLS_COUNT"
  echo ""
} > "$LOG_FILE"

SUCCESS=0
FAILED=0
FAILED_FILES=()

for xls in "${XLS_FILES[@]}"; do
  bn=$(basename "$xls")
  echo "→ $bn ..."
  if "$SOFFICE" --headless --convert-to xlsx --outdir "$OUTPUT_DIR" "$xls" >/dev/null 2>&1; then
    SUCCESS=$((SUCCESS + 1))
    echo "  ✅ OK" | tee -a "$LOG_FILE"
    echo "[OK]   $bn" >> "$LOG_FILE"
  else
    FAILED=$((FAILED + 1))
    FAILED_FILES+=("$bn")
    echo "  ❌ FAILED" | tee -a "$LOG_FILE"
    echo "[FAIL] $bn" >> "$LOG_FILE"
  fi
done

# --- 7. 总结 ---
echo ""
echo "=== 转换完成 ==="
echo "  ✅ 成功: $SUCCESS / $XLS_COUNT"
echo "  ❌ 失败: $FAILED / $XLS_COUNT"

if [ "$FAILED" -gt 0 ]; then
  echo ""
  echo "失败文件清单："
  for f in "${FAILED_FILES[@]}"; do
    echo "  - $f"
  done
fi

echo ""
echo "📂 输出目录: $OUTPUT_DIR"
echo "📄 转换日志: $LOG_FILE"
echo ""
echo "下一步建议："
echo "  python3 13_数据分析与工具脚本/_excel_converter/inspect_excel_headers.py \"$OUTPUT_DIR\""

exit 0
