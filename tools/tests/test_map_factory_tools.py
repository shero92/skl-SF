"""Tests for the Map Factory data tools: audit, version diff, reference compare, wall and terrace generators.

Execution provenance: Agent: claude (Claude Code); model: Sonnet 5.5.
"""
from __future__ import annotations

import copy
from pathlib import Path
import sys
import tempfile
import unittest

from PIL import Image, ImageDraw

TOOLS = Path(__file__).resolve().parents[1]
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import map_audit
import map_reference_compare
import map_terrace_edge
import map_version_diff
import map_wall_generator
from map_data import load_catalog, load_map

CATALOG = {"A": {"asset_id": "A", "footprint_tiles_x": 2, "footprint_tiles_y": 2},
           "B": {"asset_id": "B", "footprint_tiles_x": 1, "footprint_tiles_y": 1},
           "UNUSED": {"asset_id": "UNUSED"}}


def small_map() -> dict:
    return {"tile_size": 64, "ground_offset": [10, 20], "version": 1,
            "floor_footprint": {"row_spans": [[[0, 2]], [[0, 2]], [[1, 1]]]},
            "objects": [{"id": "A", "instance_id": "a1", "x": 100, "y": 200, "scale": 1.0},
                        {"id": "B", "instance_id": "b1", "x": 110, "y": 190, "scale": 1.0}],
            "ground_overlays": [{"id": "B", "instance_id": "b1", "x": 5, "y": 5}]}


class AuditTests(unittest.TestCase):
    def test_reports_problems_and_counts(self):
        data = small_map()
        data["objects"].append({"id": "ZZZ", "x": 1, "y": 1})
        report = map_audit.audit(data, CATALOG)
        problems = report["problems"]
        self.assertEqual(problems["duplicate_instance_ids"], ["b1"])
        self.assertEqual(len(problems["missing_instance_ids"]), 1)
        self.assertEqual(problems["unknown_assets"][0]["asset"], "ZZZ")
        self.assertTrue(problems["overlaps"], "overlapping furniture footprints are reported")
        self.assertEqual(report["unused_registered_assets"], ["UNUSED"])
        self.assertEqual(report["asset_counts"]["B"], 2)

    def test_directional_variants_resolve_to_their_base_asset(self):
        data = small_map()
        data["objects"] = [{"id": "A_south", "instance_id": "v1", "x": 0, "y": 100, "scale": 1.0}]
        data["ground_overlays"] = []
        report = map_audit.audit(data, CATALOG)
        self.assertEqual(report["problems"]["unknown_assets"], [])
        self.assertEqual(report["asset_counts"], {"A": 1})

    def test_real_latest_map_loads(self):
        report = map_audit.audit(load_map("hero_room_01"), load_catalog())
        self.assertGreater(report["instances"], 100)
        self.assertEqual(report["problems"]["duplicate_instance_ids"], [])
        self.assertEqual(report["problems"]["unknown_assets"], [], "directional variants are not unknown")


class VersionDiffTests(unittest.TestCase):
    def test_added_removed_moved_changed(self):
        old = small_map()
        old["ground_overlays"] = []
        new = copy.deepcopy(old)
        new["objects"][0]["x"] += 30
        new["objects"][1]["scale"] = 2.0
        new["objects"].append({"id": "B", "instance_id": "new1", "x": 0, "y": 0})
        new["objects"] = [o for o in new["objects"] if o["instance_id"] != "zzz"]
        report = map_version_diff.diff(old, new)
        self.assertEqual(report["added"], ["new1"])
        self.assertEqual(report["moved"][0]["instance_id"], "a1")
        self.assertEqual(report["changed"][0]["fields"]["scale"], [1.0, 2.0])
        reverse = map_version_diff.diff(new, old)
        self.assertEqual(reverse["removed"], ["new1"])

    def test_real_versions(self):
        report = map_version_diff.diff(load_map("hero_room_01", 12), load_map("hero_room_01", 13))
        self.assertGreater(report["summary"]["added"], 0)


