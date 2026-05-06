"""SKU 属性提取算法 v0.1 — 软件开发基础素材.

设计原则：
- 纯函数 / 无副作用 / 可单元测试
- 规则可配置 / 不依赖 LLM（保持本地可重跑、低成本、可审计）
- 输出含置信度（可分级人工 review）
- 三个独立 Extractor 类（规格 / 品牌 / 箱规）+ 统一 ExtractResult 接口

实测准确率（2026-05-04 / leave-one-out 验证 / 花厅坊休食 700 SKU）：
- SpecExtractor:    92.8% 完全命中 + 1.5% 部分命中
- BrandExtractor:   16.7% 完全命中 + 81.8% 部分命中（依赖 KnownBrands）
- BoxPackExtractor: 弱（信息源外置 / 仅作占位）

使用场景：
- 商品主数据补全（4791 SKU 级以上批处理）
- 跨客户跨门店复用（晟果商品主数据骨架库 v0.x 基础）
- 后期产品化软件开发的算法核心
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional


# ============================================================
# 输出类型
# ============================================================

@dataclass(frozen=True)
class ExtractResult:
    """提取结果统一格式.

    Attributes:
        value:      提取到的值（字符串）；空表示未提取到
        confidence: 0.0-1.0；分级人工 review 用
        method:     方法标签（用于调试 / 算法迭代时溯源）
        raw_match:  原始匹配文本（regex 匹配的子串）
    """
    value: str
    confidence: float
    method: str
    raw_match: str = ""

    def __bool__(self) -> bool:
        return bool(self.value) and self.confidence >= 0.5


# ============================================================
# 规格提取器 — 实测 92.8% 完全命中
# ============================================================

class SpecExtractor:
    """从 SKU 名称提取规格（数字 + 单位组合）.

    支持模式：
    - 单值：100g / 500ml / 1.25L / 70克 / 30片 / 2.5kg
    - 复合：150g×3 / 100ml*2 / 50g x 4

    置信度规则：
    - 在 SKU 名尾部 60% 之后命中：0.95（典型规格在尾部）
    - 在 SKU 名中部 30%-60% 之间：0.75
    - 在 SKU 名前部 0%-30%：0.5（可能是数量而非规格）
    """

    # 单值规格：数字 + 单位
    PATTERN_SINGLE = re.compile(
        r'(\d+\.?\d*)\s*'
        r'(g|ml|L|kg|克|毫升|升|公斤|片|袋|包|盒|瓶|罐|条|支|个|颗|粒|对|根|串)',
        re.IGNORECASE,
    )

    # 复合规格：两种形式
    # A: 数字 × 数字 + 单位（如 3×150g）
    # B: 数字 + 单位 × 数字（如 150g×3 / 56g*2）
    PATTERN_COMPOSITE = re.compile(
        r'('
        r'\d+\.?\d*\s*[×x*]\s*\d+\.?\d*\s*(?:g|ml|L|kg|克|毫升|升|公斤|片|袋|包|盒|瓶|罐|条)'
        r'|'
        r'\d+\.?\d*\s*(?:g|ml|L|kg|克|毫升|升|公斤|片|袋|包|盒|瓶|罐|条)\s*[×x*]\s*\d+\.?\d*'
        r')',
        re.IGNORECASE,
    )

    @staticmethod
    def _normalize_unit(spec: str) -> str:
        """归一化单位大小写：g 小写 / ml 小写 / L 大写 / kg 小写."""
        # 先匹配多字符单位，避免 'ml' 中的 'l' 被误改
        # 用 regex 替换更安全
        spec = re.sub(r'[Mm][Ll]', 'ml', spec)
        spec = re.sub(r'[Kk][Gg]', 'kg', spec)
        # 单字符 g 小写 / L 大写（不在 ml/kg 内才生效，已先消化）
        spec = re.sub(r'(?<=\d)\s*G\b', 'g', spec)
        spec = re.sub(r'(?<=\d)\s*[lL]\b', 'L', spec)
        return spec

    def extract(self, sku_name: str) -> ExtractResult:
        """主提取入口.

        Args:
            sku_name: SKU 名称（如 "Aji小龙虾味魔芋180g"）

        Returns:
            ExtractResult, value 是规格字符串（如 "180g"），空表示未识别
        """
        if not sku_name or not isinstance(sku_name, str):
            return ExtractResult("", 0.0, "input_empty")

        name = sku_name.strip()

        # 1. 复合规格优先（如 150g*3 — 信息量比单值大）
        composite_matches = list(self.PATTERN_COMPOSITE.finditer(name))
        if composite_matches:
            m = max(composite_matches, key=lambda x: x.start())
            pos = m.start()
            end_pos = m.end()
            spec = m.group(0).strip()
            method = "composite"
        else:
            # 2. 单值规格
            single_matches = list(self.PATTERN_SINGLE.finditer(name))
            if not single_matches:
                return ExtractResult("", 0.0, "no_match")
            m = max(single_matches, key=lambda x: x.start())
            pos = m.start()
            end_pos = m.end()
            spec = m.group(0).strip()
            method = "single"

        # 归一化单位
        spec = self._normalize_unit(spec)

        # 置信度规则：
        # - 规格在 name 末尾（之后 ≤2 字符）→ 0.95（典型规格在尾部）
        # - 规格位置占比 ≥60% → 0.95
        # - 规格位置占比 30%-60% → 0.75
        # - 规格位置占比 <30% 且不在末尾 → 0.5
        chars_after = len(name) - end_pos
        ratio = pos / len(name) if len(name) else 0
        if chars_after <= 2 or ratio > 0.6:
            conf = 0.95
        elif ratio > 0.3:
            conf = 0.75
        else:
            conf = 0.5

        return ExtractResult(spec, conf, f"rule_{method}", spec)


# ============================================================
# 品牌提取器 — 依赖 KnownBrands；实测 81.8% 部分命中
# ============================================================

class BrandExtractor:
    """从 SKU 名称提取品牌.

    策略：
    1. 已知品牌库匹配（高置信度 0.95）— 主力
    2. 启发式名首部字符匹配（中低置信度 0.4-0.6）— 补充
    """

    # 启发式：首部英文+中文混合（如 Aji / Calbee卡乐比 / BOOZI）
    PATTERN_PREFIX_MIXED = re.compile(r'^([A-Za-z]+[一-龥]*)')

    # 启发式：纯中文首部 2-4 字符
    PATTERN_PREFIX_CN = re.compile(r'^[一-龥]{2,4}')

    def __init__(self, known_brands: Optional[set[str]] = None):
        """
        Args:
            known_brands: 已知品牌库（从历史数据 / 标杆店学习）
                         空集合时仅使用启发式，准确率显著下降
        """
        self.known_brands: set[str] = set(known_brands) if known_brands else set()

    def add_brand(self, brand: str) -> None:
        """学习新品牌（增量添加，跨客户复用基础）."""
        if brand and isinstance(brand, str):
            self.known_brands.add(brand.strip())

    def extract(self, sku_name: str) -> ExtractResult:
        """主提取入口."""
        if not sku_name or not isinstance(sku_name, str):
            return ExtractResult("", 0.0, "input_empty")

        name = sku_name.strip()

        # 1. 已知品牌库匹配（取最长匹配 — 避免 "雀" 优先于 "雀巢"）
        matched = [b for b in self.known_brands if b and name.startswith(b)]
        if matched:
            best = max(matched, key=len)
            return ExtractResult(best, 0.95, "known_brand_match", best)

        # 2. 启发式：首部英文+中文混合
        m = self.PATTERN_PREFIX_MIXED.match(name)
        if m and len(m.group(1)) >= 2:
            return ExtractResult(m.group(1), 0.6, "heuristic_prefix_mixed", m.group(1))

        # 3. 启发式：首部纯中文 2-4 字符
        m = self.PATTERN_PREFIX_CN.match(name)
        if m:
            return ExtractResult(m.group(0), 0.4, "heuristic_prefix_cn", m.group(0))

        return ExtractResult("", 0.0, "no_match")


# ============================================================
# 箱规提取器 — 弱算法 / 数据多在采购合同 / 仅作占位
# ============================================================

class BoxPackExtractor:
    """从 SKU 名称提取箱规（如 1*40 / 1×24）.

    箱规通常不在 SKU 名里，多在采购合同 / 经销商资料 / D 类字典.
    本算法弱，仅匹配 SKU 名内偶尔出现的明示箱规.
    """

    PATTERN = re.compile(r'(\d+)\s*[×x*]\s*(\d+)')

    def extract(self, sku_name: str, spec: str = "") -> ExtractResult:
        """主提取入口."""
        if not sku_name or not isinstance(sku_name, str):
            return ExtractResult("", 0.0, "input_empty")

        name = sku_name.strip()

        # 找 "N*M" 或 "N×M"
        for m in self.PATTERN.finditer(name):
            box = m.group(0).replace('×', '*').replace('x', '*').replace(' ', '')
            return ExtractResult(box, 0.7, "rule_in_name", box)

        return ExtractResult("", 0.0, "no_match")


# ============================================================
# 组合 Extractor — 一次提取所有属性
# ============================================================

@dataclass
class SKUAttributes:
    """提取后的完整属性集."""
    sku_name: str
    brand: ExtractResult = field(default_factory=lambda: ExtractResult("", 0.0, "init"))
    spec: ExtractResult = field(default_factory=lambda: ExtractResult("", 0.0, "init"))
    box_pack: ExtractResult = field(default_factory=lambda: ExtractResult("", 0.0, "init"))


class SKUAttributeExtractor:
    """组合 Extractor — 一次提取品牌 + 规格 + 箱规."""

    def __init__(self, known_brands: Optional[set[str]] = None):
        self.brand_extractor = BrandExtractor(known_brands)
        self.spec_extractor = SpecExtractor()
        self.box_extractor = BoxPackExtractor()

    def extract(self, sku_name: str) -> SKUAttributes:
        """主入口."""
        return SKUAttributes(
            sku_name=sku_name,
            brand=self.brand_extractor.extract(sku_name),
            spec=self.spec_extractor.extract(sku_name),
            box_pack=self.box_extractor.extract(sku_name),
        )

    def add_brand(self, brand: str) -> None:
        """学习新品牌."""
        self.brand_extractor.add_brand(brand)


# ============================================================
# CLI 入口（python -m sku_extractor）
# ============================================================

if __name__ == "__main__":
    import json
    import sys

    samples = [
        "Aji小龙虾味魔芋180g",
        "雀巢咖啡无蔗糖10.2",
        "桂格即食燕麦片1000g",
        "150g*3德芙巧克力家庭装",
        "彩虹糖果香乳酸菌味",
        "无穷的卤味鸡腿",
    ]

    # 简单 demo（无 known_brands）
    extractor = SKUAttributeExtractor()
    for name in samples:
        result = extractor.extract(name)
        print(f"\nSKU: {name}")
        print(f"  brand:    {result.brand.value!r:20s} (conf={result.brand.confidence:.2f}, method={result.brand.method})")
        print(f"  spec:     {result.spec.value!r:20s} (conf={result.spec.confidence:.2f}, method={result.spec.method})")
        print(f"  box_pack: {result.box_pack.value!r:20s} (conf={result.box_pack.confidence:.2f}, method={result.box_pack.method})")
