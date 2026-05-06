#!/usr/bin/env python3
"""C-冲调专项 v0.2 — G4-A 74 SKU 按版本B 6 组 × 6 层映射 + 深调标准 4 段产出.

输出：
1. G4-A_深调V1_决策组重构.csv  — L4 决策组重构表（按版本B 6 组）
2. G4-A_深调V1_执行位定义.csv  — 6 组 × 6 层执行位 + 端架 + 收银位
3. G4-A_深调V1_SKU归位明细.csv  — 74 SKU 逐个归位（组/层/动作）
"""
import xlrd
import csv
import os
from collections import Counter, defaultdict

GOLD_FP = "/Users/davidliu/KnowledgeBase/retail-knowledge-vault/90_素材暂存与待整理/模板_【基础数据】花厅坊_4月日均销售_0420.xlsx"
OUT_DIR = "/Users/davidliu/KnowledgeBase/retail-knowledge-vault/09_门店案例与项目复盘/乐易购花厅坊店/03_商品诊断/01_清洗输出"
os.makedirs(OUT_DIR, exist_ok=True)

# 版本B 6 组定义（按 5/4 13:47 GPT 案例 C002）
ZONES = {
    'Z1_早餐麦片区': {'role': '主销带', '主类': '麦片谷物 主销'},
    'Z2_谷物冲调区': {'role': '利润带', '主类': '芝麻糊/核桃粉/姜茶/谷物糊'},
    'Z3_奶粉营养区': {'role': '基础覆盖带', '主类': '奶粉/豆奶粉'},
    'Z4_咖啡奶茶区': {'role': '冲动带', '主类': '咖啡/奶茶'},
    'Z5_茶叶蜂蜜区': {'role': '差异化锚点', '主类': '茶叶/蜂蜜'},
    'Z6_端架主题区': {'role': '联动放大', '主类': '早餐主题/营养主题'},
}

# L4 → 组 映射（基于 GPT 案例 C002）
def map_l4_to_zone(l4_value):
    l4 = str(l4_value).strip()
    # 第1组 早餐麦片区
    if any(k in l4 for k in ['即食麦片', '代餐谷物', '冲泡燕麦', '无糖轻负担']):
        return 'Z1_早餐麦片区'
    # 第2组 谷物冲调区
    if any(k in l4 for k in ['芝麻糊', '核桃粉', '姜茶红糖', '谷物糊']):
        return 'Z2_谷物冲调区'
    # 第3组 奶粉营养区
    if any(k in l4 for k in ['奶粉', '豆奶粉']):
        return 'Z3_奶粉营养区'
    # 第4组 咖啡奶茶区
    if any(k in l4 for k in ['咖啡', '奶茶']):
        return 'Z4_咖啡奶茶区'
    # 第5组 茶叶蜂蜜区（700 SKU 中如有"茶饮料"算到这里 / 蜂蜜不在 700 SKU 内 → 待补）
    if any(k in l4 for k in ['茶饮料', '茶叶', '蜂蜜']):
        return 'Z5_茶叶蜂蜜区'
    return None  # 未归类


# 加载 G4-A 74 SKU
wb = xlrd.open_workbook(GOLD_FP)
sh = wb.sheet_by_name('商品动销原表')
header = [sh.cell_value(0, j) for j in range(sh.ncols)]
COL = {h: idx for idx, h in enumerate(header)}

g4a_skus = []
for i in range(1, sh.nrows):
    if sh.cell_value(i, COL['L2']) != '冲调早餐/冲饮':
        continue
    row = {h: sh.cell_value(i, j) for j, h in enumerate(header)}
    row['_zone'] = map_l4_to_zone(row['L4'])
    g4a_skus.append(row)

print(f"G4-A: {len(g4a_skus)} SKU")
unmapped = [r for r in g4a_skus if r['_zone'] is None]
print(f"未归类: {len(unmapped)} (这些将归到 Z2 谷物冲调区作为补充)")
for r in unmapped[:5]:
    print(f"  L4='{r['L4']}' / 品名='{r['品名'][:40]}'")
# 把未归类的归到 Z2（多数是未识别的传统冲饮 — 茶饮料归 Z5 / 其他归 Z2）
for r in unmapped:
    l4 = str(r['L4']).strip()
    if '茶' in l4:
        r['_zone'] = 'Z5_茶叶蜂蜜区'
    else:
        r['_zone'] = 'Z2_谷物冲调区'  # 默认补 Z2

# 决策组角色分配
def assign_action(row):
    """根据 SKU 销售/库存表现 → 决策动作."""
    daily = float(row.get('日均销量') or 0)
    stock = float(row.get('当前库存') or 0)
    pre_days = float(row.get('预可售天数') or 0)
    if daily < 0.05 and pre_days > 365:  # 超长滞销
        return '清退-滞销'
    if daily < 0.05 and stock <= 0:  # 已无库存且不动销
        return '清退-停卖'
    if stock < 0:  # 负库存
        return '盘点-修正'
    if daily < 0.1:  # 弱动销
        return '观察/待砍'
    if daily >= 1.0:  # 畅销
        return '保留-做强'
    if daily >= 0.5:  # 中度动销
        return '保留'
    return '保留-精选'

