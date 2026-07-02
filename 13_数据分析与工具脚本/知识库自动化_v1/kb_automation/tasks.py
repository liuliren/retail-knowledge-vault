from __future__ import annotations

import datetime as dt
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List


TASK_SOURCES = (
    "98_AI协作中枢/02_Codex/Codex收件箱.md",
    "98_AI协作中枢/01_Claude_Code/Claude收件箱.md",
    "98_AI协作中枢/00_总控/当前任务队列.md",
)
TABLE_TASK_RE = re.compile(
    r"^\|\s*[^|]+\|\s*\*{0,2}([A-Za-z0-9]+(?:-[A-Za-z0-9]+)+)\*{0,2}\s*\|([^|]*)\|([^|]*)\|"
)
CHECKBOX_TASK_RE = re.compile(
    r"^-\s*(?:\*{2})?\[([ xX~])\]\s*(?:\*{2})?([A-Za-z0-9]+(?:-[A-Za-z0-9]+)+)(?:｜|\s|：|:)"
)


def normalize_status(raw: str) -> str:
    value = raw.strip().lower()
    if "冲突" in value:
        return "conflict"
    if "blocked" in value or "阻塞" in value or "缺字段" in value:
        return "blocked"
    if "✅" in value or "完成" in value or value == "x":
        return "completed"
    if "review" in value or "审阅" in value or "复核" in value:
        return "review"
    if "进行" in value or value == "~":
        return "in_progress"
    return "pending"


def _parse_source(path: Path, root: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    rel = path.relative_to(root).as_posix()
    tasks: List[Dict[str, str]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        table = TABLE_TASK_RE.match(line)
        if table:
            task_id, title, raw_status = table.groups()
            tasks.append(
                {
                    "id": task_id,
                    "title": title.strip().strip("*"),
                    "status": normalize_status(raw_status),
                    "source": rel,
                    "line": str(line_no),
                }
            )
            continue
        checkbox = CHECKBOX_TASK_RE.match(line)
        if checkbox:
            marker, task_id = checkbox.groups()
            tasks.append(
                {
                    "id": task_id,
                    "title": line.split("｜", 1)[1].split("**", 1)[0].strip()
                    if "｜" in line
                    else task_id,
                    "status": normalize_status(marker),
                    "source": rel,
                    "line": str(line_no),
                }
            )
    return tasks


def build_task_registry(root: Path) -> Dict[str, object]:
    root = root.resolve()
    observations: List[Dict[str, str]] = []
    for rel in TASK_SOURCES:
        observations.extend(_parse_source(root / rel, root))

    grouped: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for item in observations:
        grouped[item["id"]].append(item)

    tasks: List[Dict[str, object]] = []
    conflicts: List[Dict[str, object]] = []
    for task_id, items in sorted(grouped.items()):
        statuses = sorted({item["status"] for item in items})
        status = statuses[0] if len(statuses) == 1 else "conflict"
        task = {
            "id": task_id,
            "title": items[0]["title"],
            "status": status,
            "sources": [
                {"path": item["source"], "line": int(item["line"]), "status": item["status"]}
                for item in items
            ],
        }
        tasks.append(task)
        if status == "conflict":
            conflicts.append({"id": task_id, "statuses": statuses, "sources": task["sources"]})

    counts = Counter(str(task["status"]) for task in tasks)
    return {
        "schema_version": "1",
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "metrics": {
            "task_count": len(tasks),
            "pending": counts["pending"],
            "in_progress": counts["in_progress"],
            "review": counts["review"],
            "blocked": counts["blocked"],
            "completed": counts["completed"],
            "conflict_count": len(conflicts),
        },
        "tasks": tasks,
        "conflicts": conflicts,
    }

