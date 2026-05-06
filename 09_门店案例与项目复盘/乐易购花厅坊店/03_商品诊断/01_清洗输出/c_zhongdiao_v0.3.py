#!/usr/bin/env python3
"""C-冲调专项 v0.3 — G4-A 74 SKU 按版本B 真实 6 组（SKU 角色）映射.

版本B 真实 6 组（来自 G4_A_冲调陈列_04.png 顶部色带）：
  Z1 低价引流区（低价高频 / 引流带）
  Z2 主力奶类·麦片区（中价主销）
  Z3 功能细分区（代餐/营养/学生/中老年/高钙等）
  Z4 高端升级区（高价形象 / 进口）
  Z5 特色风味区（差异化口味）
  Z6 袋装囤量·趣味区（大包装家庭装 + 趣味款）

横向（组）= SKU 角色 / 纵向（层）= 形象层级
"""
import xlrd
import csv
import os
import re
from collections import Counter, defaultdict

GOLD_FP = "/Users/davidliu/KnowledgeBase/retail-knowledge-vault/90_素材暂存与待整理/模板_【基础数据】花厅坊_4月日均销售_0420.xlsx"
OUT_DIR = "/Users/davidliu/KnowledgeBase/retail-knowledge-vault/09_门店案例与项目复盘/乐易购花厅坊店/03_商品诊断/01_清洗输出"
os.makedirs(OUT_DIR, exist_ok=True)

# 6 组定义
ZONES = [
    ('Z1_低价引流区', '引流带', '低价高频 ≤ 10 元'),
    ('Z2_主力奶类麦片区', '主销带', '中价主力（10-30 元 / 日均 ≥ 0.1）'),
    ('Z3_功能细分区', '功能补充带', '代餐/营养/学生/中老年/高钙/高铁'),
    ('Z4_高端升级区', '升级带', '高价形象 ≥ 30 元 / 进口 / 礼盒'),
    ('Z5_特色风味区', '差异化锚点', '特殊风味（白咖啡/抹茶/姜茶/燕窝等）'),
    ('Z6_袋装囤量趣味区', '家庭装+趣味', '大包装 ≥ 500g 或家庭装'),
]

# ============================================================
# SKU 角色识别规则
# ============================================================

FUNCTIONAL_KEYWORDS = ['代餐', '营养', '学生', '中老年', '高钙', '高铁', '加钙', '加铁',
                       '怡养', '功能', '低糖', '无糖', '蛋白', '健康', '欣活', '配方',
                       '高纤', '中老', '幼儿', '青少', '孕妇', '钙铁', '葡萄糖', '黑麦']
# 注：'杂粮' 从功能列表剔除（"五谷杂粮"低价引流款不属功能型）

PREMIUM_KEYWORDS = ['醇品', '高端', '进口', '怡养', '羊奶粉', '炼乳', '礼盒',
                    '臻享', '醇香', '黄金', '金装', '蓝罐', '丝滑', '原装']

SPECIAL_FLAVOR_KEYWORDS = ['姜茶', '红糖', '白咖啡', '抹茶', '蜂蜜', '茶饮', '葡萄糖',
                            '姜枣', '红枣', '黑芝麻', '核桃', '燕窝', '阿胶', '陈皮',
                            '枇杷', '柠檬', '桂花', '花茶', '茉莉', '玫瑰']

LARGE_PACKAGE_KEYWORDS = ['家庭装', '大包', '罐装', '桶装', '大盒', '大袋', '组合装',
                          '超值装', '量贩']

def is_large_package(spec, name, price=0):
    """判断是否大包装/家庭装.

    冲调常规小包就是 400-600g，所以阈值要更高才算"家庭装/囤量"：
    - 关键词明示（家庭装/大包/桶装等）
    - 规格 ≥800g 或 ≥1L 或 ≥1kg
    - 注：金味原味麦片 600g 不算大包（冲调标配）
    """
    if not spec: spec = ""
    s = str(spec).strip()
    n = str(name).strip()
    # 关键词命中（明示）
    for k in LARGE_PACKAGE_KEYWORDS:
        if k in n:
            return True
    # 数字阈值（提高）
    m = re.search(r'(\d+\.?\d*)\s*(g|kg|ml|L|克|毫升|升)', s, re.IGNORECASE)
    if m:
        val = float(m.group(1))
        unit = m.group(2).lower()
        if unit in ('g', '克') and val >= 800:
            return True
        if unit in ('ml', '毫升') and val >= 1000:
            return True
        if unit in ('l', '升') and val >= 1:
            return True
        if unit in ('kg', '公斤') and val >= 1:
            return True
    return False

def has_keyword(text, keywords):
    if not text: return False
    s = str(text)
    return any(k in s for k in keywords)