for r in g4a_skus:
    r['_action'] = assign_action(r)

# ========================================================================
# 输出 1: 决策组重构表（按 6 组）
# ========================================================================

print("\n" + "="*80)
print("输出 1: G4-A_深调V1_决策组重构.csv（按版本B 6 组）")
print("="*80)

zone_summary = []
for zone, info in ZONES.items():
    rows = [r for r in g4a_skus if r['_zone'] == zone]
    if not rows:
        zone_summary.append({
            '组': zone, '角色': info['role'], '主类': info['主类'],
            '当前SKU': 0, '目标SKU': '待补', '压缩SKU': '-',
            '销售额(月)': 0, '销售占比': '0.0%', '毛利率': '-', '库存天数': '-',
            '动作': '🔴 必须补 6-8 SKU' if zone == 'Z5_茶叶蜂蜜区' else '空白',
        })
        continue
    daily_sum = sum(float(r.get('日均销量') or 0) for r in rows)
    sales_sum = sum(float(r.get('销售金额') or 0) for r in rows)
    cost_sum = sum(float(r.get('成本价') or 0) * float(r.get('销售数量') or 0) for r in rows)
    margin_rate = (sales_sum - cost_sum) / sales_sum if sales_sum > 0 else 0
    stock_value = sum(float(r.get('成本价') or 0) * max(float(r.get('当前库存') or 0), 0) for r in rows)
    stock_days = stock_value / (cost_sum / 30) if cost_sum > 0 else 0
    n = len(rows)
    # 目标 SKU 数（基于角色与压缩规则）
    if info['role'] == '主销带':
        target = max(15, int(n * 0.5))  # 主销至少 15 / 砍 50%
    elif info['role'] == '利润带':
        target = max(8, int(n * 0.6))   # 利润砍 40%
    elif info['role'] == '基础覆盖带':
        target = max(8, n + 3)  # 基础覆盖要补足
    elif info['role'] == '冲动带':
        target = max(8, int(n * 0.6))   # 冲动砍 40%
    elif info['role'] == '差异化锚点':
        target = max(10, n + 6)  # 茶叶蜂蜜要补
    else:
        target = max(6, int(n * 0.5))

    compress = max(0, n - target) if n > target else 0
    add = max(0, target - n) if target > n else 0

    action = []
    if compress > 0: action.append(f'压缩{compress}个')
    if add > 0: action.append(f'补{add}个')
    action_str = ' / '.join(action) if action else '保持'

    pct = sales_sum / sum(float(r.get('销售金额') or 0) for r in g4a_skus) * 100

    zone_summary.append({
        '组': zone, '角色': info['role'], '主类': info['主类'],
        '当前SKU': n, '目标SKU': target,
        '压缩SKU': compress if compress else '-',
        '补充SKU': add if add else '-',
        '销售额(月)': f'¥{sales_sum:.0f}',
        '销售占比': f'{pct:.1f}%',
        '毛利率': f'{margin_rate*100:.1f}%',
        '库存天数': f'{stock_days:.0f}天',
        '动作': action_str,
    })

out1 = os.path.join(OUT_DIR, "G4-A_深调V1_决策组重构.csv")
with open(out1, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['组', '角色', '主类', '当前SKU', '目标SKU', '压缩SKU', '补充SKU',
                                       '销售额(月)', '销售占比', '毛利率', '库存天数', '动作'])
    w.writeheader()
    for row in zone_summary:
        w.writerow(row)
print(f"  ✅ {out1}")
for row in zone_summary:
    print(f"    {row['组']:18s} | 当前{row['当前SKU']:3} → 目标{str(row['目标SKU']):4} | {row['销售占比']:6} | {row['毛利率']:6} | {row['动作']}")

# ========================================================================
# 输出 2: 执行位定义（6 组 × 6 层 + 端架 + 收银）
# ========================================================================

print("\n" + "="*80)
print("输出 2: G4-A_深调V1_执行位定义.csv（按版本B 6 层）")
print("="*80)

# 6 层定义（来自 GPT 案例 C002）
LAYERS = [
    ('第1层 形象层', '轻量形象款（不放礼盒 / 8 条修正规则 #1）', 0.10, '形象款 1-2 SKU/组'),
    ('第2层 黄金视线层', '主力 SKU', 0.25, '主力 4-6 SKU/组'),
    ('第3层 黄金手拿层', '高转化 / 高毛利', 0.30, '主销 + 利润 6-8 SKU/组'),
    ('第4层 补充/特色层', '功能 / 特色补充', 0.15, '补充 4-6 SKU/组'),
    ('第5层 大包装家庭装', '大包装下移（8 条修正规则 #4）', 0.15, '家庭装 3-4 SKU/组'),
    ('第6层 围货层', '整箱补货 / 库存缓冲', 0.05, '围货 1-2 SKU/组'),
]

