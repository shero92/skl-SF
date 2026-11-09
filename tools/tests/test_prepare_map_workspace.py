"""Tests for the Map Factory workspace preparation tool.

Execution provenance: Agent: claude (Claude Code); model: Sonnet 5.5.
"""
from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[1]
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import prepare_map_workspace as prep


class PrepareWorkspaceTests(unittest.TestCase):
    def _tree(self, base: Path, files: list[str]) -> None:
        for name in files:
            path = base / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"png")

    def test_missing_and_copy_never_overwrites(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, target = Path(tmp, "src"), Path(tmp, "dst")
            self._tree(source, ["assets_generated/a/one.png", "assets_hd/runtime/two.png", "other/ignored.png"])
            self._tree(target, ["assets_generated/a/one.png"])
            (target / "assets_generated/a/one.png").write_bytes(b"keep")
            missing = prep.missing_files(source, target)
            self.assertEqual(missing, ["assets_hd/runtime/two.png"])
            self.assertEqual(prep.copy_missing(source, target, missing), 1)
            self.assertEqual((target / "assets_generated/a/one.png").read_bytes(), b"keep")
            self.assertEqual(prep.missing_files(source, target), [])

    def test_missing_source_directory_is_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(prep.missing_files(Path(tmp, "none"), Path(tmp, "dst")), [])

    def test_main_reports_without_import(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp, "src")
            self._tree(source, ["map_factory/parts/x_only_in_source_for_test.png"])
            self.assertEqual(prep.main(["--source", str(source), "--no-import"]), 1)


if __name__ == "__main__":
    unittest.main()
