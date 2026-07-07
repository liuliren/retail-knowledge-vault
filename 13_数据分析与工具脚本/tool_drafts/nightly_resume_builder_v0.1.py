#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""nightly_resume_builder v0.1 · Phase-Y 草案（draft·只读·未经六哥签字不得当生效工具引用）

用途: 从 git 历史与工作区状态自动生成 LOOP_STATE / RESUME 骨架 md，替代手写断点文档
  的机械部分（"发生了什么"），判断部分（"下一步做什么"）留空位给人/主线程填。
输入: --since <git时间窗>（必填，如 "24 hours ago" / "2026-07-07 20:00"）；
      --repo <git仓库根>（默认当前目录）；--known-dirty <清单文件>（可选，每行一个
      路径前缀，命中者归"已知长期未提交"类）；--until <时间>（可选）
输出: LOOP_STATE 骨架 md → stdout（默认）；--out + --write 才落盘
  未提交文件四类分拣规则: ①路径含 .claude/skills/ → skill 类
  ②路径含 RESUME/LOOP_STATE/handoff/交接 → handoff 类
  ③命中 --known-dirty 前缀 → known-dirty 类  ④其余 → 待分类
用法:
  python3 nightly_resume_builder_v0.1.py --since "24 hours ago" --repo <vault根>
安全边界: 只跑 `git log` / `git status --porcelain` 两个只读命令；不 add/commit/
  checkout；不读文件内容（只用路径与提交标题）；默认不写盘。
局限: 依赖仓库是 git repo；commit 标题若含客户名会原样带入（骨架供内部断点用，
  不得直接外发）；"下一步"三条留空——判断相不自动生成。
"""
import argparse
import datetime
import subprocess
import sys
from pathlib import Path


def run_git(repo, args):
    try:
        r = subprocess.run(["git", "-C", repo, "-c", "core.quotepath=false"] + args,
                           capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as e:
        sys.exit(f"错误: git 调用失败 → {e}")
    if r.returncode != 0:
        sys.exit(f"错误: git {' '.join(args)} → {r.stderr.strip()[:200]}")
    return r.stdout


def classify(path, known_dirty):
    if ".claude/skills/" in path:
        return "skill"
    low = path.lower()
    if any(k in low for k in ("resume", "loop_state", "handoff")) or "交接" in path or "断点" in path:
        return "handoff"
    for prefix in known_dirty:
        if path.startswith(prefix):
            return "known-dirty"
    return "待分类"


def main(argv=None):
    ap = argparse.ArgumentParser(description="LOOP_STATE 骨架生成（只读git·draft）")
    ap.add_argument("--since", required=True, help='git 时间窗起点，如 "24 hours ago"')
    ap.add_argument("--until", help="时间窗终点（可选）")
    ap.add_argument("--repo", default=".", help="git 仓库根（默认当前目录）")
    ap.add_argument("--known-dirty", help="已知长期未提交路径前缀清单文件（每行一个）")
    ap.add_argument("--out", help="输出路径（须配 --write）")
    ap.add_argument("--write", action="store_true", help="允许写 --out（默认只打印）")
    args = ap.parse_args(argv)

    if not (Path(args.repo) / ".git").exists():
        print(f"错误: 非 git 仓库 → {args.repo}", file=sys.stderr)
        return 2

    known_dirty = []
    if args.known_dirty:
        kd = Path(args.known_dirty)
        if not kd.is_file():
            print(f"错误: known-dirty 清单不存在 → {args.known_dirty}", file=sys.stderr)
            return 2
        known_dirty = [l.strip() for l in kd.read_text(encoding="utf-8").splitlines()
                       if l.strip() and not l.startswith("#")]

    log_args = ["log", "--oneline", f"--since={args.since}"]
    if args.until:
        log_args.append(f"--until={args.until}")
    commits = [l for l in run_git(args.repo, log_args).splitlines() if l.strip()]

    buckets = {"skill": [], "handoff": [], "known-dirty": [], "待分类": []}
    for line in run_git(args.repo, ["status", "--porcelain"]).splitlines():
        if len(line) < 4:
            continue
        st, path = line[:2], line[3:].strip().strip('"')
        buckets[classify(path, known_dirty)].append(f"`{st.strip() or '??'}` {path}")

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = ["# LOOP_STATE 骨架（自动生成·draft·内部断点用）", "",
             f"- 生成时间: {now} · 仓库: {Path(args.repo).resolve().name}",
             f"- 时间窗: since={args.since}" + (f" until={args.until}" if args.until else ""),
             "", f"## COMPLETED（时间窗内 commits × {len(commits)}）", ""]
    lines += [f"- {c}" for c in commits] or ["- （时间窗内无 commit）"]
    lines += ["", "## UNCOMMITTED（四类分拣）", ""]
    for k in ("skill", "handoff", "known-dirty", "待分类"):
        lines.append(f"### {k}（{len(buckets[k])}）")
        lines += [f"- {x}" for x in buckets[k]] or ["- 无"]
        lines.append("")
    lines += ["## NEXT（判断相·留空待填·≤3条）", "", "- [ ] （待主线程/六哥填）",
              "- [ ] ", "- [ ] ", "",
              "> 本骨架只答\"发生了什么\"；\"下一步\"与取舍归人。RESUME 正式件≤300 tokens，",
              "> 本骨架是供压缩前参考的中间件，不直接覆盖 _当前断点_RESUME.md。"]
    report = "\n".join(lines)

    if args.out and args.write:
        Path(args.out).write_text(report + "\n", encoding="utf-8")
        print(f"骨架已写入: {args.out}")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
