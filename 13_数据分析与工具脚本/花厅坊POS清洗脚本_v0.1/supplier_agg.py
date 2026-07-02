"""
供应商能力库 dry-run 聚合。

只输出分级与计数，不输出采购额绝对值。
"""

from __future__ import annotations

import pandas as pd


def price_band(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.notna().sum() < 3:
        return pd.Series(["未知"] * len(series), index=series.index)
    q1 = numeric.quantile(0.33)
    q2 = numeric.quantile(0.66)

    def classify(value):
        if pd.isna(value):
            return "未知"
        if value <= q1:
            return "低"
        if value <= q2:
            return "中"
        return "高"

    return numeric.map(classify)


def cycle_band(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")

    def classify(value):
        if pd.isna(value) or value <= 0:
            return "未知"
        if value <= 3:
            return "高频"
        if value <= 7:
            return "周配"
        if value <= 15:
            return "半月配"
        return "低频"

    return numeric.map(classify)


def discontinued_flag(series: pd.Series) -> pd.Series:
    text = series.fillna("").astype(str).str.strip()
    return text.map(lambda value: "停购" if value and value.lower() != "nan" else "正常")


def build_supplier_capability(archive: pd.DataFrame) -> pd.DataFrame:
    required = ["供应商名称", "类别名称", "进货价", "采购周期", "停购日期"]
    missing = [col for col in required if col not in archive.columns]
    if missing:
        raise ValueError(f"供应商能力库缺少字段: {missing}")

    data = archive.copy()
    data["价格带"] = price_band(data["进货价"])
    data["采购周期带"] = cycle_band(data["采购周期"])
    data["停购状态"] = discontinued_flag(data["停购日期"])
    data["供应商名称"] = data["供应商名称"].fillna("").astype(str).str.strip()
    data["类别名称"] = data["类别名称"].fillna("未分类").astype(str).str.strip()
    data = data[data["供应商名称"] != ""]

    grouped = (
        data.groupby(["供应商名称", "类别名称", "价格带", "停购状态", "采购周期带"], dropna=False)
        .size()
        .reset_index(name="SKU数")
        .sort_values(["供应商名称", "SKU数"], ascending=[True, False])
    )
    return grouped

