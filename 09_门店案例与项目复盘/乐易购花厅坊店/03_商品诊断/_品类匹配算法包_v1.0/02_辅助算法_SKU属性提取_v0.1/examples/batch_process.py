"""SKU 属性提取算法 — 批处理示例.

输入：CSV / 含"条码"+"品名"+ 可选"品牌"+"规格"
输出：CSV / 加三层字段（原表/AI补/最终）+ 来源标注

运行：
  python3 examples/batch_process.py <输入CSV> <输出CSV>
"""
import sys
import os
import csv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sku_extractor import SKUAttributeExtractor


def batch_process(input_csv: str, output_csv: str, brand_column: str = "品牌(干净)"):
    """批处理入口.

    Args:
        input_csv:     输入 CSV 路径
        output_csv:    输出 CSV 路径
        brand_column:  CSV 里"品牌"的列名（默认 "品牌(干净)"，也支持 "品牌"）
    """
    # 1. 加载输入 + 学习已知品牌
    rows = []
    known_brands = set()
    with open(input_csv, encoding='utf-8-sig') as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(row)
            b = (row.get(brand_column) or row.get('品牌') or '').strip()
            if b:
                known_brands.add(b)
    print(f"[1] 加载 {len(rows)} 行 / 学习 {len(known_brands)} 个已知品牌")

    # 2. 实例化 extractor
    extractor = SKUAttributeExtractor(known_brands)

    # 3. 批量提取 + 三层字段
    out_rows = []
    stats = {'brand_filled_by_ai': 0, 'spec_filled_by_ai': 0,
             'brand_orig': 0, 'spec_orig': 0}
    for row in rows:
        name = (row.get('品名') or '').strip()
        brand_orig = (row.get(brand_column) or row.get('品牌') or '').strip()
        spec_orig = (row.get('规格') or '').strip()

        # AI 提取
        result = extractor.extract(name)

        # 三层来源
        brand_final = brand_orig or result.brand.value
        brand_source = '原表' if brand_orig else ('AI补' if result.brand.value else '空')
        spec_final = spec_orig or result.spec.value
        spec_source = '原表' if spec_orig else ('AI补' if result.spec.value else '空')

        if brand_orig:
            stats['brand_orig'] += 1
        elif result.brand.value:
            stats['brand_filled_by_ai'] += 1
        if spec_orig:
            stats['spec_orig'] += 1
        elif result.spec.value:
            stats['spec_filled_by_ai'] += 1

        out_row = dict(row)
        out_row['品牌(原表)'] = brand_orig
        out_row['品牌(AI补)'] = result.brand.value
        out_row['品牌(置信度)'] = f"{result.brand.confidence:.2f}"
        out_row['品牌(最终)'] = brand_final
        out_row['品牌(来源)'] = brand_source
        out_row['规格(原表)'] = spec_orig
        out_row['规格(AI补)'] = result.spec.value
        out_row['规格(置信度)'] = f"{result.spec.confidence:.2f}"
        out_row['规格(最终)'] = spec_final
        out_row['规格(来源)'] = spec_source
        out_rows.append(out_row)

    # 4. 输出
    if out_rows:
        with open(output_csv, 'w', encoding='utf-8-sig', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
            w.writeheader()
            w.writerows(out_rows)

    print(f"[2] AI 补充: 品牌 {stats['brand_filled_by_ai']} / 规格 {stats['spec_filled_by_ai']}")
    print(f"[3] 原表已有: 品牌 {stats['brand_orig']} / 规格 {stats['spec_orig']}")
    print(f"[4] 输出: {output_csv}")


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        batch_process(sys.argv[1], sys.argv[2])
    else:
        # Demo：用 ground truth 跑一遍
        demo_input = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "tests", "ground_truth_700sku.csv"
        )
        demo_output = "/tmp/batch_process_demo_output.csv"
        if os.path.exists(demo_input):
            print(f"Demo 模式: 用 ground truth 跑一遍")
            batch_process(demo_input, demo_output)
        else:
            print("用法: python3 batch_process.py <输入CSV> <输出CSV>")
            sys.exit(1)
