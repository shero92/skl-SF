"""Verify the painted shadow level and light level headlessly.

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


class ShadowPainterTests(unittest.TestCase):
    @unittest.skipUnless(_configured_godot_exists(), "configured godot_executable is not installed here")
    def test_headless_shadow_painter(self):
        code, output = run_godot("res://tools/verify_shadow_painter.gd")
        self.assertEqual(code, 0, output)
        self.assertIn("SHADOW_PAINTER_OK", output)
        self.assertNotIn("SCRIPT ERROR:", output)
        self.assertNotIn("FAIL:", output)

    def test_schema_documents_both_levels(self):
        text = (ROOT / "map_factory/LAYER_SCHEMA.md").read_text(encoding="utf-8")
        self.assertIn("Level4_PaintedShadows", text)
        self.assertIn("Level5_Light", text)


if __name__ == "__main__":
    unittest.main()
