"""T-01/T-02 ABC classifier.

口径来源：注册表 §3.1（active 2026-06-22，ABC-Rule-Confirm-001 / ABC-Rule-Text-Correction-001）。
- sales_contribution_class（销售额累计贡献）：销售额降序累计占比 ≤60%=A / 60-90%=B / >90%=C
- gross_profit_contribution_class（毛利【额】累计贡献）：毛利额降序累计占比 ≤60%=甲 / 60-90%=乙 / >90%=丙
  ⚠ 毛利维按「毛利额累计贡献」分档，**不是毛利率模型**；甲/乙/丙 ≠ 毛利率高/中/低。
裁决为完整九宫格；「观察品」已废止为最终输出（未知组合返回 invalid_combination）。
"""

from __future__ import annotations

import pandas as pd


def classify_cumulative(values: pd.Series, labels: tuple[str, str, str]) -> pd.Series:
    numeric = pd.to_numeric(values, errors="coerce").fillna(0)
    total = numeric.sum()
    if total <= 0:
        return pd.Series([labels[2]] * len(values), index=values.index)
    ordered = numeric.sort_values(ascending=False)
    cumulative = ordered.cumsum() / total
    result = pd.Series(index=values.index, dtype="object")
    result.loc[cumulative[cumulative <= 0.60].index] = labels[0]
    result.loc[cumulative[(cumulative > 0.60) & (cumulative <= 0.90)].index] = labels[1]
    result.loc[cumulative[cumulative > 0.90].index] = labels[2]
    return result.fillna(labels[2])


# 九宫格裁决映射（注册表 §3.1 active）。键 = (销售额贡献 A/B/C, 毛利额贡献 甲/乙/丙)。
NINE_GRID: dict[tuple[str, str], str] = {
    ("A", "甲"): "核心引擎",
    ("A", "乙"): "核心引擎",
    ("A", "丙"): "流量品",
    ("B", "甲"): "潜力利润品",
    ("B", "乙"): "常规品",
    ("B", "丙"): "流量补充·控利",
    ("C", "甲"): "利润品",
    ("C", "乙"): "长尾利润·待裁决",
    ("C", "丙"): "双低",
}

# C+乙 默认需人工复核（中间状态，非最终裁决）。
_REVIEW_REASON_C_YI = (
    "长尾利润·待裁决：卖得少但仍有毛利贡献，需核查非显性需求、节令、陈列、"
    "缺货与数据异常后再定留汰。"
)


def decide_identity(
    sales_contribution_class: str, gross_profit_contribution_class: str
) -> str:
    """九宫格最终裁决。

    未知组合返回 'invalid_combination'（不再 fallback 为「观察品」）。
    """
    return NINE_GRID.get(
        (sales_contribution_class, gross_profit_contribution_class),
        "invalid_combination",
    )


def decide_review(
    sales_contribution_class: str, gross_profit_contribution_class: str
) -> tuple[bool, str]:
    """返回 (needs_review, review_reason)。仅 C+乙 默认需复核，其余 8 格不需。"""
    if (sales_contribution_class, gross_profit_contribution_class) == ("C", "乙"):
        return True, _REVIEW_REASON_C_YI
    return False, ""


def assign_gross_margin_rate_tier(
    df: pd.DataFrame,
    rate_col: str = "毛利率",
    cat_col: str = "类别名称",
    min_samples: int = 20,
) -> pd.Series:
    """毛利率分层 high/mid/low/unavailable（§3.1.1·方案B）。

    优先小类 P75/P25；小类有效样本 < min_samples 时降级全店 P75/P25；
    毛利率缺失/不可计算 → unavailable。
    """
    rate = pd.to_numeric(df[rate_col], errors="coerce") if rate_col in df.columns else pd.Series(pd.NA, index=df.index)
    store_valid = rate.dropna()
    store_p75 = store_valid.quantile(0.75) if len(store_valid) else float("nan")
    store_p25 = store_valid.quantile(0.25) if len(store_valid) else float("nan")
    if cat_col in df.columns:
        grp = rate.groupby(df[cat_col])
        cnt = grp.transform(lambda s: s.notna().sum())
        cat_p75 = grp.transform(lambda s: s.quantile(0.75))
        cat_p25 = grp.transform(lambda s: s.quantile(0.25))
    else:
        cnt = pd.Series(0, index=df.index)
        cat_p75 = pd.Series(float("nan"), index=df.index)
        cat_p25 = pd.Series(float("nan"), index=df.index)
    use_cat = cnt >= min_samples
    p75 = cat_p75.where(use_cat, store_p75)
    p25 = cat_p25.where(use_cat, store_p25)
    tier = pd.Series("unavailable", index=df.index, dtype="object")
    valid = rate.notna() & p75.notna()
    tier[valid & (rate >= p75)] = "high"
    tier[valid & (rate <= p25)] = "low"
    tier[valid & (rate > p25) & (rate < p75)] = "mid"
    return tier


