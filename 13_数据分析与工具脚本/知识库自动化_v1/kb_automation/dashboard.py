from __future__ import annotations

import time
from collections import Counter
from typing import Dict, List, Optional

from .models import InventorySnapshot, SnapshotDelta


SEVEN_DAYS_NS = 7 * 24 * 60 * 60 * 1_000_000_000


def build_decision_queue(
    snapshot: InventorySnapshot, now_ns: Optional[int] = None
) -> List[Dict[str, str]]:
    now_ns = now_ns if now_ns is not None else time.time_ns()
    queue: List[Dict[str, str]] = []
    for asset in snapshot.assets:
        if "ai_output_review_required" not in asset.risk_flags:
            continue
        if now_ns - asset.modified_ns <= SEVEN_DAYS_NS:
            continue
        queue.append(
            {
                "path": asset.path,
                "decision": "review",
                "reason": "AI 输出或执行日志超过 7 天未裁决",
            }
        )
    return sorted(queue, key=lambda item: item["path"])


def _path_list(title: str, paths: List[str], limit: int = 20) -> List[str]:
    lines = ["", "## {}".format(title), ""]
    if not paths:
        return lines + ["无"]
    lines.extend("- `{}`".format(path) for path in paths[:limit])
    if len(paths) > limit:
        lines.append("- 其余 {} 项见 `delta_latest.json`".format(len(paths) - limit))
    return lines


def render_dashboard(
    snapshot: InventorySnapshot,
    delta: SnapshotDelta,
    g03_metrics: Dict[str, int],
    decision_queue: List[Dict[str, str]],
) -> str:
    zones = Counter(asset.zone for asset in snapshot.assets)
    sensitive = sum("sensitive_extension" in asset.risk_flags for asset in snapshot.assets)
    lines = [
        "# 晟果新零售知识库自动化仪表盘",
        "",
        "- 生成时间：{}".format(snapshot.generated_at),
        "- 说明：机器生成，只展示资产元数据、聚合指标和路径，不展示客户数据正文。",
        "",
        "## 运行摘要",
        "",
        "| 指标 | 数量 |",
        "|:--|--:|",
        "| 资产总数 | {} |".format(len(snapshot.assets)),
        "| 新增 | {} |".format(len(delta.added)),
        "| 修改 | {} |".format(len(delta.modified)),
        "| 删除 | {} |".format(len(delta.deleted)),
        "| 敏感扩展资产 | {} |".format(sensitive),
        "| 待人工裁决 | {} |".format(len(decision_queue)),
        "| G03 断链目标 | {} |".format(g03_metrics.get("broken", 0)),
        "| G03 敏感红线 | {} |".format(g03_metrics.get("redline", 0)),
        "| G03 candidate 越权 | {} |".format(g03_metrics.get("candidate_approved", 0)),
        "",
        "## 资产分区",
        "",
        "| 分区 | 数量 |",
        "|:--|--:|",
    ]
    lines.extend("| {} | {} |".format(zone, count) for zone, count in sorted(zones.items()))
    lines.extend(_path_list("新增资产", delta.added))
    lines.extend(_path_list("修改资产", delta.modified))
    lines.extend(_path_list("删除资产", delta.deleted))
    lines.extend(["", "## AI 输出裁决队列", ""])
    if not decision_queue:
        lines.append("无")
    else:
        lines.extend(
            "- `{}`：{}，建议 `{}`".format(item["path"], item["reason"], item["decision"])
            for item in decision_queue[:20]
        )
    return "\n".join(lines) + "\n"


def render_system_status(
    g03_metrics: Dict[str, int],
    staged_gate: Dict[str, object],
    task_registry: Dict[str, object],
) -> str:
    task_metrics = task_registry.get("metrics", {})
    blocked = (
        g03_metrics.get("redline", 0) > 0
        or g03_metrics.get("candidate_approved", 0) > 0
        or bool(staged_gate.get("blocked"))
        or int(task_metrics.get("conflict_count", 0)) > 0
    )
    has_debt = any(
        (
            g03_metrics.get("broken", 0),
            g03_metrics.get("missing_summary", 0),
            g03_metrics.get("invalid_status", 0),
            int(task_metrics.get("blocked", 0)),
            int(task_metrics.get("pending", 0)),
        )
    )
    health = "RED" if blocked else ("AMBER" if has_debt else "GREEN")
    lines = [
        "# 晟果新零售知识库机器系统状态",
        "",
        "Health: {}".format(health),
        "",
        "> 机器生成，不覆盖人工 `系统状态.md`；只报告指标和路径，不展示客户正文。",
        "",
        "## 质量与安全",
        "",
        "| 指标 | 数量 |",
        "|:--|--:|",
        "| G03 敏感红线 | {} |".format(g03_metrics.get("redline", 0)),
        "| candidate 越权 | {} |".format(g03_metrics.get("candidate_approved", 0)),
        "| staged 文件 | {} |".format(staged_gate.get("staged_count", 0)),
        "| staged 风险 | {} |".format(len(staged_gate.get("findings", []))),
        "| 断链目标 | {} |".format(g03_metrics.get("broken", 0)),
        "| 正式孤儿 | {} |".format(g03_metrics.get("orphan", 0)),
        "| 核心知识缺 summary | {} |".format(g03_metrics.get("missing_summary", 0)),
        "| 非规范 status | {} |".format(g03_metrics.get("invalid_status", 0)),
        "",
        "## 任务闭环",
        "",
        "| 指标 | 数量 |",
        "|:--|--:|",
        "| 任务总数 | {} |".format(task_metrics.get("task_count", 0)),
        "| 任务 pending | {} |".format(task_metrics.get("pending", 0)),
        "| 任务 in_progress | {} |".format(task_metrics.get("in_progress", 0)),
        "| 任务 review | {} |".format(task_metrics.get("review", 0)),
        "| 任务 blocked | {} |".format(task_metrics.get("blocked", 0)),
        "| 任务 completed | {} |".format(task_metrics.get("completed", 0)),
        "| 多源状态冲突 | {} |".format(task_metrics.get("conflict_count", 0)),
    ]
    conflicts = task_registry.get("conflicts", [])
    lines.extend(["", "## 状态冲突", ""])
    if conflicts:
        lines.extend("- `{}`：{}".format(item["id"], ", ".join(item["statuses"])) for item in conflicts)
    else:
        lines.append("无")
    return "\n".join(lines) + "\n"
