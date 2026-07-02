from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Optional, Sequence

from .inventory import scan_vault
from .pipeline import PipelineError, run_pipeline
from .scheduler import MODULE_PATH, install_launchd, write_launchd_preview


def runtime_path(vault: Path) -> Path:
    return vault.resolve() / MODULE_PATH / "runtime"


def read_status(runtime: Path) -> Dict[str, object]:
    log = runtime / "runs.jsonl"
    if not log.exists():
        return {"status": "never_run"}
    lines = [line for line in log.read_text(encoding="utf-8").splitlines() if line.strip()]
    return json.loads(lines[-1]) if lines else {"status": "never_run"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="晟果新零售知识库自动化执行层")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("run", "status", "scan", "scheduler-preview", "scheduler-install"):
        command = subparsers.add_parser(name)
        command.add_argument("--vault", default=".", help="Vault 根目录")
    for name in ("scheduler-preview", "scheduler-install"):
        scheduler = subparsers.choices[name]
        scheduler.add_argument("--hour", type=int, default=9)
        scheduler.add_argument("--minute", type=int, default=0)
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    vault = Path(args.vault).resolve()
    runtime = runtime_path(vault)
    if args.command == "status":
        print(json.dumps(read_status(runtime), ensure_ascii=False, indent=2))
        return 0
    if args.command == "scan":
        snapshot = scan_vault(vault)
        print(
            json.dumps(
                {"generated_at": snapshot.generated_at, "asset_count": len(snapshot.assets)},
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    if args.command == "scheduler-preview":
        output = write_launchd_preview(vault, hour=args.hour, minute=args.minute)
        print(output)
        return 0
    if args.command == "scheduler-install":
        output = install_launchd(vault, hour=args.hour, minute=args.minute)
        print(output)
        return 0
    try:
        result = run_pipeline(vault, runtime_dir=runtime)
    except PipelineError as exc:
        print(json.dumps({"status": "blocked_or_failed", "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0
