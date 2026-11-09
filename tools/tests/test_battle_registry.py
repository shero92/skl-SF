"""Every tools/tests/test_battle_*.py must be routed exactly once, with unique ids.

Execution provenance: Agent: claude (Claude Code); model: Sonnet 5.5.
"""
from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
TESTS = ROOT / "tools" / "tests"


def _entries() -> list[dict]:
    data = json.loads((ROOT / "tools" / "test_map.json").read_text(encoding="utf-8"))
    return data["tests"]


def _pattern(entry: dict) -> str | None:
    command = entry.get("command", [])
    if "-p" in command:
        return command[command.index("-p") + 1]
    return None


class BattleRegistryTests(unittest.TestCase):
    def test_ids_are_unique(self):
        ids = [entry["id"] for entry in _entries()]
        self.assertEqual(len(ids), len(set(ids)), "duplicate test ids in test_map.json")

    def test_every_battle_test_is_registered_once(self):
        entries = _entries()
        for test_file in sorted(TESTS.glob("test_battle_*.py")):
            matches = [e["id"] for e in entries if _pattern(e) == test_file.name]
            self.assertEqual(len(matches), 1, f"{test_file.name} registered {len(matches)}x: {matches}")

    def test_battle_entries_route_their_own_files(self):
        for entry in _entries():
            pattern = _pattern(entry)
            if pattern and pattern.startswith("test_battle_"):
                self.assertIn(f"tools/tests/{pattern}", entry["paths"], entry["id"])


if __name__ == "__main__":
    unittest.main()
