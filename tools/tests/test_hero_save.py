"""Headless check that the hero's weapon/bag save is validated and round-trips.

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


def _godot() -> bool:
    try:
        path = json.loads((ROOT / ".agents/planner/config.json").read_text(encoding="utf-8")).get("godot_executable")
    except (OSError, ValueError):
        return False
    return isinstance(path, str) and Path(path).is_file()


class HeroSaveTests(unittest.TestCase):
    @unittest.skipUnless(_godot(), "configured godot_executable is not installed here")
    def test_headless_save(self):
        code, output = run_godot("res://tools/verify_hero_save.gd")
        self.assertEqual(code, 0, output)
        self.assertIn("HERO_SAVE_OK", output)
        self.assertNotIn("SCRIPT ERROR:", output)


if __name__ == "__main__":
    unittest.main()
