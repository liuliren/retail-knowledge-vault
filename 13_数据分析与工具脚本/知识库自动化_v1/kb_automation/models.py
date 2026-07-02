from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class AssetRecord:
    path: str
    asset_type: str
    size: int
    modified_ns: int
    fingerprint: str
    content_sha256: Optional[str] = None
    title: str = ""
    version: str = ""
    status: str = ""
    owner: str = ""
    source_type: str = ""
    client_safety: str = ""
    summary: str = ""
    parent_entry: str = ""
    zone: str = ""
    risk_flags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AssetRecord":
        return cls(**data)


@dataclass(frozen=True)
class InventorySnapshot:
    generated_at: str
    assets: List[AssetRecord]
    schema_version: str = "1"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "generated_at": self.generated_at,
            "assets": [asset.to_dict() for asset in self.assets],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InventorySnapshot":
        return cls(
            schema_version=str(data.get("schema_version", "1")),
            generated_at=str(data.get("generated_at", "")),
            assets=[AssetRecord.from_dict(item) for item in data.get("assets", [])],
        )


@dataclass(frozen=True)
class SnapshotDelta:
    added: List[str] = field(default_factory=list)
    modified: List[str] = field(default_factory=list)
    deleted: List[str] = field(default_factory=list)
    unchanged: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, List[str]]:
        return asdict(self)

