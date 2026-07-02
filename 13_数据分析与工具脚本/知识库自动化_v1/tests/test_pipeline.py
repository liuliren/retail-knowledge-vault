import json
import tempfile
import unittest
from pathlib import Path

from kb_automation.pipeline import PipelineError, run_g03, run_pipeline


class PipelineTests(unittest.TestCase):
    def test_run_g03_consumes_structured_json_not_stdout(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            script_dir = root / "13_数据分析与工具脚本/G03_Lint_v2"
            script_dir.mkdir(parents=True)
            script = script_dir / "lint_v2.py"
            script.write_text(
                "import argparse,json,pathlib\n"
                "p=argparse.ArgumentParser();p.add_argument('--vault');p.add_argument('--output');"
                "p.add_argument('--json-output');a=p.parse_args()\n"
                "pathlib.Path(a.output).write_text('dashboard')\n"
                "pathlib.Path(a.json_output).write_text(json.dumps({'metrics': {'redline': 0, 'broken': 7}}))\n"
                "print('metrics: redline=99 broken=99')\n",
                encoding="utf-8",
            )

            metrics = run_g03(root, root / "g03.md")

            self.assertEqual(metrics, {"redline": 0, "broken": 7})

    def test_success_writes_runtime_outputs_and_advances_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "note.md").write_text("# Note\n", encoding="utf-8")

            result = run_pipeline(
                root,
                runtime_dir=root / "runtime",
                g03_runner=lambda _root, _output: {"broken": 0, "redline": 0},
            )

            self.assertEqual(result["status"], "success")
            self.assertTrue((root / "runtime" / "inventory_latest.json").exists())
            self.assertTrue((root / "runtime" / "delta_latest.json").exists())
            self.assertTrue((root / "runtime" / "dashboard_latest.md").exists())
            self.assertTrue((root / "runtime" / "task_registry_latest.json").exists())
            self.assertTrue((root / "runtime" / "system_status_latest.md").exists())
            log = (root / "runtime" / "runs.jsonl").read_text(encoding="utf-8").splitlines()
            self.assertEqual(json.loads(log[-1])["status"], "success")

    def test_failed_quality_gate_does_not_advance_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "note.md").write_text("# Note\n", encoding="utf-8")

            with self.assertRaises(PipelineError):
                run_pipeline(
                    root,
                    runtime_dir=root / "runtime",
                    g03_runner=lambda _root, _output: {"broken": 0, "redline": 1},
                )

            self.assertFalse((root / "runtime" / "inventory_latest.json").exists())
            log = (root / "runtime" / "runs.jsonl").read_text(encoding="utf-8").splitlines()
            self.assertEqual(json.loads(log[-1])["status"], "blocked")

    def test_staged_security_gate_blocks_before_baseline_advances(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "note.md").write_text("# Note\n", encoding="utf-8")

            with self.assertRaises(PipelineError):
                run_pipeline(
                    root,
                    runtime_dir=root / "runtime",
                    g03_runner=lambda _root, _output: {"broken": 0, "redline": 0},
                    security_runner=lambda _root: {
                        "blocked": True,
                        "staged_count": 1,
                        "findings": [{"path": "result.xlsx", "category": "sensitive_extension"}],
                    },
                )

            self.assertFalse((root / "runtime" / "inventory_latest.json").exists())
            security = json.loads(
                (root / "runtime" / "staged_gate_latest.json").read_text(encoding="utf-8")
            )
            self.assertTrue(security["blocked"])

    def test_existing_lock_prevents_parallel_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            runtime = root / "runtime"
            runtime.mkdir()
            (runtime / "pipeline.lock").write_text("locked", encoding="utf-8")

            with self.assertRaises(PipelineError):
                run_pipeline(
                    root,
                    runtime_dir=runtime,
                    g03_runner=lambda _root, _output: {"redline": 0},
                )


if __name__ == "__main__":
    unittest.main()
