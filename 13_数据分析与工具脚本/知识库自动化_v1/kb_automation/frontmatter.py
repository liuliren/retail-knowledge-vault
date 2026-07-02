from __future__ import annotations

import re
from typing import Dict


KEY_RE = re.compile(r"^([A-Za-z0-9_-]+):\s*(.*)$")


def parse_frontmatter_prefix(text: str) -> Dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    result: Dict[str, str] = {}
    for line in text[4:end].splitlines():
        match = KEY_RE.match(line)
        if not match:
            continue
        key, value = match.groups()
        result[key] = value.strip().strip("\"'")
    return result

