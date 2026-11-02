"""Headless battle controller state, actor, validation and cancellation contracts.

Execution provenance: Agent: codex; model: GPT-6.
Missing Godot fails verification rather than silently skipping the task.
"""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

TOOLS = Path(__file__).resolve().parents[1]
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from battle_godot_harness import run_godot


class BattleControllerTests(unittest.TestCase):
    def test_headless_controller(self):
        code, output = run_godot("res://tools/verify_battle_controller.gd")
        self.assertEqual(code, 0, output)
        self.assertIn("BATTLE_CONTROLLER_OK", output)
        self.assertNotIn("SCRIPT ERROR:", output)
        self.assertNotIn("FAIL:", output)


if __name__ == "__main__":
    unittest.main()
