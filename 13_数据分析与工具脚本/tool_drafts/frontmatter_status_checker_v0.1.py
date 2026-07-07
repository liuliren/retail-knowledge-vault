#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""frontmatter_status_checker v0.1 · Phase-Y 草案（draft·只读·未经六哥签字不得当生效工具引用）

用途: 扫描指定目录下 .md 文件的 YAML frontmatter，输出四类问题清单：
  ① status 值不在合法集（7值集 seed/draft/candidate/active/stable/deprecated/archived + delivered）
  ② status=active 但缺 signoff/signed/signed_off 字段
  ③ status 字段污染（值超长>24字符 或 混入备注符号 ·（(，, 等）
  ④ 缺 summary 字段
输入: --dir <目录>（必填，可多次；**禁止全库默认扫描**，必须显式给目录）
输出: markdown 报告 → stdout（默认 dry-run）；--out <路径> + --write 时才落盘
用法:
  python3 frontmatter_status_checker_v0.1.py --dir <某目录> [--dir 另一目录]
  python3 frontmatter_status_checker_v0.1.py --dir <目录> --out /tmp/report.md --write
安全边界: 纯只读，绝不修改被扫描文件；默认 dry-run 只打印；不读非 .md 文件；
  默认排除 99_原始素材/99_归档/.git/__pycache__ 路径段。
局限: 简易逐行 frontmatter 解析（key: value），不支持多行 YAML 值；合法状态集为
  Phase-Y 推断值，7值集以六哥签字口径为准；不判断 status 语义正确性，只判形式。
"""
import argparse
import sys
from pathlib import Path

LEGAL_STATUS = {"seed", "draft", "candidate", "active", "stable",
                "deprecated", "archived", "delivered"}
SIGNOFF_KEYS = ("signoff", "signed", "signed_off")
EXCLUDE_SEGMENTS = {"99_原始素材", "99_归档", ".git", "__pycache__", ".pytest_cache"}
POLLUTION_CHARS = ("·", "（", "(", "，", ",", "备注", "待", "|")
STATUS_MAX_LEN = 24


def parse_frontmatter(text):
    """返回 (dict, has_frontmatter)。只解析顶层 key: value 行。"""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, False
    fm = {}
    for line in lines[1:200]:
        if line.strip() in ("---", "..."):
            return fm, True
        if ":" in line and not line.startswith((" ", "\t", "-")):
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm, False  # 未闭合


def check_file(path):
    issues = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        return [("读取失败", str(e))]
    fm, ok = parse_frontmatter(text)
    if not fm:
        return [("无frontmatter", "-")]
    if not ok:
        issues.append(("frontmatter未闭合", "-"))
    status = fm.get("status", "")
    if status:
        base = status.split()[0] if status.split() else status
        if len(status) > STATUS_MAX_LEN or any(c in status for c in POLLUTION_CHARS):
            issues.append(("status字段污染", status[:60]))
        elif base not in LEGAL_STATUS:
            issues.append(("status非法值", status[:60]))
        if base == "active" and not any(k in fm for k in SIGNOFF_KEYS):
            issues.append(("active缺signoff", "-"))
    else:
        issues.append(("缺status", "-"))
    if "summary" not in fm or not fm.get("summary"):
        issues.append(("缺summary", "-"))
    return issues


def main(argv=None):
    ap = argparse.ArgumentParser(description="frontmatter 状态体检（只读·draft）")
    ap.add_argument("--dir", action="append", required=True,
                    help="要扫描的目录（必填，可多次；禁止全库默认）")
    ap.add_argument("--out", help="报告输出路径（须配 --write 才落盘）")
    ap.add_argument("--write", action="store_true",
                    help="允许把报告写入 --out（默认 dry-run 只打印）")
    args = ap.parse_args(argv)

    rows = []
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
            for kind, detail in check_file(p):
                rows.append((str(p), kind, detail))

    lines = ["# frontmatter 状态体检报告（draft·只读）", "",
             f"- 扫描目录: {', '.join(args.dir)}",
             f"- 扫描文件数: {scanned} · 问题条数: {len(rows)}", "",
             "| 文件 | 问题 | 详情 |", "|---|---|---|"]
    for f, kind, detail in rows:
        lines.append(f"| {f} | {kind} | {detail} |")
    if not rows:
        lines.append("| （无问题） | - | - |")
    report = "\n".join(lines)

    if args.out and args.write:
        Path(args.out).write_text(report + "\n", encoding="utf-8")
        print(f"报告已写入: {args.out}")
    else:
        print(report)
        if args.out and not args.write:
            print("\n[dry-run] 未写 --out（加 --write 才落盘）", file=sys.stderr)
    return 1 if rows else 0


if __name__ == "__main__":
    raise SystemExit(main())
