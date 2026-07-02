from __future__ import annotations

import plistlib
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional


LABEL = "com.shengguo.retail-knowledge-vault.automation"
MODULE_PATH = Path("13_数据分析与工具脚本/知识库自动化_v1")


def render_launchd_plist(
    vault: Path,
    python_executable: Optional[str] = None,
    hour: int = 9,
    minute: int = 0,
) -> bytes:
    vault = vault.resolve()
    module = vault / MODULE_PATH
    runtime = module / "runtime"
    payload = {
        "Label": LABEL,
        "ProgramArguments": [
            python_executable or sys.executable,
            str(module / "run.py"),
            "run",
            "--vault",
            str(vault),
        ],
        "WorkingDirectory": str(vault),
        "StartCalendarInterval": {"Hour": hour, "Minute": minute},
        "RunAtLoad": False,
        "StandardOutPath": str(runtime / "launchd.stdout.log"),
        "StandardErrorPath": str(runtime / "launchd.stderr.log"),
        "ProcessType": "Background",
    }
    return plistlib.dumps(payload, sort_keys=True)


def write_launchd_preview(
    vault: Path,
    output: Optional[Path] = None,
    hour: int = 9,
    minute: int = 0,
) -> Path:
    vault = vault.resolve()
    output = output or vault / MODULE_PATH / "runtime" / "{}.plist".format(LABEL)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(render_launchd_plist(vault, hour=hour, minute=minute))
    return output


def install_launchd(
    vault: Path,
    launch_agents_dir: Optional[Path] = None,
    uid: Optional[int] = None,
    hour: int = 9,
    minute: int = 0,
    runner=subprocess.run,
) -> Path:
    vault = vault.resolve()
    uid = uid if uid is not None else os.getuid()
    launch_agents_dir = launch_agents_dir or Path.home() / "Library/LaunchAgents"
    launch_agents_dir.mkdir(parents=True, exist_ok=True)
    target = launch_agents_dir / "{}.plist".format(LABEL)
    temporary = target.with_suffix(".plist.tmp")
    temporary.write_bytes(render_launchd_plist(vault, hour=hour, minute=minute))
    temporary.replace(target)

    lint = runner(["plutil", "-lint", str(target)], text=True, capture_output=True)
    if lint.returncode != 0:
        raise RuntimeError("launchd plist 校验失败：{}".format(lint.stderr or lint.stdout))

    domain = "gui/{}".format(uid)
    runner(
        ["launchctl", "bootout", "{}/{}".format(domain, LABEL)],
        text=True,
        capture_output=True,
    )
    bootstrap = runner(
        ["launchctl", "bootstrap", domain, str(target)],
        text=True,
        capture_output=True,
    )
    if bootstrap.returncode != 0:
        raise RuntimeError("launchd bootstrap 失败：{}".format(bootstrap.stderr or bootstrap.stdout))
    kickstart = runner(
        ["launchctl", "kickstart", "-k", "{}/{}".format(domain, LABEL)],
        text=True,
        capture_output=True,
    )
    if kickstart.returncode != 0:
        raise RuntimeError("launchd kickstart 失败：{}".format(kickstart.stderr or kickstart.stdout))
    return target
