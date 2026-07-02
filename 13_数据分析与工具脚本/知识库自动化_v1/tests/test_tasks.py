import tempfile
import unittest
from pathlib import Path

from kb_automation.tasks import build_task_registry


class TaskRegistryTests(unittest.TestCase):
    def test_parses_inbox_table_and_queue_checkboxes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            codex = root / "98_AI协作中枢/02_Codex"
            control = root / "98_AI协作中枢/00_总控"
            codex.mkdir(parents=True)
            control.mkdir(parents=True)
            (codex / "Codex收件箱.md").write_text(
                "| 顺序 | 任务卡 | 内容 | 状态 |\n"
                "|---|---|---|---|\n"
                "| 1 | **CODEX-001** | Build scanner | ✅ 已完成 |\n"
                "| 2 | **CODEX-002** | Waiting data | blocked_缺字段 |\n",
                encoding="utf-8",
            )
            (control / "当前任务队列.md").write_text(
                "- **[x] GOV-001｜治理完成** — 说明\n"
                "- [ ] **GOV-002｜待处理治理**\n",
                encoding="utf-8",
            )

            registry = build_task_registry(root)
            statuses = {task["id"]: task["status"] for task in registry["tasks"]}

            self.assertEqual(statuses["CODEX-001"], "completed")
            self.assertEqual(statuses["CODEX-002"], "blocked")
            self.assertEqual(statuses["GOV-001"], "completed")
            self.assertEqual(statuses["GOV-002"], "pending")
            self.assertEqual(registry["metrics"]["task_count"], 4)

    def test_conflicting_sources_are_reported_not_silently_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            codex = root / "98_AI协作中枢/02_Codex"
            control = root / "98_AI协作中枢/00_总控"
            codex.mkdir(parents=True)
            control.mkdir(parents=True)
            (codex / "Codex收件箱.md").write_text(
                "| 1 | **TASK-001** | Task | ✅ 已完成 |\n",
                encoding="utf-8",
            )
            (control / "当前任务队列.md").write_text(
                "- [ ] **TASK-001｜Task**\n",
                encoding="utf-8",
            )

            registry = build_task_registry(root)

            self.assertEqual(registry["metrics"]["conflict_count"], 1)
            self.assertEqual(registry["conflicts"][0]["id"], "TASK-001")
            self.assertEqual(registry["tasks"][0]["status"], "conflict")


if __name__ == "__main__":
    unittest.main()