class ReferenceCompareTests(unittest.TestCase):
    def _image(self, colour, accent=None):
        image = Image.new("RGB", tuple(map_reference_compare.CANVAS), colour)
        if accent:
            ImageDraw.Draw(image).rectangle([200, 400, 600, 700], fill=accent)
        return image

    def test_identical_matches_and_different_does_not(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp, "a.png"), Path(tmp, "b.png")
            self._image((200, 180, 120), (30, 60, 160)).save(a)
            self._image((200, 180, 120), (30, 60, 160)).save(b)
            same = map_reference_compare.compare(a, b)
            self.assertTrue(all(z["status_hint"] == "matched" for z in same["zones"].values()))
            self.assertFalse(same["visual_approval"])
            self._image((20, 40, 160)).save(b)
            different = map_reference_compare.compare(a, b)
            self.assertNotEqual(different["zones"]["floor"]["status_hint"], "matched")
            out = Path(tmp, "out")
            self.assertEqual(map_reference_compare.main(["--render", str(a), "--target", str(b), "--out-dir", str(out)]), 0)
            self.assertTrue((out / "compare.png").exists() and (out / "compare.json").exists())

    def test_wrong_size_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp, "a.png")
            Image.new("RGB", (100, 100)).save(a)
            with self.assertRaises(ValueError):
                map_reference_compare.compare(a, a)


class WallGeneratorTests(unittest.TestCase):
    BLUEPRINT = {"seed": 7, "step": 64, "damage": 0.4, "inside": "right",
                 "pieces": {"straight": ["W01", "W02"], "broken": ["W03", "W10"],
                            "corner_outer": "W09", "corner_inner": "W08", "cap": "W07"},
                 "path": [[0, 0], [256, 0], [256, 192]]}

    def test_deterministic_and_connected(self):
        first = map_wall_generator.generate(self.BLUEPRINT)
        second = map_wall_generator.generate(copy.deepcopy(self.BLUEPRINT))
        self.assertEqual(first, second)
        positions = [(p["x"], p["y"]) for p in first]
        self.assertEqual(len(positions), len(set(positions)), "no stacked placements")
        self.assertEqual(len({p["instance_id"] for p in first}), len(first))
        self.assertEqual([p["wall_kind"] for p in first].count("corner"), 1, "one corner at the turn")
        self.assertEqual(first[-1]["wall_kind"], "cap")
        for a, b in zip(first, first[1:]):
            gap = ((a["x"] - b["x"]) ** 2 + (a["y"] - b["y"]) ** 2) ** 0.5
            self.assertLessEqual(gap, 64.5, "the run has no holes")

    def test_corner_type_depends_on_turn_side(self):
        right = map_wall_generator.generate(self.BLUEPRINT)
        flipped = map_wall_generator.generate({**self.BLUEPRINT, "inside": "left"})
        corner = lambda placements: next(p["id"] for p in placements if p["wall_kind"] == "corner")
        self.assertNotEqual(corner(right), corner(flipped))

    def test_different_seed_changes_choices(self):
        other = map_wall_generator.generate({**self.BLUEPRINT, "seed": 99})
        self.assertNotEqual([p["id"] for p in other], [p["id"] for p in map_wall_generator.generate(self.BLUEPRINT)])

    def test_short_path_rejected(self):
        with self.assertRaises(ValueError):
            map_wall_generator.generate({**self.BLUEPRINT, "path": [[0, 0]]})


class TerraceEdgeTests(unittest.TestCase):
    def test_boundary_and_notches(self):
        data = small_map()
        cells = map_terrace_edge.floor_cells(data["floor_footprint"])
        self.assertEqual(len(cells), 7)
        edges = map_terrace_edge.boundary(cells)
        self.assertIn((1, 2, "south"), edges)
        self.assertNotIn((1, 1, "south"), edges)
        placements = map_terrace_edge.edge_notches(data, ["R1", "R2"], seed=3, density=1.0)
        self.assertEqual(len(placements), len(edges))
        self.assertEqual(placements, map_terrace_edge.edge_notches(data, ["R1", "R2"], seed=3, density=1.0))
        for item in placements:
            col, row = item["cell"]
            dx, dy = map_terrace_edge.DIRECTIONS[item["edge_side"]]
            if dx:
                self.assertEqual(int((item["x"] - 10) // 64), col + dx, "placement is in the neighbouring empty cell")
            else:
                self.assertEqual(int((item["y"] - 20) // 64), row + dy, "placement is in the neighbouring empty cell")
            self.assertNotIn((col + dx, row + dy), cells)

    def test_real_map_edge_count(self):
        placements = map_terrace_edge.edge_notches(load_map("hero_room_01"), ["R1"], seed=1, density=1.0)
        self.assertGreater(len(placements), 20)


if __name__ == "__main__":
    unittest.main()
