"""T-09/T-10 safety stock and age grading."""

from __future__ import annotations

import pandas as pd


def classify_age(days) -> str:
    value = pd.to_numeric(pd.Series([days]), errors="coerce").iloc[0]
    if pd.isna(value):
        return "blocked_缺库龄"
    if value <= 30:
        return "正常"
    if value <= 60:
        return "预警"
    if value <= 90:
        return "滞销"
    return "重滞"


def apply_safety_stock(
    df: pd.DataFrame,
    daily_sales_col: str = "日均销量",
    inventory_col: str = "库存即时快照",
    abc_col: str = "销额ABC",
    arrival_days: float = 7.0,
    age_col: str = "库龄天数",
) -> tuple[pd.DataFrame, dict]:
    result = df.copy()
    notes = []
    if daily_sales_col not in result.columns:
        notes.append("缺日均销量，若存在统计期间起/止与销售数量则用期间销量推算")
        if {"统计期间起", "统计期间止", "销售数量"}.issubset(result.columns):
            start = pd.to_datetime(result["统计期间起"], errors="coerce")
            end = pd.to_datetime(result["统计期间止"], errors="coerce")
            days = (end - start).dt.days + 1
            result[daily_sales_col] = pd.to_numeric(result["销售数量"], errors="coerce") / days
        else:
            result[daily_sales_col] = pd.NA
    if inventory_col not in result.columns:
        result[inventory_col] = pd.NA

    is_a = result[abc_col].eq("A") if abc_col in result.columns else pd.Series([False] * len(result), index=result.index)
    daily = pd.to_numeric(result[daily_sales_col], errors="coerce")
    inventory = pd.to_numeric(result[inventory_col], errors="coerce")
    result["A类水位"] = pd.NA
    result.loc[is_a, "A类水位"] = daily[is_a] * arrival_days * 1.5
    result["补货信号"] = "非A类不计算"
    result.loc[is_a & inventory.notna() & result["A类水位"].notna(), "补货信号"] = (
        inventory[is_a & inventory.notna() & result["A类水位"].notna()]
        < pd.to_numeric(result.loc[is_a & inventory.notna() & result["A类水位"].notna(), "A类水位"], errors="coerce")
    ).map({True: "补货", False: "正常"})

    if age_col in result.columns:
        result["库龄级"] = result[age_col].map(classify_age)
        age_status = "ok"
    else:
        result["库龄级"] = "blocked_缺库龄"
        age_status = "blocked_缺库龄"

    result["卖太快"] = "blocked_缺售罄率或断货记录"
    coverage = round(float((is_a & daily.notna() & inventory.notna()).mean()), 4) if len(result) else 0.0
    return result, {
        "status": "ok",
        "arrival_days_default": arrival_days,
        "safety_stock_coverage": coverage,
        "age_status": age_status,
        "sell_through_status": "blocked_缺售罄率或断货记录",
        "notes": notes,
    }

