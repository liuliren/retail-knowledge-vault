"""SKU 属性提取算法 单元测试 v0.1.

运行：python -m unittest test_sku_extractor.py
或：  python test_sku_extractor.py

测试覆盖：
- 规格提取：单值 / 复合 / 大小写归一化 / 空输入 / 无规格
- 品牌提取：已知品牌 / 启发式 / 最长匹配 / 空输入
- 箱规提取：N*M / 无箱规 / 边界
- ground truth 验证：用 700 SKU 的真实数据验证整体准确率
"""
import csv
import os
import sys
import unittest

# 加入项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sku_extractor import (
    SpecExtractor,
    BrandExtractor,
    BoxPackExtractor,
    SKUAttributeExtractor,
    ExtractResult,
)


class TestSpecExtractor(unittest.TestCase):
    """规格提取器测试."""

    def setUp(self):
        self.ext = SpecExtractor()

    def test_simple_grams(self):
        r = self.ext.extract("Aji小龙虾味魔芋180g")
        self.assertEqual(r.value, "180g")
        self.assertGreaterEqual(r.confidence, 0.95)
        self.assertEqual(r.method, "rule_single")

    def test_simple_ml(self):
        r = self.ext.extract("可口可乐500ml")
        self.assertEqual(r.value, "500ml")
        self.assertGreaterEqual(r.confidence, 0.95)

    def test_decimal_liter(self):
        r = self.ext.extract("椰树椰汁1.25L")
        self.assertEqual(r.value, "1.25L")

    def test_chinese_unit(self):
        r = self.ext.extract("某某零食70克")
        self.assertEqual(r.value, "70克")

    def test_composite_spec(self):
        r = self.ext.extract("德芙夹心巧克力150g*3")
        self.assertEqual(r.method, "rule_composite")
        self.assertIn("150g", r.value)
        self.assertIn("3", r.value)

    def test_no_spec(self):
        r = self.ext.extract("彩虹糖果香乳酸菌味")
        self.assertEqual(r.value, "")
        self.assertEqual(r.confidence, 0.0)

    def test_empty_input(self):
        r = self.ext.extract("")
        self.assertFalse(bool(r))
        r = self.ext.extract(None)  # type: ignore
        self.assertFalse(bool(r))

    def test_position_confidence(self):
        # 规格在尾部 → 高置信度
        r1 = self.ext.extract("Aji小龙虾味魔芋180g")
        # 规格在中部 → 中置信度
        r2 = self.ext.extract("180g装零食包")
        self.assertGreater(r1.confidence, r2.confidence)


class TestBrandExtractor(unittest.TestCase):
    """品牌提取器测试."""

    def setUp(self):
        self.brands = {"雀巢", "可比克", "Calbee卡乐比", "三湘古镇", "无穷"}
        self.ext = BrandExtractor(self.brands)

    def test_known_brand_exact(self):
        r = self.ext.extract("雀巢咖啡无蔗糖10.2")
        self.assertEqual(r.value, "雀巢")
        self.assertEqual(r.method, "known_brand_match")
        self.assertGreaterEqual(r.confidence, 0.95)

    def test_known_brand_longest_match(self):
        # 库里有 "Calbee卡乐比" 和 "雀巢"；输入 "Calbee卡乐比豌豆条" 应该选最长
        r = self.ext.extract("Calbee卡乐比豌豆条蔬菜条70g")
        self.assertEqual(r.value, "Calbee卡乐比")

    def test_heuristic_mixed(self):
        # 不在已知库 / 但首部英中混合
        ext = BrandExtractor()  # 空库
        r = ext.extract("Tonys特怡诗酸奶山楂球")
        self.assertEqual(r.method, "heuristic_prefix_mixed")
        self.assertEqual(r.confidence, 0.6)

    def test_heuristic_chinese(self):
        ext = BrandExtractor()  # 空库
        r = ext.extract("彩虹糖果香乳酸菌味")
        self.assertEqual(r.method, "heuristic_prefix_cn")
        self.assertEqual(r.confidence, 0.4)

    def test_add_brand(self):
        self.ext.add_brand("新品牌")
        r = self.ext.extract("新品牌产品 100g")
        self.assertEqual(r.value, "新品牌")

    def test_empty_input(self):
        self.assertFalse(bool(self.ext.extract("")))


