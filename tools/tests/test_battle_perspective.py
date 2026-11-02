"""Run perspective behaviour checks against the actual GDScript resolver."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]


def configured_godot() -> str:
    """Use the test router's existing environment/configuration precedence."""
    spec = importlib.util.spec_from_file_location(
        "battle_perspective_test_router", ROOT / "tools/run_tests.py"
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load tools/run_tests.py")
    router = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(router)
    return router.godot_executable()


class BattlePerspectiveTests(unittest.TestCase):
    def test_perspective_contract_in_godot(self) -> None:
        godot = configured_godot()
        if not (Path(godot).is_file() or shutil.which(godot)):
            self.skipTest("Godot executable unavailable: " + godot)

        command = [
            godot,
            "--headless",
            "--path",
            str(ROOT),
            "--script",
            "res://tools/verify_battle_perspective.gd",
        ]
        try:
            proc = subprocess.run(
                command,
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=60,
            )
        except subprocess.TimeoutExpired as exc:
            self.fail(f"Perspective verification timed out: {exc}")
        output = proc.stdout + proc.stderr
        self.assertEqual(proc.returncode, 0, output)
        self.assertNotIn("SCRIPT ERROR:", output, output)
        self.assertNotIn("ERROR:", output, output)
        self.assertIn("BATTLE_PERSPECTIVE_OK", output, output)


if __name__ == "__main__":
    unittest.main()
