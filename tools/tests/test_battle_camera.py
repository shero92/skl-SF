"""Headless behavioural verification for TASK-0078.

Agent: codex. Model: GPT-6.
"""
from pathlib import Path
import os
import shutil
import subprocess
import unittest

from tools.run_tests import godot_executable


ROOT = Path(__file__).resolve().parents[2]


class BattleCameraTests(unittest.TestCase):
    def test_headless_camera_contract(self):
        executable = godot_executable()
        if not (Path(executable).is_file() or shutil.which(executable)):
            self.skipTest("Godot executable unavailable: " + executable)
        environment = os.environ.copy()
        environment["GODOT_SILENCE_ROOT_WARNING"] = "1"
        try:
            result = subprocess.run(
                [
                    executable,
                    "--headless",
                    "--path",
                    str(ROOT),
                    "--script",
                    "res://tools/verify_battle_camera.gd",
                ],
                cwd=ROOT,
                env=environment,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=60,
                check=False,
            )
        except subprocess.TimeoutExpired:
            self.fail("Headless battle camera verification timed out after 60 seconds.")
        output = result.stdout + result.stderr
        self.assertEqual(result.returncode, 0, output)
        self.assertNotIn("SCRIPT ERROR", output, output)
        self.assertNotIn("ERROR:", output, output)
        self.assertIn("BATTLE_CAMERA_OK", output, output)


if __name__ == "__main__":
    unittest.main()
