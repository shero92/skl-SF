"""Fixtures for tools/graphics_validation.py plus a clean-baseline check on the real repository.

Execution provenance: Agent: claude (Claude Code); model: Sonnet 5.5.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from PIL import Image

TOOLS = Path(__file__).resolve().parents[1]
ROOT = TOOLS.parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import graphics_validation as gv


def png(path: Path, size=(8, 8), mode="RGBA", color=(200, 50, 50, 255)) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new(mode, size, color if mode == "RGBA" else color[:3]).save(path)


def write(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def errors(self, changed=None):
        return gv.validate(self.root, changed).errors


class PngChecks(Fixture):
    def test_valid_sprite_passes(self):
        png(self.root / "map_factory/parts/walls/W1_a.png")
        write(self.root / "map_factory/metadata/asset_index.json", {"assets": [
            {"id": "W1", "category": "walls", "texture_path": "res://map_factory/parts/walls/W1_a.png", "pixel_size": [8, 8]}]})
        self.assertEqual(self.errors(), [])

    def test_corrupt_png_fails_with_the_path(self):
        target = self.root / "assets/characters/hero/map/bad.png"
        target.parent.mkdir(parents=True)
        target.write_bytes(b"not a png")
        self.assertTrue(any("assets/characters/hero/map/bad.png: unreadable PNG" in e for e in self.errors()))

    def test_fully_transparent_fails(self):
        png(self.root / "assets/characters/hero/map/empty.png", color=(0, 0, 0, 0))
        self.assertTrue(any("fully transparent" in e for e in self.errors()))

    def test_opaque_sprite_fails_but_opaque_floor_is_allowed(self):
        png(self.root / "map_factory/parts/objects/O1_x.png", mode="RGB")
        png(self.root / "map_factory/parts/floors/F1_x.png", mode="RGB")
        write(self.root / "map_factory/metadata/asset_index.json", {"assets": [
            {"id": "O1", "category": "objects", "texture_path": "res://map_factory/parts/objects/O1_x.png", "pixel_size": [8, 8]},
            {"id": "F1", "category": "floors", "texture_path": "res://map_factory/parts/floors/F1_x.png", "pixel_size": [8, 8]}]})
        errors = self.errors()
        self.assertTrue(any("O1_x.png: no alpha" in e for e in errors))
        self.assertFalse(any("F1_x.png" in e for e in errors))

    def test_archive_folders_are_not_production_art(self):
        png(self.root / "assets/characters/hero/references/design.png", mode="RGB")
        png(self.root / "assets/characters/hero/rejected/old.png", mode="RGB")
        png(self.root / "assets_generated/floor/G04__default" / ("a" * 32) / "source.png", mode="RGB")
        self.assertEqual(self.errors(), [])


class MetadataChecks(Fixture):
    def test_catalog_size_mismatch_missing_file_and_duplicate_ids(self):
        png(self.root / "map_factory/parts/walls/W1_a.png", size=(8, 8))
        write(self.root / "map_factory/metadata/asset_index.json", {"assets": [
            {"id": "W1", "category": "walls", "texture_path": "res://map_factory/parts/walls/W1_a.png", "pixel_size": [16, 16]},
            {"id": "W1", "category": "walls", "texture_path": "res://map_factory/parts/walls/W1_a.png", "pixel_size": [8, 8]},
            {"id": "W2", "category": "walls", "texture_path": "res://map_factory/parts/walls/W2_gone.png", "pixel_size": [8, 8]}]})
        errors = self.errors()
        self.assertTrue(any("size [8, 8] != pixel_size [16, 16]" in e for e in errors))
        self.assertTrue(any("duplicate id W1" in e for e in errors))
        self.assertTrue(any("W2_gone.png" in e and "missing" in e for e in errors))

    def test_hd_runtime_must_be_scale_times_native(self):
        png(self.root / "assets_hd/runtime/A01__x__y__default__1x1__4x4.png", size=(8, 8))
        write(self.root / "assets_hd/hd_map.json", {"scale": 2, "map": {
            "architecture/A01__x__y__default__1x1__4x4.png": {"native_size": [4, 4]},
            "architecture/A02__x__y__default__1x1__4x4.png": {"native_size": [4, 4]}}})
        errors = self.errors()
        self.assertFalse(any("A01" in e for e in errors))
        self.assertTrue(any("A02" in e and "missing" in e for e in errors))
        png(self.root / "assets_hd/runtime/A02__x__y__default__1x1__4x4.png", size=(9, 8))
        self.assertTrue(any("A02" in e and "!= 2 x native" in e for e in self.errors()))

    def test_generated_manifest_orientation_key_and_size(self):
        png(self.root / "assets_generated/furniture/F05__furniture__bed__south__1x1__8x8.png", size=(8, 8))
        png(self.root / "assets_generated/furniture/F05__furniture__bed__north__1x1__8x8.png", size=(9, 8))
        write(self.root / "assets_generated/manifest.json", {"assets": [
            {"asset_id": "F05", "orientation": "south", "native_width": 8, "native_height": 8},
            {"asset_id": "F05", "orientation": "north", "native_width": 8, "native_height": 8}]})
        errors = self.errors()
        self.assertFalse(any("duplicate" in e for e in errors), "same id with different orientations is valid")
        self.assertTrue(any("north" in e and "!= native" in e for e in errors))
        self.assertFalse(any("south" in e for e in errors))

    def test_character_frames(self):
        base = self.root / "assets/characters/hero/map/down"
        png(base / "idle_1.png", size=(96, 96))
        png(base / "idle_2.png", size=(96, 100))
        write(self.root / "game_factory/character_manifest.json", {"characters": [{
            "slug": "hero", "map_sprite_canvas_size": [96, 96],
            "animations": {
                "map_down_idle": {"complete": True, "frames": [
                    "res://assets/characters/hero/map/down/idle_1.png", "res://assets/characters/hero/map/down/idle_2.png",
                    "res://assets/characters/hero/map/down/idle_3.png"]},
                "map_down_walk": {"complete": True, "frames": []}},
            "map_idle_frames": {}, "map_walk_frames": {}}]})
        errors = self.errors()
        self.assertTrue(any("hero/map_down_idle: frame file missing" in e for e in errors))
        self.assertTrue(any("hero/map_down_idle: frames use different canvases" in e for e in errors))
        self.assertTrue(any("hero/map_down_walk: marked complete but has no frames" in e for e in errors))

    def test_incomplete_animation_without_frames_is_not_an_error(self):
        write(self.root / "game_factory/character_manifest.json", {"characters": [{
            "slug": "neru", "animations": {"battle_hurt": {"complete": False, "frames": []}}}]})
        self.assertEqual(self.errors(), [])


class ChangedDetection(Fixture):
    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.root), *args], capture_output=True, text=True, check=True)

    def test_changed_mode_checks_only_changed_pngs(self):
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "t@example.com")
        self.git("config", "user.name", "t")
        self.git("config", "commit.gpgsign", "false")
        png(self.root / "assets/characters/hero/map/ok.png")
        broken = self.root / "assets/characters/hero/map/old_bad.png"
        broken.write_bytes(b"junk")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "base")
        self.git("checkout", "-q", "-b", "task")
        png(self.root / "assets/characters/hero/map/new.png")
        changed = gv.changed_paths(self.root, "main")
        self.assertIn("assets/characters/hero/map/new.png", changed)
        report = gv.validate(self.root, changed)
        self.assertEqual(report.errors, [], "unchanged broken files are outside a changed-only run")
        self.assertEqual(report.checked_pngs, 1)
        self.assertEqual(gv.validate(self.root, None).checked_pngs, 3)
        self.assertTrue(gv.validate(self.root, None).errors)


class RealRepository(unittest.TestCase):
    def test_current_graphics_are_technically_clean(self):
        report = gv.validate(ROOT, None)
        self.assertEqual(report.errors, [], "\n".join(report.errors[:20]))
        self.assertGreater(report.checked_pngs, 500)


if __name__ == "__main__":
    unittest.main()
