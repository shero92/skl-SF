"""Verify that evidence captures refuse draft or fallback rendering (TASK-0059).

Execution provenance: Agent: claude (Claude Code); model: Sonnet 5.5.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

TOOLS = Path(__file__).resolve().parents[1]
ROOT = TOOLS.parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from battle_godot_harness import run_godot


def _configured_godot_exists() -> bool:
    config = ROOT / ".agents/planner/config.json"
    try:
        path = json.loads(config.read_text(encoding="utf-8")).get("godot_executable")
    except (OSError, ValueError):
        return False
    return isinstance(path, str) and Path(path).is_file()


class CaptureChecksTests(unittest.TestCase):
    def test_placeholder_contract_matches_the_asset_factory(self):
        factory = (ROOT / "map_factory/scripts/asset_factory.gd").read_text(encoding="utf-8")
        checks = (ROOT / "tools/capture_checks.gd").read_text(encoding="utf-8")
        self.assertIn('asset_id + " (draft)"', factory)
        self.assertIn('"(draft)"', checks)
        self.assertIn("Color(0.80, 0.12, 0.65, 0.7)", factory)
        self.assertIn("Color(0.80, 0.12, 0.65, 0.7)", checks)

    def test_capture_script_uses_the_checks(self):
        capture = (ROOT / "tools/capture_map_previews.gd").read_text(encoding="utf-8")
        self.assertIn("capture_checks.gd", capture)
        self.assertIn("find_drafts", capture)

    @unittest.skipUnless(_configured_godot_exists(), "configured godot_executable is not installed here")
    def test_headless_draft_detection(self):
        code, output = run_godot("res://tools/verify_capture_checks.gd")
        self.assertEqual(code, 0, output)
        self.assertIn("CAPTURE_CHECKS_OK", output)
        self.assertNotIn("SCRIPT ERROR:", output)
        self.assertNotIn("FAIL:", output)


if __name__ == "__main__":
    unittest.main()
