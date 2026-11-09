"""Tests for rotation-safe scale/rotation variation and the CLI transform rules.

Execution provenance: Agent: claude (Claude Code); model: Sonnet 5.5.
"""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

TOOLS = Path(__file__).resolve().parents[1]
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import map_factory_cli as cli
import map_variation
from map_data import load_map

RULES = {"rotation_safe": ["P04"], "scale_min": 0.1, "scale_max": 4.0, "scale_snap": 0.05, "rotation_snap_degrees": 15}


def record(asset="P04", name="f1", scale=1.0):
    return {"id": asset, "instance_id": name, "x": 1, "y": 2, "scale": scale}


class VariationTests(unittest.TestCase):
    def test_deterministic_and_order_independent(self):
        a = map_variation.vary_record(record(), RULES, 7)
        self.assertEqual(a, map_variation.vary_record(record(), RULES, 7))
        self.assertNotEqual(a, map_variation.vary_record(record(name="other"), RULES, 7))
        data = {"objects": [record(name="a"), record(name="b"), record(name="c")]}
        forward = map_variation.vary(data, RULES, 3)
        data["objects"].reverse()
        backward = map_variation.vary(data, RULES, 3)

        def ordered(ops):
            return sorted(ops, key=lambda o: o["instance_id"])

        self.assertEqual(ordered(forward), ordered(backward))

    def test_only_rotation_safe_pieces_turn(self):
        self.assertEqual(map_variation.vary_record(record("F01"), RULES, 7), {})
        scale_only = map_variation.vary_record(record("F01"), RULES, 7, scale_only=frozenset({"F01"}))
        self.assertNotIn("rotation_degrees", scale_only)
        safe = map_variation.vary_record(record(), RULES, 7)
        self.assertIn("rotation_degrees", safe)

    def test_values_snap_and_stay_in_limits(self):
        for n in range(40):
            changes = map_variation.vary_record(record(name=f"x{n}", scale=3.9), RULES, n, scale_jitter=0.5)
            if "scale" in changes:
                self.assertLessEqual(changes["scale"], 4.0)
                self.assertAlmostEqual(changes["scale"] / 0.05, round(changes["scale"] / 0.05), places=6)
            if "rotation_degrees" in changes:
                self.assertEqual(changes["rotation_degrees"] % 15, 0)
                self.assertTrue(0 <= changes["rotation_degrees"] < 360)

    def test_per_asset_rotation_limit_keeps_flowers_upright(self):
        limited = {**RULES, "rotation_range_degrees": {"P04": 40}}
        for n in range(60):
            angle = map_variation.vary_record(record(name=f"t{n}"), limited, n).get("rotation_degrees", 0)
            self.assertTrue(angle <= 20 or angle >= 340, angle)

    def test_rotation_range_zero_means_scale_only(self):
        changes = map_variation.vary_record(record(), RULES, 5, rotation_range=0)
        self.assertNotIn("rotation_degrees", changes)

    def test_real_map_varies_only_flowers(self):
        operations = map_variation.vary(load_map("hero_room_01"), map_variation.load_rules(), 7)
        self.assertGreater(len(operations), 0)
        self.assertTrue(all(op["op"] == "update_block" for op in operations))


class CliTransformRuleTests(unittest.TestCase):
    RULES = {"rotation_safe": frozenset({"P04"}), "scale_min": 0.1, "scale_max": 4.0}
    UPRIGHT = {"category": "furniture", "subtype": "furniture", "tags": ["bed"]}
    FLAT = {"category": "decor", "subtype": "rug", "tags": ["rug"]}

    def test_upright_piece_cannot_take_free_rotation(self):
        with self.assertRaises(ValueError):
            cli.validate_transform({"id": "F01", "rotation_degrees": 37}, self.UPRIGHT, self.RULES, "bed")
        cli.validate_transform({"id": "F01", "rotation_degrees": 90}, self.UPRIGHT, self.RULES, "bed")
        cli.validate_transform({"id": "F01"}, self.UPRIGHT, self.RULES, "bed")

    def test_safe_and_flat_pieces_rotate_freely(self):
        cli.validate_transform({"id": "P04", "rotation_degrees": 37}, self.UPRIGHT, self.RULES, "flowers")
        cli.validate_transform({"id": "D01", "rotation_degrees": 37}, self.FLAT, self.RULES, "rug")

    def test_scale_limits(self):
        for bad in (0.01, 9, True):
            with self.assertRaises(ValueError):
                cli.validate_transform({"id": "P04", "scale": bad}, self.UPRIGHT, self.RULES, "x")
        cli.validate_transform({"id": "P04", "scale": 2.4}, self.UPRIGHT, self.RULES, "x")

    def test_real_rules_file(self):
        rules = cli.transform_rules()
        self.assertIn("P04", rules["rotation_safe"])
        self.assertLess(rules["scale_min"], rules["scale_max"])


if __name__ == "__main__":
    unittest.main()
