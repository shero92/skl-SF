"""Run the real combo sequencer in headless Godot, without production scenes."""

from pathlib import Path
import shutil
import subprocess
import sys
import unittest

TOOLS = Path(__file__).resolve().parents[1]
ROOT = TOOLS.parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from run_tests import godot_executable


class BattleComboTests(unittest.TestCase):
    def test_combo_behaviour_in_godot(self):
        executable = godot_executable()
        if not (Path(executable).is_file() or shutil.which(executable)):
            self.skipTest("Godot unavailable; set GODOT_EXECUTABLE to run behavioural checks")
        result = subprocess.run(
            [
                executable,
                "--headless",
                "--path",
                str(ROOT),
                "--script",
                "res://tools/verify_battle_combo.gd",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
            check=False,
        )
        output = result.stdout + result.stderr
        self.assertEqual(result.returncode, 0, output)
        self.assertIn("BATTLE_COMBO_OK", output, output)
        for marker in ("SCRIPT ERROR:", "ERROR:", "FAIL:"):
            self.assertNotIn(marker, output, output)


if __name__ == "__main__":
    unittest.main()
