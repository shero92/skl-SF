"""Directional furniture regression coverage.

Execution tool: codex. Model: GPT-6.
"""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import build_hero_room_blueprint as blueprint
from map_factory_orientation import (
    FACINGS, furniture_direction_ids, resolve_orientation,
)


class DirectionalFurnitureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = blueprint.load_catalog()
        cls.assets = {
            asset["id"]: asset for asset in cls.catalog["assets"]
        }

    def test_all_furniture_has_four_existing_canonical_images(self):
        entries = [
            entry for entry in blueprint.layout_entries()
            if blueprint.is_furniture(entry)
        ]
        self.assertEqual(
            {entry["id"] for entry in entries},
            {"F01", "F05", "F06", "F07", "F08", "F09", "F10", "F11", "F12"},
        )
        for entry in entries:
            images = []
            for facing in FACINGS:
                with self.subTest(instance=entry["instance_id"], facing=facing):
                    oriented = dict(entry, facing=facing)
                    blocks, _ = blueprint.resolve_entries(self.catalog, [oriented])
                    block = blocks[0]
                    self.assertEqual(block["facing"], facing)
                    self.assertEqual(block["orientation_mode"], "variants")
                    variants = block["direction_asset_ids"]
                    self.assertEqual(set(variants), set(FACINGS))
                    self.assertEqual(len(set(variants.values())), 4)
                    # The bed uses plain ids (F03/F04/F01/F02); others use X_dir.
                    self.assertTrue(all(value in self.assets for value in variants.values()))
                    self.assertEqual(block["id"], variants[facing])
                    resolved = resolve_orientation(block, self.assets)
                    self.assertEqual(resolved["resolved_asset_id"], block["id"])
                    self.assertEqual(block.get("rotation_degrees", 0), 0)
                    path = blueprint.sidecar_png(self.catalog, block["id"])
                    self.assertTrue(path.is_file(), str(path))
                    images.append(path.resolve())
            self.assertEqual(len(set(images)), 4)

    def test_bed_registry_without_aliases_retains_legacy_metadata(self):
        bed_ids = dict(zip(FACINGS, ("F03", "F04", "F01", "F02")))
        legacy = {
            "assets": [
                {
                    "id": asset_id,
                    "category": "furniture",
                    "origin": [96, 256],
                    "placement_contract": {
                        "footprint_cells": (
                            [4, 3] if facing in ("east", "west") else [3, 4]
                        ),
                    },
                }
                for facing, asset_id in bed_ids.items()
            ],
        }
        registry = {
            "assets": [
                {
                    "id": "F01@" + facing,
                    "category": "registry_" + facing,
                }
                for facing in FACINGS
            ],
        }
        original_legacy = copy.deepcopy(legacy)
        original_registry = copy.deepcopy(registry)
        merged = blueprint.merge_directional_catalog(legacy, registry)
        assets = {asset["id"]: asset for asset in merged["assets"]}
        expected = {facing: "F01@" + facing for facing in FACINGS}
        for facing, legacy_id in bed_ids.items():
            with self.subTest(facing=facing):
                canonical_id = expected[facing]
                self.assertIn(legacy_id, assets[canonical_id]["legacy_aliases"])
                self.assertEqual(assets[canonical_id]["origin"], [96, 256])
                self.assertEqual(assets[canonical_id]["category"], "furniture")
                self.assertEqual(
                    furniture_direction_ids(legacy_id, assets), expected,
                )
                self.assertEqual(
                    furniture_direction_ids(canonical_id, assets), expected,
                )
                block = {
                    "id": legacy_id,
                    "facing": facing,
                    "orientation_mode": "variants",
                    "direction_asset_ids": bed_ids,
                }
                self.assertEqual(
                    resolve_orientation(block, assets)["resolved_asset_id"],
                    canonical_id,
                )
                entry = {
                    "id": canonical_id, "facing": facing,
                }
                self.assertEqual(
                    blueprint.entry_footprint(merged, entry),
                    [4, 3] if facing in ("east", "west") else [3, 4],
                )
        self.assertEqual(legacy, original_legacy)
        self.assertEqual(registry, original_registry)

    def test_bed_legacy_group_and_existing_variant_maps(self):
        bed = furniture_direction_ids("F01", self.assets)
        expected = dict(zip(FACINGS, ("F03", "F04", "F01", "F02")))
        for facing, legacy_id in expected.items():
            self.assertEqual(bed[facing].split("@")[0], legacy_id)
        for asset_id in ("F01", "F05", "F09"):
            legacy = self.assets[asset_id].get("direction_asset_ids")
            if legacy:
                for facing in FACINGS:
                    block = {
                        "id": asset_id, "facing": facing,
                        "orientation_mode": "variants",
                        "direction_asset_ids": legacy,
                    }
                    resolved = resolve_orientation(block, self.assets)
                    self.assertEqual(
                        resolved["resolved_asset_id"],
                        furniture_direction_ids(asset_id, self.assets)[facing],
                    )

    def test_footprint_and_anchor_follow_facing(self):
        for facing in FACINGS:
            entry = dict(
                kind="grid", id="F01", facing=facing, cell=(2, 1),
                layer="objects", instance_id="Bed",
            )
            expected = [4, 3] if facing in ("east", "west") else [3, 4]
            with self.subTest(facing=facing):
                self.assertEqual(
                    blueprint.entry_footprint(self.catalog, entry), expected,
                )
                blocks, _ = blueprint.resolve_entries(self.catalog, [entry])
                self.assertEqual(
                    [blocks[0]["x"], blocks[0]["y"]],
                    [
                        blueprint.GROUND_OFFSET[0] + (2 + expected[0] / 2) * blueprint.TILE,
                        blueprint.GROUND_OFFSET[1] + (1 + expected[1]) * blueprint.TILE,
                    ],
                )

    def test_room_facings(self):
        entries = {
            entry["instance_id"]: entry for entry in blueprint.layout_entries()
        }
        self.assertEqual(entries["RightBookcase"]["facing"], "north")
        self.assertEqual(entries["TableBenchLeft"]["facing"], "south")
        self.assertEqual(entries["TableBenchRight"]["facing"], "south")
        left = blueprint.entry_footprint(self.catalog, entries["TableBenchLeft"])
        right = blueprint.entry_footprint(self.catalog, entries["TableBenchRight"])
        self.assertEqual(left, right)

    def test_missing_direction_and_rotation_are_rejected(self):
        variants = furniture_direction_ids("F05", self.assets)
        block = {
            "id": "F05", "facing": "south", "orientation_mode": "variants",
            "direction_asset_ids": variants,
        }
        missing = copy.deepcopy(block)
        missing["direction_asset_ids"]["south"] = "missing@south"
        with self.assertRaises(ValueError):
            resolve_orientation(missing, self.assets)
        incomplete = copy.deepcopy(block)
        del incomplete["direction_asset_ids"]["north"]
        with self.assertRaises(ValueError):
            resolve_orientation(incomplete, self.assets)
        duplicate = copy.deepcopy(block)
        duplicate["direction_asset_ids"]["north"] = variants["south"]
        with self.assertRaises(ValueError):
            resolve_orientation(duplicate, self.assets)
        with self.assertRaises(ValueError):
            resolve_orientation(dict(block, rotation_degrees=90), self.assets)

    def test_resolution_does_not_mutate_inputs(self):
        entries = blueprint.layout_entries()
        original_entries = copy.deepcopy(entries)
        original_catalog = copy.deepcopy(self.catalog)
        first = blueprint.resolve_entries(self.catalog, entries)
        self.assertEqual(first, blueprint.resolve_entries(self.catalog, entries))
        self.assertEqual(entries, original_entries)
        self.assertEqual(self.catalog, original_catalog)


if __name__ == "__main__":
    unittest.main()
