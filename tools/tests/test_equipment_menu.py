"""Verify the EquipmentMenu UI over WeaponSystem headlessly.

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


class EquipmentMenuTests(unittest.TestCase):
    @unittest.skipUnless(_configured_godot_exists(), "configured godot_executable is not installed here")
    def test_main_scene_opens_the_menu_with_i(self):
        code, output = run_godot("res://tools/verify_main_equipment.gd")
        self.assertEqual(code, 0, output)
        self.assertIn("MAIN_EQUIPMENT_OK", output)
        self.assertNotIn("SCRIPT ERROR:", output)
        self.assertNotIn("FAIL:", output)


    @unittest.skipUnless(_configured_godot_exists(), "configured godot_executable is not installed here")
    def test_headless_menu(self):
        code, output = run_godot("res://tools/verify_equipment_menu.gd")
        self.assertEqual(code, 0, output)
        self.assertIn("EQUIPMENT_MENU_OK", output)
        self.assertNotIn("SCRIPT ERROR:", output)
        self.assertNotIn("FAIL:", output)


if __name__ == "__main__":
    unittest.main()
