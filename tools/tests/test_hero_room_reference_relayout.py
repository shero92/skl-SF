"""Reference relayout geometry and read-only generation checks."""
from copy import deepcopy
import importlib
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
builder = importlib.import_module("build_hero_room_blueprint")
assembly = importlib.import_module("room_assembly")


class AnchorTests(unittest.TestCase):
    def test_uniform_fit_uses_registered_origin(self):
        asset = {"origin": [80, 190]}
        measured = {"content": [20, 30, 100, 140]}
        block = {"x": 0, "y": 0, "scale": 1}
        result = assembly.fit_registered_block(
            asset, measured, block, (200, 300, 250, 400),
        )
        self.assertEqual(result["scale"], 0.5)
        self.assertEqual(
            assembly.content_bounds(asset, measured, result),
            (200, 330, 250, 400),
        )
        self.assertEqual(block, {"x": 0, "y": 0, "scale": 1})

    def test_empty_content_is_rejected(self):
        with self.assertRaises(ValueError):
            assembly.fit_registered_block(
                {"origin": [0, 0]}, {"content": [0, 0, 0, 1]},
                {}, (0, 0, 10, 10),
            )


class ReferenceRelayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = builder.load_catalog()
        cls.blocks = builder.reference_relayout_blocks(cls.catalog)

    def test_features_and_registered_assets(self):
        builder.validate_reference_relayout(self.catalog, self.blocks)
        assets = {asset["id"]: asset for asset in self.catalog["assets"]}
        for block in self.blocks:
            with self.subTest(instance=block["instance_id"]):
                self.assertEqual(
                    block["id"], builder.canonical_asset_id(block["id"], assets),
                )
                self.assertTrue(builder.sidecar_png(
                    self.catalog, block["id"],
                ).is_file())
        names = {block["instance_id"] for block in self.blocks}
        self.assertTrue(set(builder.REFERENCE_ZONES) <= names)
        self.assertTrue({
            "RearArchFlowersLeft", "RearArchFlowersRight",
            "TerraceRockFrontLeft", "TerraceRockFrontRight",
            "StairStep1", "StairStep4",
        } <= names)

    def test_wall_run_and_openings_are_retained(self):
        expected = {
            entry["instance_id"] for entry in builder.perimeter_wall_entries()
        }
        actual = {block["instance_id"] for block in self.blocks}
        self.assertTrue(expected <= actual)
        cells = {
            tuple(entry["perimeter_cell"])
            for entry in builder.perimeter_wall_entries()
        }
        self.assertFalse(cells & set().union(*builder.wall_gaps().values()))

    def test_rug_overlap_is_allowed(self):
        by_id = {block["instance_id"]: block for block in self.blocks}
        for furniture, rug in (
            ("RoyalBed", "BedRug"), ("DiningTable", "TableRug"),
        ):
            bounds = []
            for name in (furniture, rug):
                block = by_id[name]
                bounds.append(assembly.content_bounds(
                    builder.record(self.catalog, block["id"]),
                    builder.measurement(self.catalog, block["id"]), block,
                ))
            a, b = bounds
            self.assertLess(max(a[0], b[0]), min(a[2], b[2]))
            self.assertLess(max(a[1], b[1]), min(a[3], b[3]))

    def test_invalid_placement_and_texture_are_rejected(self):
        for field, value in (("x", 760), ("id", "NOT_REGISTERED")):
            blocks = deepcopy(self.blocks)
            bed = next(b for b in blocks if b["instance_id"] == "RoyalBed")
            bed[field] = value
            with self.subTest(field=field), self.assertRaises((ValueError, KeyError)):
                builder.validate_reference_relayout(self.catalog, blocks)

    def test_generation_is_deterministic_and_does_not_write(self):
        parent = {"version": 13}
        with patch.object(builder, "LATEST") as latest:
            latest.open.side_effect = AssertionError("Unexpected path method")
            # The generator uses built-in open for its read-only parent input.
            from unittest.mock import mock_open
            with patch("builtins.open", mock_open(read_data='{"version":13}')):
                with patch.object(builder, "load_catalog", return_value=self.catalog):
                    first = builder.build_patch(14)
                    second = builder.build_patch(14)
        self.assertEqual(first, second)
        self.assertEqual(first["base_version"], parent["version"])
        self.assertEqual(first["base_sha256"], builder.digest_json(parent))
        qa = next(
            change["value"] for change in first["changes"]
            if change.get("key") == "visual_qa"
        )
        self.assertIs(qa["visual_approval"], False)

    def test_next_version_refuses_existing_output(self):
        from unittest.mock import mock_open
        with patch("builtins.open", mock_open(read_data='{"version":13}')):
            with patch.object(builder, "PATCH_DIR") as directory:
                directory.__truediv__.return_value.exists.return_value = True
                with self.assertRaises(FileExistsError):
                    builder.next_reference_version()


if __name__ == "__main__":
    unittest.main()
