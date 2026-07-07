# -*- coding: utf-8 -*-
"""
category_pos_cleaner v0.2 · Phase-Z 实验件（draft，mock 数据专用，未经六哥签字不得用于真实客户数据）

必答 10 问
1. 解决什么：v0.1 的两大已知缺陷——误伤（无排除词）与多候选乱裁（行序即真理）。
   引入 exclude 一票否决、alias 同义扩展、priority 裁决、人工复核标记。
2. 输入字段：同 v0.1；品类表额外消费 alias / exclude_keywords / mapping_priority /
   manual_review_required 四列（category_table v2+）。
3. 输出表：v02_mapping.csv（+命中候选数/复核标记列）、v02_unmatched.csv（原因细分：
   无命中 / 全部候选被排除词否决）、v02_review.csv（需人工复核行）。
4. 异常：同 v0.1；alias 格式非法（无=号）跳过并记警告。
5. 未匹配：先收集全部候选再裁决；候选为 0 → unmatched，并区分"从未命中"vs"命中但被排除"。
6. 多候选：收集全部命中 → 排除词否决 → 按 mapping_priority 降序取最高；打平 → 全组进复核。
7. 人工复核：三种触发——① 品类 manual_review_required=Y；② priority 打平；
   ③ 商品挂靠候选≥3（关键词过热信号）。
8. 相比上版提升：陷阱品（牛奶糖/冰红茶/苹果醋饮/鱼皮花生等）不再误入；裁决顺序确定、可解释。
9. 不能处理什么：无量化评分与置信分级（priority 是品类级先验，不是命中强度）；
   无多轮循环、无批处理、无质量报告；原POS分类信息完全没用上。
10. 是否作下轮基础：是——候选收集/否决/裁决框架被 v0.3 继承并加评分层。
"""
import csv
import logging
import sys

# 复用 v0.1 的基础件（同目录）
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location(
    "cleaner_v01", __file__.rsplit("/", 1)[0] + "/category_pos_cleaner_v0.1.py")
_v01 = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_v01)
normalize_name, detect_fields = _v01.normalize_name, _v01.detect_fields

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("cleaner_v0.2")


def load_rules_v2(path):
    rules = []
    with open(path, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    need = {"keywords", "exclude_keywords", "mapping_priority"}
    if not rows or not need.issubset(rows[0].keys()):
        raise SystemExit("品类表需 v2+ 格式（keywords/exclude_keywords/mapping_priority）")
    for r in rows:
        kws = [k for k in (r.get("keywords") or "").split("|") if k]
        if not kws:
            continue
        aliases = {}
        for pair in (r.get("alias") or "").split("|"):
            if "=" in pair:
                a, b = pair.split("=", 1)
                aliases[a.strip()] = b.strip()
            elif pair.strip():
                log.warning("alias 格式非法，跳过: %r (%s)", pair, r["category_code"])
        rules.append({
            "code": r["category_code"], "L1": r["L1"], "L2": r["L2"],
            "L3": r["L3"], "L4": r["L4"], "keywords": kws, "aliases": aliases,
            "excludes": [e for e in (r.get("exclude_keywords") or "").split("|") if e],
            "priority": int(r.get("mapping_priority") or 0),
            "review": (r.get("manual_review_required") or "N").strip().upper() == "Y",
        })
    log.info("载入映射规则 %d 条", len(rules))
    return rules


def is_excluded(norm_name, rule):
    return any(e and e in norm_name for e in rule["excludes"])


def collect_candidates(norm_name, rules):
    """返回 (候选列表, 被排除数)。候选=关键词或 alias 命中且未被排除词否决。"""
    cands, vetoed = [], 0
    for rule in rules:
        name2 = norm_name
        for a, b in rule["aliases"].items():
            name2 = name2.replace(a, b)
        hit = next((kw for kw in rule["keywords"] if kw in name2), None)
        if not hit:
            continue
        if is_excluded(norm_name, rule):
            vetoed += 1
            continue
        cands.append((rule, hit))
    return cands, vetoed


def adjudicate(cands):
    """按 priority 降序裁决。返回 (winner, hit_kw, tie:bool)。"""
    cands = sorted(cands, key=lambda c: -c[0]["priority"])
    top_p = cands[0][0]["priority"]
    tied = [c for c in cands if c[0]["priority"] == top_p]
    return tied[0][0], tied[0][1], len(tied) > 1


def run(goods_path, cat_path, outdir="."):
    rules = load_rules_v2(cat_path)
    with open(goods_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        goods = list(reader)
    fmap = detect_fields(headers)
    matched, unmatched, review = [], [], []
    for g in goods:
        norm = normalize_name(g.get(fmap["name"], ""))
        cands, vetoed = collect_candidates(norm, rules)
        base = dict(g)
        base["标准化名称"] = norm
        if not cands:
            base["未匹配原因"] = "命中但全被排除词否决" if vetoed else "无关键词命中"
            unmatched.append(base)
            continue
        rule, kw, tie = adjudicate(cands)
        base.update({"category_code": rule["code"], "L1": rule["L1"], "L2": rule["L2"],
                     "L3": rule["L3"], "L4": rule["L4"], "命中词": kw,
                     "候选数": len(cands)})
        reasons = []
        if rule["review"]:
            reasons.append("品类强制复核")
        if tie:
            reasons.append("priority打平")
        if len(cands) >= 3:
            reasons.append("候选过多")
        base["复核标记"] = ";".join(reasons)
        matched.append(base)
        if reasons:
            review.append(base)
    _v01._write(f"{outdir}/v02_mapping.csv", matched)
    _v01._write(f"{outdir}/v02_unmatched.csv", unmatched)
    _v01._write(f"{outdir}/v02_review.csv", review)
    log.info("完成：%d 命中(其中 %d 需复核) / %d 未匹配 / 共 %d",
             len(matched), len(review), len(unmatched), len(goods))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python3 category_pos_cleaner_v0.2.py <商品表.csv> <品类表.csv> [输出目录]")
        raise SystemExit(1)
    run(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else ".")
