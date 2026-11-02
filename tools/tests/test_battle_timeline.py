"""Battle timeline integration and shared harness failure-path checks."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from tools.battle_godot_harness import run_godot

SCRIPT = "res://tools/verify_battle_timeline.gd"


class BattleTimelineTests(unittest.TestCase):
    def test_headless_timeline(self) -> None:
        code, output = run_godot(SCRIPT)
        self.assertEqual(code, 0, output)
        self.assertIn("PASS battle timeline", output)
        # Godot can report script failures without a useful process exit status.
        self.assertNotIn("SCRIPT ERROR:", output)
        self.assertNotIn("ERROR:", output)
        self.assertNotIn("FAIL:", output)


class BattleGodotHarnessTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        config = self.root / ".agents/planner/config.json"
        config.parent.mkdir(parents=True)
        self.executable = self.root / "godot.exe"
        self.executable.write_bytes(b"")
        config.write_text(
            json.dumps({"godot_executable": str(self.executable)}),
            encoding="utf-8",
        )
        verifier = self.root / "tools/verify_battle_timeline.gd"
        verifier.parent.mkdir()
        verifier.write_text("extends SceneTree\n", encoding="utf-8")

    def test_command_and_output(self) -> None:
        result = subprocess.CompletedProcess([], 7, "stdout\n", "stderr\n")
        with patch(
            "tools.battle_godot_harness.subprocess.run", return_value=result
        ) as run:
            self.assertEqual(
                run_godot(SCRIPT, root=self.root), (7, "stdout\nstderr\n")
            )
        args, kwargs = run.call_args
        self.assertEqual(
            args[0],
            [
                str(self.executable),
                "--headless",
                "--path",
                ".",
                "--script",
                SCRIPT,
            ],
        )
        self.assertEqual(kwargs["cwd"], str(self.root.resolve()))
        self.assertEqual(kwargs["timeout"], 60.0)

    def test_missing_godot_fails_without_launching(self) -> None:
        self.executable.unlink()
        with (
            patch("tools.battle_godot_harness.shutil.which", return_value=None),
            patch("tools.battle_godot_harness.subprocess.run") as run,
        ):
            code, output = run_godot(SCRIPT, root=self.root)
        self.assertNotEqual(code, 0)
        self.assertIn("executable not found", output)
        run.assert_not_called()

    def test_missing_config_fails(self) -> None:
        (self.root / ".agents/planner/config.json").unlink()
        code, output = run_godot(SCRIPT, root=self.root)
        self.assertNotEqual(code, 0)
        self.assertIn("Cannot run Godot verifier", output)

    def test_timeout_preserves_output(self) -> None:
        error = subprocess.TimeoutExpired(
            "godot", 2, output=b"partial stdout\n", stderr=b"partial stderr\n"
        )
        with patch(
            "tools.battle_godot_harness.subprocess.run", side_effect=error
        ):
            code, output = run_godot(SCRIPT, root=self.root, timeout=2)
        self.assertEqual(code, 124)
        self.assertIn("partial stdout\npartial stderr\n", output)

    def test_launch_error_fails(self) -> None:
        with patch(
            "tools.battle_godot_harness.subprocess.run",
            side_effect=OSError("launch failed"),
        ):
            code, output = run_godot(SCRIPT, root=self.root)
        self.assertNotEqual(code, 0)
        self.assertIn("launch failed", output)

    def test_rejects_scripts_outside_verifier_directory(self) -> None:
        for script in (
            "res://scenes/battle/battle_timeline.gd",
            "res://tools/../verify_escape.gd",
            "res://tools/nested/verify_nested.gd",
        ):
            with self.subTest(script=script):
                code, output = run_godot(script, root=self.root)
                self.assertNotEqual(code, 0)
                self.assertIn("Invalid verifier", output)


if __name__ == "__main__":
    unittest.main()
