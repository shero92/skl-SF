"""Hands-on room editor: the Godot scene (headless) and the save tool that publishes its edits.

Execution provenance: Agent: claude (Claude Code); model: Fable 5.2.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import unittest

TOOLS = Path(__file__).resolve().parents[1]
ROOT = TOOLS.parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from battle_godot_harness import run_godot
import room_editor_save as saver

PATCHES = ROOT / "map_factory/maps/hero_room_01/patches"


def _godot() -> bool:
    try:
        path = json.loads((ROOT / ".agents/planner/config.json").read_text(encoding="utf-8")).get("godot_executable")
    except (OSError, ValueError):
        return False
    return isinstance(path, str) and Path(path).is_file()


def _latest() -> dict:
    return json.loads((ROOT / "map_factory/maps/hero_room_01/latest.json").read_text(encoding="utf-8"))


class SaveToolTests(unittest.TestCase):
    def setUp(self):
        self.before = sorted(p.name for p in PATCHES.glob("*.json"))
        self.version = int(_latest()["version"])
        self.block = next(b for b in _latest()["objects"] if not b.get("grid_placement"))

    def tearDown(self):
        self.assertEqual(sorted(p.name for p in PATCHES.glob("*.json")), self.before, "a dry run or a rejected edit left a patch behind")
        self.assertEqual(int(_latest()["version"]), self.version)

    def test_add_update_remove_pass_the_factory_rules(self):
        name = self.block["instance_id"]
        request = {"map_id": "hero_room_01", "changes": [
            {"op": "add", "layer": "objects", "id": "P05", "instance_id": "EdP05_1", "x": 640, "y": 420,
             "scale": 0.8, "rotation_degrees": 30, "flip_h": True},
            {"op": "update", "instance_id": name, "set": {"x": float(self.block["x"]) + 12, "scale": 1.2, "ignored": 1}},
        ]}
        design = saver.build_design(request)
        add, update = design.changes
        self.assertTrue(add["block"]["free_transform"] and add["block"]["flip_h"])
        self.assertEqual(update["set"], {"x": float(self.block["x"]) + 12, "scale": 1.2, "free_transform": True})
        self.assertEqual(saver.save(request, dry_run=True), self.version + 1)
        self.assertEqual(saver.save({"map_id": "hero_room_01", "changes": [{"op": "remove", "instance_id": name}]}, dry_run=True),
                         self.version + 1)

    def test_ground_edits_and_new_map_checks(self):
        latest = _latest()
        rows = [list(map(list, spans)) for spans in latest["floor_footprint"]["row_spans"]]
        rows[5] = [[1, rows[5][0][1]]]  # drop square 0 of row 5
        request = {"map_id": "hero_room_01", "changes": [
            {"op": "tile", "x": 0, "y": 5, "id": None},
            {"op": "tile", "x": 3, "y": 3, "id": "G09"},
            {"op": "property", "key": "floor_footprint", "value": {"row_spans": rows, "shape": "editor"}}]}
        self.assertEqual(saver.save(request, dry_run=True), self.version + 1)
        with self.assertRaises(ValueError):
            saver.save({"map_id": "hero_room_01", "changes": [{"op": "property", "key": "camera", "value": {}}]}, dry_run=True)
        self.assertEqual(saver.new_map("editor_test_map", "courtyard", dry_run=True), 1)
        for name, preset in (("hero_room_01", "courtyard"), ("Bad Name", "courtyard"), ("fine_name", "no_such_preset")):
            with self.assertRaises(ValueError):
                saver.new_map(name, preset, dry_run=True)
        self.assertFalse((ROOT / "map_factory/maps/editor_test_map").exists())

    def test_rejected_edits_leave_nothing_behind(self):
        for changes in ([{"op": "add", "layer": "objects", "id": "NO_SUCH_PART", "instance_id": "EdX_1", "x": 1, "y": 1}],
                        [{"op": "remove", "instance_id": "NoSuchBlock"}],
                        [{"op": "paint"}], []):
            with self.assertRaises(Exception):
                saver.save({"map_id": "hero_room_01", "changes": changes})


class EditorSceneTests(unittest.TestCase):
    @unittest.skipUnless(_godot(), "configured godot_executable is not installed here")
    def test_headless_editor(self):
        os.environ["ROOM_EDITOR_PYTHON"] = sys.executable
        code, output = run_godot("res://tools/verify_room_editor.gd")
        self.assertEqual(code, 0, output)
        self.assertIn("ROOM_EDITOR_OK", output)


if __name__ == "__main__":
    unittest.main()
