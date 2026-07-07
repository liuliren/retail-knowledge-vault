#!/usr/bin/env python3
"""barcode_gap_classifier.py 单测 —— 全部用构造的小型数据,不依赖真实客户csv。"""
import os
import sys

import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from barcode_gap_classifier import (  # noqa: E402
    classify_gaps, ean13_valid, j1_structural_hit, load_store_frames,
)


def _sales(rows):
    """rows: list of (分店,日期,柜组,条码) → DataFrame,补齐其余占位列。"""
    df = pd.DataFrame(rows, columns=["分店", "日期", "柜组", "条码"])
    df["日期"] = pd.to_datetime(df["日期"])
    for col in ("品名", "单位", "规格", "现进价", "末售价", "销售量", "销售额", "销进额"):
        df[col] = ""
    return df


def _registry(codes, store="顺景店"):
    return pd.DataFrame({"分店": [store] * len(codes), "货号": range(len(codes)), "条码": codes})


# ---------------------------------------------------------------------------
# 1. EAN-13 校验位算法本身
# ---------------------------------------------------------------------------

def test_ean13_valid_true_for_real_checksum():
    # 6923309766993: 逐位校验位算法应通过(真实商品条码结构)
    assert ean13_valid("6923309766993") is True


def test_ean13_valid_false_for_bad_checksum():
    # 改动最后一位破坏校验位
    assert ean13_valid("6923309766990") is False


def test_ean13_valid_false_for_non_13_or_non_digit():
    assert ean13_valid("1234567") is False
    assert ean13_valid("abcdefghijklm") is False


# ---------------------------------------------------------------------------
# 2. J1 结构判(码长/前缀)
# ---------------------------------------------------------------------------

def test_j1_short_code_hits():
    assert j1_structural_hit("1100342") is True   # 长度7 <=8


def test_j1_prefix_2x_hits():
    assert j1_structural_hit("2010000012345") is True  # 13位,前缀20


def test_j1_normal_ean_does_not_hit():
    assert j1_structural_hit("6923309766993") is False  # 13位但前缀69,非20-29区间


# ---------------------------------------------------------------------------
# 3. H1 分类: 称重柜组 + 结构命中 → high;结构命中但非称重柜组 → medium
# ---------------------------------------------------------------------------

def test_h1_weighing_counter_high_confidence():
    sales = _sales([
        ("顺景店", "2026-05-01", "散装柜", "2010000012345"),  # 13位,前缀20 → J1结构命中
        ("顺景店", "2026-05-03", "散装柜", "2010000012345"),
        ("顺景店", "2026-04-10", "粮油柜", "6923309766993"),  # 已在册对照码(不缺口)
    ])
    registry = _registry(["6923309766993"])
    result = classify_gaps(sales, registry)
    row = result[result["条码"] == "2010000012345"].iloc[0]
    assert row["分类"] == "H1"
    assert row["置信度"] == "high"


def test_h1_structural_but_wrong_counter_medium_confidence():
    sales = _sales([
        ("顺景店", "2026-05-01", "文体柜", "1100342"),  # 短码但柜组不在称重白名单
        ("顺景店", "2026-04-10", "顺景店", "6923309766993"),
    ])
    registry = _registry(["6923309766993"])
    result = classify_gaps(sales, registry)
    row = result[result["条码"] == "1100342"].iloc[0]
    assert row["分类"] == "H1"
    assert row["置信度"] == "medium"


# ---------------------------------------------------------------------------
# 4. H2 分类: 外租候选柜组 + 覆盖率倒挂 → high
# ---------------------------------------------------------------------------

def test_h2_nonfood_lease_counter_coverage_inversion():
    # 家居用品柜: 3个条码都不在registry里(覆盖率0%) → 应显著低于全店均值
    sales = _sales([
        ("顺景店", "2026-05-01", "家居用品柜", "6958299381888"),
        ("顺景店", "2026-05-02", "家居用品柜", "6958299381889"),
        ("顺景店", "2026-05-03", "家居用品柜", "6958299381890"),
        # 其余柜组条码在registry中大量命中,拉高全店均值覆盖率
        ("顺景店", "2026-04-01", "猪肉柜", "6900000000001"),
        ("顺景店", "2026-04-01", "猪肉柜", "6900000000002"),
        ("顺景店", "2026-04-01", "猪肉柜", "6900000000003"),
    ])
    registry = _registry(["6900000000001", "6900000000002", "6900000000003"])
    result = classify_gaps(sales, registry)
    row = result[result["条码"] == "6958299381888"].iloc[0]
    assert row["分类"] == "H2"
    assert row["置信度"] == "high"


