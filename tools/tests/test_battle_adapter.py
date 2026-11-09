"""Verify the ModularBattleCharacter adapter headlessly and that original scripts are untouched.

Execution provenance: Agent: claude (Claude Code); model: Sonnet 5.5.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest

TOOLS = Path(__file__).resolve().parents[1]
ROOT = TOOLS.parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from battle_godot_harness import run_godot

PROTECTED = ("scenes/modular_battle_character.gd", "scenes/modular_battle_demo.gd")


def _configured_godot_exists() -> bool:
    config = ROOT / ".agents/planner/config.json"
    try:
        path = json.loads(config.read_text(encoding="utf-8")).get("godot_executable")
    except (OSError, ValueError):
        return False
    return isinstance(path, str) and Path(path).is_file()


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


class BattleAdapterTests(unittest.TestCase):
    # Python-only CI has no Godot at the owner's path; this runs wherever it is installed.
    @unittest.skipUnless(_configured_godot_exists(), "configured godot_executable is not installed here")
    def test_headless_adapter(self):
        code, output = run_godot("res://tools/verify_battle_adapter.gd")
        self.assertEqual(code, 0, output)
        self.assertIn("BATTLE_ADAPTER_OK", output)
        self.assertNotIn("SCRIPT ERROR:", output)
        self.assertNotIn("FAIL:", output)

    def test_original_character_scripts_unchanged(self):
        base = _git("merge-base", "HEAD", "origin/main")
        if base.returncode != 0:
            self.skipTest("origin/main is not available")
        diff = _git("diff", "--quiet", base.stdout.strip(), "--", *PROTECTED)
        self.assertEqual(diff.returncode, 0, "original character scripts were modified")


if __name__ == "__main__":
    unittest.main()
