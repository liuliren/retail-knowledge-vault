#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
7D 现场打分工具 v0.1（draft·未经校准）
========================================
用法:
    python3 score_7d.py <打分单.yaml|.json> [--no-png]

输入: 一份 YAML/JSON 打分单(见同目录 打分单模板.yaml)
输出:
    1) 控制台: 7 维得分表 + 加权总分 + 证据等级分布
    2) 同目录: 7D打分结果_<门店代号>_<日期>.md (ASCII 条形 + judgment 边界声明)
    3) 可选: PNG 雷达图(matplotlib 可用时; 失败不阻断)

权重来源(SSOT·照抄不改):
    KB-DX-FULLSTORE-001_全店7D诊断框架2.0_v0.1.md
    - §1 七维度总览与权重表(D1=20/D2=25/D3=10/D4=15/D5=15/D6=10/D7=5, 满分100)
    - §8 POS 生鲜占比校准公式(D2=min(45,25*f/0.42); D1=max(0,min(25,20*(1-f)/0.58));
      D6/D7 不参与校准; D3:D4:D5=10:15:15 等比填充剩余; f<27.5% 时 D1 触顶 25)
    - §3 D6② 雇员再分配(夫妻店 D6=0, 10 分按 D2:D5=6:4 并入; 1-4 雇员灰区 D6=5)
    - §7 证据分级 A-E(C/D/E 禁写精确结论)
    注意: 框架本身 status=draft(审议轮次2·未签字), §9① 权重与校准分母
    均为花厅坊单例 inferred——本工具全部输出同为 draft, 未经多店校准。

打分纪律(2026-07-04 花厅坊首诊卡 v1.1 修订·六哥挑战后定):
    - 证据 C/D/E 级维度只给"档位(强/中偏强/中/中偏弱/弱)+证据级",
      **不写假精确百分数**。
    - 7 维证据级不齐时, 不硬凑一个精确总分对外; 全维加权总分仅标
      "内部参考·禁对外引用精确分"。
    - 判断相在六哥: 工具只算加权, 打分裁量、维度证据级覆盖(override_grade)、
      最终判定与签字均归六哥。

