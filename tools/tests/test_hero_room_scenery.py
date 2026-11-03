"""Pure layout checks for TASK-0092; never invoke blueprint writers."""

import json
import re
import unittest

from tools import build_hero_room_blueprint as blueprint


class HeroRoomSceneryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        registry_path = (
            blueprint.ROOT / "map_factory" / "metadata"
            / "environment_assets_v2.json"
        )
        with registry_path.open(encoding="utf-8") as stream:
            cls.assets = json.load(stream)["assets"]
        cls.entries = blueprint.layout_entries()

    def test_every_layout_asset_has_an_approved_v2_registry_key(self):
        self.assertTrue(self.entries)
        for entry in self.entries:
            with self.subTest(instance=entry["instance_id"]):
                asset_id = entry["id"]
                self.assertIsNone(
                    re.match(r"^(?:E\d+|F00\d+|S0\d+)$", asset_id)
                )
                # Furniture uses a base ID plus an existing facing contract.
                key = asset_id
                if key not in self.assets:
                    key = f"{asset_id}@{entry.get('facing', 'north')}"
                self.assertIn(key, self.assets)
                self.assertEqual(self.assets[key]["registry_key"], key)
                self.assertEqual(
                    self.assets[key]["approval_status"], "approved"
                )

    def test_scenery_categories_match_approved_registry(self):
        expected = {
            "DistantIsleLeft": "sea_stack_island_small",
            "DistantIsleRight": "sea_stack_island_medium",
            "DistantIsleArch": "distant_rock_arch_formation",
            "LeftIslandDistantExtra": "sea_stack_island_small",
            "RightIslandDistantExtra": "sea_stack_island_medium",
            "SeaStackLeft": "sea_stack_island_small",
            "SeaStackRight": "sea_stack_island_medium",
            "TerraceRockFrontLeft": "near_cliff_rock_segment",
            "TerraceRockFrontRight": "near_cliff_rock_segment",
        }
        scenery = {
            entry["instance_id"]: entry
            for entry in self.entries
            if entry["layer"] in ("background_objects", "front_objects")
        }
        self.assertEqual(set(scenery), set(expected))
        for instance_id, category in expected.items():
            with self.subTest(instance=instance_id):
                entry = scenery[instance_id]
                self.assertEqual(
                    self.assets[entry["id"]]["category"], category
                )

    def test_full_cliff_boxes_clear_lower_wall_boxes(self):
        catalog = blueprint.load_catalog()
        entries = [
            entry for entry in self.entries
            if entry["instance_id"].startswith("FrontLowWall")
            or entry["instance_id"].startswith("TerraceRockFront")
        ]
        blocks, positions = blueprint.resolve_entries(catalog, entries)
        cliffs = [
            entry for entry in entries
            if entry["instance_id"].startswith("TerraceRockFront")
        ]
        walls = [entry for entry in entries if entry["id"] == "W10"]
        self.assertEqual(len(cliffs), 2)
        self.assertEqual(len(walls), 9)

        def bounds(entry, full_canvas=False):
            asset = blueprint.record(catalog, entry["id"])
            measured = blueprint.measurement(catalog, entry["id"])
            ox, oy = asset["origin"]
            if full_canvas:
                width, height = measured["size"]
                left, top = 0, 0
            else:
                left, top, width, height = measured["content"]
            self.assertGreater(width, 0)
            self.assertGreater(height, 0)
            scale = entry.get("scale", 1.0)
            x, y = positions[entry["instance_id"]]
            x += scale * (left - ox)
            y += scale * (top - oy)
            return x, y, x + scale * width, y + scale * height

        for cliff in cliffs:
            cliff_box = bounds(cliff, full_canvas=True)
            self.assertGreaterEqual(cliff_box[0], 0)
            self.assertLessEqual(cliff_box[2], blueprint.CANVAS[0])
            self.assertLessEqual(cliff_box[3], blueprint.CANVAS[1])
            for wall in walls:
                wall_box = bounds(wall)
                with self.subTest(
                    cliff=cliff["instance_id"], wall=wall["instance_id"]
                ):
                    self.assertGreaterEqual(cliff_box[1], wall_box[3])
        for block in blocks:
            if block["instance_id"].startswith("TerraceRockFront"):
                self.assertEqual(block["render_layer"], "walls")

    def test_layout_is_deterministic_and_returns_fresh_entries(self):
        again = blueprint.layout_entries()
        self.assertEqual(self.entries, again)
        again[0]["id"] = "changed"
        self.assertNotEqual(self.entries[0]["id"], again[0]["id"])


if __name__ == "__main__":
    unittest.main()
