#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""evidence_pack_indexer v0.1 · Phase-Y 草案（draft·只读·未经六哥签字不得当生效工具引用）

用途: 扫描指定目录（如 16_/花厅坊样板证据区）的 .md，按 frontmatter `source_type`
  分组生成"证据包索引"markdown——audit_note / promote_review / aar / signoff_package
  等类型各一节，节内列 标题/summary/status/更新时间/路径，供组装签字包时快速定位。
输入: --dir <目录>（必填，可多次；禁止全库默认扫描）
输出: 索引 md → stdout（默认）；--out + --write 才落盘
用法:
  python3 evidence_pack_indexer_v0.1.py --dir <证据目录> [--out /tmp/index.md --write]
安全边界: 纯只读；只读 .md 的 frontmatter 区（前200行内），不读正文明细；
  排除 99_原始素材/99_归档/.git；不读 xls/csv 等 raw。
局限: source_type 缺失的文件归入"未分类"节（本身即体检信号）；分节顺序为
  Phase-Y 预置常见类型，新类型自动追加尾部；不判断证据内容真伪与充分性。
"""
import argparse
import sys
from collections import OrderedDict
from pathlib import Path

PREFERRED_ORDER = ["signoff_package", "promote_review", "audit_note", "aar",
                   "decision", "methodology", "tool", "data"]
EXCLUDE_SEGMENTS = {"99_原始素材", "99_归档", ".git", "__pycache__"}


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


def main(argv=None):
    ap = argparse.ArgumentParser(description="证据包索引生成（只读·draft）")
    ap.add_argument("--dir", action="append", required=True,
                    help="证据目录（必填，可多次；禁止全库默认）")
    ap.add_argument("--out", help="索引输出路径（须配 --write）")
    ap.add_argument("--write", action="store_true", help="允许写 --out（默认只打印）")
    args = ap.parse_args(argv)

    groups = OrderedDict()
    scanned = 0
    for d in args.dir:
        root = Path(d)
        if not root.is_dir():
            print(f"错误: 目录不存在 → {d}", file=sys.stderr)
            return 2
        for p in sorted(root.rglob("*.md")):
            if any(seg in EXCLUDE_SEGMENTS for seg in p.parts):
                continue
            scanned += 1
            try:
                fm = parse_frontmatter(p.read_text(encoding="utf-8", errors="replace"))
            except OSError:
                fm = {}
            st = fm.get("source_type", "") or "未分类"
            groups.setdefault(st, []).append((
                fm.get("title", p.stem), fm.get("summary", "-"),
                fm.get("status", "-"), fm.get("updated", fm.get("created", "-")),
                str(p)))

    ordered = [k for k in PREFERRED_ORDER if k in groups] + \
              [k for k in groups if k not in PREFERRED_ORDER]

    lines = ["# 证据包索引（draft·自动生成·只读扫描）", "",
             f"- 扫描目录: {', '.join(args.dir)} · 文件数: {scanned}",
             f"- 类型分布: " + " / ".join(f"{k}×{len(groups[k])}" for k in ordered), ""]
    for k in ordered:
        lines += [f"## {k}（{len(groups[k])}）", "",
                  "| 标题 | summary | status | 更新 | 路径 |", "|---|---|---|---|---|"]
        for title, summary, status, upd, path in groups[k]:
            lines.append(f"| {title} | {summary[:60]} | {status} | {upd} | {path} |")
        lines.append("")
    if "未分类" in groups:
        lines.append("> ⚠️ 「未分类」= 缺 source_type 字段，建议随 frontmatter 消债批次补齐。")
    report = "\n".join(lines)

    if args.out and args.write:
        Path(args.out).write_text(report + "\n", encoding="utf-8")
        print(f"索引已写入: {args.out}")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
