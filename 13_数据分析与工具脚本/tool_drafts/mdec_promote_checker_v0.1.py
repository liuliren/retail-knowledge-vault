#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mdec_promote_checker v0.1.1 · Phase-Y 草案（draft·只读·未经六哥签字不得当生效工具引用）

v0.1.1 修复说明（2026-07-07）:
  D1: 检查项③ wikilink 解析改用全库 basename 索引 + canonical_link_target 规范化
      （剥离 |别名 / #锚点 / 路径前缀 / 尾部.md；不再用 Path.stem——它会误剥
      "..._v0.1_候选" 中版本段的 ".1_候选"，造成假阴性）。逻辑取自
      13_数据分析与工具脚本/G03_Lint_v2/lint_v2.py 的 canonical_link_target。
      索引排除 .git/99_归档/99_原始素材/Clippings/__pycache__。
  D2: 检查项⑤ promoted_from/promoted_to 反向存在性同样经 canonical_link_target
      + 全库索引解析（修复 16_ 原卡真实存在却报 ❌ 的假阴性）。
  D3: 检查项⑥ 消歧三件套由关键词嗅探改为实证检查：
      a. 本卡 frontmatter 同时有 promoted_from + promote_date 两字段
      b. promoted_from 指向的对侧文件正文含指向本卡目录的 wikilink，
         或 "SSOT"/"权威版本" 字样指针块
      c. SignoffLedger（00_入口与总索引/03_治理规范/签字门台账_SignoffLedger_v0.1.md）
         中能 grep 到本卡名（全 stem 或 M-DEC/DEC 编号）

用途: 对指定 M-DEC 决策卡文件做 promote 就绪度机械检查（/promote skill 的机械相候选）：
  就绪度4项: ①status=active ②signoff 字段在 ③正文引用的证据文件链接可解析
             ④文件命名合规（含 DEC-YYYYMMDD-NN 或 M-DEC 标识）
  附加项:   ⑤promoted_from/promoted_to 指向的文件反向存在性
             ⑥双权威消歧三件套（实证检查，见上 D3）
输入: 一个或多个 M-DEC 卡 .md 路径（位置参数，必填）；--vault <根目录>（可选，
      用于解析 [[wikilink]]；不给则跳过 wikilink 存在性检查并明示）
输出: markdown 检查表 → stdout（默认）；--out + --write 才落盘
用法:
  python3 mdec_promote_checker_v0.1.py <M-DEC卡.md> [--vault <vault根>]
安全边界: 纯只读；不修改被查文件；--vault 给出时索引 .md 文件名；⑥b/⑥c 需读
  对侧文件与 SignoffLedger 正文（仍只读）；排除 99_原始素材/99_归档/.git/Clippings。
局限: 就绪≠应当 promote——留/汰/蒸馏判断仍归六哥；wikilink 解析按 basename 匹配，
  同名文件多处存在时只报"存在"不辨真身。
