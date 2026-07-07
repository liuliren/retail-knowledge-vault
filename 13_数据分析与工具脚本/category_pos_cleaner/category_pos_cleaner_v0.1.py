# -*- coding: utf-8 -*-
"""
category_pos_cleaner v0.1 · Phase-Z 实验件（draft，mock 数据专用，未经六哥签字不得用于真实客户数据）

必答 10 问
1. 解决什么：POS 商品表"品类脏"的第一刀——字段自动识别 + 商品名标准化 + 关键词单遍映射，
   把"名称→品类"从人肉判断变成可复现程序动作。
2. 输入字段：商品表 csv（名称必需；条码/货号/规格/原POS分类/售价 可选，表头模糊识别）；
   品类表 csv（category_table v2+ 格式，用 category_code/L1-L4/keywords）。
3. 输出表：mapping.csv（命中行：原字段+标准化名+category_code+L1-L4+命中词）、
   unmatched.csv（未命中行+原因）。
4. 异常：缺名称列→报错退出；品类表无 keywords 列→报错退出；空行/缺条码→照常处理并记日志。
5. 未匹配：单遍关键词扫不中即落 unmatched.csv，不猜。
6. 多候选：不处理——按品类表行序取第一个命中（已知缺陷，v0.2 解决）。
7. 人工复核：无复核概念（已知缺陷，v0.2 解决）。
8. 相比上版提升：首版，无上版。
9. 不能处理什么：排除词误伤（"牛奶糖"会误进牛奶）、多候选裁决、置信度、批处理、
   与原POS分类的冲突检测、真实POS格式坑（那是 POS清洗库 的职责）。
10. 是否作下轮基础：是——normalize/detect_fields/load 三件被 v0.2 继承。
"""
import csv
import logging
import re
import sys
import unicodedata

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("cleaner_v0.1")

FIELD_CANDIDATES = {
    "name": ["商品名称", "品名", "名称", "商品名"],
    "barcode": ["条码", "barcode", "国条", "条形码"],
    "sku_no": ["货号", "商品编码", "编码"],
    "spec": ["规格", "规格型号"],
    "old_cat": ["原POS分类", "分类", "类别", "品类"],
    "price": ["售价", "单价", "零售价"],
}

SPEC_RE = re.compile(
    r"[（(]?\d+(?:\.\d+)?\s*(?:g|kg|ml|l|克|千克|毫升|升|片|枚|卷|抽|粒|双|只|支|听|罐|袋|盒|包|连包)"
    r"(?:[*×xX]\d+)?[)）]?", re.IGNORECASE)


def to_halfwidth(s: str) -> str:
    return unicodedata.normalize("NFKC", s)


def normalize_name(name: str) -> str:
    s = to_halfwidth(str(name or ""))
    s = s.replace("×", "*")
    s = SPEC_RE.sub("", s)
    s = re.sub(r"\s+", "", s)
    return s.strip()


def detect_fields(headers):
    mapping = {}
    for key, cands in FIELD_CANDIDATES.items():
        for h in headers:
            hn = to_halfwidth(h).strip()
            if any(c == hn or c in hn for c in cands):
                mapping[key] = h
                break
    log.info("字段识别结果: %s", mapping)
    if "name" not in mapping:
        raise SystemExit("致命错误：找不到商品名称列，表头=%s" % headers)
    return mapping


def load_category_rules(path):
    rules = []
    with open(path, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if not rows or "keywords" not in rows[0]:
        raise SystemExit("品类表缺 keywords 列（需 category_table v2+ 格式）")
    for r in rows:
        kws = [k for k in (r.get("keywords") or "").split("|") if k]
        if not kws:
            continue
        rules.append({"code": r["category_code"], "L1": r["L1"], "L2": r["L2"],
                      "L3": r["L3"], "L4": r["L4"], "keywords": kws})
    log.info("载入映射规则 %d 条", len(rules))
    return rules


def match_one(norm_name, rules):
    """单遍：返回第一个关键词命中的规则（行序优先）。"""
    for rule in rules:
        for kw in rule["keywords"]:
            if kw and kw in norm_name:
                return rule, kw
    return None, None


def run(goods_path, cat_path, outdir="."):
    rules = load_category_rules(cat_path)
    with open(goods_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        goods = list(reader)
    fmap = detect_fields(headers)
    matched, unmatched = [], []
    for g in goods:
        raw = g.get(fmap["name"], "")
        norm = normalize_name(raw)
        rule, kw = match_one(norm, rules)
        base = dict(g)
        base["标准化名称"] = norm
        if rule:
            base.update({"category_code": rule["code"], "L1": rule["L1"], "L2": rule["L2"],
                         "L3": rule["L3"], "L4": rule["L4"], "命中词": kw})
            matched.append(base)
        else:
            base["未匹配原因"] = "无关键词命中"
            unmatched.append(base)
    _write(f"{outdir}/v01_mapping.csv", matched)
    _write(f"{outdir}/v01_unmatched.csv", unmatched)
    log.info("完成：%d 命中 / %d 未匹配 / 共 %d", len(matched), len(unmatched), len(goods))


def _write(path, rows):
    if not rows:
        open(path, "w").close()
        return
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python3 category_pos_cleaner_v0.1.py <商品表.csv> <品类表.csv> [输出目录]")
        raise SystemExit(1)
    run(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else ".")
