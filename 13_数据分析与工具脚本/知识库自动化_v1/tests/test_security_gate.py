import subprocess
import tempfile
import unittest
from pathlib import Path

from kb_automation.security_gate import inspect_staged


def init_repo(root: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)


class SecurityGateTests(unittest.TestCase):
    def test_empty_staging_area_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)

            result = inspect_staged(root)

            self.assertFalse(result["blocked"])
            self.assertEqual(result["staged_count"], 0)

    def test_sensitive_extension_is_blocked_without_reading_binary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            path = root / "result.xlsx"
            path.write_bytes(b"binary")
            subprocess.run(["git", "add", "result.xlsx"], cwd=root, check=True)

            result = inspect_staged(root)

            self.assertTrue(result["blocked"])
            self.assertEqual(result["findings"][0]["category"], "sensitive_extension")
            self.assertNotIn("binary", str(result))

    def test_customer_operating_judgment_is_blocked_without_echoing_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            path = root / "review.md"
            path.write_text("花厅坊 金矿候选 经营判断\n", encoding="utf-8")
            subprocess.run(["git", "add", "review.md"], cwd=root, check=True)

            result = inspect_staged(root)

            self.assertTrue(result["blocked"])
            self.assertEqual(result["findings"][0]["category"], "customer_derived_content")
            self.assertNotIn("经营判断", str(result))

    def test_generic_code_is_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_repo(root)
            path = root / "tool.py"
            path.write_text("def add(a, b): return a + b\n", encoding="utf-8")
            subprocess.run(["git", "add", "tool.py"], cwd=root, check=True)

            result = inspect_staged(root)

            self.assertFalse(result["blocked"])
            self.assertEqual(result["staged_count"], 1)


if __name__ == "__main__":
    unittest.main()
