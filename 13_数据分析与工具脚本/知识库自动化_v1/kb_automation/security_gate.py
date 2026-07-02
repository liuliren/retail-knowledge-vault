from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Dict, List


SENSITIVE_EXTENSIONS = {".xls", ".xlsx", ".csv", ".db", ".sqlite", ".sqlite3"}
PRIVATE_PATH_MARKERS = ("_client_private/",)
SENSITIVE_PATH_TERMS = (
    "完整明细",
    "dry-run",
    "dryrun",
    "execute",
    "金矿",
    "清库",
    "补货",
    "ce桶",
    "b桶",
    "d桶",
    "客户诊断",
)
KNOWN_CUSTOMER_TERMS = ("花厅坊",)
OPERATING_TERMS = (
    "经营判断",
    "派生结论",
    "金矿",
    "候选",
    "清库",
    "补货",
    "完整明细",
    "毛利",
    "psd",
    "死货",
    "动销",
    "库龄",
    "库存诊断",
    "ce桶",
    "b桶",
    "d桶",
    "dry-run",
    "dryrun",
    "execute",
)


def _git(root: Path, args: List[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git"] + args,
        cwd=str(root),
        text=True,
        capture_output=True,
    )


def _finding(path: str, category: str) -> Dict[str, str]:
    return {"path": path, "category": category}


def inspect_staged(root: Path) -> Dict[str, object]:
    root = root.resolve()
    inside = _git(root, ["rev-parse", "--is-inside-work-tree"])
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        return {
            "schema_version": "1",
            "status": "not_git_repo",
            "blocked": False,
            "staged_count": 0,
            "findings": [],
        }

    names_process = _git(root, ["diff", "--cached", "--name-only", "--diff-filter=ACMR"])
    if names_process.returncode != 0:
        return {
            "schema_version": "1",
            "status": "git_error",
            "blocked": True,
            "staged_count": 0,
            "findings": [{"path": "[git]", "category": "inspection_failed"}],
        }
    paths = sorted(line for line in names_process.stdout.splitlines() if line.strip())
    findings: List[Dict[str, str]] = []
    seen = set()

    def add(path: str, category: str) -> None:
        key = (path, category)
        if key not in seen:
            seen.add(key)
            findings.append(_finding(path, category))

    for path in paths:
        lowered = path.lower()
        suffix = Path(path).suffix.lower()
        if suffix in SENSITIVE_EXTENSIONS:
            add(path, "sensitive_extension")
        if any(marker in lowered for marker in PRIVATE_PATH_MARKERS):
            add(path, "private_zone")
        if any(term in lowered for term in SENSITIVE_PATH_TERMS):
            add(path, "sensitive_path")

    text_paths = [
        path
        for path in paths
        if Path(path).suffix.lower() in {".md", ".txt", ".py", ".json", ".yaml", ".yml"}
    ]
    if text_paths:
        diff_process = _git(
            root,
            ["diff", "--cached", "--unified=0", "--no-color", "--"] + text_paths,
        )
        if diff_process.returncode != 0:
            add("[git]", "inspection_failed")
        else:
            current_path = ""
            added_lines: Dict[str, List[str]] = {}
            for line in diff_process.stdout.splitlines():
                if line.startswith("+++ b/"):
                    current_path = line[6:]
                    added_lines.setdefault(current_path, [])
                elif current_path and line.startswith("+") and not line.startswith("+++"):
                    added_lines[current_path].append(line[1:].lower())
            for path, lines in added_lines.items():
                joined = "\n".join(lines)
                has_customer = any(term.lower() in joined for term in KNOWN_CUSTOMER_TERMS)
                has_operating = any(term.lower() in joined for term in OPERATING_TERMS)
                if has_customer and has_operating:
                    add(path, "customer_derived_content")

    return {
        "schema_version": "1",
        "status": "blocked" if findings else "pass",
        "blocked": bool(findings),
        "staged_count": len(paths),
        "findings": sorted(findings, key=lambda item: (item["path"], item["category"])),
    }

