#!/usr/bin/env python3
"""验收 Checker v0.1 — 品类表交付件机械门禁(G2/G4/G5/G6)独立校验脚本

来源: 《品类表生成验收标准与评分框架_v0.3》
  (05_品类管理与商品规划/品类表生成验收标准与评分框架_v0.3.md · stable · 六哥2026-07-05签字)
  §五③ T1修订原文: "机械门禁 G2/G4/G5/G6……应由独立于生成器的 checker（脚本或独立
  Agent 实例）跑，零 token、不进 LLM 自评"。本脚本承接该缺口——checker 脚本上线，
  过渡期"非生成本表的独立 Agent 实例执行"的安排从此可被脚本替代。

⚠️ 字母口径说明(重要·见 README「已知局限」):
  本脚本的 G2/G4/G5/G6 命名对齐**P3-3任务下达时给定的口径**(机械可核字段/客户安全/
  summary规范/状态机)，与原框架文档 §二 的 G-labels 定义**不是逐字重合**(原文档
  G2=T码作用域、G5=Schema与链接完整、G6=词表闭合、G4=客户安全)。
  本脚本实际逐字对应原文档 G4(客户安全红线) + G5 第一条(frontmatter必填齐)
  + 全局 CLAUDE.md §11.3(状态机合法值)。原文档 G2(T码作用域)、G6(词表闭合)、
  G1(SSOT对齐)、G3(数据锚定)均需领域判断，本脚本不覆盖——见 README。

用法:
  python3 gate_checker.py <md文件路径>

退出码: 0 = 四门全过；1 = 至少一门 FAIL。
只读: 本脚本只读取被检文件，绝不修改。
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# ── G2: frontmatter 必填字段 ──
REQUIRED_FIELDS = ("title", "version", "status", "client_safety", "fact_layer", "summary")
SUMMARY_MAX_LEN = 40

# ── G6: 状态机合法值(全局 CLAUDE.md §11.3 + retail vault 七值定版 + delivered/executed/active_plan/superseded 扩展) ──
VALID_STATUSES = {
    "draft", "candidate", "active", "stable", "deprecated",
    "delivered", "executed", "active_plan", "superseded",
}
SIGNOFF_REQUIRED_STATUSES = {"stable", "active"}
SIGNOFF_FIELDS = ("signoff", "signed", "signed_off")

# ── G4: 客户安全红线正则(与 G03_Lint_v2 的判据对齐，避免同一红线两套口径打架) ──
EAN13_RE = re.compile(r"(?<![0-9])([0-9]{13})(?![0-9])")
PRICE_RE = re.compile(r"(进价|成本价|采购价|含税进价|不含税进价)[ \t]*[:：=][ \t]*([0-9]+(?:\.[0-9]{1,4})?)")
# 已知供应商真名词表：留扩展位。当前为空——六哥可按需补充真实供应商名单(不进版本库明文，
# 建议指向 David-Liu-Vault 敏感区映射表并在运行时注入，见 README「已知局限」)。
SUPPLIER_NAME_PATTERNS: list[str] = []


def parse_frontmatter(text: str) -> tuple[dict, int, int]:
    """解析 YAML frontmatter(手写行级解析，不依赖 pyyaml，保持与 lint_v2.py 同构风格)。

    返回 (frontmatter字典, frontmatter闭合`---`所在行号(1-based，未闭合/无frontmatter=0),
          正文起始行号(1-based))。
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, 0, 1
    data: dict[str, object] = {}
    current_key: str | None = None
    for i in range(1, len(lines)):
        line = lines[i]
        if line.strip() == "---":
            end_line = i + 1
            body_start = i + 2
            return data, end_line, body_start
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = re.match(r"^([A-Za-z0-9_\-]+):\s*(.*)$", line)
        if m:
            key, value = m.group(1), m.group(2).strip()
            if value:
                data[key] = value.strip("\"'")
                current_key = None
            else:
                data[key] = []
                current_key = key
            continue
        if current_key is not None and line.strip().startswith("- "):
            existing = data.setdefault(current_key, [])
            if isinstance(existing, list):
                existing.append(line.strip()[2:].strip().strip("\"'"))
    # frontmatter 未闭合(缺第二个 `---`)：按"无 frontmatter"处理，全部字段视为缺失
    return {}, 0, 1


def gate_g2(fm: dict) -> tuple[bool, list[str]]:
    """G2 · 机械可核字段: frontmatter 必填字段齐全(title/version/status/client_safety/
    fact_layer/summary)，summary≤40字。"""
    violations = []
    for field in REQUIRED_FIELDS:
        value = fm.get(field, "")
        empty = (not value) if isinstance(value, list) else (not str(value).strip())
        if empty:
            violations.append(f"frontmatter 缺失或为空字段: `{field}`")
    summary = fm.get("summary", "")
    if isinstance(summary, str) and summary.strip() and len(summary.strip()) > SUMMARY_MAX_LEN:
        violations.append(f"summary 超过{SUMMARY_MAX_LEN}字(实际{len(summary.strip())}字): \"{summary.strip()}\"")
    return (len(violations) == 0, violations)


