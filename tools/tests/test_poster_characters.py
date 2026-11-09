"""Tests for the poster character sprites, the HD master layout and the NPC data.

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
import organize_hd_masters

SLUGS = ("cely", "neru", "old_father", "reef_friend", "temple_archer")


def _configured_godot_exists() -> bool:
    config = ROOT / ".agents/planner/config.json"
    try:
        path = json.loads(config.read_text(encoding="utf-8")).get("godot_executable")
    except (OSError, ValueError):
        return False
    return isinstance(path, str) and Path(path).is_file()


class PosterCharacterTests(unittest.TestCase):
    def test_sprite_files_exist_for_every_direction(self):
        for slug in SLUGS:
            for direction in ("down", "left", "right", "up"):
                self.assertTrue((ROOT / f"assets/characters/{slug}/map/{slug}_map_{direction}.png").is_file(), (slug, direction))
                for number in (1, 2, 3):
                    frame = ROOT / f"assets/characters/{slug}/map/{direction}/{slug}_map_{direction}_{number:02d}.png"
                    self.assertTrue(frame.is_file(), frame)

    def test_extraction_finds_twelve_sprites(self):
        try:
            import numpy  # noqa: F401
            import extract_poster_sprites as extract
        except ImportError:
            self.skipTest("numpy is not installed")
        for slug in ("cely", "temple_archer"):  # cely: tall rows; temple_archer: panel border merged into the mask
            sprites = extract.extract(slug)
            self.assertEqual({k: len(v) for k, v in sprites.items()}, {"down": 3, "left": 3, "right": 3, "up": 3}, slug)

    def test_npcs_use_available_characters(self):
        data = json.loads((ROOT / "map_factory/rooms/hero_room.json").read_text(encoding="utf-8"))
        characters = [npc.get("character", "") for npc in data["npcs"]]
        self.assertTrue(all(c in SLUGS for c in characters), characters)
        self.assertEqual(len(set(characters)), len(characters), "each character appears once")
        ids = [npc["instance_id"] for npc in data["npcs"]]
        self.assertEqual(len(ids), len(set(ids)))

    @unittest.skipUnless(_configured_godot_exists(), "configured godot_executable is not installed here")
    def test_headless_poster_characters(self):
        code, output = run_godot("res://tools/verify_poster_characters.gd")
        self.assertEqual(code, 0, output)
        self.assertIn("POSTER_CHARACTERS_OK", output)
        self.assertNotIn("SCRIPT ERROR:", output)
        self.assertNotIn("FAIL:", output)


class HdMasterLayoutTests(unittest.TestCase):
    def test_subfolder_is_the_stem_without_number(self):
        self.assertEqual(organize_hd_masters.subfolder("assets_hd/hero/hero_pose_01.png"), "hero_pose")
        self.assertEqual(organize_hd_masters.subfolder("bench_blue_runner_12.png"), "bench_blue_runner")
        self.assertEqual(organize_hd_masters.subfolder("concept_art_action_scene.png"), "concept_art_action_scene")

    def test_plan_is_idempotent(self):
        items = [{"path": "assets_hd/hero/hero_pose_01.png"}, {"path": "assets_hd/hero/hero_pose/hero_pose_02.png"}]
        self.assertEqual(organize_hd_masters.plan(items), [("hero/hero_pose_01.png", "hero/hero_pose/hero_pose_01.png"),
                                                           ("hero/hero_pose/hero_pose_02.png", "hero/hero_pose/hero_pose_02.png")])

    def test_manifest_and_hd_map_paths_are_sorted(self):
        manifest = json.loads((ROOT / "assets_hd/manifest.json").read_text(encoding="utf-8"))
        for item in manifest["items"]:
            self.assertEqual(len(Path(item["path"]).parts), 4, item["path"])
        hd_map = json.loads((ROOT / "assets_hd/hd_map.json").read_text(encoding="utf-8"))["map"]
        known = {i["path"].removeprefix("assets_hd/") for i in manifest["items"]}
        for record in hd_map.values():
            self.assertIn(record["master"], known)


if __name__ == "__main__":
    unittest.main()
