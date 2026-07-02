from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from .models import InventorySnapshot, SnapshotDelta


def diff_snapshots(
    previous: Optional[InventorySnapshot], current: InventorySnapshot
) -> SnapshotDelta:
    old = {asset.path: asset.fingerprint for asset in previous.assets} if previous else {}
    new = {asset.path: asset.fingerprint for asset in current.assets}
    old_paths = set(old)
    new_paths = set(new)
    common = old_paths & new_paths
    return SnapshotDelta(
        added=sorted(new_paths - old_paths),
        modified=sorted(path for path in common if old[path] != new[path]),
        deleted=sorted(old_paths - new_paths),
        unchanged=sorted(path for path in common if old[path] == new[path]),
    )


def load_snapshot(path: Path) -> Optional[InventorySnapshot]:
    if not path.exists():
        return None
    return InventorySnapshot.from_dict(json.loads(path.read_text(encoding="utf-8")))


def write_snapshot(path: Path, snapshot: InventorySnapshot) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(snapshot.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)

