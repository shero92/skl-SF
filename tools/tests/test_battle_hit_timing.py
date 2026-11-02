"""Verify the signal-only hit bridge against the real Godot controller.

Execution provenance: Agent: codex; model: GPT-6.
Missing Godot is a failure, never a skip.
"""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

TOOLS = Path(__file__).resolve().parents[1]
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from battle_godot_harness import run_godot


class BattleHitTimingTests(unittest.TestCase):
    def test_headless_hit_timing(self):
        code, output = run_godot("res://tools/verify_hit_timing.gd")
        self.assertEqual(code, 0, output)
        self.assertIn("BATTLE_HIT_TIMING_OK", output)
        self.assertNotIn("SCRIPT ERROR:", output)
        self.assertNotIn("FAIL:", output)


if __name__ == "__main__":
    unittest.main()
