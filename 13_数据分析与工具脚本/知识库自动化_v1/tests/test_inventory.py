import tempfile
import unittest
from pathlib import Path

from kb_automation.inventory import InventoryConfig, scan_vault


class InventoryTests(unittest.TestCase):
    def test_scan_excludes_private_git_and_runtime(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "notes").mkdir()
            (root / "_client_private").mkdir()
            (root / ".git").mkdir()
            (root / "runtime").mkdir()
            (root / "notes" / "note.md").write_text(
                "---\ntitle: Test\nstatus: draft\nsource_type: methodology\n---\nBody\n",
                encoding="utf-8",
            )
            (root / "_client_private" / "secret.md").write_text("secret", encoding="utf-8")
            (root / ".git" / "config").write_text("git", encoding="utf-8")
            (root / "runtime" / "inventory.json").write_text("{}", encoding="utf-8")

            result = scan_vault(root, InventoryConfig(runtime_dir="runtime"))

            self.assertEqual([asset.path for asset in result.assets], ["notes/note.md"])
            self.assertEqual(result.assets[0].title, "Test")
            self.assertEqual(result.assets[0].status, "draft")
            self.assertIsNotNone(result.assets[0].content_sha256)

    def test_non_markdown_records_metadata_without_reading_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            binary = root / "data.xlsx"
            binary.write_bytes(b"not-a-real-workbook")

            result = scan_vault(root)

            asset = result.assets[0]
            self.assertEqual(asset.asset_type, "office_data")
            self.assertEqual(asset.size, len(b"not-a-real-workbook"))
            self.assertIsNone(asset.content_sha256)
            self.assertIn("sensitive_extension", asset.risk_flags)

    def test_parent_entry_uses_nearest_readme(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / "section"
            folder.mkdir()
            (folder / "README.md").write_text("# Entry\n", encoding="utf-8")
            (folder / "child.md").write_text("# Child\n", encoding="utf-8")

            result = scan_vault(root)
            child = next(asset for asset in result.assets if asset.path.endswith("child.md"))

            self.assertEqual(child.parent_entry, "section/README.md")


if __name__ == "__main__":
    unittest.main()

