"""SKU 属性提取算法 — 入门示例.

运行: python3 examples/basic_usage.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sku_extractor import SKUAttributeExtractor

# 1. 加载已知品牌库（首次运行可空 / 后续从干净版主数据加载）
known_brands = {"雀巢", "可比克", "Calbee卡乐比", "三湘古镇", "无穷", "桂格", "皇麦世家"}

# 2. 实例化
extractor = SKUAttributeExtractor(known_brands)

# 3. 批量提取
samples = [
    "可比克爽口青瓜味薯片55g",
    "雀巢咖啡无蔗糖10.2",
    "桂格即食燕麦片1000g",
    "150g×3德芙巧克力家庭装",
    "彩虹糖果香乳酸菌味",
    "三湘古镇风干鸭翅根118g",
]

print(f"{'SKU 名称':<35s} | {'品牌':<15s}{'置信':<6s} | {'规格':<10s}{'置信':<6s}")
print("-" * 85)
for sku in samples:
    r = extractor.extract(sku)
    print(f"{sku:<35s} | "
          f"{r.brand.value:<15s}{r.brand.confidence:<6.2f} | "
          f"{r.spec.value:<10s}{r.spec.confidence:<6.2f}")
