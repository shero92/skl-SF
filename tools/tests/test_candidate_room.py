"""Review-only Hero Room candidates: cell -> pixel placement, regions and reference comparison."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

from PIL import Image, ImageDraw

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import candidate_room as cr  # noqa: E402


def fake_repo(root: Path):
    (root / "map_factory/maps/demo/versions").mkdir(parents=True)
    (root / "map_factory/maps/demo/versions/v0003.json").write_text(json.dumps(
        {"tile_size": 64, "ground_offset": [226, 225], "canvas_size": [400, 300]}))
    (root / ".agents/graphics/deliveries/ART-0001").mkdir(parents=True)
    (root / ".agents/graphics/deliveries/ART-0001/manifest.json").write_text(json.dumps({"files": [
        {"path": ".agents/graphics/deliveries/ART-0001/wall_west.png", "sha256": "a" * 64, "pixel_size": [115, 286],
         "anchors_px": {"foot_center_front": [44.75, 186.0]}, "shadow": ".agents/graphics/deliveries/ART-0001/wall_west_shadow.png"},
        {"path": ".agents/graphics/deliveries/ART-0001/edge.png", "sha256": "b" * 64, "pixel_size": [142, 155],
         "anchors_px": {"tile_top_left": [10.0, 10.0]}}]}))
    layout = root / "layout.json"
    layout.write_text(json.dumps({"candidate_id": "demo_c1", "base": {"map_id": "demo", "version": 3},
        "hide_instances": ["OldWall"], "hide_floor_cells": [[3, 9]],
        "pieces": [{"art": "ART-0001", "file": "edge", "anchor": "tile_top_left", "point": "top_left", "layer": "ground", "cells": [[3, 9]]},
                   {"art": "ART-0001", "file": "wall_west", "anchor": "foot_center_front", "point": "left_center", "layer": "walls",
                    "cells": [[0, 3], [1, 7]]}]}))
    return layout


class Resolve(unittest.TestCase):
    def test_cells_become_grid_pixels_with_measured_anchors(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = cr.resolve(fake_repo(Path(tmp)), Path(tmp))
            self.assertEqual(r["base_path"], "res://map_factory/maps/demo/versions/v0003.json")
            by = {p["name"]: p for p in r["placements"]}
            self.assertEqual(by["edge_3_9"]["position"], [226 + 3 * 64, 225 + 9 * 64])
            self.assertEqual(by["wall_west_0_3"]["position"], [226, 225 + 3 * 64 + 32])
            self.assertEqual(by["wall_west_1_7"]["position"], [226 + 64, 225 + 7 * 64 + 32])
            self.assertEqual(by["wall_west_0_3"]["anchor_px"], [44.75, 186.0])
            self.assertTrue(by["wall_west_0_3"]["shadow"].endswith("wall_west_shadow.png"))
            self.assertEqual(by["edge_3_9"]["shadow"], "")
            self.assertEqual(r["hide_instances"], ["OldWall"])

    def test_unknown_piece_or_layer_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            layout = fake_repo(Path(tmp))
            data = json.loads(layout.read_text())
            data["pieces"][0]["file"] = "missing"
            layout.write_text(json.dumps(data))
            with self.assertRaises(ValueError):
                cr.resolve(layout, Path(tmp))
            data["pieces"][0].update(file="edge", layer="sky")
            layout.write_text(json.dumps(data))
            with self.assertRaises(ValueError):
                cr.resolve(layout, Path(tmp))

    def test_repository_candidate_layout_resolves(self):
        layout = TOOLS.parent / "map_factory/candidates/hero_room_01_blender_v1.json"
        r = cr.resolve(layout)
        self.assertEqual(len(r["placements"]), 27)
        self.assertTrue(all(Path(p["texture"]).is_file() for p in r["placements"]))


class Compare(unittest.TestCase):
    def test_closer_candidate_scores_lower_and_sheet_is_written(self):
        with tempfile.TemporaryDirectory() as tmp:
            t = Path(tmp)
            ref = Image.new("RGB", (400, 300), (200, 160, 100))
            base = ref.copy()
            ImageDraw.Draw(base).rectangle((100, 100, 200, 200), fill=(0, 0, 0))
            cand = ref.copy()
            ImageDraw.Draw(cand).rectangle((100, 100, 200, 200), fill=(190, 150, 95))
            for name, im in (("ref", ref), ("base", base), ("cand", cand)):
                im.save(t / f"{name}.png")
            resolved = {"candidate_id": "c1", "base_path": "res://x/v0003.json",
                        "placements": [{"layer": "walls", "position": [100, 100], "anchor_px": [0, 0], "pixel_size": [100, 100]}]}
            m = cr.compare(t / "base.png", t / "cand.png", t / "ref.png", resolved, t / "sheet.png")
            self.assertLess(m["regions"]["walls"]["candidate"], m["regions"]["walls"]["base"])
            self.assertLess(m["whole"]["candidate"], m["whole"]["base"])
            self.assertEqual(Image.open(t / "sheet.png").size, (200 * 3 + 40, 150 + 40))


if __name__ == "__main__":
    unittest.main()
