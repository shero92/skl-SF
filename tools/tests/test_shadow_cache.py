"""Verify the painted-shadow cache (memory + disk) is byte-identical and faster (headless).

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


class ShadowCacheTests(unittest.TestCase):
    def test_cache_is_outside_the_repo_and_versioned(self):
        text = (ROOT / "map_factory/scripts/shadow_painter.gd").read_text(encoding="utf-8")
        self.assertIn('static var cache_dir := "user://shadow_cache/"', text)
        self.assertIn("const CACHE_VERSION", text)

    @unittest.skipUnless(_configured_godot_exists(), "configured godot_executable is not installed here")
    def test_headless_cache(self):
        # The corrupt-entry case makes the engine print an expected image-load error; only script errors fail.
        code, output = run_godot("res://tools/verify_shadow_cache.gd", timeout=240)
        self.assertEqual(code, 0, output)
        self.assertIn("SHADOW_CACHE_OK", output)
        self.assertNotIn("SCRIPT ERROR:", output)
        self.assertNotIn("FAIL:", output)


if __name__ == "__main__":
    unittest.main()
