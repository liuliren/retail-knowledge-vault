#!/usr/bin/env python3
"""
CODEX-2026-06-20-01 主供应商并表 dry-run。

边界：
- 原始文件和既有清洗输出只读。
- 只写 _dryrun_preview/supplier_* 文件。
- 不输出采购额绝对值。
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from config import EXECUTE_OUTPUT_DIR, PROJECT_ROOT
from loaders import compute_sha256
from normalizers import normalize_barcode
from supplier_agg import build_supplier_capability


RAW_DATA_DIR = PROJECT_ROOT / "99_原始素材/01_门店数据材料"
SUPPLIER_ARCHIVE = RAW_DATA_DIR / "20260510_商品档案表_包含供应商信息.xls"
SUPPLIER_SALES = RAW_DATA_DIR / "供应商销售汇总_90天_20260508.xls"
SUPPLIER_MASTER = RAW_DATA_DIR / "20260510_供应商信息.xls"
MERGED_SALES = EXECUTE_OUTPUT_DIR / "销售统计汇总_合并版_v0.1.xlsx"
PREVIEW_DIR = SCRIPT_DIR / "_dryrun_preview"


def mask_key(value: object) -> str:
    text = "" if pd.isna(value) else str(value).strip()
    if len(text) <= 5:
        return "*" * len(text)
    return f"{text[:3]}{'*' * (len(text) - 5)}{text[-2:]}"


def read_excel_table(path: Path, required_headers: set[str]) -> pd.DataFrame:
    raw = pd.read_excel(path, engine="calamine", header=None)
    header_idx = None
    for idx, row in raw.head(12).iterrows():
        cells = {str(cell).strip() for cell in row.tolist() if str(cell).strip() and str(cell) != "nan"}
        if required_headers.issubset(cells):
            header_idx = idx
            break
    if header_idx is None:
        raise ValueError(f"未找到表头: {path.name} required={sorted(required_headers)}")
    df = pd.read_excel(path, engine="calamine", header=header_idx)
    df = df.dropna(how="all")
    df.columns = [str(col).strip() for col in df.columns]
    if "行号" in df.columns:
        df = df[df["行号"].notna()]
    return df


def normalize_goods_key(goods_no: object) -> str:
    key, _kind = normalize_barcode(None, goods_no)
    return key


def normalize_sales_key(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]
    return text


def build_supplier_map(archive: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    data = archive.copy()
    data["归一条码主键"] = data["货号"].map(normalize_goods_key)
    data["供应商名称"] = data["供应商名称"].fillna("").astype(str).str.strip()
    usable = data[(data["归一条码主键"] != "") & (data["供应商名称"] != "")]

    supplier_counts = (
        usable.groupby("归一条码主键")["供应商名称"]
        .nunique()
        .reset_index(name="供应商数")
    )
    conflicts = supplier_counts[supplier_counts["供应商数"] > 1]

    # ERP 商品档案当前一 SKU 一供应商，若出现重复，先取第一条并在 dry-run 报冲突。
    supplier_map = (
        usable.sort_values(["归一条码主键", "供应商名称"])
        .drop_duplicates("归一条码主键", keep="first")
        [["归一条码主键", "供应商名称", "类别名称", "采购周期", "停购日期"]]
    )
    return supplier_map, conflicts


def run() -> dict:
    started_at = datetime.now(timezone.utc)
    files = {
        "supplier_archive": SUPPLIER_ARCHIVE,
        "supplier_sales": SUPPLIER_SALES,
        "supplier_master": SUPPLIER_MASTER,
        "merged_sales": MERGED_SALES,
    }
    missing = [name for name, path in files.items() if not path.exists()]
    if missing:
        raise FileNotFoundError(f"缺失输入: {missing}")

    sha_before = {name: compute_sha256(path) for name, path in files.items()}

    archive = read_excel_table(SUPPLIER_ARCHIVE, {"货号", "供应商名称", "进货价", "采购周期", "停购日期"})
    # 仅验证可读和记录行数；dry-run 不使用采购额绝对值输出。
    supplier_sales = read_excel_table(SUPPLIER_SALES, {"主供应商名称", "货号", "进货金额", "类别名称"})
    supplier_master = read_excel_table(SUPPLIER_MASTER, {"编码", "名称", "区域", "采购间隔", "送货天数"})
    sales = pd.read_excel(MERGED_SALES)
    sales.columns = [str(col).strip() for col in sales.columns]
    if "商品条码" not in sales.columns:
        raise ValueError("销售统计汇总缺少 商品条码 列")

    supplier_map, conflicts = build_supplier_map(archive)
    sales["归一条码主键"] = sales["商品条码"].map(normalize_sales_key)
    joined = sales.merge(supplier_map, how="left", on="归一条码主键", suffixes=("", "_供应商档案"))

    existing_supplier = sales["主供应商"].fillna("").astype(str).str.strip() if "主供应商" in sales.columns else pd.Series([""] * len(sales))
    new_supplier = joined["供应商名称"].fillna("").astype(str).str.strip()
    fillable = (existing_supplier == "") & (new_supplier != "")
    total = len(sales)
    fill_rate = float(fillable.sum() / total) if total else 0.0
    conflict_rate = float(len(conflicts) / len(supplier_map)) if len(supplier_map) else 0.0
    unmatched = joined[new_supplier == ""]
    anomaly_rate = float(len(unmatched) / total) if total else 0.0
    gate = "PASS" if anomaly_rate <= 0.15 else "BLOCK"

    capability = build_supplier_capability(archive)

    preview = joined.loc[:, ["商品条码", "商品名称", "主供应商", "供应商名称"]].head(30).copy()
    preview["商品条码"] = preview["商品条码"].map(mask_key)
    preview = preview.rename(columns={"商品条码": "商品条码_掩码", "供应商名称": "拟填主供应商"})

    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    preview.to_csv(PREVIEW_DIR / "supplier_join_preview.csv", index=False, encoding="utf-8-sig")
    conflicts.head(50).to_csv(PREVIEW_DIR / "supplier_conflicts_top50.csv", index=False, encoding="utf-8-sig")
    capability.head(200).to_csv(PREVIEW_DIR / "supplier_capability_tableB_preview.csv", index=False, encoding="utf-8-sig")

    sha_after = {name: compute_sha256(path) for name, path in files.items()}
    sha_ok = sha_before == sha_after
    summary = {
        "task": "CODEX-2026-06-20-01",
        "mode": "dry-run",
        "started_at": started_at.isoformat(),
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "inputs": {name: str(path) for name, path in files.items()},
        "sha256_unchanged": sha_ok,
        "row_counts": {
            "supplier_archive": int(len(archive)),
            "supplier_sales": int(len(supplier_sales)),
            "supplier_master": int(len(supplier_master)),
            "merged_sales": int(len(sales)),
            "supplier_map": int(len(supplier_map)),
            "capability_rows_preview_total": int(len(capability)),
        },
        "metrics": {
            "main_supplier_fillable_rows": int(fillable.sum()),
            "main_supplier_fillable_rate": round(fill_rate, 4),
            "one_sku_multi_supplier_keys": int(len(conflicts)),
            "one_sku_multi_supplier_rate": round(conflict_rate, 4),
            "unmatched_sales_rows": int(len(unmatched)),
            "unmatched_sales_rate": round(anomaly_rate, 4),
            "gate": gate,
        },
        "outputs": [
            str(PREVIEW_DIR / "supplier_join_preview.csv"),
            str(PREVIEW_DIR / "supplier_conflicts_top50.csv"),
            str(PREVIEW_DIR / "supplier_capability_tableB_preview.csv"),
        ],
        "notes": [
            "dry-run 未写正式清洗输出。",
            "能力库预览只输出价格带/采购周期带/停购状态/SKU数，不输出采购额绝对值。",
            "商品条码在预览中已掩码。",
        ],
    }
    with open(PREVIEW_DIR / "supplier_dryrun_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(json.dumps(summary["metrics"], ensure_ascii=False, indent=2))
    return summary


if __name__ == "__main__":
    run()
