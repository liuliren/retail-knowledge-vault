#!/usr/bin/env python3
"""Minimal unit tests for P1-3 retail tools."""

import unittest

import pandas as pd

from abc_classifier import (
    NINE_GRID,
    apply_abc,
    assign_cost_reliable,
    assign_data_quality_scope,
    assign_goldmine,
    assign_gross_margin_rate_tier,
    assign_recently_sold,
    decide_identity,
    decide_review,
)
from ir_calculator import calculate_ir
from safety_stock import classify_age


# 九宫格预期裁决（注册表 §3.1 active）
NINE_GRID_EXPECTED = {
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


class RetailToolsTest(unittest.TestCase):
    def test_abc_identity(self):
        df = pd.DataFrame({"销售金额": [60, 30, 10], "毛利额": [30, 10, 60]})
        out = apply_abc(df)
        self.assertIn("销额ABC", out.columns)
        self.assertIn("毛利ABC", out.columns)
        self.assertIn("身份", out.columns)
        self.assertIn("需复核", out.columns)
        self.assertIn("复核原因", out.columns)

    def test_nine_grid_full_coverage(self):
        """9 格裁决必须全部覆盖且与 §3.1 一致。"""
        for (sales, profit), expected in NINE_GRID_EXPECTED.items():
            with self.subTest(cell=f"{sales}+{profit}"):
                self.assertEqual(decide_identity(sales, profit), expected)

    def test_no_observation_label(self):
        """废止「观察品」：9 格输出中不得出现。"""
        outputs = {decide_identity(s, p) for (s, p) in NINE_GRID_EXPECTED}
        self.assertNotIn("观察品", outputs)

    def test_unknown_combination_not_fallback_observation(self):
        """未知组合返回 invalid_combination，而非「观察品」。"""
        self.assertEqual(decide_identity("X", "甲"), "invalid_combination")
        self.assertEqual(decide_identity("A", "丁"), "invalid_combination")

    def test_c_yi_needs_review(self):
        """C+乙 必须 needs_review=True，其余格默认 False。"""
        needs, reason = decide_review("C", "乙")
        self.assertTrue(needs)
        self.assertIn("长尾利润·待裁决", reason)
        for (sales, profit) in NINE_GRID_EXPECTED:
            if (sales, profit) == ("C", "乙"):
                continue
            with self.subTest(cell=f"{sales}+{profit}"):
                self.assertFalse(decide_review(sales, profit)[0])

    def test_profit_dimension_uses_gross_profit_amount(self):
        """毛利维按毛利额累计贡献分档，不是毛利率：高销低毛利率但毛利额最大者应为甲。"""
        # SKU1 销额低但毛利额最高 → 毛利额贡献甲；若误用毛利率会判错。
        df = pd.DataFrame({"销售金额": [10, 30, 60], "毛利额": [60, 30, 10]})
        out = apply_abc(df).sort_index()
        self.assertEqual(out.loc[0, "毛利ABC"], "甲")  # 毛利额最大 → 甲
        self.assertEqual(NINE_GRID[("A", "甲")], "核心引擎")

    def test_ir_formula(self):
        result = calculate_ir(pd.Series([0.25]), pd.Series([4])).iloc[0]
        self.assertAlmostEqual(result, 2.25)

    def test_age_grade(self):
        self.assertEqual(classify_age(30), "正常")
        self.assertEqual(classify_age(60), "预警")
        self.assertEqual(classify_age(90), "滞销")
        self.assertEqual(classify_age(91), "重滞")


class GoldmineTest(unittest.TestCase):
    def _cat_df(self, n_per_cat=25):
        # 构造一个小类，毛利率有梯度，便于 P75/P25 分层
        rates = [i / 100 for i in range(n_per_cat)]  # 0.00..0.24
        return pd.DataFrame({
            "类别名称": ["膨化"] * n_per_cat,
            "毛利率": rates,
            "销额ABC": ["C"] * n_per_cat,
            "缺货标记": [False] * n_per_cat,
            "新品标记": [False] * n_per_cat,
        })

    def test_tier_category_p75(self):
        df = self._cat_df(25)  # 小类样本≥20 → 用小类 P75
        df["gross_margin_rate_tier"] = assign_gross_margin_rate_tier(df)
        # 最高毛利率行应 high，最低应 low
        self.assertEqual(df.sort_values("毛利率").iloc[-1]["gross_margin_rate_tier"], "high")
        self.assertEqual(df.sort_values("毛利率").iloc[0]["gross_margin_rate_tier"], "low")

    def test_tier_small_category_fallback(self):
        # 小类样本<20 → 降级全店分位（这里只验不报错且能产出非 unavailable）
        df = pd.DataFrame({
            "类别名称": ["A"] * 5 + ["B"] * 5,
            "毛利率": [0.1, 0.2, 0.3, 0.4, 0.5, 0.05, 0.15, 0.25, 0.35, 0.45],
            "销额ABC": ["C"] * 10, "缺货标记": [False] * 10, "新品标记": [False] * 10,
        })
        tier = assign_gross_margin_rate_tier(df, min_samples=20)
        self.assertIn("high", set(tier))

    def test_tier_unavailable_when_rate_missing(self):
        df = pd.DataFrame({"类别名称": ["x"], "毛利率": [None], "销额ABC": ["C"]})
        tier = assign_gross_margin_rate_tier(df)
        self.assertEqual(tier.iloc[0], "unavailable")

    def test_goldmine_c_high_no_exclusion_true(self):
        df = pd.DataFrame({"销额ABC": ["C"], "gross_margin_rate_tier": ["high"],
                           "缺货标记": [False], "新品标记": [False]})
        cand, _ = assign_goldmine(df)
        self.assertTrue(bool(cand.iloc[0]))

    def test_goldmine_non_c_false(self):
        for s in ("A", "B"):
            df = pd.DataFrame({"销额ABC": [s], "gross_margin_rate_tier": ["high"],
                               "缺货标记": [False], "新品标记": [False]})
            self.assertFalse(bool(assign_goldmine(df)[0].iloc[0]))

    def test_goldmine_mid_low_false(self):
        for t in ("mid", "low"):
            df = pd.DataFrame({"销额ABC": ["C"], "gross_margin_rate_tier": [t],
                               "缺货标记": [False], "新品标记": [False]})
            self.assertFalse(bool(assign_goldmine(df)[0].iloc[0]))

    def test_goldmine_shortage_excluded(self):
        df = pd.DataFrame({"销额ABC": ["C"], "gross_margin_rate_tier": ["high"],
                           "缺货标记": [True], "新品标记": [False]})
        cand, reason = assign_goldmine(df)
        self.assertFalse(bool(cand.iloc[0]))
        self.assertIn("缺货", reason.iloc[0])

    def test_goldmine_newproduct_excluded(self):
        df = pd.DataFrame({"销额ABC": ["C"], "gross_margin_rate_tier": ["high"],
                           "缺货标记": [False], "新品标记": [True]})
        self.assertFalse(bool(assign_goldmine(df)[0].iloc[0]))

    def test_goldmine_unavailable_false(self):
        df = pd.DataFrame({"销额ABC": ["C"], "gross_margin_rate_tier": ["unavailable"],
                           "缺货标记": [False], "新品标记": [False]})
        cand, reason = assign_goldmine(df)
        self.assertFalse(bool(cand.iloc[0]))
        self.assertIn("不可用", reason.iloc[0])


class ScopeAndTightenTest(unittest.TestCase):
    def _row(self, **kw):
        base = dict(销额ABC="C", gross_margin_rate_tier="high", 缺货标记=False, 新品标记=False,
                    cost_reliable=True, recently_sold=True,
                    data_quality_scope_status="eligible")
        base.update(kw)
        return pd.DataFrame([base])

    def test_full_eligible_candidate_true(self):
        self.assertTrue(bool(assign_goldmine(self._row())[0].iloc[0]))

    def test_client_specific_excluded_false(self):
        cand, reason = assign_goldmine(self._row(data_quality_scope_status="client_specific_excluded"))
        self.assertFalse(bool(cand.iloc[0]))
        self.assertIn("client_specific_excluded", reason.iloc[0])

    def test_cost_unreliable_scope_false(self):
        self.assertFalse(bool(assign_goldmine(self._row(data_quality_scope_status="cost_unreliable"))[0].iloc[0]))

    def test_cost_not_reliable_false(self):
        self.assertFalse(bool(assign_goldmine(self._row(cost_reliable=False))[0].iloc[0]))

    def test_not_recently_sold_false(self):
        self.assertFalse(bool(assign_goldmine(self._row(recently_sold=False))[0].iloc[0]))

    def test_cost_reliable_rule(self):
        df = pd.DataFrame({"销售成本": [10, 0, 5, 5], "毛利率": [0.3, 0.3, None, 0.99]})
        cr = assign_cost_reliable(df)
        self.assertEqual(list(cr), [True, False, False, False])  # 正常/成本0/毛利缺/毛利>0.95

    def test_recently_sold_rule(self):
        df = pd.DataFrame({"销量": [4, 3, 10, 10], "库龄天数": [30, 30, 90, 120]})
        rs = assign_recently_sold(df)
        self.assertEqual(list(rs), [True, False, True, False])  # ≥4&≤90 / 销量<4 / 边界90 / 库龄>90

    def test_scope_priority_client_over_cost(self):
        df = pd.DataFrame({"client_excluded": [True], "cost_reliable": [False]})
        status, _ = assign_data_quality_scope(df)
        self.assertEqual(status.iloc[0], "client_specific_excluded")  # 客户排除优先于成本

    def test_scope_eligible_when_clean(self):
        df = pd.DataFrame({"client_excluded": [False], "cost_reliable": [True]})
        status, _ = assign_data_quality_scope(df)
        self.assertEqual(status.iloc[0], "eligible")

    def test_fresh_not_universal_excluded(self):
        # 生鲜不靠品类名硬排除：同样是"水果"，client_excluded=False 时仍 eligible
        df = pd.DataFrame({"类别名称": ["水果"], "client_excluded": [False], "cost_reliable": [True]})
        status, _ = assign_data_quality_scope(df)
        self.assertEqual(status.iloc[0], "eligible")


if __name__ == "__main__":
    unittest.main()

