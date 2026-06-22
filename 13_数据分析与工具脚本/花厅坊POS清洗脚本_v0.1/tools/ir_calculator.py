"""T-07 IR calculator."""

from __future__ import annotations

import pandas as pd


def calculate_ir(margin_rate: pd.Series, ito: pd.Series) -> pd.Series:
    margin = pd.to_numeric(margin_rate, errors="coerce")
    turnover = pd.to_numeric(ito, errors="coerce")
    return 12 * (1 - margin) / turnover


def apply_ir(df: pd.DataFrame, margin_col: str = "毛利率", ito_col: str = "ITO") -> tuple[pd.DataFrame, dict]:
    result = df.copy()
    if margin_col not in result.columns:
        return result, {"status": "blocked_缺毛利率", "coverage": 0.0}
    if ito_col not in result.columns:
        result["IR"] = "blocked_缺ITO"
        return result, {"status": "blocked_缺ITO", "coverage": 0.0}
    valid = pd.to_numeric(result[ito_col], errors="coerce") > 0
    result.loc[valid, "IR"] = calculate_ir(result.loc[valid, margin_col], result.loc[valid, ito_col])
    result.loc[~valid, "IR"] = "blocked_缺ITO"
    return result, {"status": "ok", "coverage": round(float(valid.mean()), 4)}

