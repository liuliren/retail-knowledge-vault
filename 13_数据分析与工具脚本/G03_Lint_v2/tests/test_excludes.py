import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "lint_v2.py"
SPEC = importlib.util.spec_from_file_location("g03_lint_v2", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class ExcludeTests(unittest.TestCase):
    def test_automation_runtime_is_excluded(self):
        root = Path("/vault")
        generated = root / "13_数据分析与工具脚本/知识库自动化_v1/runtime/dashboard_latest.md"

        self.assertTrue(MODULE.should_exclude(generated, root))

    def test_json_output_contains_stable_metrics_and_paths_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "01_method").mkdir()
            (root / "01_method" / "note.md").write_text(
                "---\ntitle: Note\nversion: v0.1\nstatus: draft\nowner: Codex\nsource_type: methodology\n---\n# Note\n",
                encoding="utf-8",
            )
            (root / "01_method" / "running.md").write_text(
                "---\ntitle: Running\nversion: v0.1\nstatus: running\nowner: Codex\n"
                "source_type: methodology\nsummary: Has summary\n---\n# Running\n",
                encoding="utf-8",
            )
            dashboard = root / "dashboard.md"
            json_output = root / "metrics.json"

            process = subprocess.run(
                [
                    sys.executable,
                    str(MODULE_PATH),
                    "--vault",
                    str(root),
                    "--output",
                    str(dashboard),
                    "--json-output",
                    str(json_output),
                ],
                text=True,
                capture_output=True,
            )

            self.assertEqual(process.returncode, 0, process.stderr)
            payload = json.loads(json_output.read_text(encoding="utf-8"))
            self.assertEqual(payload["schema_version"], "1")
            self.assertEqual(payload["metrics"]["redline"], 0)
            self.assertEqual(payload["metrics"]["missing_summary"], 1)
            self.assertEqual(payload["metrics"]["invalid_status"], 1)
            self.assertIn("broken_targets", payload["findings"])
            self.assertNotIn("body", json.dumps(payload, ensure_ascii=False).lower())


if __name__ == "__main__":
    unittest.main()
