#!/usr/bin/env python3
"""Dry-run for CODEX-2026-06-22-01 P1-3 tools."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import EXECUTE_OUTPUT_DIR
from loaders import compute_sha256
from abc_classifier import apply_abc
from ir_calculator import apply_ir
from safety_stock import apply_safety_stock


INPUT = EXECUTE_OUTPUT_DIR / "销售统计汇总_合并版_v0.1.xlsx"
PREVIEW_DIR = SCRIPT_DIR / "_dryrun_preview"


def mask_key(value: object) -> str:
    text = "" if pd.isna(value) else str(value).strip()
    if len(text) <= 5:
        return "*" * len(text)
    return f"{text[:3]}{'*' * (len(text) - 5)}{text[-2:]}"


def run() -> dict:
    started_at = datetime.now(timezone.utc)
    sha_before = compute_sha256(INPUT)
    df = pd.read_excel(INPUT)
    out = apply_abc(df)
    out, ir_summary = apply_ir(out)
    out, stock_summary = apply_safety_stock(out, arrival_days=7.0)
    sha_after = compute_sha256(INPUT)

    preview_cols = [
        "商品条码",
        "商品名称",
        "销售金额",
        "毛利额",
        "销额ABC",
        "毛利ABC",
        "身份",
        "IR",
        "A类水位",
        "补货信号",
        "库龄级",
        "卖太快",
    ]
    preview = out[[col for col in preview_cols if col in out.columns]].copy()
    if "商品条码" in preview.columns:
        preview["商品条码"] = preview["商品条码"].map(mask_key)
        preview = preview.rename(columns={"商品条码": "商品条码_掩码"})

    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    preview.to_csv(PREVIEW_DIR / "retail_tools_p1_3_preview.csv", index=False, encoding="utf-8-sig")

    summary = {
        "task": "CODEX-2026-06-22-01",
        "mode": "dry-run",
        "started_at": started_at.isoformat(),
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "input": str(INPUT),
        "sha256_unchanged": sha_before == sha_after,
        "row_count": int(len(df)),
        "abc": {
            "status": "ok",
            "coverage": 1.0 if len(df) else 0.0,
            "identity_counts": out["身份"].value_counts(dropna=False).to_dict(),
        },
        "ir": ir_summary,
        "safety_stock": stock_summary,
        "outputs": [str(PREVIEW_DIR / "retail_tools_p1_3_preview.csv")],
        "limitations": [
            "当前合并版输入只有 10 行，dry-run 只能验证执行器口径，不能代表全量门店结果。",
            "IR 缺 ITO 时按注册表纪律标 blocked，不强算。",
            "库龄与售罄闸缺输入字段时标 blocked，不使用占位值。",
        ],
    }
    with open(PREVIEW_DIR / "retail_tools_p1_3_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


if __name__ == "__main__":
    run()

