import json
import tempfile
import unittest
from pathlib import Path

from kb_automation.cli import read_status


class CliTests(unittest.TestCase):
    def test_read_status_returns_latest_jsonl_entry(self):
        with tempfile.TemporaryDirectory() as tmp:
            runtime = Path(tmp)
            (runtime / "runs.jsonl").write_text(
                json.dumps({"status": "success", "finished_at": "now"}) + "\n",
                encoding="utf-8",
            )

            status = read_status(runtime)

            self.assertEqual(status["status"], "success")

    def test_read_status_reports_never_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            status = read_status(Path(tmp))

            self.assertEqual(status["status"], "never_run")


if __name__ == "__main__":
    unittest.main()
