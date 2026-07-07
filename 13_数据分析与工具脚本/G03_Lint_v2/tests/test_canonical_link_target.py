import importlib.util
import sys
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "lint_v2.py"
SPEC = importlib.util.spec_from_file_location("g03_lint_v2", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class CanonicalLinkTargetTests(unittest.TestCase):
    def test_versioned_target_in_subpath_is_preserved(self):
        self.assertEqual(
            MODULE.canonical_link_target("05_xxx/文件_v0.1_候选.md"),
            "文件_v0.1_候选",
        )

    def test_versioned_target_v1_0_is_preserved(self):
        self.assertEqual(
            MODULE.canonical_link_target("abc/文件_v1.0.md"),
            "文件_v1.0",
        )

    def test_anchor_is_stripped(self):
        self.assertEqual(
            MODULE.canonical_link_target("abc/文件.md#标题"),
            "文件",
        )

    def test_alias_is_stripped_and_version_preserved(self):
        self.assertEqual(
            MODULE.canonical_link_target("abc/文件_v0.2.md|显示名"),
            "文件_v0.2",
        )

    def test_bare_filename_without_path_still_works(self):
        self.assertEqual(
            MODULE.canonical_link_target("文件_v0.1.md"),
            "文件_v0.1",
        )

    def test_windows_style_backslash_path(self):
        self.assertEqual(
            MODULE.canonical_link_target("abc\\文件_v1.0.md"),
            "文件_v1.0",
        )


if __name__ == "__main__":
    unittest.main()
