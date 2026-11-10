"""Verify BattleDirector (TurnManager results played through the animation controller) headlessly.

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
    try:
        path = json.loads((ROOT / ".agents/planner/config.json").read_text(encoding="utf-8")).get("godot_executable")
    except (OSError, ValueError):
        return False
    return isinstance(path, str) and Path(path).is_file()


class BattleDirectorTests(unittest.TestCase):
    def test_every_art_profile_has_an_attack(self):
        director = (ROOT / "scenes/battle/battle_director.gd").read_text(encoding="utf-8")
        profiles = json.loads((ROOT / "game_factory/weapons/profiles.json").read_text(encoding="utf-8"))["profiles"]
        for profile in profiles:
            self.assertIn(f'"{profile}": &', director, f"no attack mapped for profile {profile}")

    @unittest.skipUnless(_configured_godot_exists(), "configured godot_executable is not installed here")
    def test_headless_director(self):
        code, output = run_godot("res://tools/verify_battle_director.gd")
        self.assertEqual(code, 0, output)
        self.assertIn("BATTLE_DIRECTOR_OK", output)
        self.assertNotIn("SCRIPT ERROR:", output)
        self.assertNotIn("FAIL:", output)


if __name__ == "__main__":
    unittest.main()
