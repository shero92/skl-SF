"""free_transform (turn, resize, free position while keeping grid cells) and the room_design code API.

Execution provenance: Agent: claude (Claude Code); model: Fable 5.2.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[1]
ROOT = TOOLS.parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import map_factory_cli as cli
from room_design import Design
from art_reference_crop import crop_reference

RULES = {"rotation_safe": frozenset(), "scale_min": 0.1, "scale_max": 4.0}
UPRIGHT = {"id": "F01", "category": "furniture", "tags": []}


class FreeTransformTests(unittest.TestCase):
    def test_upright_piece_turns_only_with_free_transform(self):
        with self.assertRaises(ValueError):
            cli.validate_transform({"id": "F01", "rotation_degrees": 30}, UPRIGHT, RULES, "Bed")
        cli.validate_transform({"id": "F01", "rotation_degrees": 30, "free_transform": True}, UPRIGHT, RULES, "Bed")

    def test_flag_must_be_boolean_and_scale_limits_stay(self):
        with self.assertRaises(ValueError):
            cli.validate_transform({"id": "F01", "free_transform": "yes"}, UPRIGHT, RULES, "Bed")
        with self.assertRaises(ValueError):
            cli.validate_transform({"id": "F01", "scale": 9, "free_transform": True}, UPRIGHT, RULES, "Bed")

    def test_latest_room_validates_and_keeps_grid_cell_of_a_resized_part(self):
        latest = json.loads((ROOT / "map_factory/maps/hero_room_01/latest.json").read_text(encoding="utf-8"))
        rug = next(b for b in latest["ground_overlays"] if b["instance_id"] == "BedRug")
        self.assertTrue(rug["free_transform"])
        self.assertNotEqual(float(rug["scale"]), 1.0)
        self.assertEqual(rug["grid_placement"]["cell"], [2, 2])  # walking grid untouched
        cli.validate_room(latest, _catalog())


def _catalog():
    data = json.loads((ROOT / cli.CATALOG).read_text(encoding="utf-8"))
    records = data.get("assets", data) if isinstance(data, dict) else data
    return {r["id"]: r for r in (records.values() if isinstance(records, dict) else records)}


class DesignApiTests(unittest.TestCase):
    def test_place_transform_remove_build_one_patch(self):
        d = Design("hero_room_01")
        d.place("P05", "TestFern", 600, 400, scale=0.7, rotation=20, flip=True)
        d.transform("BedRug", scale=1.5).remove("CrateF12")
        add, update, remove = d.changes
        self.assertEqual(add["block"]["rotation_degrees"], 20.0)
        self.assertTrue(add["block"]["free_transform"] and add["block"]["flip_h"])
        self.assertEqual(update["set"], {"scale": 1.5, "free_transform": True})
        self.assertEqual(remove, {"op": "remove_block", "instance_id": "CrateF12"})
        with self.assertRaises(ValueError):
            d.transform("NoSuchBlock", x=1)

    def test_reference_crop_writes_target_and_comparison(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            Image.new("RGB", (40, 30), (10, 20, 30)).save(root / "t.png")
            Image.new("RGB", (40, 30), (200, 20, 30)).save(root / "g.png")
            out = crop_reference("ART-9999", (5, 5, 25, 15), Path("t.png"), Path("g.png"), root=root)
            names = list(out)
            self.assertTrue(names[0].endswith("ART-9999_target.png") and names[1].endswith("ART-9999_compare.png"))
            for name, size in zip(names, [(20, 10), (48, 10)]):
                with Image.open(root / name) as image:
                    self.assertEqual(image.size, size)


if __name__ == "__main__":
    unittest.main()
