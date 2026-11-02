"""Battle timeline integration and shared Godot runner failure contracts."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1]
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from battle_godot_harness import run_godot


class BattleTimelineTests(unittest.TestCase):
    def test_headless_timeline(self):
        code, output = run_godot("res://tools/verify_battle_timeline.gd")
        self.assertEqual(code, 0, output)
        self.assertIn("BATTLE_TIMELINE_OK", output)
        self.assertNotIn("SCRIPT ERROR:", output)
        self.assertNotIn("FAIL:", output)


class GodotHarnessTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.config = self.root / ".agents/planner/config.json"
        self.config.parent.mkdir(parents=True)
        self.config.write_text(
            json.dumps({"godot_executable": "configured-godot"}),
            encoding="utf-8",
            newline="\n",
        )

    def test_command_and_output(self):
        result = subprocess.CompletedProcess([], 7, "stdout\n", "stderr\n")
        with patch("battle_godot_harness.subprocess.run", return_value=result) as run:
            code, output = run_godot(
                "res://tools/verify_battle_timeline.gd", root=self.root,
            )
        self.assertEqual((code, output), (7, "stdout\nstderr\n"))
        self.assertEqual(
            run.call_args.args[0],
            [
                "configured-godot", "--headless", "--path", ".",
                "--script", "res://tools/verify_battle_timeline.gd",
            ],
        )
        self.assertEqual(run.call_args.kwargs["cwd"], str(self.root.resolve()))
        self.assertEqual(run.call_args.kwargs["timeout"], 60)

    def test_missing_executable_fails(self):
        with patch(
            "battle_godot_harness.subprocess.run",
            side_effect=FileNotFoundError("Godot missing"),
        ):
            code, output = run_godot(
                "res://tools/verify_battle_timeline.gd", root=self.root,
            )
        self.assertNotEqual(code, 0)
        self.assertIn("Godot missing", output)

    def test_missing_configuration_fails(self):
        self.config.unlink()
        code, output = run_godot(
            "res://tools/verify_battle_timeline.gd", root=self.root,
        )
        self.assertNotEqual(code, 0)
        self.assertIn("could not run", output)

    def test_missing_setting_fails(self):
        self.config.write_text("{}", encoding="utf-8", newline="\n")
        code, output = run_godot(
            "res://tools/verify_battle_timeline.gd", root=self.root,
        )
        self.assertNotEqual(code, 0)
        self.assertIn("Missing godot_executable", output)

    def test_timeout_preserves_output(self):
        with patch(
            "battle_godot_harness.subprocess.run",
            side_effect=subprocess.TimeoutExpired(
                ["configured-godot"], 2, output=b"partial", stderr=b"error",
            ),
        ):
            code, output = run_godot(
                "res://tools/verify_battle_timeline.gd",
                root=self.root,
                timeout=2,
            )
        self.assertEqual(code, 124)
        self.assertIn("partial", output)
        self.assertIn("error", output)

    def test_rejects_non_verification_script(self):
        with patch("battle_godot_harness.subprocess.run") as run:
            code, _ = run_godot("res://scenes/main.gd", root=self.root)
        self.assertNotEqual(code, 0)
        run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
