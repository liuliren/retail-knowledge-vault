#!/usr/bin/env python3
"""G03_Lint v2 for the retail knowledge vault.

Read-only scanner for Markdown files. It writes a dashboard report only.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


DEFAULT_EXCLUDES = {"99_归档", "Clippings", ".git", "worktrees"}
AUTOMATION_RUNTIME = Path("13_数据分析与工具脚本/知识库自动化_v1/runtime")
# 红线/越权检测豁免冻结源料与历史日志（只检测正式件，不误伤不可变源/留痕）
SIGNOFF_AUDIT_EXCLUDES = ("99_原始素材", "Claude执行日志", "Codex执行日志")
# Schema查(缺字段)豁免区: 冻结raw/外部参考/归档/系统配置不按正式件schema考核(六哥2026-07-06 D3裁)
SCHEMA_EXEMPT_PREFIXES = ("99_原始素材", "14_外部案例与行业研究", "60_archive", ".claude", ".agents", "90_素材")
FORMAL_ROOTS = ("01_", "04_", "09_", "10_", "16_")
REQUIRED_FIELDS = ("title", "version", "status", "owner", "source_type")
SIGNOFF_FIELDS = ("signoff", "signed", "signed_off")
STATUS_EXEMPT_PATTERNS = ("案例", "记录", "导航", "索引", "README")
# execute 前置状态登记表（存在性检查目标）
EXECUTE_PRECOND_FILE = "00_入口与总索引/03_治理规范/Codex执行前置状态登记表_v0.1.md"
CANDIDATE_APPROVED_RE = re.compile(r"approval_status:\s*approved|approved_by:")

# ── 语义规则（弱检测·只 warning）──
# 语义检测豁免：冻结源料 + 历史日志 + 输出区草稿（不误伤）
SEMANTIC_EXCLUDES = ("99_原始素材", "Claude执行日志", "Codex执行日志", "Claude输出区", "Codex输出区", "90_素材")
# provenance 检测优先目录
PROVENANCE_ROOTS = ("00_入口与总索引/03_治理规范/", "01_科学零售方法论/", "04_", "05_", "16_客户与战役档案/")
# provenance frontmatter 键（存其一即视为有来源）
PROVENANCE_FM_KEYS = ("provenance", "source", "source_attribution", "definition_source", "related")
# provenance 正文标志词
PROVENANCE_BODY_TERMS = ("来源", "依据", "原典", "evidence", "provenance", "source_attribution")
# supersession：frontmatter 标记被取代的键/值
SUPERSESSION_STATUSES = ("superseded", "deprecated", "replaced")
SUPERSESSION_TARGET_KEYS = ("superseded_by", "replaced_by", "superseded_reason", "归档说明")
# failed 资产：需附原因的状态值
FAILED_STATES = ("failed", "侥幸", "果差但决策稳", "blocked")
FAILED_REASON_KEYS = ("failure_reason", "blocked_reason", "pending_reason", "superseded_reason", "lessons")
FAILED_REASON_BODY = ("失败原因", "阻塞原因", "回填点", "下一步", "外因", "教训")
# 7 值定版(六哥2026-07-03签字·文档工程化标准§status);seed=draft合法别名(lint不报错)
CANONICAL_STATUSES = {"draft", "review", "candidate", "active", "stable", "deprecated", "archived", "seed", "delivered"}
SUMMARY_REQUIRED_SOURCE_TYPES = {
    "method",
    "methodology",
    "decision_rule",
    "product_definition",
}

WIKI_LINK_RE = re.compile(r"(?<!!)\[\[([^\]\n]+)\]\]")
EAN13_RE = re.compile(r"(?<![0-9])(69[0-9]{11})(?![0-9])")
GENERAL_13_RE = re.compile(r"(?<![0-9])([0-9]{13})(?![0-9])")
PRICE_RE = re.compile(
    r"(进价|成本价|采购价|含税进价|不含税进价)[ \t]*[:：=][ \t]*([0-9]+(?:\.[0-9]{1,4})?)"
)
VERSION_IN_NAME_RE = re.compile(r"(?<![A-Za-z0-9])v([0-9]+(?:\.[0-9]+)*)(?![A-Za-z0-9])", re.I)


@dataclass(frozen=True)
class MarkdownDoc:
    path: Path
    rel: str
    stem: str
    text: str
    body: str
    frontmatter: dict[str, object]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run G03_Lint v2 checks.")
    parser.add_argument("--vault", default=".", help="Vault root path.")
    parser.add_argument(
        "--output",
        default="00_入口与总索引/05_审计与档案/lint_仪表盘_最新.md",
        help="Dashboard output path, relative to vault unless absolute.",
    )
    parser.add_argument(
        "--json-output",
        help="Optional structured JSON output path, relative to vault unless absolute.",
    )
    return parser.parse_args()


def should_exclude(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    if any(part in DEFAULT_EXCLUDES for part in rel.parts):
        return True
    try:
        rel.relative_to(AUTOMATION_RUNTIME)
        return True
    except ValueError:
        return False


def iter_markdown(root: Path) -> Iterable[Path]:
    for path in root.rglob("*.md"):
        if not should_exclude(path, root):
            yield path


def parse_scalar(value: str) -> object:
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [item.strip().strip("\"'") for item in inner.split(",")]
    return value.strip("\"'")


def parse_frontmatter(text: str) -> tuple[dict[str, object], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 4)
    if end == -1:
        return {}, text
    raw = text[4:end].splitlines()
    body = text[end + len("\n---") :].lstrip("\n")
    data: dict[str, object] = {}
    current_key: str | None = None
    for line in raw:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if re.match(r"^[A-Za-z0-9_\-]+:", line):
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            if value:
                data[key] = parse_scalar(value)
                current_key = None
            else:
                data[key] = []
                current_key = key
            continue
        if current_key and line.strip().startswith("- "):
            existing = data.setdefault(current_key, [])
            if isinstance(existing, list):
                existing.append(line.strip()[2:].strip().strip("\"'"))
    return data, body


def load_docs(root: Path) -> list[MarkdownDoc]:
    docs: list[MarkdownDoc] = []
    for path in sorted(iter_markdown(root)):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="utf-8", errors="replace")
        frontmatter, body = parse_frontmatter(text)
        docs.append(
            MarkdownDoc(
                path=path,
                rel=path.relative_to(root).as_posix(),
                stem=path.stem,
                text=text,
                body=body,
                frontmatter=frontmatter,
            )
        )
    return docs


def as_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()] if str(value).strip() else []


def canonical_link_target(raw: str) -> str:
    target = raw.split("|", 1)[0].split("#", 1)[0].strip()
    target = target.replace("\\", "/")
    if "/" in target:
        # NOTE: use basename split, not Path(...).stem — Path.stem strips
        # everything after the LAST dot, which corrupts filenames that
        # contain a literal "." in a version segment (e.g. "..._v0.1_候选"),
        # turning a valid full-path link into a false-positive broken link.
        target = target.rsplit("/", 1)[-1]
    if target.endswith(".md"):
        target = target[:-3]
    return target.strip()


def extract_links(doc: MarkdownDoc) -> list[str]:
    return [canonical_link_target(match.group(1)) for match in WIKI_LINK_RE.finditer(doc.text)]


def build_title_index(docs: list[MarkdownDoc]) -> set[str]:
    titles: set[str] = set()
    for doc in docs:
        titles.add(doc.stem)
        title = doc.frontmatter.get("title")
        if title:
            titles.add(str(title).strip())
        for alias in as_list(doc.frontmatter.get("aliases")) + as_list(doc.frontmatter.get("alias")):
            titles.add(alias)
    return {title for title in titles if title}


def formal_doc(doc: MarkdownDoc) -> bool:
    return doc.rel.startswith(FORMAL_ROOTS)


def has_signoff(doc: MarkdownDoc) -> bool:
    return any(str(doc.frontmatter.get(field, "")).strip() for field in SIGNOFF_FIELDS)


def is_status_exempt(doc: MarkdownDoc) -> bool:
    haystack = f"{doc.rel} {doc.frontmatter.get('title', '')} {' '.join(as_list(doc.frontmatter.get('tags')))}"
    return any(pattern in haystack for pattern in STATUS_EXEMPT_PATTERNS)


def linked_to_doc(doc: MarkdownDoc, inbound_targets: set[str]) -> bool:
    names = {doc.stem}
    names.update(as_list(doc.frontmatter.get("aliases")))
    names.update(as_list(doc.frontmatter.get("alias")))
    return any(name in inbound_targets for name in names if name)


def mask_digits(value: str) -> str:
    if len(value) <= 5:
        return "*" * len(value)
    return f"{value[:3]}{'*' * (len(value) - 5)}{value[-2:]}"


def version_from_name(stem: str) -> str | None:
    matches = VERSION_IN_NAME_RE.findall(stem)
    if not matches:
        return None
    return f"v{matches[-1]}"


def version_equal(name_version: str, fm_version: object) -> bool:
    value = str(fm_version).strip()
    if not value:
        return False
    return value.lower().lstrip("v") == name_version.lower().lstrip("v")


def top_rows(counter: Counter[str], limit: int = 20) -> list[tuple[str, int]]:
    return counter.most_common(limit)


def render_table(headers: list[str], rows: list[list[object]]) -> list[str]:
    if not rows:
        return ["无"]
    lines = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join([":--" for _ in headers]) + "|",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(cell).replace("\n", " ") for cell in row) + " |")
    return lines


def atomic_write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def main() -> int:
    args = parse_args()
    root = Path(args.vault).resolve()
    output = Path(args.output)
    if not output.is_absolute():
        output = root / output
    json_output = Path(args.json_output) if args.json_output else None
    if json_output is not None and not json_output.is_absolute():
        json_output = root / json_output

    docs = load_docs(root)
    title_index = build_title_index(docs)
    inbound_by_target: Counter[str] = Counter()
    inbound_by_file: defaultdict[str, set[str]] = defaultdict(set)
    broken_targets: Counter[str] = Counter()
    broken_files: defaultdict[str, set[str]] = defaultdict(set)

    all_links_by_doc: dict[str, list[str]] = {}
    for doc in docs:
        links = [link for link in extract_links(doc) if link]
        all_links_by_doc[doc.rel] = links
        for link in links:
            inbound_by_target[link] += 1
            inbound_by_file[link].add(doc.rel)
            if link not in title_index:
                broken_targets[link] += 1
                broken_files[link].add(doc.rel)

    inbound_targets = set(inbound_by_target)
    orphan_docs = [
        doc
        for doc in docs
        if formal_doc(doc)
        and not linked_to_doc(doc, inbound_targets)
    ]

    active_without_signoff = [
        doc
        for doc in docs
        if str(doc.frontmatter.get("status", "")).strip() == "active"
        and not has_signoff(doc)
    ]

    missing_fields: list[tuple[MarkdownDoc, list[str]]] = []
    for doc in docs:
        if doc.rel.startswith(SCHEMA_EXEMPT_PREFIXES):
            continue
        missing = [field for field in REQUIRED_FIELDS if not str(doc.frontmatter.get(field, "")).strip()]
        if missing:
            missing_fields.append((doc, missing))

    sensitive_hits: list[tuple[str, str, int, str]] = []
    for doc in docs:
        ean_hits = EAN13_RE.findall(doc.text)
        general_hits = [hit for hit in GENERAL_13_RE.findall(doc.text) if not hit.startswith("69")]
        price_hits = PRICE_RE.findall(doc.text)
        if ean_hits:
            sample = ", ".join(mask_digits(hit) for hit in sorted(set(ean_hits))[:3])
            sensitive_hits.append((doc.rel, "EAN13_69", len(ean_hits), sample))
        if general_hits:
            sample = ", ".join(mask_digits(hit) for hit in sorted(set(general_hits))[:3])
            sensitive_hits.append((doc.rel, "GENERAL_13_DIGIT", len(general_hits), sample))
        if price_hits:
            sensitive_hits.append((doc.rel, "PRICE_VALUE", len(price_hits), "masked"))

    version_mismatches: list[tuple[str, str, str]] = []
    for doc in docs:
        name_version = version_from_name(doc.stem)
        if name_version and not version_equal(name_version, doc.frontmatter.get("version")):
            version_mismatches.append((doc.rel, name_version, str(doc.frontmatter.get("version", ""))))

    # 7. candidate 越权签字查：status=candidate 却带 approved 签字（candidate 不得 approved）
    def _signoff_audit_skip(doc: MarkdownDoc) -> bool:
        return any(p in doc.rel for p in SIGNOFF_AUDIT_EXCLUDES)

    candidate_approved: list[tuple[str, str]] = []
    for doc in docs:
        if _signoff_audit_skip(doc):
            continue
        if str(doc.frontmatter.get("status", "")).strip() != "candidate":
            continue
        fm_end = doc.text.find("\n---", 4) if doc.text.startswith("---\n") else -1
        fm_raw = doc.text[4:fm_end] if fm_end != -1 else ""
        if CANDIDATE_APPROVED_RE.search(fm_raw):
            candidate_approved.append((doc.rel, str(doc.frontmatter.get("title", ""))))

    # 8. execute 前置状态登记表存在性 + 是否声明「不允许 execute」
    precond_path = root / EXECUTE_PRECOND_FILE
    precond_exists = precond_path.exists()
    precond_blocks_execute = False
    if precond_exists:
        ptext = precond_path.read_text(encoding="utf-8", errors="replace")
        precond_blocks_execute = "不允许 execute" in ptext or "不允许execute" in ptext

    # ── 语义规则（弱检测·只 warning，不 fatal，不自动修）──
    def _semantic_skip(doc: MarkdownDoc) -> bool:
        return any(p in doc.rel for p in SEMANTIC_EXCLUDES)

    def _fm_has(doc: MarkdownDoc, keys: tuple[str, ...]) -> bool:
        return any(str(doc.frontmatter.get(k, "")).strip() not in ("", "[]") for k in keys)

    # 9. provenance 弱检测：优先目录 + status candidate/active，缺所有来源信号
    provenance_warnings: list[tuple[str, str]] = []
    for doc in docs:
        if _semantic_skip(doc) or not doc.rel.startswith(PROVENANCE_ROOTS):
            continue
        if str(doc.frontmatter.get("status", "")).strip() not in ("candidate", "active"):
            continue
        has_fm = _fm_has(doc, PROVENANCE_FM_KEYS) or str(doc.frontmatter.get("source_type", "")).strip() != ""
        has_body = any(term in doc.body for term in PROVENANCE_BODY_TERMS)
        if not (has_fm or has_body):
            provenance_warnings.append((doc.rel, "缺 source/来源/依据/原典/related 等来源信号"))

    # 10. supersession 弱检测：标记被取代但无替代目标
    supersession_warnings: list[tuple[str, str]] = []
    for doc in docs:
        if _semantic_skip(doc):
            continue
        status_val = str(doc.frontmatter.get("status", "")).strip().lower()
        if status_val in SUPERSESSION_STATUSES:
            if not _fm_has(doc, SUPERSESSION_TARGET_KEYS) and "被取代::" not in doc.body:
                supersession_warnings.append((doc.rel, f"status={status_val} 但缺 superseded_by/replaced_by/被取代:: 目标"))

    # 11. failed 记录保护弱检测：failed/侥幸/果差但决策稳/blocked 状态缺原因说明
    failed_record_warnings: list[tuple[str, str]] = []
    for doc in docs:
        if _semantic_skip(doc):
            continue
        ds = str(doc.frontmatter.get("decision_status", "")).strip()
        st = str(doc.frontmatter.get("status", "")).strip()
        if ds in FAILED_STATES or st in FAILED_STATES:
            has_reason = _fm_has(doc, FAILED_REASON_KEYS) or any(t in doc.body for t in FAILED_REASON_BODY)
            if not has_reason:
                failed_record_warnings.append((doc.rel, f"状态={ds or st} 但缺 原因/回填点/下一步（failed 是资产，须留因）"))

    # 12. summary 检测：只强检耐久知识，不对日志/原料/全部历史件批量施压
    missing_summary: list[str] = []
    for doc in docs:
        if _semantic_skip(doc):
            continue
        source_type = str(doc.frontmatter.get("source_type", "")).strip()
        summary_required = (
            doc.rel.startswith("01_科学零售方法论/")
            or source_type in SUMMARY_REQUIRED_SOURCE_TYPES
        )
        if summary_required and not str(doc.frontmatter.get("summary", "")).strip():
            missing_summary.append(doc.rel)

    # 13. status 枚举：非规范值只报告，不自动改写
    invalid_status: list[tuple[str, str]] = []
    for doc in docs:
        status_value = str(doc.frontmatter.get("status", "")).strip()
        if status_value and status_value not in CANONICAL_STATUSES:
            invalid_status.append((doc.rel, status_value))

    timestamp = dt.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    lines: list[str] = []
    lines.extend(
        [
            "# G03_Lint v2 知识库体检仪表盘",
            "",
            f"- 扫描时间：{timestamp}",
            f"- Vault：`{root}`",
            f"- 扫描文件总数：{len(docs)}",
            f"- 排除目录：`{', '.join(sorted(DEFAULT_EXCLUDES))}, {AUTOMATION_RUNTIME.as_posix()}`",
            "",
            "## 顶部指标卡",
            "",
        ]
    )
    metrics = [
        ["断链目标数", len(broken_targets)],
        ["孤儿文件数", len(orphan_docs)],
        ["active 无签字数", len(active_without_signoff)],
        ["缺字段文件数", len(missing_fields)],
        ["红线命中文件项", len(sensitive_hits)],
        ["版本不一致数", len(version_mismatches)],
        ["candidate 越权签字数", len(candidate_approved)],
        ["execute 前置登记表", "存在·已声明阻断" if (precond_exists and precond_blocks_execute) else ("存在" if precond_exists else "缺失")],
        ["provenance warning", len(provenance_warnings)],
        ["supersession warning", len(supersession_warnings)],
        ["failed 记录 warning", len(failed_record_warnings)],
        ["核心知识缺 summary", len(missing_summary)],
        ["非规范 status", len(invalid_status)],
    ]
    lines.extend(render_table(["指标", "数量"], metrics))

    lines.extend(["", "## 1. 断链查", ""])
    broken_rows = [
        [target, count, len(broken_files[target]), "; ".join(sorted(broken_files[target])[:3])]
        for target, count in top_rows(broken_targets)
    ]
    lines.extend(render_table(["断链目标", "引用数", "引用文件数", "示例引用文件"], broken_rows))

    lines.extend(["", "## 2. 孤儿查", ""])
    orphan_rows = [[doc.rel, doc.frontmatter.get("title", "")] for doc in orphan_docs[:20]]
    lines.extend(render_table(["文件", "title"], orphan_rows))

    lines.extend(["", "## 3. 状态查", ""])
    active_rows = [
        [
            doc.rel,
            doc.frontmatter.get("title", ""),
            doc.frontmatter.get("owner", ""),
            "是" if is_status_exempt(doc) else "否",
        ]
        for doc in active_without_signoff[:20]
    ]
    lines.extend(render_table(["文件", "title", "owner", "豁免类"], active_rows))

    lines.extend(["", "## 4. Schema 查", ""])
    schema_rows = [[doc.rel, ", ".join(missing)] for doc, missing in missing_fields[:20]]
    lines.extend(render_table(["文件", "缺失字段"], schema_rows))

    lines.extend(["", "## 5. 敏感查（红线）", ""])
    sensitive_rows = [[path, kind, count, sample] for path, kind, count, sample in sensitive_hits[:20]]
    lines.extend(render_table(["文件", "类型", "命中数", "掩码示例"], sensitive_rows))

    lines.extend(["", "## 6. 版本查", ""])
    version_rows = [[path, name_version, fm_version] for path, name_version, fm_version in version_mismatches[:20]]
    lines.extend(render_table(["文件", "文件名版本", "frontmatter version"], version_rows))

    lines.extend(["", "## 7. candidate 越权签字查", ""])
    cand_rows = [[rel, title] for rel, title in candidate_approved[:20]]
    lines.extend(render_table(["文件", "title"], cand_rows))
    lines.append("")
    lines.append("> 规则：status=candidate 不得带 approved 签字（candidate 不得 approved）。命中=越权，需降签字或升 active 后再签。")

    lines.extend(["", "## 8. execute 前置状态查", ""])
    lines.append(f"- 登记表：`{EXECUTE_PRECOND_FILE}` → {'存在' if precond_exists else '**缺失**'}")
    lines.append(f"- 是否声明「不允许 execute」：{'是（闸门关闭）' if precond_blocks_execute else '否（需复核）'}")

    lines.extend(["", "## 9. provenance 弱检测（warning）", ""])
    prov_rows = [[rel, reason] for rel, reason in provenance_warnings[:20]]
    lines.extend(render_table(["文件", "原因"], prov_rows))
    lines.append("")
    lines.append("> 弱检测：优先目录(治理/方法论/04/05/16)的 candidate/active 缺来源信号。warning，不 fatal，不自动修。")

    lines.extend(["", "## 10. supersession 弱检测（warning）", ""])
    sup_rows = [[rel, reason] for rel, reason in supersession_warnings[:20]]
    lines.extend(render_table(["文件", "原因"], sup_rows))
    lines.append("")
    lines.append("> 弱检测：status=superseded/deprecated 但无 superseded_by/replaced_by/被取代:: 目标。warning。")

    lines.extend(["", "## 11. failed 记录保护弱检测（warning）", ""])
    fail_rows = [[rel, reason] for rel, reason in failed_record_warnings[:20]]
    lines.extend(render_table(["文件", "原因"], fail_rows))
    lines.append("")
    lines.append("> failed/侥幸/果差但决策稳/blocked 是资产；须留原因/回填点/下一步。warning，**严禁据此删除 failed 记录**。")

    lines.extend(["", "## 12. 核心知识 summary 查", ""])
    lines.extend(render_table(["文件"], [[rel] for rel in missing_summary[:20]]))
    lines.append("")
    lines.append("> 仅检查方法论、决策规则、产品定义与 `01_科学零售方法论`；按需回填，不批量改写全库。")

    lines.extend(["", "## 13. status 枚举查", ""])
    lines.extend(render_table(["文件", "当前 status"], [[rel, value] for rel, value in invalid_status[:20]]))
    lines.append("")
    lines.append("> 规范枚举：draft / candidate / active / deprecated / archived。非规范值只报告，不自动改写。")

    lines.extend(["", "## 阻断项", ""])
    if sensitive_hits:
        lines.append("- 阻断级：敏感查存在命中。需先复核并处理红线项。")
    else:
        lines.append("- 无红线敏感命中。")
    if candidate_approved:
        lines.append("- 阻断级：存在 candidate 越权签字，需处理。")
    lines.append(
        f"- warning 级（不阻断）：provenance {len(provenance_warnings)} / "
        f"supersession {len(supersession_warnings)} / failed {len(failed_record_warnings)}。"
    )

    lines.extend(["", "## 运行说明", ""])
    lines.append("- 本报告由 `13_数据分析与工具脚本/G03_Lint_v2/lint_v2.py` 生成。")
    lines.append("- 脚本只扫描 Markdown，不读取 Excel/CSV，不修改被扫描文件。")
    lines.append("- signoff/红线/越权审计豁免：`99_原始素材`（冻结源料）与执行日志（历史留痕）。")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if json_output is not None:
        structured_metrics = {
            "broken": len(broken_targets),
            "orphan": len(orphan_docs),
            "active_no_signoff": len(active_without_signoff),
            "missing_fields": len(missing_fields),
            "redline": len(sensitive_hits),
            "version_mismatch": len(version_mismatches),
            "candidate_approved": len(candidate_approved),
            "execute_precondition_exists": int(precond_exists),
            "execute_precondition_blocks": int(precond_blocks_execute),
            "prov_warn": len(provenance_warnings),
            "sup_warn": len(supersession_warnings),
            "failed_warn": len(failed_record_warnings),
            "missing_summary": len(missing_summary),
            "invalid_status": len(invalid_status),
        }
        atomic_write_json(
            json_output,
            {
                "schema_version": "1",
                "generated_at": timestamp,
                "vault": str(root),
                "scan": {
                    "markdown_files": len(docs),
                    "excluded": sorted(DEFAULT_EXCLUDES)
                    + [AUTOMATION_RUNTIME.as_posix()],
                },
                "metrics": structured_metrics,
                "blocked": bool(sensitive_hits or candidate_approved),
                "block_reasons": [
                    reason
                    for condition, reason in (
                        (bool(sensitive_hits), "sensitive_redline"),
                        (bool(candidate_approved), "candidate_approved"),
                    )
                    if condition
                ],
                "findings": {
                    "broken_targets": sorted(broken_targets),
                    "orphan_files": [doc.rel for doc in orphan_docs],
                    "active_without_signoff": [doc.rel for doc in active_without_signoff],
                    "missing_fields": [
                        {"path": doc.rel, "fields": missing}
                        for doc, missing in missing_fields
                    ],
                    "sensitive_files": sorted({path for path, _, _, _ in sensitive_hits}),
                    "version_mismatches": [
                        {"path": path, "name_version": name_version, "frontmatter_version": fm_version}
                        for path, name_version, fm_version in version_mismatches
                    ],
                    "candidate_approved": [rel for rel, _ in candidate_approved],
                    "provenance_warnings": [rel for rel, _ in provenance_warnings],
                    "supersession_warnings": [rel for rel, _ in supersession_warnings],
                    "failed_record_warnings": [rel for rel, _ in failed_record_warnings],
                    "missing_summary": missing_summary,
                    "invalid_status": [
                        {"path": rel, "status": value}
                        for rel, value in invalid_status
                    ],
                },
            },
        )
    print(f"wrote {output}")
    print(
        "metrics: "
        f"broken={len(broken_targets)} orphan={len(orphan_docs)} "
        f"active_no_signoff={len(active_without_signoff)} "
        f"missing_fields={len(missing_fields)} redline={len(sensitive_hits)} "
        f"version_mismatch={len(version_mismatches)} "
        f"prov_warn={len(provenance_warnings)} sup_warn={len(supersession_warnings)} "
        f"failed_warn={len(failed_record_warnings)} "
        f"missing_summary={len(missing_summary)} invalid_status={len(invalid_status)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