"""
import argparse
import re
import sys
from pathlib import Path

EXCLUDE_SEGMENTS = {"99_原始素材", "99_归档", ".git", "__pycache__", "Clippings"}
WIKILINK_RE = re.compile(r"\[\[([^\]]+?)\]\]")
MDLINK_RE = re.compile(r"\]\(([^)#]+\.md)\)")
NAME_RE = re.compile(r"(DEC-\d{8}-\d{2}|M-?DEC)", re.I)
CARD_ID_RE = re.compile(r"(M-?DEC-\d+|DEC-\d{8}-\d{2})", re.I)
LEDGER_REL = "00_入口与总索引/03_治理规范/签字门台账_SignoffLedger_v0.1.md"


def canonical_link_target(raw):
    """规范化 wikilink 目标（D1·取自 G03_Lint_v2/lint_v2.py 同名函数）。

    剥离 |别名、#锚点、路径前缀、尾部 .md。注意用 basename split 而非
    Path(...).stem——stem 会剥最后一个点之后的内容，把 "..._v0.1_候选"
    这种版本段带点的合法链接目标砍成 "..._v0"，制造假阴性断链。
    """
    target = raw.split("|", 1)[0].split("#", 1)[0].strip()
    target = target.replace("\\", "/")
    if "/" in target:
        target = target.rsplit("/", 1)[-1]
    if target.endswith(".md"):
        target = target[:-3]
    return target.strip()


def parse_frontmatter(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    fm = {}
    for line in lines[1:200]:
        if line.strip() in ("---", "..."):
            break
        if ":" in line and not line.startswith((" ", "\t", "-")):
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm


def build_name_index(vault):
    idx = {}
    for p in Path(vault).rglob("*.md"):
        if any(seg in EXCLUDE_SEGMENTS for seg in p.parts):
            continue
        # 用 name[:-3] 而非 p.stem 语义等价但意图明确：只剥 ".md"
        idx.setdefault(p.name[:-3], []).append(p)
    return idx


def check_disambig_trio(path, fm, name_idx, vault):
    """⑥ 双权威消歧三件套实证检查（D3）。返回 [(名, 通过?, 说明)]。"""
    out = []
    promoted_from = fm.get("promoted_from", "")
    # a. 本卡 frontmatter 有 promoted_from + promote_date 两字段
    has_a = bool(promoted_from) and bool(fm.get("promote_date"))
    out.append(("⑥a promoted_from+promote_date 双字段", has_a,
                f"promoted_from={'有' if promoted_from else '缺'}; promote_date={'有' if fm.get('promote_date') else '缺'}"))
    # b. 对侧文件正文含指向本卡目录的 wikilink 或 SSOT/权威版本 指针块
    counterpart = None
    if promoted_from and name_idx is not None:
        cands = name_idx.get(canonical_link_target(promoted_from))
        if cands:
            counterpart = cands[0]
    if counterpart is None:
        out.append(("⑥b 对侧指针块", None if name_idx is None else False,
                    "未给 --vault 无法定位对侧" if name_idx is None else f"对侧文件未找到: {promoted_from}"))
    else:
        try:
            ctext = counterpart.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            out.append(("⑥b 对侧指针块", False, f"对侧读取失败: {e}"))
        else:
            card_dir = ""
            if vault:
                try:
                    card_dir = str(path.resolve().parent.relative_to(Path(vault).resolve())).replace("\\", "/")
                except ValueError:
                    card_dir = ""
            hit_dir = bool(card_dir) and card_dir in ctext
            hit_kw = ("SSOT" in ctext) or ("权威版本" in ctext)
            out.append(("⑥b 对侧指针块", hit_dir or hit_kw,
                        f"对侧={counterpart.name}; 指向本卡目录wikilink={'✓' if hit_dir else '✗'}; SSOT/权威版本字样={'✓' if hit_kw else '✗'}"))
    # c. SignoffLedger 中 grep 到本卡名
    if not vault:
        out.append(("⑥c SignoffLedger 登记", None, "未给 --vault 无法定位台账"))
    else:
        ledger = Path(vault) / LEDGER_REL
        if not ledger.is_file():
            out.append(("⑥c SignoffLedger 登记", False, f"台账不存在: {LEDGER_REL}"))
        else:
            ltext = ledger.read_text(encoding="utf-8", errors="replace")
            stem = path.name[:-3] if path.name.endswith(".md") else path.stem
            m = CARD_ID_RE.search(path.name)
            card_id = m.group(1) if m else ""
            hit = (stem in ltext) or (bool(card_id) and card_id in ltext)
            out.append(("⑥c SignoffLedger 登记", hit,
                        f"grep '{card_id or stem}' → {'命中' if hit else '未命中'}（台账: 签字门台账_SignoffLedger_v0.1.md）"))
    return out


def check_card(path, name_idx, vault=None):
    """返回 [(检查项, 通过?, 说明)]"""
    out = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        return [("读取", False, str(e))]
    fm = parse_frontmatter(text)

    status = fm.get("status", "")
    out.append(("① status=active", status.startswith("active"),
                f"实际: {status or '缺失'}"))
    has_sig = any(k in fm for k in ("signoff", "signed", "signed_off"))
    out.append(("② signoff 在", has_sig,
                fm.get("signoff", "")[:40] if has_sig else "缺 signoff/signed/signed_off"))

    # ③ 证据链接
    wikis = sorted({w.strip() for w in WIKILINK_RE.findall(text)})
    mdlinks = sorted(set(MDLINK_RE.findall(text)))
    missing = []
    if name_idx is None:
        note = f"wikilink×{len(wikis)} 未验证（未给 --vault）"
        for rel in mdlinks:
            if not (path.parent / rel).exists():
                missing.append(rel)
        out.append(("③ 证据链接可解析", not missing, note + (f"; 相对链接缺失: {missing}" if missing else "; 相对链接OK")))
    else:
        for w in wikis:
            # D1: canonical_link_target 规范化后查全库 basename 索引
            if canonical_link_target(w) not in name_idx:
                missing.append(f"[[{w}]]")
        for rel in mdlinks:
            if not (path.parent / rel).exists() and canonical_link_target(rel) not in name_idx:
                missing.append(rel)
        out.append(("③ 证据链接可解析", not missing,
                    f"wikilink×{len(wikis)}+md链接×{len(mdlinks)}; 缺失: {missing or '无'}"))

    out.append(("④ 命名合规", bool(NAME_RE.search(path.name)),
                f"文件名: {path.name}"))

    # ⑤ promoted_from / promoted_to 反向存在
    for key in ("promoted_from", "promoted_to"):
        val = fm.get(key, "")
        if not val:
            out.append((f"⑤ {key}", None, "字段不存在（若尚未promote属正常）"))
            continue
        # D2: 同 ③，用 canonical_link_target + 全库索引解析（不再用 Path.stem）
        target = canonical_link_target(val.strip("[] "))
        if name_idx is None:
            out.append((f"⑤ {key} 反向存在", None, f"{val} 未验证（未给 --vault）"))
        else:
            out.append((f"⑤ {key} 反向存在", target in name_idx, val))

    # ⑥ 双权威消歧三件套（D3: 实证检查，替换关键词嗅探）
    if fm.get("promoted_from"):
        out.extend(check_disambig_trio(path, fm, name_idx, vault))
    else:
        out.append(("⑥ 消歧三件套", None, "frontmatter 无 promoted_from（尚未promote），跳过"))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="M-DEC promote 就绪度检查（只读·draft）")
    ap.add_argument("cards", nargs="+", help="M-DEC 卡 .md 路径")
    ap.add_argument("--vault", help="vault 根目录（可选，用于 wikilink 解析）")
    ap.add_argument("--out", help="报告输出路径（须配 --write）")
    ap.add_argument("--write", action="store_true", help="允许写 --out（默认只打印）")
    args = ap.parse_args(argv)

    name_idx = None
    if args.vault:
        if not Path(args.vault).is_dir():
            print(f"错误: vault 根不存在 → {args.vault}", file=sys.stderr)
            return 2
        name_idx = build_name_index(args.vault)

    lines = ["# M-DEC promote 就绪度检查表（draft·只读）", ""]
    any_fail = False
    for c in args.cards:
        p = Path(c)
        lines += [f"## {p.name}", "", "| 检查项 | 结果 | 说明 |", "|---|---|---|"]
        if not p.is_file():
            lines.append(f"| 文件存在 | ❌ | 路径不存在: {c} |")
            any_fail = True
            continue
        for item, ok, note in check_card(p, name_idx, vault=args.vault):
            mark = "⚪跳过" if ok is None else ("✅" if ok else "❌")
            if ok is False:
                any_fail = True
            lines.append(f"| {item} | {mark} | {note} |")
        lines.append("")
    lines.append("> 就绪≠应当promote：留/汰/蒸馏判断归六哥（判断相不下放）。")
    report = "\n".join(lines)

    if args.out and args.write:
        Path(args.out).write_text(report + "\n", encoding="utf-8")
        print(f"报告已写入: {args.out}")
    else:
        print(report)
    return 1 if any_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
