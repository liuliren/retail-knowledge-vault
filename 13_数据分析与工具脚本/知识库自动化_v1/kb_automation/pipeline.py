from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Callable, Dict, Optional

from .dashboard import build_decision_queue, render_dashboard, render_system_status
from .inventory import InventoryConfig, scan_vault
from .security_gate import inspect_staged
from .snapshot import diff_snapshots, load_snapshot, write_snapshot
from .tasks import build_task_registry


class PipelineError(RuntimeError):
    pass


class RunLock:
    def __init__(self, path: Path):
        self.path = path
        self.fd: Optional[int] = None

    def __enter__(self) -> "RunLock":
        try:
            self.fd = os.open(str(self.path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError as exc:
            raise PipelineError("已有自动化任务运行或上次锁未清理：{}".format(self.path)) from exc
        os.write(self.fd, str(os.getpid()).encode("ascii"))
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if self.fd is not None:
            os.close(self.fd)
        self.path.unlink(missing_ok=True)


def _atomic_json(path: Path, data: object) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def _append_log(path: Path, entry: Dict[str, object]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")


def run_g03(root: Path, output: Path) -> Dict[str, int]:
    script = root / "13_数据分析与工具脚本/G03_Lint_v2/lint_v2.py"
    if not script.exists():
        raise PipelineError("G03 脚本不存在：{}".format(script))
    json_output = output.with_suffix(".json")
    process = subprocess.run(
        [
            sys.executable,
            str(script),
            "--vault",
            str(root),
            "--output",
            str(output),
            "--json-output",
            str(json_output),
        ],
        cwd=str(root),
        text=True,
        capture_output=True,
    )
    if process.returncode != 0:
        raise PipelineError("G03 执行失败：{}".format(process.stderr.strip() or process.stdout.strip()))
    try:
        payload = json.loads(json_output.read_text(encoding="utf-8"))
        metrics = payload["metrics"]
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise PipelineError("G03 结构化输出无效：{}".format(json_output)) from exc
    return {str(key): int(value) for key, value in metrics.items()}


def _is_blocked(metrics: Dict[str, int]) -> bool:
    return metrics.get("redline", 0) > 0 or metrics.get("candidate_approved", 0) > 0


def run_pipeline(
    root: Path,
    runtime_dir: Optional[Path] = None,
    g03_runner: Optional[Callable[[Path, Path], Dict[str, int]]] = None,
    security_runner: Optional[Callable[[Path], Dict[str, object]]] = None,
) -> Dict[str, object]:
    root = root.resolve()
    runtime = (
        runtime_dir.resolve()
        if runtime_dir
        else root / "13_数据分析与工具脚本/知识库自动化_v1/runtime"
    )
    runtime.mkdir(parents=True, exist_ok=True)
    runner = g03_runner or run_g03
    staged_runner = security_runner or inspect_staged
    started_at = dt.datetime.now(dt.timezone.utc).isoformat()
    log_path = runtime / "runs.jsonl"

    with RunLock(runtime / "pipeline.lock"):
        try:
            try:
                runtime_rel = runtime.relative_to(root).as_posix()
            except ValueError:
                runtime_rel = "__external_runtime__"
            snapshot = scan_vault(root, InventoryConfig(runtime_dir=runtime_rel))
            previous = load_snapshot(runtime / "inventory_latest.json")
            delta = diff_snapshots(previous, snapshot)
            _atomic_json(runtime / "inventory_candidate.json", snapshot.to_dict())
            _atomic_json(runtime / "delta_latest.json", delta.to_dict())

            staged_gate = staged_runner(root)
            _atomic_json(runtime / "staged_gate_latest.json", staged_gate)
            metrics = runner(root, runtime / "g03_latest.md")
            task_registry = build_task_registry(root)
            _atomic_json(runtime / "task_registry_latest.json", task_registry)
            queue = build_decision_queue(snapshot)
            dashboard = render_dashboard(snapshot, delta, metrics, queue)
            (runtime / "dashboard_latest.md").write_text(dashboard, encoding="utf-8")
            (runtime / "system_status_latest.md").write_text(
                render_system_status(metrics, staged_gate, task_registry),
                encoding="utf-8",
            )

            if bool(staged_gate.get("blocked")) or _is_blocked(metrics):
                entry = {
                    "started_at": started_at,
                    "finished_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                    "status": "blocked",
                    "metrics": metrics,
                    "staged_gate": {
                        "blocked": bool(staged_gate.get("blocked")),
                        "staged_count": int(staged_gate.get("staged_count", 0)),
                        "finding_count": len(staged_gate.get("findings", [])),
                    },
                }
                _append_log(log_path, entry)
                raise PipelineError("质量门阻断，成功基线未更新")

            write_snapshot(runtime / "inventory_latest.json", snapshot)
            (runtime / "inventory_candidate.json").unlink(missing_ok=True)
            entry = {
                "started_at": started_at,
                "finished_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                "status": "success",
                "metrics": metrics,
                "staged_gate": {
                    "blocked": False,
                    "staged_count": int(staged_gate.get("staged_count", 0)),
                    "finding_count": 0,
                },
                "delta": {
                    "added": len(delta.added),
                    "modified": len(delta.modified),
                    "deleted": len(delta.deleted),
                },
            }
            _append_log(log_path, entry)
            return entry
        except PipelineError:
            raise
        except Exception as exc:
            _append_log(
                log_path,
                {
                    "started_at": started_at,
                    "finished_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                    "status": "failed",
                    "error": type(exc).__name__,
                },
            )
            raise PipelineError("自动化流水线失败：{}".format(exc)) from exc
