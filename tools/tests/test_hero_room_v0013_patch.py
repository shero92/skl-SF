"""Read-only acceptance checks for the version 13 room patch.

Agent: codex. Model: GPT-6. Tests are supplied for worker execution.
"""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import build_hero_room_blueprint as blueprint


class HeroRoomV0013PatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = blueprint.load_catalog()
        cls.assets = {item["id"]: item for item in cls.catalog["assets"]}
        registry_path = blueprint.CATALOG_PATH.with_name(
            "environment_" + "assets_v2" + ".json"
        )
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        registered = registry.get("assets", registry.get("items", []))
        if isinstance(registered, dict):
            registered = [
                dict(value, id=key) for key, value in registered.items()
            ]
        cls.registered = {
            item.get("id", item.get("key")): item for item in registered
        }
        cls.manifest = blueprint.build_patch(13)
        cls.blocks = [
            change["block"] for change in cls.manifest["changes"]
            if change["op"] == "add_block"
        ]
        cls.properties = {
            change["key"]: change["value"]
            for change in cls.manifest["changes"]
            if change["op"] == "set_property"
        }

    def assert_v2(self, asset_id):
        # Legacy directional ids (F08_north) map to v2 keys (F08@north).
        aliases = json.loads(
            (blueprint.ROOT / "map_factory" / "metadata"
             / "environment_assets_v2.json").read_text(encoding="utf-8")
        ).get("legacy_aliases", {})
        v2_key = aliases.get(asset_id, asset_id)
        if asset_id not in self.registered and v2_key not in self.registered:
            # Plain directional ids (bed F01-F04) are registered as ID@facing.
            prefixed = [k for k in self.registered if k.startswith(asset_id + "@")]
            self.assertTrue(prefixed, asset_id)
            v2_key = prefixed[0]
        return self.registered.get(asset_id) or self.registered[v2_key]

    def test_parent_and_complete_replacement(self):
        latest = json.loads(blueprint.LATEST.read_text(encoding="utf-8"))
        self.assertEqual(self.manifest["base_version"], 12)
        self.assertEqual(self.manifest["base_sha256"],
                         blueprint.digest_json(latest))
        expected = {
            block["instance_id"]
            for layer in (
                "background_objects", "ground_overlays", "back_objects",
                "objects", "front_objects",
            )
            for block in latest.get(layer, [])
        }
        removed = [
            change["instance_id"] for change in self.manifest["changes"]
            if change["op"] == "remove_block"
        ]
        self.assertEqual(set(removed), expected)
        self.assertEqual(len(removed), len(expected))
        names = [block["instance_id"] for block in self.blocks]
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(
            set(names),
            {entry["instance_id"] for entry in blueprint.layout_entries()},
        )
        self.assertEqual(self.properties["visual_qa"]["status"], "needs_review")

    def test_v2_ids_and_seventy_distinct_approved_pngs(self):
        used = {block["id"] for block in self.blocks}
        used.update(self.properties["floor_ids"])
        used.update(
            change["id"] for change in self.manifest["changes"]
            if change["op"] == "set_tile" and change["id"] is not None
        )
        used.update(self.properties["floor_tile_style"]["tile_ids"])
        used.update(self.properties["floor_art"]["ids"])
        textures = set()
        for asset_id in used:
            with self.subTest(asset_id=asset_id):
                registered = self.assert_v2(asset_id)
                asset = self.assets[asset_id]
                # Registration establishes v2 identity. Delivery status is
                # required in the placement catalog; registry records may omit
                # it. Reject an explicit unready registry status as well.
                # Room visual approval remains a separate needs_review gate.
                self.assertIn(asset.get("status"), ("ready", "approved"))
                if "status" in registered:
                    self.assertIn(registered["status"], ("ready", "approved"))
                texture = blueprint.sidecar_png(self.catalog, asset_id)
                self.assertTrue(texture.is_file())
                self.assertEqual(texture.suffix.lower(), ".png")
                textures.add(texture.resolve())
        self.assertGreaterEqual(len(textures), 60)

    def test_floor_is_g_only_and_covers_footprint(self):
        tiles = [
            change for change in self.manifest["changes"]
            if change["op"] == "set_tile" and change["id"] is not None
        ]
        self.assertEqual(
            {(tile["x"], tile["y"]) for tile in tiles},
            {(tile["x"], tile["y"]) for tile in blueprint.floor_layout()},
        )
        self.assertEqual(len(tiles), len(blueprint.floor_layout()))
        ids = set(self.properties["floor_ids"])
        ids.update(tile["id"] for tile in tiles)
        ids.update(self.properties["floor_tile_style"]["tile_ids"])
        for asset_id in ids:
            self.assert_v2(asset_id)
            self.assertTrue(asset_id.split("@", 1)[0].startswith("G"))
            self.assertEqual(self.assets[asset_id]["category"], "floors")

    def test_perimeter_lanterns_and_banners(self):
        entries = blueprint.layout_entries()
        walls = [
            entry for entry in entries if "perimeter_cell" in entry
        ]
        self.assertEqual(
            {tuple(entry["perimeter_cell"]) for entry in walls},
            blueprint.wall_perimeter()
            - set().union(*blueprint.wall_gaps().values()),
        )
        blocks = {block["instance_id"]: block for block in self.blocks}
        for wall in walls:
            self.assertIn(wall["instance_id"], blocks)
        lanterns = [
            block for block in self.blocks
            if block["id"].split("@", 1)[0] in ("L01", "L02", "L04")
        ]
        banners = [
            block for block in self.blocks
            if block["id"].split("@", 1)[0] in ("D04", "D05")
        ]
        self.assertGreaterEqual(len(lanterns), 6)
        self.assertGreaterEqual(len(banners), 4)
        for block in lanterns + banners:
            self.assertIn(block["mount_on"], blocks)

    def test_furniture_declares_four_directions(self):
        furniture = [
            block for block in self.blocks if blueprint.is_furniture(block)
        ]
        self.assertTrue(furniture)
        for block in furniture:
            with self.subTest(instance=block["instance_id"]):
                self.assertEqual(block["orientation_mode"], "variants")
                variants = block["direction_asset_ids"]
                self.assertEqual(set(variants),
                                 {"north", "east", "south", "west"})
                self.assertEqual(len(set(variants.values())), 4)
                self.assertEqual(block["id"], variants[block["facing"]])
                for asset_id in variants.values():
                    self.assert_v2(asset_id)

    def test_full_sprite_bounds_and_mount_offsets(self):
        blocks = {block["instance_id"]: block for block in self.blocks}
        for block in self.blocks:
            with self.subTest(instance=block["instance_id"]):
                asset = self.assets[block["id"]]
                width, height = asset["pixel_size"]
                ox, oy = asset["origin"]
                scale = block["scale"]
                self.assertGreater(scale, 0)
                self.assertGreaterEqual(block["x"] - ox * scale, -1e-6)
                self.assertGreaterEqual(block["y"] - oy * scale, -1e-6)
                self.assertLessEqual(
                    block["x"] + (width - ox) * scale,
                    blueprint.CANVAS[0] + 1e-6,
                )
                self.assertLessEqual(
                    block["y"] + (height - oy) * scale,
                    blueprint.CANVAS[1] + 1e-6,
                )
                if block.get("mount_on"):
                    host = blocks[block["mount_on"]]
                    dx, dy = block["mount_offset"]
                    self.assertAlmostEqual(block["x"], host["x"] + dx)
                    self.assertAlmostEqual(block["y"], host["y"] + dy)

    def test_deterministic_and_no_output_writes(self):
        previous = blueprint.PATCH.read_bytes()
        with patch.object(Path, "mkdir", side_effect=AssertionError("write")), \
                patch.object(Path, "write_text",
                             side_effect=AssertionError("write")), \
                patch.object(Path, "write_bytes",
                             side_effect=AssertionError("write")), \
                patch.object(blueprint, "open", create=True) as guarded:
            import builtins

            def read_only(file, mode="r", *args, **kwargs):
                if any(flag in mode for flag in ("w", "a", "x", "+")):
                    raise AssertionError("Unexpected output write")
                return builtins.open(file, mode, *args, **kwargs)

            guarded.side_effect = read_only
            self.assertEqual(blueprint.build_patch(13), self.manifest)
        self.assertEqual(blueprint.PATCH.read_bytes(), previous)

    def test_manifest_builder_preserves_inputs(self):
        latest = json.loads(blueprint.LATEST.read_text(encoding="utf-8"))
        blocks, _ = blueprint.resolve_entries(
            self.catalog, blueprint.layout_entries()
        )
        original_blocks, original_latest = deepcopy(blocks), deepcopy(latest)
        blueprint.patch_manifest(self.catalog, blocks, latest)
        self.assertEqual(blocks, original_blocks)
        self.assertEqual(latest, original_latest)

    def test_invalid_versions_are_rejected(self):
        for version in (None, True, 1, 0, -1, 13.0, "13"):
            with self.subTest(version=version):
                with self.assertRaises(ValueError):
                    blueprint.build_patch(version)
        with self.assertRaises(ValueError):
            blueprint.build_patch(14)


if __name__ == "__main__":
    unittest.main()