def assign_role(row):
    """SKU 角色映射 - 按版本B 6 组逻辑.

    优先级：囤量 > 升级 > 功能 > 特色 > 引流/主力（互斥）
    """
    name = str(row.get('品名', ''))
    spec = str(row.get('规格', ''))
    price = float(row.get('售价') or 0)
    daily = float(row.get('日均销量') or 0)
    l4 = str(row.get('L4', ''))

    # 1. 囤量优先（大包装一律进 Z6，不分价位）
    if is_large_package(spec, name, price):
        return 'Z6_袋装囤量趣味区'

    # 2. 升级带（高价 ≥ 25 元 + 形象/进口/礼盒关键词 / 或 ≥35 元）
    if price >= 25 and has_keyword(name, PREMIUM_KEYWORDS):
        return 'Z4_高端升级区'
    if price >= 35:
        return 'Z4_高端升级区'

    # 3. 低价高频引流优先（如顺天缘五谷杂粮 16g ¥1 / 日均 0.43 = 引流不是功能）
    if price <= 8 and daily >= 0.2:
        return 'Z1_低价引流区'

    # 4. 功能细分（按人群/功能关键词 + 价位 ≥ 5 排除低价小包装假功能）
    if (has_keyword(name, FUNCTIONAL_KEYWORDS) or has_keyword(l4, FUNCTIONAL_KEYWORDS)) and price >= 5:
        return 'Z3_功能细分区'

    # 5. 特色风味（差异化口味）
    if has_keyword(name, SPECIAL_FLAVOR_KEYWORDS):
        return 'Z5_特色风味区'

    # 6. 一般低价引流（小包/低价但低频）
    if price <= 10:
        return 'Z1_低价引流区'

    # 7. 默认主销
    return 'Z2_主力奶类麦片区'


def assign_layer(row, zone):
    """6 层定位 - 按 SKU 形象层级 + 销量.

    第 1 层 形象层  - 每组 1-2 个形象款（高知名度品牌 / 醒目包装）
    第 2 层 黄金视线 - 主力销量 SKU
    第 3 层 黄金手拿 - 高转化 / 高毛利
    第 4 层 补充层   - 二线品牌 / 长尾补充
    第 5 层 大包装层 - 大包装下移（仅非 Z6 / Z6 自身平均布局）
    第 6 层 围货层   - 整箱 / 库存缓冲
    """
    daily = float(row.get('日均销量') or 0)
    spec = str(row.get('规格', ''))
    name = str(row.get('品名', ''))
    stock = float(row.get('当前库存') or 0)

    # Z6 自身就是大包装区，不需要纵向"大包装下移"
    if zone == 'Z6_袋装囤量趣味区':
        if daily >= 0.1:
            return '第2-3层 黄金'
        elif daily >= 0.05:
            return '第4层 补充'
        else:
            return '第5-6层 围货'

    # 其他组按形象层逻辑
    # 形象层 = 高知名度品牌（雀巢 / 桂格 / 西麦 / 阿华田 等大牌头部 SKU）
    PREMIUM_BRANDS_LAYER1 = ['雀巢', '桂格', '西麦', '阿华田', '南方', '伊利', '蒙牛', '维维']
    is_brand_lead = any(b in name for b in PREMIUM_BRANDS_LAYER1) and daily >= 0.15

    if is_brand_lead and daily >= 0.2:
        return '第1层 形象'
    if daily >= 0.3:
        return '第2层 黄金视线'
    if daily >= 0.1:
        return '第3层 黄金手拿'
    if daily >= 0.05:
        return '第4层 补充'
    if stock <= 0:
        return '第6层 围货（库存缓冲）'
    return '第5层 大包装/补充'


def assign_action(row):
    """决策动作."""
    daily = float(row.get('日均销量') or 0)
    stock = float(row.get('当前库存') or 0)
    pre_days = float(row.get('预可售天数') or 0)
    if daily < 0.05 and pre_days > 365:
        return '清退-滞销'
    if daily < 0.05 and stock <= 0:
        return '清退-停卖'
    if stock < 0:
        return '盘点-修正'
    if daily >= 1.0:
        return '保留-做强'
    if daily >= 0.3:
        return '保留-主力'
    if daily >= 0.1:
        return '保留-观察'
    return '观察/待砍'


# ============================================================
# 加载 + 映射
# ============================================================

wb = xlrd.open_workbook(GOLD_FP)
sh = wb.sheet_by_name('商品动销原表')
header = [sh.cell_value(0, j) for j in range(sh.ncols)]
COL = {h: idx for idx, h in enumerate(header)}

