"""Verify the shared NavigationGrid headlessly (hero room navigation, slide, closed-by-default, wiring).

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


class NavigationGridTests(unittest.TestCase):
    def test_every_map_snapshot_navigation_is_schema_one(self):
        latest = json.loads((ROOT / "map_factory/maps/hero_room_01/latest.json").read_text(encoding="utf-8"))
        nav = latest["navigation"]
        self.assertEqual(nav["schema_version"], 1)
        self.assertFalse(any(nav["default"].values()), "unknown cells must stay closed by default")

    def test_movement_code_shares_one_validator(self):
        for name in ("scenes/player.gd", "scenes/game_factory_actor.gd"):
            self.assertIn("allowed_motion", (ROOT / name).read_text(encoding="utf-8"), name)
        self.assertNotIn("walkable_cells", (ROOT / "scenes/game_factory_actor.gd").read_text(encoding="utf-8"))

    @unittest.skipUnless(_configured_godot_exists(), "configured godot_executable is not installed here")
    def test_headless_navigation(self):
        code, output = run_godot("res://tools/verify_navigation_grid.gd")
        self.assertEqual(code, 0, output)
        self.assertIn("NAVIGATION_GRID_OK", output)
        self.assertNotIn("SCRIPT ERROR:", output)
        self.assertNotIn("FAIL:", output)


if __name__ == "__main__":
    unittest.main()
