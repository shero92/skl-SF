"""Headless behavioural tests for TASK-0082 defender reactions.

Execution provenance: Agent: codex; model: GPT-6.
"""
from __future__ import annotations

import json
import importlib.util
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]


def load_router():
    spec = importlib.util.spec_from_file_location(
        "battle_reactions_test_router", ROOT / "tools" / "run_tests.py"
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load repository test router")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _configured_godot_exists() -> bool:
    config = Path(__file__).resolve().parents[2] / ".agents/planner/config.json"
    try:
        path = json.loads(config.read_text(encoding="utf-8")).get("godot_executable")
    except (OSError, ValueError):
        return False
    return isinstance(path, str) and Path(path).is_file()


class BattleReactionsTests(unittest.TestCase):
    def test_router_registration(self):
        router = load_router()
        entries = [
            entry for entry in router.load_map()
            if entry["id"] == "battle_reactions"
        ]
        self.assertEqual(len(entries), 1)
        entry = entries[0]
        self.assertEqual(entry["kind"], "python")
        for path in (
            "scenes/battle/battle_reactions.gd",
            "tools/verify_battle_reactions.gd",
            "tools/tests/test_battle_reactions.py",
        ):
            self.assertTrue(router.matches(path, entry["paths"]), path)
        self.assertEqual(
            entry["command"],
            ["{python}", "-m", "unittest", "discover", "-s", "tools/tests",
             "-p", "test_battle_reactions.py"],
        )

    # Python-only CI has no Godot at the owner's path; this runs wherever it is installed.
    @unittest.skipUnless(_configured_godot_exists(), "configured godot_executable is not installed here")
    def test_headless_reactions(self):
        executable = load_router().godot_executable()
        self.assertTrue(
            Path(executable).is_file() or shutil.which(executable),
            f"Godot executable not found: {executable}",
        )
        result = subprocess.run(
            [executable, "--headless", "--path", str(ROOT),
             "--script", "res://tools/verify_battle_reactions.gd"],
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
        self.assertNotIn("SCRIPT ERROR", output)
        self.assertNotIn("ERROR:", output)
        self.assertIn("BATTLE_REACTIONS_OK", output)


if __name__ == "__main__":
    unittest.main()
