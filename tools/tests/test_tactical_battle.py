"""Headless check of the playable tactical skirmish session and scene.

Execution provenance: Agent: claude (Claude Code); model: Fable 5.2.
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


def _godot() -> bool:
    try:
        path = json.loads((ROOT / ".agents/planner/config.json").read_text(encoding="utf-8")).get("godot_executable")
    except (OSError, ValueError):
        return False
    return isinstance(path, str) and Path(path).is_file()


class TacticalBattleTests(unittest.TestCase):
    @unittest.skipUnless(_godot(), "configured godot_executable is not installed here")
    def test_headless_battle(self):
        code, output = run_godot("res://tools/verify_tactical_battle.gd")
        self.assertEqual(code, 0, output)
        self.assertIn("TACTICAL_BATTLE_OK", output)
        self.assertNotIn("SCRIPT ERROR:", output)


if __name__ == "__main__":
    unittest.main()