def assign_goldmine(
    df: pd.DataFrame,
    sales_abc_col: str = "销额ABC",
    tier_col: str = "gross_margin_rate_tier",
    shortage_col: str = "缺货标记",
    new_col: str = "新品标记",
) -> tuple[pd.Series, pd.Series]:
    """C 行毛利率复核闸 → (goldmine_candidate bool, goldmine_reason str)（§3.1.1）。

    candidate=True ⇔ 销额C + tier=high + 非缺货 + 非新品保护（促销缺字段不自动排除，记入 reason）。
    goldmine_candidate 是复核字段，非最终裁决标签。
    """
    n = len(df)
    sales = df[sales_abc_col].astype(str) if sales_abc_col in df.columns else pd.Series("", index=df.index)
    tier = df[tier_col].astype(str) if tier_col in df.columns else pd.Series("unavailable", index=df.index)
    shortage = df[shortage_col].fillna(False).astype(bool) if shortage_col in df.columns else pd.Series(False, index=df.index)
    newp = df[new_col].fillna(False).astype(bool) if new_col in df.columns else pd.Series(False, index=df.index)
    # §3.1.2/§3.1.3 三闸（缺列时 pass-through，保旧测试兼容）
    scope = df["data_quality_scope_status"].astype(str) if "data_quality_scope_status" in df.columns else pd.Series("eligible", index=df.index)
    cost_ok = df["cost_reliable"].fillna(True).astype(bool) if "cost_reliable" in df.columns else pd.Series(True, index=df.index)
    sold_ok = df["recently_sold"].fillna(True).astype(bool) if "recently_sold" in df.columns else pd.Series(True, index=df.index)
    eligible = scope.eq("eligible")
    is_c = sales.eq("C")
    cand = eligible & is_c & tier.eq("high") & cost_ok & sold_ok & ~shortage & ~newp
    reason = pd.Series("", index=df.index, dtype="object")
    # 原因（优先级：scope > 非C > tier > 成本 > 死货 > 缺货/新品 > 命中）
    reason[~is_c] = "非C行"
    reason[is_c & tier.eq("unavailable")] = "毛利率不可用/数据异常"
    reason[is_c & ~tier.eq("high") & ~tier.eq("unavailable")] = "毛利率未达阈值"
    reason[is_c & tier.eq("high") & ~cost_ok] = "成本/毛利率不可靠，进cost_missing_review_pool"
    reason[is_c & tier.eq("high") & cost_ok & ~sold_ok] = "90天销量<4或库龄>90，进dead_stock_review_pool"
    reason[is_c & tier.eq("high") & cost_ok & sold_ok & shortage] = "缺货排除"
    reason[is_c & tier.eq("high") & cost_ok & sold_ok & ~shortage & newp] = "新品保护排除"
    reason[~eligible & (scope == "client_specific_excluded")] = "当前客户/门店数据质量范围排除(client_specific_excluded)"
    reason[~eligible & (scope == "cost_unreliable")] = "成本不可信(数据质量范围外)"
    reason[cand] = "数据质量eligible；销售贡献C；毛利率达P75；成本可信；90天销量≥4(动销)；未触发缺货/新品；促销字段缺失需人工复核"
    # Fix-002：库龄>90 不再排除金矿，仅在候选 reason 标注老库存风险
    if "old_inventory_risk" in df.columns:
        oir = df["old_inventory_risk"].fillna(False).astype(bool)
        reason[cand & oir] = reason[cand & oir].astype(str) + "；⚠老库存风险(库龄>90)需关注清库/缩面/补货"
    return cand, reason


def assign_cost_reliable(
    df: pd.DataFrame, cost_col: str = "销售成本", rate_col: str = "毛利率"
) -> pd.Series:
    """成本/毛利率是否可信（§3.1.2）。false ⇔ 成本≤0/缺 或 毛利率缺/不可算/>0.95。"""
    cost = pd.to_numeric(df.get(cost_col), errors="coerce") if cost_col in df.columns else pd.Series(float("nan"), index=df.index)
    rate = pd.to_numeric(df.get(rate_col), errors="coerce") if rate_col in df.columns else pd.Series(float("nan"), index=df.index)
    reliable = (cost > 0) & rate.notna() & (rate <= 0.95)
    return reliable.fillna(False).astype(bool)


