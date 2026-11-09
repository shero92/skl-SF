"""Verify the live Map Factory viewer headlessly.

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


class MapViewerTests(unittest.TestCase):
    @unittest.skipUnless(_configured_godot_exists(), "configured godot_executable is not installed here")
    def test_headless_viewer(self):
        code, output = run_godot("res://tools/verify_map_factory_viewer.gd")
        self.assertEqual(code, 0, output)
        self.assertIn("MAP_VIEWER_OK", output)
        self.assertNotIn("SCRIPT ERROR:", output)
        self.assertNotIn("FAIL:", output)

    def test_scene_references_the_viewer_script(self):
        text = (ROOT / "scenes/map_factory_viewer.tscn").read_text(encoding="utf-8")
        self.assertIn("res://scenes/map_factory_viewer.gd", text)


if __name__ == "__main__":
    unittest.main()
