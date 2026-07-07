# -*- coding: utf-8 -*-
"""
category_pos_cleaner v0.3 · Phase-Z 实验件（draft，mock 数据专用，未经六哥签字不得用于真实客户数据）

必答 10 问
1. 解决什么：把 v0.2 的"能裁"升级为"可量化、可收敛、可交付"——命中评分 + 置信分级 +
   多轮双重循环映射（六哥 2026-07-08 补充要求：先严后宽逐轮迭代，外层可再加宽松循环，
   直到无新增匹配即收敛）+ 批处理 + 质量报告 + argparse/错误处理。
2. 输入字段：商品表同 v0.1（表头模糊识别）；品类表 category_table v2+ 全部映射列，
   v3 诊断列（business_role 等）若存在则原样透传进映射输出。
3. 输出表：<前缀>_output_mapping.csv / _output_unmatched.csv / _output_review.csv /
   _quality_report.md（含逐轮收敛统计、重复条码、品类表反哺建议三章）。
4. 异常：缺名称列/品类表格式不符→明确报错退出(exit code 2)；单行处理异常→记日志跳过不炸盘；
   目录批处理时单文件失败不影响其余文件。
5. 未匹配：跑满全部轮次仍 0 候选才落 unmatched，原因分"无命中/全被排除词否决/仅宽松轮命中但低于阈值"。
6. 多候选：score=Σ命中词长度加权，裁决序 = mapping_priority 降序 → score 降序；打平→复核。
7. 人工复核：① 品类 manual_review_required=Y；② 打平；③ confidence=low（含宽松轮命中）；
   ④ 原POS分类与命中品类跨 L1 冲突。
8. 相比上版提升：多轮循环让"洗衣液薰衣草"这类首轮擦肩的商品有第二/三次机会（alias 轮、
   原分类提示轮、宽松轮）；质量报告使每次运行可审计、可反哺品类表迭代。
9. 不能处理什么：语义级歧义（"小苏打"是饼干还是清洁用品）仍需人审；不做条码库比对；
   不做真实 POS 格式修复（上游 POS清洗库职责）；宽松轮阈值是经验值未经真实数据标定。
10. 是否作下轮基础：是——进入生产版(v1.0)前需补：V6.0 真实品类表接入（须授权）、
    花厅坊金标准回归测试、错误码规范化。
"""
import argparse
import csv
import logging
import os
import re
import sys
import unicodedata
from collections import Counter

log = logging.getLogger("cleaner_v0.3")

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
V3_PASSTHROUGH = ["business_role", "diagnosis_dimension", "price_band_required",
                  "display_required", "inventory_required", "promotion_required"]


# ---------- 基础件 ----------
def normalize_name(name: str) -> str:
    s = unicodedata.normalize("NFKC", str(name or ""))
    s = s.replace("×", "*")
    s = SPEC_RE.sub("", s)
    s = re.sub(r"\s+", "", s)
    return s.strip()


def detect_fields(headers):
    mapping = {}
    for key, cands in FIELD_CANDIDATES.items():
        for h in headers:
            hn = unicodedata.normalize("NFKC", h).strip()
            if any(c == hn or c in hn for c in cands):
                mapping[key] = h
                break
    if "name" not in mapping:
        raise ValueError("找不到商品名称列，表头=%s" % headers)
    log.info("字段识别结果: %s", mapping)
    return mapping


def parse_conf_rule(rule_text):
    """'kw_hit>=1:mid;kw_hit>=2:high' -> [(2,'high'),(1,'mid')] 降序。"""
    out = []
    for part in (rule_text or "").split(";"):
        m = re.match(r"kw_hit>=(\d+):(\w+)", part.strip())
        if m:
            out.append((int(m.group(1)), m.group(2)))
    return sorted(out, key=lambda x: -x[0]) or [(1, "mid")]


def confidence_of(n_hits, conf_rules, forced_low=False):
    if forced_low:
        return "low"
    for thresh, level in conf_rules:
        if n_hits >= thresh:
            return level
    return "low"