def assign_recently_sold(
    df: pd.DataFrame, qty_col: str = "销量", min_qty: int = 4,
) -> pd.Series:
    """近90天有效动销（§3.1.2·Fix-002 销量优先）。true ⇔ 90天销量≥min_qty。

    Fix-002：去掉「库龄≤90」一票否决（库龄≠动销，误杀老库存但仍卖的货）；
    库龄改由 assign_old_inventory_risk 作风险标签。
    """
    qty = pd.to_numeric(df.get(qty_col), errors="coerce") if qty_col in df.columns else pd.Series(float("nan"), index=df.index)
    return (qty >= min_qty).fillna(False).astype(bool)


def assign_old_inventory_risk(
    df: pd.DataFrame, age_col: str = "库龄天数", max_age: int = 90,
) -> pd.Series:
    """老库存风险标签（§3.1.2·Fix-002）。true ⇔ 库龄>max_age。

    **仅风险标签,不排除 goldmine_candidate**;供人工复核提示清库/缩面/补货。
    """
    age = pd.to_numeric(df.get(age_col), errors="coerce") if age_col in df.columns else pd.Series(float("nan"), index=df.index)
    return (age > max_age).fillna(False).astype(bool)


def assign_data_quality_scope(
    df: pd.DataFrame, client_excluded_col: str = "client_excluded",
    cost_reliable_col: str = "cost_reliable",
) -> tuple[pd.Series, pd.Series]:
    """§3.1.3 数据质量范围筛选 → (data_quality_scope_status, reason)。

    优先级：client_specific_excluded(当前客户配置,如花厅坊生鲜) > cost_unreliable(成本不可信)
    > eligible。requires_manual_scope_review 预留人工(本函数不自动判)。
    **客户级配置驱动,不硬编码品类永久排除。**
    """
    n = len(df)
    client_ex = df[client_excluded_col].fillna(False).astype(bool) if client_excluded_col in df.columns else pd.Series(False, index=df.index)
    cost_ok = df[cost_reliable_col].fillna(False).astype(bool) if cost_reliable_col in df.columns else assign_cost_reliable(df)
    status = pd.Series("eligible", index=df.index, dtype="object")
    reason = pd.Series("成本/毛利率可信，纳入毛利率型判断", index=df.index, dtype="object")
    status[~cost_ok] = "cost_unreliable"
    reason[~cost_ok] = "成本缺失/≤0或毛利率不可算/>0.95"
    status[client_ex] = "client_specific_excluded"
    reason[client_ex] = "当前客户/门店数据质量范围排除（如花厅坊生鲜成本口径异常）·非通用永久规则"
    return status, reason


def assign_exclusion_pool(df: pd.DataFrame) -> pd.Series:
    """排除池（§3.1.2/§3.1.3）。优先级 client_specific_excluded>cost_missing>dead_stock>none。"""
    scope = df.get("data_quality_scope_status", pd.Series("eligible", index=df.index)).astype(str)
    cost_ok = df.get("cost_reliable", pd.Series(True, index=df.index)).fillna(False).astype(bool)
    sold_ok = df.get("recently_sold", pd.Series(True, index=df.index)).fillna(False).astype(bool)
    pool = pd.Series("none", index=df.index, dtype="object")
    pool[(scope == "eligible") & cost_ok & ~sold_ok] = "dead_stock"
    pool[(scope == "eligible") & ~cost_ok] = "cost_missing"
    pool[scope == "cost_unreliable"] = "cost_missing"
    pool[scope == "requires_manual_scope_review"] = "requires_manual_scope_review"
    pool[scope == "client_specific_excluded"] = "client_specific_excluded"
    return pool


def apply_abc(
    df: pd.DataFrame, sales_col: str = "销售金额", profit_col: str = "毛利额"
) -> pd.DataFrame:
    if sales_col not in df.columns:
        raise ValueError(f"缺少字段: {sales_col}")
    result = df.copy()
    if profit_col not in result.columns:
        # 毛利额缺失时由 销售额 × 毛利率 推算【毛利额】本身；分档仍按毛利额贡献，非按毛利率。
        if "毛利率" not in result.columns:
            raise ValueError(f"缺少字段: {profit_col}，且无法用 毛利率 推算")
        result[profit_col] = pd.to_numeric(result[sales_col], errors="coerce") * pd.to_numeric(
            result["毛利率"], errors="coerce"
        )
    # 销售额累计贡献分档 A/B/C
    result["销额ABC"] = classify_cumulative(result[sales_col], ("A", "B", "C"))
    # 毛利【额】累计贡献分档 甲/乙/丙（非毛利率）
    result["毛利ABC"] = classify_cumulative(result[profit_col], ("甲", "乙", "丙"))
    result["身份"] = [
        decide_identity(s, p) for s, p in zip(result["销额ABC"], result["毛利ABC"])
    ]
    reviews = [decide_review(s, p) for s, p in zip(result["销额ABC"], result["毛利ABC"])]
    result["需复核"] = [r[0] for r in reviews]
    result["复核原因"] = [r[1] for r in reviews]
    return result
