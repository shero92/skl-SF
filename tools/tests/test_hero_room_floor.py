"""TASK-0091: pure floor layout checks; never generate blueprint outputs."""

import importlib.util
import json
from collections import Counter
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "hero_room_blueprint", ROOT / "tools" / "build_hero_room_blueprint.py"
)
blueprint = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(blueprint)


class HeroRoomFloorTests(unittest.TestCase):
    def test_footprint_is_unchanged_and_fully_covered(self):
        expected_rows = (
            [[[0, 4], [11, 16]]]
            + [[[0, 16]] for _ in range(7)]
            + [[[1, 15]], [[6, 10]]]
        )
        self.assertEqual(blueprint.floor_footprint_rows(), expected_rows)
        expected_cells = {
            (x, y)
            for y, spans in enumerate(expected_rows)
            for start, end in spans
            for x in range(start, end + 1)
        }
        cells = blueprint.floor_layout()
        self.assertEqual(len(expected_cells), 150)
        self.assertEqual(len(cells), len(expected_cells))
        self.assertEqual(
            {(cell["x"], cell["y"]) for cell in cells}, expected_cells
        )

    def test_floor_uses_only_approved_v2_tiles(self):
        with (
            ROOT / "map_factory" / "metadata" / "environment_assets_v2.json"
        ).open(encoding="utf-8") as stream:
            assets = json.load(stream)["assets"]
        expected_ids = {f"G{i:02d}" for i in range(1, 13)}
        used_ids = {cell["id"] for cell in blueprint.floor_layout()}
        settings = blueprint.floor_settings()
        self.assertEqual(used_ids, expected_ids)
        self.assertEqual(set(settings["floor_ids"]), expected_ids)
        self.assertEqual(
            set(settings["floor_tile_style"]["tile_ids"]), expected_ids
        )
        for tile_id in used_ids:
            with self.subTest(tile_id=tile_id):
                self.assertIn(tile_id, assets)
                self.assertEqual(assets[tile_id]["approval_status"], "approved")
                self.assertEqual(assets[tile_id]["asset_role"], "floor_tile")

    def test_clean_tiles_dominate_and_accents_are_sparse(self):
        counts = Counter(cell["id"] for cell in blueprint.floor_layout())
        self.assertEqual(counts["G01"] + counts["G02"], 120)
        for i in range(3, 13):
            with self.subTest(tile_id=f"G{i:02d}"):
                self.assertEqual(counts[f"G{i:02d}"], 3)

    def test_layout_and_settings_are_deterministic_and_independent(self):
        first = blueprint.floor_layout()
        second = blueprint.floor_layout()
        self.assertEqual(first, second)
        first[0]["id"] = "F001"
        self.assertEqual(blueprint.floor_layout(), second)

        settings = blueprint.floor_settings()
        expected_settings = blueprint.floor_settings()
        self.assertEqual(settings, expected_settings)
        settings["floor_ids"].clear()
        settings["floor_tile_style"]["tile_ids"].clear()
        self.assertEqual(blueprint.floor_settings(), expected_settings)

        rows = blueprint.floor_footprint_rows()
        rows[0][0][0] = 99
        self.assertEqual(blueprint.floor_footprint_rows()[0][0], [0, 4])


if __name__ == "__main__":
    unittest.main()