零第三方硬依赖: YAML 优先用 PyYAML, 缺失时回退内置迷你解析器(仅支持模板结构);
matplotlib 仅用于可选 PNG 雷达, 缺失/报错自动跳过。
"""

import json
import os
import re
import sys
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# 维度与子项定义 (照抄 KB-DX-FULLSTORE-001 §1 权重表 + §3 各维 ③关键诊断指标)
# ---------------------------------------------------------------------------
DIMENSIONS = {
    "D1": {
        "name": "商品力(品类结构)",
        "base_weight": 20.0,   # §1 表: D1 固定权重 20
        "items": {
            "D1-1": "ABC-Z结构健康度(A类占最佳位/Z类占比)",
            "D1-2": "五态宽度空缺数(空缺-紧急态品类数)",
            "D1-3": "价格带完整度(三档齐/无空档重叠)",
            "D1-4": "CR5品牌集中度",
            "D1-5": "空销率(30天0动销/在档SKU)",
        },
    },
    "D2": {
        "name": "生鲜运营",
        "base_weight": 25.0,   # §1 表: D2 固定权重 25(权重最高·护城河)
        "items": {
            "D2-1": "生鲜销售占比f(≥40稳固/30-40待改善/<30失守)",
            "D2-2": "肉类日清率(阶梯打折/无隔夜肉)",
            "D2-3": "品种结构完整度(叶菜≥10种/猪肉三档/清远鸡)",
            "D2-4": "损耗率by子品类(叶菜≤8%/水果≤5%/肉≤5%)",
            "D2-5": "生鲜毛利率(口径警示:ERP进价常虚高)",
        },
    },
    "D3": {
        "name": "陈列空间",
        "base_weight": 10.0,   # §1 表: D3 固定权重 10
        "items": {
            "D3-1": "销售-陈列比错配数(>1.5或<0.5的品类数)",
            "D3-2": "黄金层A类占有率(1.4-1.6m视线层)",
            "D3-3": "时间效率(30秒找到率/5分钟采购完成比)",
            "D3-4": "端架/堆头有效性(推A类/季节品)",
        },
    },
    "D4": {
        "name": "客流人效",
        "base_weight": 15.0,   # §1 表: D4 固定权重 15
        "items": {
            "D4-1": "客单数趋势(代理客流·标注非真实人次)",
            "D4-2": "增长归因(危险信号=客流降+客单价涨)",
            "D4-3": "时段客流分布(排班匹配高峰)",
            "D4-4": "时段人效(高峰单量/在岗人时)",
            "D4-5": "可观测性+数据意识(设备/老板看数)",
        },
    },
    "D5": {
        "name": "财务健康",
        "base_weight": 15.0,   # §1 表: D5 固定权重 15
        "items": {
            "D5-1": "综合毛利率(基准20-25%)",
            "D5-2": "综合周转天数(<结算周期30-45天·现金流硬红线)",
            "D5-3": "GMROI(健康≥2.5)",
            "D5-4": "库存坪效(月销售额/卖场面积)",
            "D5-5": "盈亏平衡/现金周期",
        },
    },
    "D6": {
        "name": "人员运营",
        "base_weight": 10.0,   # §1 表: D6 固定权重 10(全新维度)
        "items": {
            "D6-1": "人工成本占比(基准8-12%)",
            "D6-2": "关键岗位技能完整度(生鲜加工/收银/陈列)",
            "D6-3": "人员成本效率(销售额/人工总成本)",
            "D6-4": "排班合理性(无单点依赖)",
            "D6-5": "人员稳定性(近6月流失/在职时长)",
        },
    },
    "D7": {
        "name": "顾客体验",
        "base_weight": 5.0,    # §1 表: D7 固定权重 5
        "items": {
            "D7-1": "复购代理(活跃会员占比/复购率)",
            "D7-2": "服务质量(收银速度/态度/称重纠纷)",
            "D7-3": "称重诚信(缺斤少两/价签一致性)",
            "D7-4": "口碑代理(线上评分/社群活跃)",
            "D7-5": "熟客关系深度(老板叫得出常客)",
        },
    },
}

DIM_ORDER = ["D1", "D2", "D3", "D4", "D5", "D6", "D7"]
GRADES = ["A", "B", "C", "D", "E"]           # §7 证据分级 A-E, A 最强
LOW_GRADES = {"C", "D", "E"}                 # 禁写精确% 的证据级
MAX_ITEM_SCORE = 5.0                          # 子项打分 0-5(5=满分锚点达标)

# 档位映射(工具层约定·draft): 得分率 -> 定性档位
BANDS = [
    (0.80, "强"),
    (0.65, "中偏强"),
    (0.50, "中"),
    (0.35, "中偏弱"),
    (0.00, "弱"),
]


def band_of(rate):
    for lo, label in BANDS:
        if rate >= lo:
            return label
    return "弱"


# ---------------------------------------------------------------------------
# 迷你 YAML 解析器(降级路径·仅支持模板的两/三层缩进结构)
# ---------------------------------------------------------------------------
def _coerce(v):
    v = v.strip()
    if v == "" or v.lower() in ("null", "~", "none"):
        return None
    if v.lower() == "true":
        return True
    if v.lower() == "false":
        return False
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        return v[1:-1]
    try:
        return int(v)
    except ValueError:
        pass
    try:
        return float(v)
    except ValueError:
        pass
    return v


def mini_yaml_load(text):
    """极简 YAML 子集解析: 仅 key: value 与嵌套 dict(空格缩进), 无列表/多行值。"""
    root = {}
    stack = [(-1, root)]
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip() if not raw.strip().startswith("#") else ""
        # 保留值内含 # 的引号串: 简化处理——若去注释后引号不配对则用原行
        if raw.strip() and not raw.strip().startswith("#"):
            candidate = raw.rstrip("\n")
            hash_idx = candidate.find(" #")
            line = candidate[:hash_idx].rstrip() if hash_idx != -1 else candidate
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        if ":" not in line:
            continue
        key, _, val = line.lstrip().partition(":")
        key = key.strip().strip('"').strip("'")
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if val.strip() == "":
            child = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = _coerce(val)
    return root


def load_sheet(path):
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    if path.lower().endswith(".json"):
        return json.loads(text)
    try:
        import yaml  # type: ignore
        return yaml.safe_load(text)
    except ImportError:
        sys.stderr.write("[提示] 未装 PyYAML, 使用内置迷你解析器(仅支持模板结构)。\n")
        return mini_yaml_load(text)


# ---------------------------------------------------------------------------
# 权重计算 (KB-DX-FULLSTORE-001 §8 校准公式 + §3 D6② 雇员再分配·照抄)
# ---------------------------------------------------------------------------
def compute_weights(fresh_ratio, employee_mode):
    """
    返回 (weights: {dim: w}, notes: [str])
    fresh_ratio: POS 生鲜占比 f (0-1), None = 不校准, 用 §1 固定权重
    employee_mode: 'full'(≥5雇员) / 'gray'(1-4雇员) / 'none'(纯夫妻店)
    """
    notes = []
    if fresh_ratio is None:
        w = {d: DIMENSIONS[d]["base_weight"] for d in DIM_ORDER}
        notes.append("未提供生鲜占比 f → 使用 §1 固定权重(20/25/10/15/15/10/5)。")
    else:
        f = float(fresh_ratio)
        if not (0.0 <= f <= 1.0):
            raise ValueError("fresh_ratio 须在 0-1 之间(如 0.42)")
        # §8: D2_final = min(45, 25*f/0.42); D1_final = max(0, min(25, 20*(1-f)/0.58))
        d2 = min(45.0, 25.0 * f / 0.42)
        d1 = max(0.0, min(25.0, 20.0 * (1.0 - f) / 0.58))
        # §8: D6/D7 合计15不参与校准; 剩余 85-D2-D1 按 D3:D4:D5=10:15:15 等比
        resid = 85.0 - d2 - d1
        d3 = resid * 10.0 / 40.0
        d4 = resid * 15.0 / 40.0
        d5 = resid * 15.0 / 40.0
        w = {"D1": d1, "D2": d2, "D3": d3, "D4": d4, "D5": d5,
             "D6": 10.0, "D7": 5.0}
        notes.append(
            "已按 §8 POS 生鲜占比校准: f={:.2%} → D2={:.1f} D1={:.1f} "
            "D3={:.1f} D4={:.1f} D5={:.1f} (D6/D7 固定)。".format(f, d2, d1, d3, d4, d5))
        if f < 0.30:
            notes.append("⚠ f<30% 触发『护城河失守』标注(§3 D2②), 权重仅供参考, 须在 D8 注明经营模式异常。")
        if f > 0.756:
            notes.append("⚠ f>75.6% 已入 D2 触顶非单调区(§8 公式边界·§9①待裁决), 结果解释须谨慎。")
    # §3 D6②: 夫妻店/灰区再分配
    if employee_mode == "none":
        moved = w["D6"]
        w["D2"] += moved * 0.6
        w["D5"] += moved * 0.4
        w["D6"] = 0.0
        notes.append("纯夫妻店: D6 权重置 0, 其 {:.0f} 分按 D2:D5=6:4 并入(§3 D6②), 须在 D8 注明。".format(moved))
    elif employee_mode == "gray":
        moved = w["D6"] - 5.0
        if moved > 0:
            w["D2"] += moved * 0.6
            w["D5"] += moved * 0.4
            w["D6"] = 5.0
            notes.append("1-4 雇员灰区: D6 取 5 分(§3 D6②线性插值), 余 {:.0f} 分按 6:4 并入 D2/D5"
                         "(并入去向为工具层推断·框架未明文·待校准)。".format(moved))
    total = sum(w.values())
    if abs(total - 100.0) > 0.05:
        notes.append("⚠ 权重合计 {:.2f} ≠ 100, 请核对输入。".format(total))
    return w, notes


# ---------------------------------------------------------------------------
# 打分
# ---------------------------------------------------------------------------
GRADE_RANK = {g: i for i, g in enumerate(GRADES)}  # A=0 最强


def score_dimension(dim_id, dim_input):
    """返回 dict: rate(0-1|None), grade(str|None), n_scored, items detail, override"""
    items_def = DIMENSIONS[dim_id]["items"]
    items_in = (dim_input or {}).get("items", {}) or {}
    detail, scores, grades = [], [], []
    for iid, label in items_def.items():
        raw = items_in.get(iid) or {}
        s = raw.get("score")
        g = raw.get("evidence")
        note = raw.get("note") or ""
        if isinstance(g, str):
            g = g.strip().upper()
            if g not in GRADES:
                raise ValueError("{} 证据等级非法: {} (须 A-E)".format(iid, g))
        if s is not None:
            s = float(s)
            if not (0 <= s <= MAX_ITEM_SCORE):
                raise ValueError("{} score={} 越界(0-{})".format(iid, s, MAX_ITEM_SCORE))
            if g is None:
                raise ValueError("{} 已打分但缺证据等级 evidence(A-E 必填)".format(iid))
            scores.append(s)
            grades.append(g)
        detail.append({"id": iid, "label": label, "score": s, "grade": g, "note": note})
    rate = (sum(scores) / (len(scores) * MAX_ITEM_SCORE)) if scores else None
    # 维度证据级 = 已打分子项中最弱一级(fail-safe·查不到=最严格);
    # 六哥可用 override_grade 行使裁量覆盖(判断相归六哥)
    auto_grade = max(grades, key=lambda g: GRADE_RANK[g]) if grades else None
    override = dim_input.get("override_grade") if dim_input else None
    if isinstance(override, str):
        override = override.strip().upper()
        if override not in GRADES:
            raise ValueError("{} override_grade 非法: {}".format(dim_id, override))
    grade = override or auto_grade
    return {"rate": rate, "grade": grade, "auto_grade": auto_grade,
            "override": override, "n_scored": len(scores),
            "n_items": len(items_def), "detail": detail}


# ---------------------------------------------------------------------------
# 呈现
# ---------------------------------------------------------------------------
def ascii_bar(rate, width=30):
    if rate is None:
        return "(未评)".ljust(width)
    n = int(round(rate * width))
    return "█" * n + "░" * (width - n)


def fmt_rate(rate, grade):
    """C/D/E 级禁写精确%——只给档位。"""
    if rate is None:
        return "未评"
    if grade in LOW_GRADES:
        return "档位:{}".format(band_of(rate))
    return "{:.0f}% ({})".format(rate * 100, band_of(rate))


def run(sheet_path, make_png=True):
    data = load_sheet(sheet_path)
    meta = data.get("meta", {}) or {}
    store = str(meta.get("store_code") or "UNKNOWN")
    date = str(meta.get("date") or datetime.date.today().isoformat())
    scorer = str(meta.get("scorer") or "")
    f = meta.get("fresh_ratio")
    emp = str(meta.get("employee_mode") or "full").strip().lower()
    if emp not in ("full", "gray", "none"):
        raise ValueError("employee_mode 须为 full/gray/none")

    weights, wnotes = compute_weights(f, emp)
    dims_in = data.get("dimensions", {}) or {}
    results = {d: score_dimension(d, dims_in.get(d)) for d in DIM_ORDER}

    # 加权计算(§1: 总分 = Σ 得分率×权重/100 ×100 → 即 Σ 得分率×权重)
    weighted_total, covered_w = 0.0, 0.0            # 全维参考总分(内部)
    solid_score, solid_w = 0.0, 0.0                 # B级及以上"实证半张卡"
    grade_dist = {g: 0 for g in GRADES}
    for d in DIM_ORDER:
        r = results[d]
        for it in r["detail"]:
            if it["grade"]:
                grade_dist[it["grade"]] += 1
        if r["rate"] is not None and weights[d] > 0:
            weighted_total += r["rate"] * weights[d]
            covered_w += weights[d]
            if r["grade"] not in LOW_GRADES:
                solid_score += r["rate"] * weights[d]
                solid_w += weights[d]
    low_dims = [d for d in DIM_ORDER
                if results[d]["grade"] in LOW_GRADES and weights[d] > 0]
    unscored = [d for d in DIM_ORDER
                if results[d]["rate"] is None and weights[d] > 0]
    evidence_uneven = bool(low_dims) or bool(unscored)

    # ------------------------- 控制台输出 -------------------------
    W = 78
    print("=" * W)
    print("7D 现场打分结果 · {} · {}   (工具 v0.1 draft·权重未经多店校准)".format(store, date))
    if scorer:
        print("打分人: {}   (打分裁量与最终判定归六哥, 工具只算加权)".format(scorer))
    print("=" * W)
    for n in wnotes:
        print("· " + n)
    print("-" * W)
    print("{:<4} {:<14} {:>6} {:>7} {:>5}  {}".format("维", "名称", "权重", "得分", "证据", "呈现"))
    print("-" * W)
    for d in DIM_ORDER:
        r, w = results[d], weights[d]
        g = r["grade"] or "-"
        gmark = g + ("*" if r["override"] else "")
        print("{:<4} {:<14} {:>6.1f} {:>7} {:>5}  {}".format(
            d, DIMENSIONS[d]["name"], w,
            ("-" if r["rate"] is None else "{:.0f}%".format(r["rate"] * 100)
             if g not in LOW_GRADES else "见档位"),
            gmark, fmt_rate(r["rate"], r["grade"])))
    print("-" * W)
    print("证据等级分布(子项计): " + "  ".join(
        "{}:{}".format(g, grade_dist[g]) for g in GRADES) +
        "   (*=六哥 override)")
    print("-" * W)
    if evidence_uneven:
        print("■ 判定模式: 结构化判定(证据级不齐·不凑对外精确总分——07-04 首诊卡 v1.1 纪律)")
        if solid_w > 0:
            print("  B级及以上实证维加权: {:.1f} / {:.1f} 权重 (得分率 {:.0f}%) —— 可对外的\"半张卡\"".format(
                solid_score, solid_w, solid_score / solid_w * 100))
        if low_dims:
            print("  C/D/E 级维(仅方向性参考·禁写精确%): " + ", ".join(
                "{}={}".format(d, band_of(results[d]["rate"])) for d in low_dims))
        if unscored:
            print("  未评维(待采数据): " + ", ".join(unscored))
        print("  全维加权参考: {:.1f} / {:.1f} —— 仅内部参考·禁对外引用精确分".format(
            weighted_total, covered_w))
    else:
        print("■ 7D 加权总分: {:.1f} / {:.1f}".format(weighted_total, covered_w))
    print("=" * W)

    # ------------------------- Markdown 报告 -------------------------
    md_path = os.path.join(HERE, "7D打分结果_{}_{}.md".format(store, date))
    png_name = "7D雷达_{}_{}.png".format(store, date)
    png_ok = False
    if make_png:
        png_ok = try_radar_png(results, weights, os.path.join(HERE, png_name), store, date)
    write_md(md_path, store, date, scorer, f, emp, weights, wnotes, results,
             grade_dist, weighted_total, covered_w, solid_score, solid_w,
             low_dims, unscored, evidence_uneven, png_name if png_ok else None)
    print("已生成: {}".format(md_path))
    if png_ok:
        print("已生成: {}".format(os.path.join(HERE, png_name)))
    return md_path


def write_md(path, store, date, scorer, f, emp, weights, wnotes, results,
             grade_dist, weighted_total, covered_w, solid_score, solid_w,
             low_dims, unscored, evidence_uneven, png_name):
    L = []
    L.append("---")
    L.append("title: 7D打分结果_{}_{}".format(store, date))
    L.append("version: v0.1")
    L.append("status: draft")
    L.append("owner: 六哥")
    L.append("source_type: diagnosis_scorecard")
    L.append("client_safety: internal_only")
    L.append("fact_layer: mixed")
    L.append("summary: 7D打分工具v0.1对{}的打分输出;权重据KB-DX-FULLSTORE-001(draft),C级维仅档位".format(store))
    L.append("tags: [7D诊断, 打分工具, draft]")
    L.append("---")
    L.append("")
    L.append("# 7D 打分结果 · {} · {}".format(store, date))
    L.append("")
    L.append("> **judgment 边界声明**:本表由 `score_7d.py v0.1(draft)` 生成——工具只做加权算术;")
    L.append("> 打分裁量、维度证据级覆盖与最终判定**均在六哥**(90/10 的 10%,不可代签)。")
    L.append("> 权重照抄 [[KB-DX-FULLSTORE-001_全店7D诊断框架2.0_v0.1]](§1/§8/§3-D6②),该框架本身")
    L.append("> status=draft(§9①权重为花厅坊单例 inferred·未签字),故本结果全链 draft,不得对外引用为定论。")
    L.append("> **C/D/E 级证据维度只给档位,禁写精确%**(07-04 花厅坊首诊卡 v1.1 打分纪律)。")
    L.append("")
    if scorer:
        L.append("- 打分人: {}".format(scorer))
    L.append("- 生鲜占比 f: {}".format("{:.2%}".format(float(f)) if f is not None else "未提供(用固定权重)"))
    L.append("- 雇员档: {}".format({"full": "≥5人(D6全额)", "gray": "1-4人灰区(D6=5)",
                                    "none": "纯夫妻店(D6=0并入D2/D5)"}[emp]))
    for n in wnotes:
        L.append("- {}".format(n))
    L.append("")
    L.append("## 一、七维得分表(条形呈现)")
    L.append("")
    L.append("| 维 | 名称 | 权重 | 呈现 | 证据级 | 条形(得分率) |")
    L.append("|---|---|---:|---|:---:|---|")
    for d in DIM_ORDER:
        r, w = results[d], weights[d]
        g = (r["grade"] or "-") + ("※" if r["override"] else "")
        low_flag = " ⚠仅方向性参考·禁写精确%" if r["grade"] in LOW_GRADES else ""
        L.append("| {} | {} | {:.1f} | {}{} | {} | `{}` |".format(
            d, DIMENSIONS[d]["name"], w, fmt_rate(r["rate"], r["grade"]), low_flag,
            g, ascii_bar(r["rate"])))
    L.append("")
    L.append("(※=六哥 override_grade 裁量覆盖;条形为得分率示意,C级维条形仅方向性)")
    if png_name:
        L.append("")
        L.append("![7D雷达]({})".format(png_name))
    L.append("")
    L.append("## 二、总判定")
    L.append("")
    if evidence_uneven:
        L.append("**结构化判定模式**——7 维证据级不齐,不凑对外精确总分(07-04 首诊卡 v1.1 纪律):")
        L.append("")
        if solid_w > 0:
            L.append("- **B级及以上实证维(可对外\"半张卡\")**: 加权 {:.1f} / {:.1f} 权重,得分率 **{:.0f}%**".format(
                solid_score, solid_w, solid_score / solid_w * 100))
        if low_dims:
            L.append("- **C/D/E 级维(仅方向性参考·禁写精确%)**: " + "; ".join(
                "{} {} → **{}**".format(d, DIMENSIONS[d]["name"], band_of(results[d]["rate"]))
                for d in low_dims))
        if unscored:
            L.append("- **未评维(待采数据)**: " + ", ".join(unscored))
        L.append("- 全维加权参考: {:.1f} / {:.1f} —— **仅内部参考·禁对外引用精确分**".format(
            weighted_total, covered_w))
    else:
        L.append("- **7D 加权总分: {:.1f} / {:.1f}**(全维证据 ≥B 级)".format(weighted_total, covered_w))
    L.append("")
    L.append("## 三、证据等级分布(子项计·§7 A-E)")
    L.append("")
    L.append("| A | B | C | D | E |")
    L.append("|---|---|---|---|---|")
    L.append("| {} | {} | {} | {} | {} |".format(*[grade_dist[g] for g in GRADES]))
    L.append("")
    L.append("## 四、子项明细(证据链)")
    L.append("")
    for d in DIM_ORDER:
        r = results[d]
        L.append("### {} {}(权重 {:.1f} · 维度证据级 {})".format(
            d, DIMENSIONS[d]["name"], weights[d], r["grade"] or "未评"))
        L.append("")
        L.append("| 子项 | 指标 | 得分(0-5) | 证据级 | 证据一句话 |")
        L.append("|---|---|---:|:---:|---|")
        for it in r["detail"]:
            L.append("| {} | {} | {} | {} | {} |".format(
                it["id"], it["label"],
                "-" if it["score"] is None else "{:g}".format(it["score"]),
                it["grade"] or "-", it["note"] or "-"))
        L.append("")
    L.append("---")
    L.append("*生成: score_7d.py v0.1 · {} · D8 顾问综合判断留空待六哥(框架 §5 操作规则:"
             "D8 待补状态下不得作为正式交付件对外输出)。*".format(
                 datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
    L.append("")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))


def try_radar_png(results, weights, png_path, store, date):
    """可选 matplotlib 雷达图; 任何异常直接放弃, 不阻断主流程。"""
    try:
        import math
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        labels, vals = [], []
        for d in DIM_ORDER:
            labels.append(d)
            r = results[d]["rate"]
            vals.append(0.0 if r is None else r)
        angles = [i * 2 * math.pi / len(labels) for i in range(len(labels))]
        angles += angles[:1]
        vals += vals[:1]
        fig = plt.figure(figsize=(5, 5))
        ax = fig.add_subplot(111, polar=True)
        ax.plot(angles, vals, linewidth=2)
        ax.fill(angles, vals, alpha=0.25)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels)
        ax.set_ylim(0, 1)
        # 标题用 ASCII, 避免默认字体缺 CJK 字形出豆腐字
        ax.set_title("7D {} {} (draft / C-grade dims: direction only)".format(store, date),
                     fontsize=9)
        fig.savefig(png_path, dpi=120, bbox_inches="tight")
        plt.close(fig)
        return True
    except Exception as exc:  # noqa: BLE001 — 可选功能, 失败不阻断
        sys.stderr.write("[提示] 雷达 PNG 生成跳过: {}\n".format(exc))
        return False


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    make_png = "--no-png" not in argv
    if not args:
        print(__doc__)
        sys.exit(1)
    path = args[0]
    if not os.path.isfile(path):
        sys.exit("找不到打分单: {}".format(path))
    run(path, make_png=make_png)


if __name__ == "__main__":
    main(sys.argv)
