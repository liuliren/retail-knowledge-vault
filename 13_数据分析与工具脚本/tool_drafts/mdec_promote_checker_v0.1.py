#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mdec_promote_checker v0.1 · Phase-Y 草案（draft·只读·未经六哥签字不得当生效工具引用）

用途: 对指定 M-DEC 决策卡文件做 promote 就绪度机械检查（/promote skill 的机械相候选）：
  就绪度4项: ①status=active ②signoff 字段在 ③正文引用的证据文件链接可解析
             ④文件命名合规（含 DEC-YYYYMMDD-NN 或 M-DEC 标识）
  附加项:   ⑤promoted_from/promoted_to 指向的文件反向存在性
             ⑥双权威消歧三件套痕迹（a.canonical/权威指针声明 b.非权威方标注 c.消歧/log记录）
输入: 一个或多个 M-DEC 卡 .md 路径（位置参数，必填）；--vault <根目录>（可选，
      用于解析 [[wikilink]]；不给则跳过 wikilink 存在性检查并明示）
输出: markdown 检查表 → stdout（默认）；--out + --write 才落盘
用法:
  python3 mdec_promote_checker_v0.1.py <M-DEC卡.md> [--vault <vault根>]
安全边界: 纯只读；不修改被查文件；--vault 给出时仅索引 .md 文件名（不读内容），
  排除 99_原始素材/99_归档/.git。
局限: "双权威消歧三件套"为关键词级痕迹检查（canonical/权威/消歧），非语义判断；
  就绪≠应当 promote——留/汰/蒸馏判断仍归六哥；wikilink 解析按 basename 匹配，
  同名文件多处存在时只报"存在"不辨真身。
"""
import argparse
import re
import sys
from pathlib import Path

EXCLUDE_SEGMENTS = {"99_原始素材", "99_归档", ".git", "__pycache__"}
WIKILINK_RE = re.compile(r"\[\[([^\]\|#]+)")
MDLINK_RE = re.compile(r"\]\(([^)#]+\.md)\)")
NAME_RE = re.compile(r"(DEC-\d{8}-\d{2}|M-?DEC)", re.I)


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
        idx.setdefault(p.stem, []).append(p)
    return idx


def check_card(path, name_idx):
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
            stem = Path(w).stem
            if stem not in name_idx:
                missing.append(f"[[{w}]]")
        for rel in mdlinks:
            if not (path.parent / rel).exists() and Path(rel).stem not in name_idx:
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
        stem = Path(val.strip("[] ")).stem
        if name_idx is None:
            out.append((f"⑤ {key} 反向存在", None, f"{val} 未验证（未给 --vault）"))
        else:
            out.append((f"⑤ {key} 反向存在", stem in name_idx, val))

    # ⑥ 双权威消歧三件套（关键词痕迹）
    trio = [("a.canonical指针", ("canonical" in text.lower()) or ("权威" in text)),
            ("b.非权威方标注", ("非权威" in text) or ("已被取代" in text) or ("指针" in text)),
            ("c.消歧/log记录", ("消歧" in text) or ("log" in text.lower()))]
    if fm.get("promoted_from") or "promote" in text.lower():
        for name, hit in trio:
            out.append((f"⑥ 消歧三件套 {name}", hit, "关键词级痕迹检查"))
    else:
        out.append(("⑥ 消歧三件套", None, "无 promote 痕迹，跳过"))
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
        for item, ok, note in check_card(p, name_idx):
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
