"""Verify the Shining Force style weapon system headlessly.

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

DATA = ROOT / "game_factory/weapons/weapon_stats.json"


def _configured_godot_exists() -> bool:
    try:
        path = json.loads((ROOT / ".agents/planner/config.json").read_text(encoding="utf-8")).get("godot_executable")
    except (OSError, ValueError):
        return False
    return isinstance(path, str) and Path(path).is_file()


class WeaponSystemTests(unittest.TestCase):
    def test_data_is_consistent(self):
        data = json.loads(DATA.read_text(encoding="utf-8"))
        profiles = json.loads((ROOT / "game_factory/weapons/profiles.json").read_text(encoding="utf-8"))
        for class_id, cls in data["classes"].items():
            for type_id in cls["weapon_types"]:
                self.assertIn(type_id, data["weapon_types"], class_id)
            self.assertIn(cls["unarmed"], data["weapons"], class_id)
        for weapon_id, item in data["weapons"].items():
            self.assertIn(item["type"], data["weapon_types"], weapon_id)
        for character_id in profiles["character_profiles"]:
            self.assertIn(character_id, data["characters"])
            self.assertIn(data["characters"][character_id]["class"], data["classes"])
        used = {t for c in data["classes"].values() for t in c["weapon_types"]}
        self.assertEqual(used, set(data["weapon_types"]), "every weapon type is usable by some class")

    @unittest.skipUnless(_configured_godot_exists(), "configured godot_executable is not installed here")
    def test_headless_rules(self):
        code, output = run_godot("res://tools/verify_weapon_system.gd")
        self.assertEqual(code, 0, output)
        self.assertIn("WEAPON_SYSTEM_OK", output)
        self.assertNotIn("SCRIPT ERROR:", output)
        self.assertNotIn("FAIL:", output)


if __name__ == "__main__":
    unittest.main()