def gate_g4(body: str, body_start_line: int) -> tuple[bool, list[str]]:
    """G4 · 客户安全红线: 正文 0 条码(EAN-13)/ 0 进价裸值 / 0 已知供应商真名。"""
    violations = []
    for offset, line in enumerate(body.splitlines()):
        lineno = body_start_line + offset
        for hit in EAN13_RE.findall(line):
            violations.append(f"第{lineno}行: 疑似EAN-13条码裸值 `{hit}`")
        for name, val in PRICE_RE.findall(line):
            violations.append(f"第{lineno}行: `{name}` 后跟裸数值 `{val}`")
        for pattern in SUPPLIER_NAME_PATTERNS:
            if pattern and pattern in line:
                violations.append(f"第{lineno}行: 命中已知供应商真名词表 `{pattern}`")
    return (len(violations) == 0, violations)


def gate_g5(fm: dict) -> tuple[bool, list[str]]:
    """G5 · summary规范: 存在 + ≤40字 + 单句 + 无换行。"""
    violations = []
    summary = fm.get("summary", "")
    if isinstance(summary, list) or not str(summary).strip():
        return (False, ["summary 字段缺失或为空"])
    summary = str(summary).strip()
    if "\n" in summary:
        violations.append("summary 含换行(应为单行)")
    if len(summary) > SUMMARY_MAX_LEN:
        violations.append(f"summary 超过{SUMMARY_MAX_LEN}字(实际{len(summary)}字)")
    # 单句判定: 去掉末尾句末标点后，若内部仍出现句末标点 → 判定为多句
    trimmed = summary.rstrip("。!?！？")
    if any(p in trimmed for p in "。!?！？"):
        violations.append(f"summary 疑似多句(内部含句末标点): \"{summary}\"")
    return (len(violations) == 0, violations)


def gate_g6(fm: dict) -> tuple[bool, list[str]]:
    """G6 · 状态机合法: status ∈ 合法枚举值；status=stable/active 时若无 signoff 字段
    → 仅警告(需查是否六哥已签字)，不计入 FAIL(签字核验属判断门，脚本只提醒不裁决)。"""
    violations: list[str] = []
    warnings: list[str] = []
    status = str(fm.get("status", "")).strip()
    if not status:
        violations.append("status 字段缺失或为空")
    elif status not in VALID_STATUSES:
        violations.append(f"status 值非法: `{status}`(合法值: {', '.join(sorted(VALID_STATUSES))})")
    if status in SIGNOFF_REQUIRED_STATUSES:
        has_signoff = any(str(fm.get(f, "")).strip() for f in SIGNOFF_FIELDS)
        if not has_signoff:
            warnings.append(
                f"status={status} 但未见 signoff/signed 字段——需人工核查该文件是否已由六哥签字"
            )
    passed = len(violations) == 0
    return (passed, violations + [f"⚠️ {w}" for w in warnings])


def run_gate(name: str, passed: bool, details: list[str]) -> bool:
    print(f"[{name}] {'✅ PASS' if passed else '❌ FAIL'}")
    for d in details:
        print(f"  - {d}")
    return passed


def check_file(path: Path) -> tuple[bool, dict[str, tuple[bool, list[str]]]]:
    """对单个 md 文件跑四门，返回 (全过, {门名: (是否过, 违规明细)})。供 pytest 直接调用。"""
    text = path.read_text(encoding="utf-8", errors="replace")
    fm, fm_end_line, body_start_line = parse_frontmatter(text)
    if fm_end_line:
        body = "\n".join(text.splitlines()[body_start_line - 1:])
    else:
        body = text
        body_start_line = 1

    results = {
        "G2 机械可核字段": gate_g2(fm),
        "G4 客户安全红线": gate_g4(body, body_start_line),
        "G5 summary规范": gate_g5(fm),
        "G6 状态机合法": gate_g6(fm),
    }
    all_pass = all(ok for ok, _ in results.values())
    return all_pass, results


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("md_path", help="待检 markdown 文件路径")
    args = parser.parse_args()

    path = Path(args.md_path)
    if not path.exists():
        print(f"文件不存在: {path}", file=sys.stderr)
        return 1
    if not path.is_file():
        print(f"不是文件: {path}", file=sys.stderr)
        return 1

    print(f"=== 机械门禁体检: {path} ===\n")
    all_pass, results = check_file(path)
    overall = True
    for name, (ok, details) in results.items():
        overall &= run_gate(name, ok, details)

    print()
    print(f"=== 总裁定: {'全过 ✅' if overall else '有 FAIL ❌'} ===")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
