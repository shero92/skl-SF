"""Runtime acceptance tests for the isolated battle VFX layer.

Uses the repository's Godot executable configuration. No artwork is generated.
"""
from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import unittest

from tools import run_tests


ROOT = Path(__file__).resolve().parents[2]


class BattleVFXTests(unittest.TestCase):
    def test_runtime_acceptance(self) -> None:
        executable = run_tests.godot_executable()
        if not (Path(executable).is_file() or shutil.which(executable)):
            self.skipTest("Godot executable unavailable: " + executable)

        try:
            result = subprocess.run(
                [
                    executable,
                    "--headless",
                    "--path",
                    str(ROOT),
                    "--script",
                    "res://tools/verify_battle_vfx.gd",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=60,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            self.fail(f"Battle VFX verification timed out: {exc}")
        output = result.stdout + result.stderr
        self.assertEqual(result.returncode, 0, output)
        self.assertIn("BATTLE_VFX_OK", result.stdout.splitlines(), output)
        self.assertNotIn("SCRIPT ERROR:", output, output)
        self.assertNotIn("ERROR:", output, output)


if __name__ == "__main__":
    unittest.main()
