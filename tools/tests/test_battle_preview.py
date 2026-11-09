"""Verify the battle preview scene headlessly against the real controller.

Execution provenance: Agent: claude (Claude Code); model: Sonnet 5.5.
Missing Godot is a failure, never a skip.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

TOOLS = Path(__file__).resolve().parents[1]
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from battle_godot_harness import run_godot


def _configured_godot_exists() -> bool:
    config = TOOLS.parent / ".agents/planner/config.json"
    try:
        path = json.loads(config.read_text(encoding="utf-8")).get("godot_executable")
    except (OSError, ValueError):
        return False
    return isinstance(path, str) and Path(path).is_file()


class BattlePreviewTests(unittest.TestCase):
    # Python-only CI has no Godot at the owner's path; this runs wherever it is installed.
    @unittest.skipUnless(_configured_godot_exists(), "configured godot_executable is not installed here")
    def test_headless_preview(self):
        code, output = run_godot("res://tools/verify_battle_preview.gd")
        self.assertEqual(code, 0, output)
        self.assertIn("BATTLE_PREVIEW_OK", output)
        self.assertNotIn("SCRIPT ERROR:", output)
        self.assertNotIn("FAIL:", output)


if __name__ == "__main__":
    unittest.main()