def load_rules(path):
    with open(path, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    need = {"keywords", "exclude_keywords", "mapping_priority", "category_code"}
    if not rows or not need.issubset(rows[0].keys()):
        raise ValueError("品类表需 category_table v2+ 格式")
    rules = []
    for r in rows:
        kws = [k for k in (r.get("keywords") or "").split("|") if k]
        if not kws:
            continue
        aliases = {}
        for pair in (r.get("alias") or "").split("|"):
            if "=" in pair:
                a, b = pair.split("=", 1)
                aliases[a.strip()] = b.strip()
        rules.append({
            "code": r["category_code"], "L1": r["L1"], "L2": r["L2"],
            "L3": r["L3"], "L4": r["L4"], "keywords": kws, "aliases": aliases,
            "excludes": [e for e in (r.get("exclude_keywords") or "").split("|") if e],
            "priority": int(r.get("mapping_priority") or 0),
            "conf_rules": parse_conf_rule(r.get("mapping_confidence_rule")),
            "review": (r.get("manual_review_required") or "N").strip().upper() == "Y",
            "extra": {k: r.get(k, "") for k in V3_PASSTHROUGH if k in r},
        })
    log.info("载入映射规则 %d 条（自 %s）", len(rules), os.path.basename(path))
    return rules


def lcs_len(a, b):
    """最长公共子串长度（宽松轮用，O(len(a)*len(b))，短词可接受）。"""
    best = 0
    for i in range(len(a)):
        for j in range(len(b)):
            k = 0
            while i + k < len(a) and j + k < len(b) and a[i + k] == b[j + k]:
                k += 1
            best = max(best, k)
    return best


# ---------- 匹配轮（内循环 pass 1-4） ----------
def hits_for(rule, name):
    return [kw for kw in rule["keywords"] if kw in name]


def pass_strict(norm, rules, _ctx):
    return [(r, hits_for(r, norm), "strict") for r in rules if hits_for(r, norm)]


def pass_alias(norm, rules, _ctx):
    out = []
    for r in rules:
        if not r["aliases"]:
            continue
        name2 = norm
        for a, b in r["aliases"].items():
            name2 = name2.replace(a, b)
        h = hits_for(r, name2)
        if h:
            out.append((r, h, "alias"))
    return out


def pass_oldcat(norm, rules, ctx):
    """原POS分类提示轮：原分类文本与品类 L2/L3/L4 名互含 → 低置信候选。"""
    old = normalize_name(ctx.get("old_cat", ""))
    if not old:
        return []
    out = []
    for r in rules:
        for nm in (r["L4"], r["L3"], r["L2"]):
            if nm and (nm in old or old in nm):
                out.append((r, [nm], "oldcat"))
                break
    return out


def make_pass_relaxed(threshold):
    def pass_relaxed(norm, rules, _ctx):
        out = []
        for r in rules:
            best = max((lcs_len(kw, norm) / len(kw) for kw in r["keywords"] if len(kw) >= 2),
                       default=0)
            if best >= threshold:
                out.append((r, ["~relaxed"], "relaxed"))
        return out
    return pass_relaxed


def veto(norm, cands):
    """排除词一票否决。返回 (存活候选, 否决数)。"""
    alive, killed = [], 0
    for r, h, how in cands:
        if any(e and e in norm for e in r["excludes"]):
            killed += 1
        else:
            alive.append((r, h, how))
    return alive, killed


def adjudicate(cands):
    """priority ↓ → score(命中词总长) ↓；返回 (rule, hits, how, score, tie)。"""
    scored = []
    for r, h, how in cands:
        score = sum(len(k) for k in h if not k.startswith("~"))
        scored.append((r, h, how, score))
    scored.sort(key=lambda x: (-x[0]["priority"], -x[3]))
    top = [s for s in scored if (s[0]["priority"], s[3]) == (scored[0][0]["priority"], scored[0][3])]
    r, h, how, score = top[0]
    return r, h, how, score, len(top) > 1


# ---------- 主流程 ----------
def clean_file(goods_path, rules, outdir, max_passes=5, outer_loops=1,
               relax_start=0.67, relax_step=0.06):
    """
    双重循环：外层 outer_loops 次（每次放宽 relaxed 阈值），
    内层最多 max_passes 轮（strict→alias→oldcat→relaxed→relaxed-2…），
    每轮只扫上一轮的未匹配；本轮新增=0 即收敛提前退出。
    """
    with open(goods_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        goods = list(reader)
    fmap = detect_fields(headers)

    prefix = os.path.join(outdir, os.path.splitext(os.path.basename(goods_path))[0].replace("sample_pos_goods", "sample"))
    pending = []
    seen_bc, dup_bc = set(), []
    for g in goods:
        bc = (g.get(fmap.get("barcode", ""), "") or "").strip()
        if bc:
            if bc in seen_bc:
                dup_bc.append({**g, "重复策略": "保留首行，本行照常映射并标记"})
            seen_bc.add(bc)
        pending.append(g)

    matched, review = [], []
    veto_total = 0
    pass_stats = []  # (loop, pass_name, threshold, new_matched, remaining)
    unmatched_reason = {}

    for loop in range(1, outer_loops + 1):
        threshold = max(relax_start - (loop - 1) * relax_step, 0.4)
        passes = [("strict", pass_strict), ("alias", pass_alias), ("oldcat", pass_oldcat),
                  (f"relaxed@{threshold:.2f}", make_pass_relaxed(threshold))]
        # 超过 4 的 max_passes：追加更宽松的 relaxed 轮
        for extra in range(max_passes - 4):
            t2 = max(threshold - (extra + 1) * relax_step, 0.35)
            passes.append((f"relaxed@{t2:.2f}", make_pass_relaxed(t2)))
        passes = passes[:max_passes]

        for pname, pfunc in passes:
            if not pending:
                break
            still, new_cnt = [], 0
            for g in pending:
                try:
                    norm = normalize_name(g.get(fmap["name"], ""))
                    ctx = {"old_cat": g.get(fmap.get("old_cat", ""), "")}
                    cands = pfunc(norm, [r for r in RULES_CACHE], ctx)
                    cands, killed = veto(norm, cands)
                    veto_total += killed
                    if killed and not cands:
                        unmatched_reason[id(g)] = "命中但全被排除词否决"
                    if not cands:
                        still.append(g)
                        continue
                    rule, hits, how, score, tie = adjudicate(cands)
                    forced_low = how in ("oldcat",) or how.startswith("relaxed") if isinstance(how, str) else False
                    conf = confidence_of(len(hits), rule["conf_rules"], forced_low=forced_low)
                    row = dict(g)
                    row.update({"标准化名称": norm, "category_code": rule["code"],
                                "L1": rule["L1"], "L2": rule["L2"], "L3": rule["L3"],
                                "L4": rule["L4"], "命中词": "|".join(hits),
                                "命中方式": how, "映射轮次": f"loop{loop}/{pname}",
                                "mapping_score": score, "confidence_level": conf,
                                "候选数": len(cands)})
                    row.update(rule["extra"])
                    reasons = []
                    if rule["review"]:
                        reasons.append("品类强制复核")
                    if tie:
                        reasons.append("裁决打平")
                    if conf == "low":
                        reasons.append("低置信")
                    oldc = normalize_name(ctx["old_cat"])
                    if oldc and how == "strict" and oldc not in (rule["L1"] + rule["L2"] + rule["L3"] + rule["L4"]):
                        # 仅当原分类词强命中另一 L1 下的规则时才算冲突
                        others = [r2 for r2, _, _ in pass_strict(oldc, RULES_CACHE, {})
                                  if r2["L1"] != rule["L1"]]
                        if others:
                            reasons.append("与原POS分类跨L1冲突")
                    row["复核标记"] = ";".join(reasons)
                    matched.append(row)
                    if reasons:
                        review.append(row)
                    new_cnt += 1
                except Exception as e:  # 单行异常不炸盘
                    log.error("行处理异常(%s)，跳过: %s", e, g)
                    still.append(g)
            pending = still
            pass_stats.append((loop, pname, new_cnt, len(pending)))
            log.info("loop%d %s: 新增 %d，剩余 %d", loop, pname, new_cnt, len(pending))
        if not pending:
            break
        # 外层收敛判断：整个内层循环一单未增 → 再宽松也无意义时停
        loop_new = sum(n for l, _, n, _ in pass_stats if l == loop)
        if loop_new == 0 and loop > 1:
            log.info("外层第 %d 轮零新增，收敛退出", loop)
            break

    unmatched = []
    for g in pending:
        row = dict(g)
        row["标准化名称"] = normalize_name(g.get(fmap["name"], ""))
        row["未匹配原因"] = unmatched_reason.get(id(g), "跑满全部轮次无命中")
        unmatched.append(row)

    _write(prefix + "_output_mapping.csv", matched)
    _write(prefix + "_output_unmatched.csv", unmatched)
    _write(prefix + "_output_review.csv", review)
    _quality_report(prefix + "_quality_report.md", goods_path, len(goods), matched,
                    unmatched, review, pass_stats, dup_bc, veto_total)
    return len(matched), len(unmatched), len(review)


def _write(path, rows):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        if not rows:
            f.write("")
            return
        keys = []
        for r in rows:
            for k in r.keys():
                if k not in keys:
                    keys.append(k)
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def _quality_report(path, src, total, matched, unmatched, review, pass_stats, dup_bc, veto_total):
    conf_dist = Counter(m["confidence_level"] for m in matched)
    tokens = Counter()
    for u in unmatched:
        s = u.get("标准化名称", "")
        for i in range(len(s) - 1):
            tokens[s[i:i + 2]] += 1
    lines = [
        "# sample 质量报告（category_pos_cleaner v0.3 · mock 数据实验件 · draft）", "",
        f"- 输入：`{os.path.basename(src)}`（{total} 行，纯 mock 假条码/假价）",
        f"- 映射：{len(matched)}（{len(matched)/total:.1%}）｜未匹配：{len(unmatched)}（{len(unmatched)/total:.1%}）｜需复核：{len(review)}（{len(review)/total:.1%}）",
        f"- 置信度分布：high={conf_dist.get('high',0)} / mid={conf_dist.get('mid',0)} / low={conf_dist.get('low',0)}",
        f"- 排除词否决次数（误伤防护命中）：{veto_total}", "",
        "## 逐轮收敛统计（双重循环）", "",
        "| 外层loop | 内层pass | 新增匹配 | 剩余未匹配 |", "|---|---|---|---|",
    ]
    for l, p, n, rem in pass_stats:
        lines.append(f"| {l} | {p} | {n} | {rem} |")
    lines += ["", "## 重复条码", ""]
    if dup_bc:
        lines.append(f"共 {len(dup_bc)} 行重复条码（策略：保留首行，重复行照常映射并在此列示）：")
        for d in dup_bc:
            lines.append(f"- 条码 {d.get('条码')} · {d.get('商品名称')}")
    else:
        lines.append("无重复条码。")
    lines += ["", "## 品类表反哺建议（未匹配高频词根 Top10）", ""]
    for tk, c in tokens.most_common(10):
        lines.append(f"- `{tk}` ×{c} —— 若属正当品类，建议在品类表新增节点或补 keywords")
    lines += ["", "## 未匹配明细原因分布", ""]
    for reason, c in Counter(u["未匹配原因"] for u in unmatched).items():
        lines.append(f"- {reason}: {c}")
    lines += ["", "> 声明：本报告由 mock 数据产生，仅验证程序逻辑；不代表任何真实门店数据结论。"]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


RULES_CACHE = []


def main(argv=None):
    ap = argparse.ArgumentParser(description="category_pos_cleaner v0.3（Phase-Z 实验件·mock 专用）")
    ap.add_argument("goods", help="商品表 csv 或目录（目录=批处理）")
    ap.add_argument("--category", required=True, help="品类表 csv（category_table v2+）")
    ap.add_argument("--outdir", default=".", help="输出目录")
    ap.add_argument("--max-passes", type=int, default=5, help="内层最大轮数（默认5，可加到8-10）")
    ap.add_argument("--outer-loops", type=int, default=1, help="外层宽松循环次数（六哥补充：可再加3-5次）")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(levelname)s %(message)s")
    try:
        global RULES_CACHE
        RULES_CACHE = load_rules(args.category)
    except (ValueError, OSError) as e:
        log.error("品类表载入失败: %s", e)
        return 2
    os.makedirs(args.outdir, exist_ok=True)
    files = ([os.path.join(args.goods, f) for f in sorted(os.listdir(args.goods)) if f.endswith(".csv")]
             if os.path.isdir(args.goods) else [args.goods])
    rc = 0
    for fp in files:
        try:
            m, u, r = clean_file(fp, RULES_CACHE, args.outdir,
                                 max_passes=args.max_passes, outer_loops=args.outer_loops)
            log.info("[%s] 映射 %d / 未匹配 %d / 复核 %d", os.path.basename(fp), m, u, r)
        except (ValueError, OSError) as e:
            log.error("[%s] 处理失败: %s", fp, e)
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
