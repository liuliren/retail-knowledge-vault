#!/usr/bin/env bash
# 花厅坊 POS 清洗 — Dry-run 启动脚本
# 不写入正式清洗结果；预览输出到 _dryrun_preview/
set -euo pipefail
cd "$(dirname "$0")"
python3 main.py
