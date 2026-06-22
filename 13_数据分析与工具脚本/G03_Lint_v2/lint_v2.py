#!/usr/bin/env python3
"""G03_Lint v2 for the retail knowledge vault.

Read-only scanner for Markdown files. It writes a dashboard report only.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


DEFAULT_EXCLUDES = {"99_归档", "Clippings", ".git"}
FORMAL_ROOTS = ("01_", "04_", "09_", "10_", "16_")
REQUIRED_FIELDS = ("title", "version", "status", "owner", "source_type")
SIGNOFF_FIELDS = ("signoff", "signed", "signed_off")
STATUS_EXEMPT_PATTERNS = ("案例", "记录", "导航", "索引", "README")

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
    return parser.parse_args()


def should_exclude(path: Path, root: Path) -> bool:
    rel_parts = path.relative_to(root).parts
    return any(part in DEFAULT_EXCLUDES for part in rel_parts)


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
        target = Path(target).stem
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


def main() -> int:
    args = parse_args()
    root = Path(args.vault).resolve()
    output = Path(args.output)
    if not output.is_absolute():
        output = root / output

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

    timestamp = dt.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    lines: list[str] = []
    lines.extend(
        [
            "# G03_Lint v2 知识库体检仪表盘",
            "",
            f"- 扫描时间：{timestamp}",
            f"- Vault：`{root}`",
            f"- 扫描文件总数：{len(docs)}",
            f"- 排除目录：`{', '.join(sorted(DEFAULT_EXCLUDES))}`",
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

    lines.extend(["", "## 阻断项", ""])
    if sensitive_hits:
        lines.append("- 阻断级：敏感查存在命中。需先复核并处理红线项。")
    else:
        lines.append("- 无红线敏感命中。")

    lines.extend(["", "## 运行说明", ""])
    lines.append("- 本报告由 `13_数据分析与工具脚本/G03_Lint_v2/lint_v2.py` 生成。")
    lines.append("- 脚本只扫描 Markdown，不读取 Excel/CSV，不修改被扫描文件。")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {output}")
    print(
        "metrics: "
        f"broken={len(broken_targets)} orphan={len(orphan_docs)} "
        f"active_no_signoff={len(active_without_signoff)} "
        f"missing_fields={len(missing_fields)} redline={len(sensitive_hits)} "
        f"version_mismatch={len(version_mismatches)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
