"""Verify world depth sorting of characters against walls and furniture headlessly.

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


class DepthSortingTests(unittest.TestCase):
    def test_latest_hero_room_uses_unified_sort(self):
        latest = json.loads((ROOT / "map_factory/maps/hero_room_01/latest.json").read_text(encoding="utf-8"))
        self.assertEqual(latest.get("occlusion_mode"), "world_y_sort")

    def test_main_scene_uses_the_shared_parent(self):
        text = (ROOT / "scenes/main.gd").read_text(encoding="utf-8")
        self.assertIn("RoomFactory.entities_parent(room)", text)
        self.assertNotIn("z_index = 35", text)

    @unittest.skipUnless(_configured_godot_exists(), "configured godot_executable is not installed here")
    def test_headless_depth_sorting(self):
        code, output = run_godot("res://tools/verify_depth_sorting.gd")
        self.assertEqual(code, 0, output)
        self.assertIn("DEPTH_SORTING_OK", output)
        self.assertNotIn("SCRIPT ERROR:", output)
        self.assertNotIn("FAIL:", output)


if __name__ == "__main__":
    unittest.main()
