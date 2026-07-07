# -*- coding: utf-8 -*-
"""category_pos_cleaner v0.3 最小单测（Phase-Z 实验件）。
覆盖四块：字段识别 / 名称标准化 / 排除词否决 / 评分与置信。
运行：python3 -m unittest test_category_pos_cleaner -v
"""
import importlib.util
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "cleaner_v03", os.path.join(HERE, "category_pos_cleaner_v0.3.py"))
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


def rule(**kw):
    base = dict(code="T01-01", L1="食品", L2="休闲食品", L3="薯片膨化", L4="薯片",
                keywords=["薯片"], aliases={}, excludes=[], priority=50,
                conf_rules=[(2, "high"), (1, "mid")], review=False, extra={})
    base.update(kw)
    return base


class TestFieldDetect(unittest.TestCase):
    def test_detect_standard_headers(self):
        fmap = m.detect_fields(["货号", "条码", "商品名称", "规格", "原POS分类", "售价"])
        self.assertEqual(fmap["name"], "商品名称")
        self.assertEqual(fmap["barcode"], "条码")
        self.assertEqual(fmap["old_cat"], "原POS分类")

    def test_missing_name_raises(self):
        with self.assertRaises(ValueError):
            m.detect_fields(["条码", "售价"])


class TestNormalize(unittest.TestCase):
    def test_fullwidth_and_spaces(self):
        self.assertEqual(m.normalize_name("品客薯片洋葱味１１０ｇ"), "品客薯片洋葱味")
        self.assertEqual(m.normalize_name("  三得利乌龙茶  "), "三得利乌龙茶")

    def test_spec_stripped(self):
        self.assertEqual(m.normalize_name("康师傅红烧牛肉面105g*5"), "康师傅红烧牛肉面")
        self.assertEqual(m.normalize_name("蒙牛纯牛奶２５０ｍｌ×１６"), "蒙牛纯牛奶")


class TestExclude(unittest.TestCase):
    def test_exclude_vetoes_hit(self):
        r = rule(code="D01-01", L4="常温纯奶", keywords=["牛奶"], excludes=["牛奶糖", "奶茶"])
        cands = m.pass_strict("旺仔牛奶糖", [r], {})
        self.assertEqual(len(cands), 1)  # 命中
        alive, killed = m.veto("旺仔牛奶糖", cands)
        self.assertEqual(alive, [])      # 但被否决
        self.assertEqual(killed, 1)

    def test_non_excluded_survives(self):
        r = rule(code="D01-01", L4="常温纯奶", keywords=["牛奶"], excludes=["牛奶糖"])
        alive, killed = m.veto("伊利纯牛奶", m.pass_strict("伊利纯牛奶", [r], {}))
        self.assertEqual(len(alive), 1)
        self.assertEqual(killed, 0)


class TestScoringConfidence(unittest.TestCase):
    def test_priority_then_score(self):
        low = rule(code="T03-03", L4="其他饼干", keywords=["饼干"], priority=30)
        high = rule(code="T03-01", L4="夹心饼干", keywords=["夹心饼", "饼干"], priority=60)
        cands = m.pass_strict("奥利奥夹心饼干", [low, high], {})
        cands, _ = m.veto("奥利奥夹心饼干", cands)
        winner, hits, how, score, tie = m.adjudicate(cands)
        self.assertEqual(winner["code"], "T03-01")
        self.assertFalse(tie)
        self.assertEqual(score, len("夹心饼") + len("饼干"))  # 命中词总长

    def test_confidence_levels(self):
        cr = m.parse_conf_rule("kw_hit>=1:mid;kw_hit>=2:high")
        self.assertEqual(m.confidence_of(2, cr), "high")
        self.assertEqual(m.confidence_of(1, cr), "mid")
        self.assertEqual(m.confidence_of(1, cr, forced_low=True), "low")


if __name__ == "__main__":
    unittest.main()