exec_positions = []
for zone in ZONES.keys():
    for layer_name, layer_desc, ratio, sku_guidance in LAYERS:
        zone_target = next((z['目标SKU'] for z in zone_summary if z['组'] == zone), 0)
        target_in_layer = max(1, int(zone_target * ratio)) if isinstance(zone_target, int) else 1
        exec_positions.append({
            '执行位': f"{zone[:5]}-{layer_name[:5]}",
            '组': zone,
            '层': layer_name,
            '类型': '主货架',
            '建议SKU数': target_in_layer,
            '陈列说明': sku_guidance,
            '注意事项': layer_desc,
        })
# 端架主题
exec_positions.extend([
    {'执行位': 'T1_早餐主题', '组': 'Z6_端架主题区', '层': '端架', '类型': '端架',
     '建议SKU数': 6, '陈列说明': '麦片+牛奶+蜂蜜 早餐组合', '注意事项': '8 条修正规则 #8 端架优先早餐主题'},
    {'执行位': 'T2_营养主题', '组': 'Z6_端架主题区', '层': '端架', '类型': '端架',
     '建议SKU数': 6, '陈列说明': '营养奶粉+代餐+谷物 营养组合', '注意事项': '健康营养主题联动'},
    {'执行位': 'T3_家庭装主题', '组': 'Z6_端架主题区', '层': '端架', '类型': '端架',
     '建议SKU数': 4, '陈列说明': '大包装麦片/咖啡/奶粉', '注意事项': '周末家庭客流承接（来自区域定位说明书 §3.3）'},
])
# 收银位（小包装冲动购）
exec_positions.append({
    '执行位': 'C1_收银位冲动购', '组': 'Z4_咖啡奶茶区', '层': '收银位', '类型': '挂条',
    '建议SKU数': 4, '陈列说明': '小包装即饮咖啡/三合一', '注意事项': '收银等待 30s 内冲动购'
})

out2 = os.path.join(OUT_DIR, "G4-A_深调V1_执行位定义.csv")
with open(out2, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['执行位', '组', '层', '类型', '建议SKU数', '陈列说明', '注意事项'])
    w.writeheader()
    for row in exec_positions:
        w.writerow(row)
print(f"  ✅ {out2} ({len(exec_positions)} 个执行位)")

# ========================================================================
# 输出 3: SKU 归位明细
# ========================================================================

print("\n" + "="*80)
print("输出 3: G4-A_深调V1_SKU归位明细.csv（74 SKU 逐个归位）")
print("="*80)

# 按组排序 + 按动作排序
g4a_skus.sort(key=lambda r: (r['_zone'], -float(r.get('日均销量') or 0)))

out3 = os.path.join(OUT_DIR, "G4-A_深调V1_SKU归位明细.csv")
with open(out3, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['归位组', 'L3', 'L4', '条码', '品名', '品牌', '规格', '售价',
                '日均销量', '当前库存', '预可售天数', '动作', '建议层位'])
    for r in g4a_skus:
        # 建议层位（基于动作）
        action = r['_action']
        daily = float(r.get('日均销量') or 0)
        if action == '保留-做强':
            layer = '第2-3层 黄金'
        elif action == '保留':
            layer = '第3-4层'
        elif action == '保留-精选':
            layer = '第4层 补充'
        elif action.startswith('清退'):
            layer = '下架'
        elif action == '盘点-修正':
            layer = '盘点 → 决策'
        else:
            layer = '观察 / 第5-6层下移'
        # 大包装识别（规格 ≥500g）
        spec = str(r.get('规格', ''))
        if any(s in spec for s in ['600g', '800g', '900g', '1000g', '480g', '5L']):
            layer = '第5层 大包装'

        w.writerow([
            r['_zone'], r['L3'], r['L4'], r['条码'], r['品名'],
            r['品牌'], r['规格'], r['售价'],
            r.get('日均销量'), r['当前库存'], r['预可售天数'],
            r['_action'], layer,
        ])
print(f"  ✅ {out3}")

# 动作汇总
action_counts = Counter(r['_action'] for r in g4a_skus)
print(f"\n动作分布:")
for action, count in action_counts.most_common():
    print(f"  {action}: {count}")

# 各组动作分布
print(f"\n各组动作分布:")
for zone in ZONES.keys():
    rows = [r for r in g4a_skus if r['_zone'] == zone]
    actions = Counter(r['_action'] for r in rows)
    print(f"  {zone}: {dict(actions)}")