# ---------------------------------------------------------------------------
# 5. H3 分类: 残差走J4(EAN合法性 + 销售日期分布)
# ---------------------------------------------------------------------------

def test_h3_valid_ean_late_window_suspected_new_sku():
    # 窗口 2026-04-01 ~ 2026-06-30(91天),首销落在末15天内 → 疑似新品未建档
    sales = _sales([
        ("顺景店", "2026-04-01", "粮油柜", "6900000000009"),  # 撑开窗口起点(在册对照码)
        ("顺景店", "2026-06-25", "粮油柜", "6923309766993"),  # 首销/末销都在窗口末15天内
    ])
    registry = _registry(["6900000000009"])
    result = classify_gaps(sales, registry)
    row = result[result["条码"] == "6923309766993"].iloc[0]
    assert row["分类"] == "H3"
    assert "新品" in row["子类型"]


def test_h3_valid_ean_early_window_suspected_delisted():
    # 首销和末销都在窗口早15天内 → 疑似已清档(H0口径)
    sales = _sales([
        ("顺景店", "2026-04-02", "粮油柜", "6923309766993"),
        ("顺景店", "2026-04-05", "粮油柜", "6923309766993"),
        ("顺景店", "2026-06-30", "粮油柜", "6900000000009"),  # 撑开窗口终点(在册对照码)
    ])
    registry = _registry(["6900000000009"])
    result = classify_gaps(sales, registry)
    row = result[result["条码"] == "6923309766993"].iloc[0]
    assert row["分类"] == "H3"
    assert "清档" in row["子类型"]


def test_h3_invalid_ean_low_confidence():
    sales = _sales([
        ("顺景店", "2026-05-01", "粮油柜", "6923309766990"),  # 校验位错误
    ])
    registry = _registry([])
    result = classify_gaps(sales, registry)
    row = result[result["条码"] == "6923309766990"].iloc[0]
    assert row["分类"] == "H3"
    assert row["置信度"] == "low"


# ---------------------------------------------------------------------------
# 6. MECE 完整性 + 无缺口场景
# ---------------------------------------------------------------------------

def test_no_gap_returns_empty_frame_with_expected_columns():
    sales = _sales([("顺景店", "2026-05-01", "粮油柜", "6923309766993")])
    registry = _registry(["6923309766993"])
    result = classify_gaps(sales, registry)
    assert len(result) == 0
    assert "条码" in result.columns and "分类" in result.columns


def test_every_gap_code_classified_exactly_once():
    sales = _sales([
        ("顺景店", "2026-05-01", "散装柜", "26102909454"),
        ("顺景店", "2026-05-01", "家居用品柜", "6958299381888"),
        ("顺景店", "2026-05-01", "粮油柜", "6923309766993"),
        ("顺景店", "2026-04-01", "粮油柜", "6900000000009"),
    ])
    registry = _registry(["6900000000009"])
    result = classify_gaps(sales, registry)
    assert result["条码"].nunique() == len(result)  # 一码一行,无重复归类
    assert set(result["分类"]).issubset({"H1", "H2", "H3"})


# ---------------------------------------------------------------------------
# 7. load_store_frames 分店子串过滤
# ---------------------------------------------------------------------------

def test_load_store_frames_filters_by_substring(tmp_path):
    master_csv = tmp_path / "master.csv"
    registry_csv = tmp_path / "registry.csv"
    _sales([
        ("顺景店", "2026-05-01", "粮油柜", "6923309766993"),
        ("富城店", "2026-05-01", "粮油柜", "6900000000009"),
    ]).to_csv(master_csv, index=False)
    _registry(["6923309766993"]).to_csv(registry_csv, index=False)

    s, r = load_store_frames(str(master_csv), str(registry_csv), "顺景")
    assert set(s["分店"].unique()) == {"顺景店"}
    assert len(s) == 1


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
