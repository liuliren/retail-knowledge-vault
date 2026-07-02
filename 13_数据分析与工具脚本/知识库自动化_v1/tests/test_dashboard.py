import unittest

from kb_automation.dashboard import build_decision_queue, render_dashboard, render_system_status
from kb_automation.models import AssetRecord, InventorySnapshot, SnapshotDelta


def record(path: str, modified_ns: int = 0, flags=None) -> AssetRecord:
    return AssetRecord(
        path=path,
        asset_type="markdown",
        size=10,
        modified_ns=modified_ns,
        fingerprint="x",
        risk_flags=flags or [],
    )


class DashboardTests(unittest.TestCase):
    def test_ai_output_older_than_seven_days_enters_review_queue(self):
        snapshot = InventorySnapshot(
            generated_at="2026-06-24T00:00:00+00:00",
            assets=[
                record(
                    "98_AI协作中枢/02_Codex/Codex输出区/old.md",
                    modified_ns=1,
                    flags=["ai_output_review_required"],
                )
            ],
        )

        queue = build_decision_queue(snapshot, now_ns=8 * 24 * 3600 * 1_000_000_000)

        self.assertEqual(queue[0]["decision"], "review")
        self.assertEqual(queue[0]["path"], "98_AI协作中枢/02_Codex/Codex输出区/old.md")

    def test_dashboard_contains_metrics_and_paths_only(self):
        snapshot = InventorySnapshot(
            generated_at="now",
            assets=[record("notes/a.md"), record("data.xlsx", flags=["sensitive_extension"])],
        )
        delta = SnapshotDelta(added=["notes/a.md"], modified=[], deleted=[], unchanged=[])

        output = render_dashboard(snapshot, delta, {"redline": 0, "broken": 2}, [])

        self.assertIn("资产总数 | 2", output)
        self.assertIn("新增 | 1", output)
        self.assertIn("G03 敏感红线 | 0", output)
        self.assertNotIn("Body", output)

    def test_system_status_combines_quality_security_and_tasks(self):
        output = render_system_status(
            {"redline": 0, "broken": 2, "missing_summary": 3, "invalid_status": 1},
            {"blocked": False, "staged_count": 0, "findings": []},
            {
                "metrics": {
                    "task_count": 4,
                    "pending": 1,
                    "in_progress": 1,
                    "review": 0,
                    "blocked": 1,
                    "completed": 1,
                    "conflict_count": 0,
                },
                "conflicts": [],
            },
        )

        self.assertIn("Health: AMBER", output)
        self.assertIn("核心知识缺 summary | 3", output)
        self.assertIn("任务 blocked | 1", output)


if __name__ == "__main__":
    unittest.main()
