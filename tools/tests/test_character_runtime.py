"""Verify the shared asset catalog and the opt-in Game Factory hero art headlessly.

Execution provenance: Agent: claude (Claude Code); model: Sonnet 5.5.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

TOOLS = Path(__file__).resolve().parents[1]
ROOT = TOOLS.parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from battle_godot_harness import run_godot


def _configured_godot_exists() -> bool:
    try:
        path = json.loads((ROOT / ".agents/planner/config.json").read_text(encoding="utf-8")).get("godot_executable")
    except (OSError, ValueError):
        return False
    return isinstance(path, str) and Path(path).is_file()


class CharacterRuntimeTests(unittest.TestCase):
    def test_gameplay_scripts_use_the_shared_catalog(self):
        for name in ("scenes/player.gd", "scenes/room_npc.gd", "scenes/room_companion.gd"):
            text = (ROOT / name).read_text(encoding="utf-8")
            self.assertIn("AssetCatalog.shared()", text, name)
            self.assertNotIn("AssetCatalog.new()", text, name)

    def test_factory_art_is_opt_in_and_uses_complete_frames_only(self):
        player = (ROOT / "scenes/player.gd").read_text(encoding="utf-8")
        self.assertIn("@export var use_factory_art: bool = false", player)
        manifest = json.loads((ROOT / "game_factory/character_manifest.json").read_text(encoding="utf-8"))
        hero = next(c for c in manifest["characters"] if c["slug"] == "hero")
        for direction in ("down", "left", "right", "up"):
            for state in ("idle", "walk"):
                self.assertTrue(hero["animations"][f"map_{direction}_{state}"]["complete"])
        others = [c for c in manifest["characters"] if c["slug"] != "hero"]
        self.assertTrue(all(not any(a.get("complete") for a in c["animations"].values()) for c in others),
                        "only the hero has complete animations; the others must stay incomplete")

    @unittest.skipUnless(_configured_godot_exists(), "configured godot_executable is not installed here")
    def test_headless_character_runtime(self):
        code, output = run_godot("res://tools/verify_character_runtime.gd")
        self.assertEqual(code, 0, output)
        self.assertIn("CHARACTER_RUNTIME_OK", output)
        self.assertNotIn("SCRIPT ERROR:", output)
        self.assertNotIn("FAIL:", output)


if __name__ == "__main__":
    unittest.main()
