"""Verify the battle preview scene headlessly against the real controller.

Execution provenance: Agent: claude (Claude Code); model: Sonnet 5.5.
Missing Godot is a failure, never a skip.
"""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

TOOLS = Path(__file__).resolve().parents[1]
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from battle_godot_harness import run_godot


class BattlePreviewTests(unittest.TestCase):
    def test_headless_preview(self):
        code, output = run_godot("res://tools/verify_battle_preview.gd")
        self.assertEqual(code, 0, output)
        self.assertIn("BATTLE_PREVIEW_OK", output)
        self.assertNotIn("SCRIPT ERROR:", output)
        self.assertNotIn("FAIL:", output)


if __name__ == "__main__":
    unittest.main()
