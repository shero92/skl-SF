"""Read-only placement checks. Agent: codex; model: GPT-6."""

import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "hero_room_lighting_blueprint",
    ROOT / "tools" / "build_hero_room_blueprint.py",
)
blueprint = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(blueprint)


class HeroRoomLightingDecorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = blueprint.layout_entries()
        cls.by_name = {
            entry["instance_id"]: entry for entry in cls.entries
        }
        cls.decor = [
            entry for entry in cls.entries if entry["kind"] == "mount"
        ]

    def test_decor_mounts_are_valid_and_ordered(self):
        self.assertTrue(self.decor)
        self.assertEqual(len(self.entries), len(self.by_name))
        walls = {
            entry["instance_id"]: entry
            for entry in blueprint.perimeter_wall_entries()
        }
        gaps = set().union(*blueprint.wall_gaps().values())
        seen = set()
        for entry in self.entries:
            name = entry["instance_id"]
            with self.subTest(instance=name):
                if entry["kind"] == "mount":
                    host_name = entry["mount_on"]
                    self.assertIn(host_name, seen)
                    host = self.by_name[host_name]
                    if entry["id"] == "L05":
                        # Glow mounts on a wall/furniture host (lanterns are not valid hosts).
                        self.assertNotIn(host["id"], ("L01", "L02", "L03", "L04", "L05"))
                    elif host_name in walls:
                        cell = tuple(walls[host_name]["perimeter_cell"])
                        self.assertIn(cell, blueprint.wall_perimeter())
                        self.assertNotIn(cell, gaps)
                    else:
                        self.assertTrue(host["id"].startswith("F"))
                        self.assertEqual(host["kind"], "grid")
                seen.add(name)

    def test_layers_and_lighting_coverage(self):
        glows = [entry for entry in self.decor if entry["id"] == "L05"]
        lights = [
            entry for entry in self.decor
            if entry["id"] in ("L01", "L02", "L03", "L04")
        ]
        self.assertEqual(len(glows), len(lights))
        for light in lights:
            matching = [
                glow for glow in glows
                if glow["instance_id"] == light["instance_id"] + "Glow"
            ]
            self.assertEqual(len(matching), 1)
            self.assertEqual(matching[0]["layer"], "front_objects")
        for entry in self.decor:
            with self.subTest(instance=entry["instance_id"]):
                if entry["id"] in ("D04", "D05"):
                    self.assertEqual(entry["layer"], "back_objects")
                    self.assertIn(
                        "perimeter_cell", self.by_name[entry["mount_on"]]
                    )
                elif entry["id"] == "L05":
                    self.assertEqual(entry["layer"], "front_objects")
                elif entry["id"].startswith("R") or entry["id"] in ("L03", "L04"):
                    self.assertEqual(entry["layer"], "objects")
        ids = {entry["id"] for entry in self.decor}
        self.assertTrue({
            "L01", "L02", "L03", "L04", "L05", "D04", "D05",
            "P01", "P02", "P03", "P04", "P05", "P06", "R01", "R02", "R06",
        }.issubset(ids))
        candle_hosts = {
            entry["mount_on"] for entry in self.decor if entry["id"] == "L03"
        }
        self.assertEqual(
            candle_hosts, {"LeftBookcase", "RightBookcase", "DiningTable"}
        )
        for x in (0, 16):
            cells = {
                tuple(self.by_name[entry["mount_on"]]["perimeter_cell"])
                for entry in lights if entry["id"] in ("L01", "L02")
                and self.by_name[entry["mount_on"]]["perimeter_cell"][0] == x
            }
            self.assertEqual(cells, {(x, y) for y in (0, 2, 4, 6)})

    def test_decor_ids_exist_in_v2_and_catalog(self):
        registry_path = ROOT.joinpath(
            "map" + "_factory", "metadata",
            "environment" + "_assets" + "_v2" + ".json",
        )
        with registry_path.open(encoding="utf-8") as handle:
            registry = json.load(handle)

        def identifiers(value):
            found = set()
            if isinstance(value, dict):
                found.update(value)
                for key, child in value.items():
                    if key in ("id", "asset_id", "registry_key"):
                        if isinstance(child, str):
                            found.add(child)
                    found.update(identifiers(child))
            elif isinstance(value, list):
                for child in value:
                    found.update(identifiers(child))
            return found

        approved_ids = identifiers(registry)
        catalog = blueprint.load_catalog()
        for entry in self.decor:
            with self.subTest(asset=entry["id"]):
                self.assertIn(entry["id"], approved_ids)
                self.assertIsNotNone(
                    blueprint.catalog_lookup(catalog, entry["id"])
                )

    def test_resolved_mounts_keep_layers_offsets_and_scale(self):
        catalog = blueprint.load_catalog()
        # Avoid image measurement: mount arithmetic needs only host positions.
        def target_position(catalog, asset_id, scale, centre, base):
            return [centre, base]

        with patch.object(
            blueprint, "position_from_target", side_effect=target_position
        ):
            blocks, positions = blueprint.resolve_entries(catalog, self.entries)
        by_name = {block["instance_id"]: block for block in blocks}
        for entry in self.decor:
            name = entry["instance_id"]
            with self.subTest(instance=name):
                host_x, host_y = positions[entry["mount_on"]]
                dx, dy = entry["mount_offset"]
                block = by_name[name]
                self.assertEqual(
                    [block["x"], block["y"]],
                    [round(host_x + dx, 3), round(host_y + dy, 3)],
                )
                self.assertEqual(block["_layer"], entry["layer"])
                self.assertEqual(block["render_layer"], "decorations")
                self.assertEqual(block["mount_on"], entry["mount_on"])
                self.assertEqual(block["scale"], entry["scale"])

    def test_layout_is_deterministic_and_returns_fresh_entries(self):
        first = blueprint.layout_entries()
        second = blueprint.layout_entries()
        self.assertEqual(first, second)
        first[-1]["mount_offset"] = (999, 999)
        self.assertEqual(second, blueprint.layout_entries())


if __name__ == "__main__":
    unittest.main()
