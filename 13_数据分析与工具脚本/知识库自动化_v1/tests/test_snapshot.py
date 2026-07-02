import unittest

from kb_automation.models import AssetRecord, InventorySnapshot
from kb_automation.snapshot import diff_snapshots


def asset(path: str, fingerprint: str) -> AssetRecord:
    return AssetRecord(
        path=path,
        asset_type="markdown",
        size=1,
        modified_ns=1,
        fingerprint=fingerprint,
    )


class SnapshotTests(unittest.TestCase):
    def test_first_run_marks_every_asset_added(self):
        current = InventorySnapshot(generated_at="now", assets=[asset("a.md", "1")])

        delta = diff_snapshots(None, current)

        self.assertEqual(delta.added, ["a.md"])
        self.assertEqual(delta.modified, [])
        self.assertEqual(delta.deleted, [])

    def test_diff_classifies_added_modified_deleted_and_unchanged(self):
        previous = InventorySnapshot(
            generated_at="before",
            assets=[asset("same.md", "1"), asset("changed.md", "1"), asset("gone.md", "1")],
        )
        current = InventorySnapshot(
            generated_at="after",
            assets=[asset("same.md", "1"), asset("changed.md", "2"), asset("new.md", "1")],
        )

        delta = diff_snapshots(previous, current)

        self.assertEqual(delta.added, ["new.md"])
        self.assertEqual(delta.modified, ["changed.md"])
        self.assertEqual(delta.deleted, ["gone.md"])
        self.assertEqual(delta.unchanged, ["same.md"])


if __name__ == "__main__":
    unittest.main()