g4a = []
for i in range(1, sh.nrows):
    if sh.cell_value(i, COL['L2']) != '冲调早餐/冲饮':
        continue
    row = {h: sh.cell_value(i, j) for j, h in enumerate(header)}
    row['_zone'] = assign_role(row)
    row['_layer'] = assign_layer(row, row['_zone'])
    row['_action'] = assign_action(row)
    g4a.append(row)

print(f"G4-A: {len(g4a)} SKU")
zone_dist = Counter(r['_zone'] for r in g4a)
print(f"\n6 组分布:")
for zone, _, _ in ZONES:
    n = zone_dist.get(zone, 0)
    print(f"  {zone}: {n} SKU")

# ============================================================
# 输出 1: 决策组重构表（按角色 6 组）
# ============================================================

print("\n" + "="*80)
print("输出 1: G4-A_深调V1_决策组重构_v0.3.csv")
print("="*80)

zone_summary = []
total_sales = sum(float(r.get('销售金额') or 0) for r in g4a)

for zone, role, definition in ZONES:
    rows = [r for r in g4a if r['_zone'] == zone]
    n = len(rows)
    sales = sum(float(r.get('销售金额') or 0) for r in rows)
    cost = sum(float(r.get('成本价') or 0) * float(r.get('销售数量') or 0) for r in rows)
    margin = (sales - cost) / sales if sales > 0 else 0
    stock_value = sum(float(r.get('成本价') or 0) * max(float(r.get('当前库存') or 0), 0) for r in rows)
    stock_days = stock_value / (cost / 30) if cost > 0 else 0

    # 目标 SKU 数（基于角色分布建议 / GPT 案例 C002 + 区域定位说明书）
    if zone == 'Z1_低价引流区':
        target = max(8, int(n * 0.7))   # 引流要高频 / 砍掉低效引流
    elif zone == 'Z2_主力奶类麦片区':
        target = max(15, int(n * 0.6))  # 主销砍 40% 长尾
    elif zone == 'Z3_功能细分区':
        target = max(10, n + 3) if n < 10 else max(8, int(n * 0.7))
    elif zone == 'Z4_高端升级区':
        target = max(5, int(n * 0.7)) if n > 5 else max(4, n + 2)
    elif zone == 'Z5_特色风味区':
        target = max(10, n + 5)  # 特色锚点要补
    else:  # Z6 囤量
        target = max(8, int(n * 0.6))

    compress = max(0, n - target) if n > target else 0
    add = max(0, target - n) if target > n else 0
    pct = sales / total_sales * 100 if total_sales > 0 else 0

    actions = []
    if compress > 0: actions.append(f'压缩{compress}个')
    if add > 0: actions.append(f'补{add}个')
    action_str = ' / '.join(actions) if actions else '保持'

    zone_summary.append({
        '组': zone, '角色': role, '定义': definition,
        '当前SKU': n, '目标SKU': target,
        '压缩': compress if compress else '-',
        '补充': add if add else '-',
        '销售额(月)': f'¥{sales:.0f}',
        '销售占比': f'{pct:.1f}%',
        '毛利率': f'{margin*100:.1f}%' if sales > 0 else '-',
        '库存天数': f'{stock_days:.0f}天' if stock_days else '-',
        '动作': action_str,
    })

out1 = os.path.join(OUT_DIR, "G4-A_深调V1_决策组重构_v0.3.csv")
with open(out1, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['组', '角色', '定义', '当前SKU', '目标SKU', '压缩', '补充',
                                       '销售额(月)', '销售占比', '毛利率', '库存天数', '动作'])
    w.writeheader()
    for row in zone_summary:
        w.writerow(row)
print(f"  ✅ {out1}")
for row in zone_summary:
    print(f"    {row['组']:25s} | {row['当前SKU']:3} → {row['目标SKU']:3} | {row['销售占比']:6} | {row['毛利率']:6} | {row['动作']}")

# ============================================================
# 输出 2: 执行位（6 组 × 6 层 + 端架 + 收银）
# ============================================================

print("\n" + "="*80)
print("输出 2: G4-A_深调V1_执行位定义_v0.3.csv")
print("="*80)

LAYERS_NORMAL = [
    ('第1层 形象', 0.10, '形象款 1-2 个'),
    ('第2层 黄金视线', 0.20, '主力 3-4 个'),
    ('第3层 黄金手拿', 0.25, '主销+利润 4-5 个'),
    ('第4层 补充', 0.20, '补充 3-4 个'),
    ('第5层 大包装', 0.15, '大包装 / 二线 2-3 个'),
    ('第6层 围货', 0.10, '围货 1-2 个'),
]

