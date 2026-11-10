"""Prove the optimised ShadowPainter is byte-identical to the unoptimised reference (headless).

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


class ShadowPainterTests(unittest.TestCase):
    def test_reference_is_kept_and_not_a_global_class(self):
        reference = (ROOT / "tools/tests/fixtures/shadow_painter_reference.gd").read_text(encoding="utf-8")
        self.assertIn("GOLDEN REFERENCE", reference)
        self.assertNotIn("class_name", reference)

    def test_painter_has_no_per_pixel_api_calls_left_in_the_hot_loops(self):
        text = (ROOT / "map_factory/scripts/shadow_painter.gd").read_text(encoding="utf-8")
        self.assertNotIn(".get_pixel(", text)
        self.assertNotIn(".set_pixel(", text)

    @unittest.skipUnless(_configured_godot_exists(), "configured godot_executable is not installed here")
    def test_headless_identical_output(self):
        code, output = run_godot("res://tools/verify_shadow_speed.gd", timeout=180)
        self.assertEqual(code, 0, output)
        self.assertIn("SHADOW_PAINTER_OK", output)
        self.assertNotIn("SCRIPT ERROR:", output)
        self.assertNotIn("FAIL:", output)


if __name__ == "__main__":
    unittest.main()
