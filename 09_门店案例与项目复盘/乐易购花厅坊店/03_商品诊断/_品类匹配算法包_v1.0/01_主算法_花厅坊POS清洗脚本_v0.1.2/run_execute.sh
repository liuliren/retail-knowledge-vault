#!/usr/bin/env bash
# 花厅坊 POS 清洗 — 正式执行启动脚本
# ⚠️ 仅在 dry-run 通过且用户预审后允许运行
set -euo pipefail
cd "$(dirname "$0")"
echo "⚠️  即将进入 --execute 模式，会写入正式清洗结果到："
echo "    09_门店案例与项目复盘/乐易购花厅坊店/03_商品诊断/01_清洗输出/"
echo ""
read -p "是否继续？(yes/no): " confirm
if [[ "$confirm" != "yes" ]]; then
  echo "已取消"
  exit 0
fi
python3 main.py --execute
