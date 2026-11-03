"""Read-only geometry checks for TASK-0093.

Execution tool: Codex. Model: GPT-6.
Only layout helpers and resolvers are called; no writers are invoked.
"""

import itertools
import json
import unittest

from tools import build_hero_room_blueprint as blueprint


class EnclosingWallTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = blueprint.load_catalog()
        registry_path = (
            blueprint.ROOT / "map_factory" / "metadata"
            / ("environment_assets_" + "v2" + ".json")
        )
        with registry_path.open(encoding="utf-8") as stream:
            cls.assets = json.load(stream)["assets"]
        cls.entries = blueprint.layout_entries()
        cls.walls = [
            entry for entry in cls.entries
            if entry["id"].startswith("W")
        ]

    def test_perimeter_coverage_and_exact_openings(self):
        floor = {
            (x, y)
            for y, spans in enumerate(blueprint.floor_footprint_rows())
            for start, stop in spans
            for x in range(start, stop + 1)
        }
        boundary = {
            (x, y) for x, y in floor
            if any(
                (x + dx, y + dy) not in floor
                for dx in (-1, 0, 1)
                for dy in (-1, 0, 1)
                if dx or dy
            )
        }
        arch = {(x, 1) for x in range(5, 11)}
        stairs = {(7, 9), (8, 9), (9, 9)}
        self.assertEqual(blueprint.wall_gaps(), {
            "arch": arch, "stairs": stairs,
        })
        cells = [tuple(entry["perimeter_cell"]) for entry in self.walls]
        self.assertEqual(len(cells), len(set(cells)))
        self.assertEqual(set(cells), boundary - arch - stairs)
        self.assertEqual(boundary - set(cells), arch | stairs)
        self.assertEqual(blueprint.wall_perimeter(), boundary)

    def test_wall_palette_and_front_run(self):
        ids = {entry["id"] for entry in self.walls}
        self.assertTrue(
            {f"W{i:02d}" for i in range(1, 15)} <= ids
        )
        front = [
            entry for entry in self.walls
            if entry["instance_id"].startswith("FrontLowWall")
        ]
        self.assertEqual(len(front), 9)
        self.assertTrue(all(entry["id"] == "W10" for entry in front))
        by_cell = {
            tuple(entry["perimeter_cell"]): entry["id"]
            for entry in self.walls
        }
        self.assertEqual(by_cell[(4, 0)], "W13")
        self.assertEqual(by_cell[(11, 0)], "W14")
        self.assertEqual(by_cell[(6, 9)], "W11")
        self.assertEqual(by_cell[(10, 9)], "W12")
        for entry in self.walls:
            with self.subTest(instance=entry["instance_id"]):
                self.assertIn(entry["id"], self.assets)
                self.assertEqual(
                    self.assets[entry["id"]]["approval_status"], "approved"
                )
                self.assertEqual(entry["layer"], "back_objects")
                self.assertEqual(entry.get("rotation_degrees", 0), 0)
                self.assertNotIn("facing", entry)

    def test_registered_wall_footprints_do_not_overlap(self):
        blocks, _ = blueprint.resolve_entries(self.catalog, self.walls)
        boxes = []
        by_instance = {entry["instance_id"]: entry for entry in self.walls}
        for block in blocks:
            entry = by_instance[block["instance_id"]]
            asset = blueprint.record(self.catalog, block["id"])
            contract = asset.get("placement_contract") or {}
            width, depth = contract.get("footprint_cells", (1, 1))
            scale = block["scale"]
            self.assertGreater(scale, 0)
            self.assertLessEqual(scale, 1)
            width *= blueprint.TILE * scale
            depth *= blueprint.TILE * scale
            x, y = block["x"], block["y"]
            box = (x - width / 2, y - depth, x + width / 2, y)
            cell_x, cell_y = entry["perimeter_cell"]
            left = blueprint.GROUND_OFFSET[0] + cell_x * blueprint.TILE
            top = blueprint.GROUND_OFFSET[1] + cell_y * blueprint.TILE
            with self.subTest(instance=block["instance_id"]):
                self.assertGreaterEqual(box[0], left - 1e-6)
                self.assertGreaterEqual(box[1], top - 1e-6)
                self.assertLessEqual(box[2], left + blueprint.TILE + 1e-6)
                self.assertLessEqual(box[3], top + blueprint.TILE + 1e-6)
                self.assertLessEqual(
                    asset["pixel_size"][0] * scale, blueprint.TILE + 1e-6
                )
            boxes.append((block["instance_id"], box))
        for (first, a), (second, b) in itertools.combinations(boxes, 2):
            with self.subTest(first=first, second=second):
                overlap_x = min(a[2], b[2]) - max(a[0], b[0])
                overlap_y = min(a[3], b[3]) - max(a[1], b[1])
                self.assertTrue(overlap_x <= 1e-6 or overlap_y <= 1e-6)

    def test_layout_is_fresh_and_mount_hosts_survive(self):
        again = blueprint.layout_entries()
        self.assertEqual(self.entries, again)
        hosts = {entry["instance_id"] for entry in again}
        self.assertEqual(len(hosts), len(again))
        for entry in again:
            if "mount_on" in entry:
                self.assertIn(entry["mount_on"], hosts)
        walls = blueprint.perimeter_wall_entries()
        walls[0]["shadow"]["opacity"] = 0
        self.assertNotEqual(walls, blueprint.perimeter_wall_entries())


if __name__ == "__main__":
    unittest.main()