exec_pos = []
for zone, role, _ in ZONES:
    target = next((z['目标SKU'] for z in zone_summary if z['组'] == zone), 0)
    if isinstance(target, str):
        target = 8
    for layer, ratio, hint in LAYERS_NORMAL:
        sku_n = max(1, round(target * ratio))
        exec_pos.append({
            '执行位': f'{zone[:5]}_{layer[:5]}',
            '组': zone, '层': layer, '类型': '主货架',
            '建议SKU数': sku_n, '陈列说明': hint, '注意事项': f'角色={role}',
        })

# 端架 T1-T3（独立资源位）
exec_pos.extend([
    {'执行位': 'T1_早餐主题端架', '组': '端架', '层': '端架', '类型': '端架',
     '建议SKU数': 6, '陈列说明': '麦片+牛奶+蜂蜜 早餐组合',
     '注意事项': '8 条修正规则 #8 端架优先早餐主题'},
    {'执行位': 'T2_营养主题端架', '组': '端架', '层': '端架', '类型': '端架',
     '建议SKU数': 6, '陈列说明': '营养奶粉+代餐+谷物 营养组合',
     '注意事项': '健康营养主题联动'},
    {'执行位': 'T3_家庭装主题端架', '组': '端架', '层': '端架', '类型': '端架',
     '建议SKU数': 4, '陈列说明': '大包装麦片/咖啡/奶粉',
     '注意事项': '周末家庭客流承接（区域定位说明书 §3.3）'},
])
# 收银位
exec_pos.append({
    '执行位': 'C1_收银位冲动购', '组': '收银区', '层': '挂条', '类型': '挂条',
    '建议SKU数': 4, '陈列说明': '小包装即饮咖啡 / 三合一',
    '注意事项': '收银等待 30s 内冲动购'
})

out2 = os.path.join(OUT_DIR, "G4-A_深调V1_执行位定义_v0.3.csv")
with open(out2, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['执行位', '组', '层', '类型', '建议SKU数', '陈列说明', '注意事项'])
    w.writeheader()
    for row in exec_pos:
        w.writerow(row)
print(f"  ✅ {out2} ({len(exec_pos)} 个执行位)")

# ============================================================
# 输出 3: SKU 归位明细
# ============================================================

print("\n" + "="*80)
print("输出 3: G4-A_深调V1_SKU归位明细_v0.3.csv")
print("="*80)

g4a.sort(key=lambda r: (r['_zone'], -float(r.get('日均销量') or 0)))

out3 = os.path.join(OUT_DIR, "G4-A_深调V1_SKU归位明细_v0.3.csv")
with open(out3, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['归位组', '建议层位', 'L3', 'L4', '条码', '品名', '品牌', '规格', '售价',
                '日均销量', '当前库存', '预可售天数', '动作', '角色判据'])
    for r in g4a:
        # 角色判据描述
        name = str(r.get('品名', ''))
        spec = str(r.get('规格', ''))
        price = float(r.get('售价') or 0)
        l4 = str(r.get('L4', ''))
        criteria = []
        if is_large_package(spec, name):
            criteria.append('大包装')
        if has_keyword(name, FUNCTIONAL_KEYWORDS) or has_keyword(l4, FUNCTIONAL_KEYWORDS):
            criteria.append('功能型')
        if price >= 30 and has_keyword(name, PREMIUM_KEYWORDS):
            criteria.append('升级款')
        if price >= 50:
            criteria.append('高价段')
        if has_keyword(name, SPECIAL_FLAVOR_KEYWORDS):
            criteria.append('特色风味')
        if price <= 10:
            criteria.append('低价引流')
        criteria_str = '/'.join(criteria) if criteria else '默认主销'

        w.writerow([
            r['_zone'], r['_layer'], r['L3'], r['L4'], r['条码'], r['品名'],
            r['品牌'], r['规格'], r['售价'],
            r.get('日均销量'), r['当前库存'], r['预可售天数'],
            r['_action'], criteria_str,
        ])
print(f"  ✅ {out3}")

# 各组动作分布
print(f"\n各组动作分布:")
for zone, _, _ in ZONES:
    rows = [r for r in g4a if r['_zone'] == zone]
    if rows:
        actions = Counter(r['_action'] for r in rows)
        print(f"  {zone:25s}: {dict(actions)}")

# 顶部畅销 + 关键风险
print(f"\n各组 TOP 销量 SKU:")
for zone, _, _ in ZONES:
    rows = sorted([r for r in g4a if r['_zone'] == zone], key=lambda r: -float(r.get('日均销量') or 0))
    if rows:
        top = rows[0]
        print(f"  {zone}: [{float(top.get('日均销量') or 0):.2f}/天] {top['品名'][:30]} ¥{float(top.get('售价') or 0):.1f}")