class TestBoxPackExtractor(unittest.TestCase):
    """箱规提取器测试."""

    def setUp(self):
        self.ext = BoxPackExtractor()

    def test_with_box(self):
        r = self.ext.extract("脆香米超值装24*12")
        self.assertEqual(r.value, "24*12")

    def test_no_box(self):
        r = self.ext.extract("Aji小龙虾味魔芋180g")
        self.assertFalse(bool(r))


class TestComposite(unittest.TestCase):
    """组合 Extractor 测试."""

    def setUp(self):
        self.ext = SKUAttributeExtractor(known_brands={"雀巢", "可比克"})

    def test_full_extract(self):
        result = self.ext.extract("可比克爽口青瓜味薯片55g")
        self.assertEqual(result.brand.value, "可比克")
        self.assertEqual(result.spec.value, "55g")

    def test_add_brand_propagates(self):
        self.ext.add_brand("新品牌")
        result = self.ext.extract("新品牌产品 100g")
        self.assertEqual(result.brand.value, "新品牌")
        self.assertEqual(result.spec.value, "100g")


class TestGroundTruth(unittest.TestCase):
    """用 700 SKU ground truth 验证整体准确率（如果数据可获取）."""

    @classmethod
    def setUpClass(cls):
        # 找 ground truth CSV
        candidates = [
            os.path.join(os.path.dirname(__file__), "ground_truth_700sku.csv"),
            "/Users/davidliu/KnowledgeBase/retail-knowledge-vault/13_数据分析与工具脚本/SKU属性提取算法_v0.1/tests/ground_truth_700sku.csv",
        ]
        cls.gt_path = None
        for c in candidates:
            if os.path.exists(c):
                cls.gt_path = c
                break

    def test_spec_accuracy_threshold(self):
        """规格算法在 700 SKU 上应 ≥85% 完全命中."""
        if not self.gt_path:
            self.skipTest("ground truth CSV 不存在")

        ext = SpecExtractor()
        hit = 0
        total = 0
        with open(self.gt_path, encoding='utf-8-sig') as f:
            r = csv.DictReader(f)
            for row in r:
                truth = (row.get('规格') or '').strip()
                name = (row.get('品名') or '').strip()
                if not truth or not name:
                    continue
                pred = ext.extract(name)
                if pred.value.replace(' ', '').lower() == truth.replace(' ', '').lower():
                    hit += 1
                total += 1
        accuracy = hit / total if total else 0
        print(f"\n  Spec accuracy on {total} ground-truth SKUs: {accuracy*100:.1f}%")
        self.assertGreaterEqual(accuracy, 0.85,
                                f"Spec accuracy {accuracy*100:.1f}% below 85% threshold")

    def test_brand_accuracy_with_known(self):
        """品牌算法在 known_brands 满载时应 ≥80% 完全命中."""
        if not self.gt_path:
            self.skipTest("ground truth CSV 不存在")

        # 加载 ground truth + 全部品牌作为 known_brands
        # CSV 列名兼容："品牌" 或 "品牌(干净)"
        rows = []
        all_brands = set()
        with open(self.gt_path, encoding='utf-8-sig') as f:
            r = csv.DictReader(f)
            for row in r:
                rows.append(row)
                b = (row.get('品牌(干净)') or row.get('品牌') or '').strip()
                if b:
                    all_brands.add(b)

        ext = BrandExtractor(all_brands)
        hit = 0
        total = 0
        for row in rows:
            truth = (row.get('品牌(干净)') or row.get('品牌') or '').strip()
            name = (row.get('品名') or '').strip()
            if not truth or not name:
                continue
            pred = ext.extract(name)
            if pred.value == truth:
                hit += 1
            total += 1
        accuracy = hit / total if total else 0
        print(f"\n  Brand accuracy (with full known_brands) on {total} SKUs: {accuracy*100:.1f}%")
        self.assertGreaterEqual(accuracy, 0.80,
                                f"Brand accuracy {accuracy*100:.1f}% below 80% threshold")


if __name__ == "__main__":
    unittest.main(verbosity=2)
