from __future__ import annotations

import datetime as dt
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Set

from .frontmatter import parse_frontmatter_prefix
from .models import AssetRecord, InventorySnapshot


SENSITIVE_EXTENSIONS = {".xls", ".xlsx", ".csv", ".db", ".sqlite", ".sqlite3"}
OFFICE_EXTENSIONS = SENSITIVE_EXTENSIONS | {".doc", ".docx", ".pdf", ".ppt", ".pptx"}
MEDIA_EXTENSIONS = {".jpg", ".jpeg", ".png", ".heic", ".webp", ".mp4", ".mov"}
ARCHIVE_EXTENSIONS = {".zip", ".rar", ".7z", ".gz"}
DEFAULT_EXCLUDES = {".git", "_client_private", "__pycache__", ".venv", "venv"}
METADATA_ONLY_PREFIXES = ("99_归档/", "Clippings/", "99_原始素材/")


@dataclass(frozen=True)
class InventoryConfig:
    runtime_dir: str = "13_数据分析与工具脚本/知识库自动化_v1/runtime"
    extra_excludes: tuple = ()

    @property
    def excluded_names(self) -> Set[str]:
        return set(DEFAULT_EXCLUDES).union(self.extra_excludes)


def _excluded(path: Path, root: Path, config: InventoryConfig) -> bool:
    rel = path.relative_to(root)
    if any(part in config.excluded_names for part in rel.parts):
        return True
    runtime = Path(config.runtime_dir)
    try:
        rel.relative_to(runtime)
        return True
    except ValueError:
        return False


def _iter_files(root: Path, config: InventoryConfig) -> Iterable[Path]:
    for path in root.rglob("*"):
        if path.is_file() and not _excluded(path, root, config):
            yield path


def _asset_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".md":
        return "markdown"
    if suffix in OFFICE_EXTENSIONS:
        return "office_data"
    if suffix in MEDIA_EXTENSIONS:
        return "media"
    if suffix in ARCHIVE_EXTENSIONS:
        return "archive"
    if suffix in {".py", ".sh", ".js", ".jsx", ".css", ".sql"}:
        return "code"
    if suffix in {".json", ".yaml", ".yml", ".toml"}:
        return "config"
    return "other"


def _zone(rel: str) -> str:
    if rel.startswith("99_归档/"):
        return "archive"
    if rel.startswith("Clippings/"):
        return "external_source"
    if "99_原始素材/" in rel or rel.startswith("99_原始素材/"):
        return "raw_source"
    if rel.startswith("98_AI协作中枢/"):
        return "ai_control"
    if rel.startswith(("00_", "01_", "02_", "03_", "04_", "05_", "06_", "07_", "08_")):
        return "formal_knowledge"
    if rel.startswith(("10_", "13_")):
        return "execution_asset"
    if rel.startswith(("09_", "15_", "16_")):
        return "evidence"
    return "infrastructure"


def _metadata_fingerprint(rel: str, size: int, modified_ns: int) -> str:
    value = "{}\0{}\0{}".format(rel, size, modified_ns).encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def _read_markdown(path: Path, rel: str) -> tuple:
    if rel.startswith(METADATA_ONLY_PREFIXES) or "99_原始素材/" in rel:
        return {}, None
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    text = data[:65536].decode("utf-8", errors="replace")
    return parse_frontmatter_prefix(text), digest


def _find_parent_entry(path: Path, root: Path) -> str:
    directory = path.parent if path.name != "README.md" else path.parent.parent
    while directory != root and root in directory.parents:
        candidate = directory / "README.md"
        if candidate.exists():
            return candidate.relative_to(root).as_posix()
        directory = directory.parent
    root_readme = root / "README.md"
    return "README.md" if root_readme.exists() and path != root_readme else ""


def _risk_flags(path: Path, rel: str) -> List[str]:
    flags: List[str] = []
    if path.suffix.lower() in SENSITIVE_EXTENSIONS:
        flags.append("sensitive_extension")
    if rel.startswith("98_AI协作中枢/") and ("输出区/" in rel or "执行日志" in rel):
        flags.append("ai_output_review_required")
    if "99_原始素材/" in rel or rel.startswith("99_原始素材/"):
        flags.append("raw_source")
    return flags


def scan_vault(root: Path, config: Optional[InventoryConfig] = None) -> InventorySnapshot:
    root = root.resolve()
    config = config or InventoryConfig()
    assets: List[AssetRecord] = []
    for path in sorted(_iter_files(root, config)):
        rel = path.relative_to(root).as_posix()
        stat = path.stat()
        frontmatter = {}
        content_sha256 = None
        if path.suffix.lower() == ".md":
            frontmatter, content_sha256 = _read_markdown(path, rel)
        assets.append(
            AssetRecord(
                path=rel,
                asset_type=_asset_type(path),
                size=stat.st_size,
                modified_ns=stat.st_mtime_ns,
                fingerprint=content_sha256 or _metadata_fingerprint(rel, stat.st_size, stat.st_mtime_ns),
                content_sha256=content_sha256,
                title=frontmatter.get("title", ""),
                version=frontmatter.get("version", ""),
                status=frontmatter.get("status", ""),
                owner=frontmatter.get("owner", ""),
                source_type=frontmatter.get("source_type", ""),
                client_safety=frontmatter.get("client_safety", ""),
                summary=frontmatter.get("summary", ""),
                parent_entry=_find_parent_entry(path, root),
                zone=_zone(rel),
                risk_flags=_risk_flags(path, rel),
            )
        )
    generated_at = dt.datetime.now(dt.timezone.utc).isoformat()
    return InventorySnapshot(generated_at=generated_at, assets=assets)

