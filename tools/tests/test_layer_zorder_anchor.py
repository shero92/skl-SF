"""Independent layer contract checks.

Execution tool: Codex. Model: GPT-6.
"""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

TOOLS = Path(__file__).resolve().parents[1]
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from map_factory_layers import verify_layers


class LayerZOrderAnchorTests(unittest.TestCase):
    def setUp(self):
        self.registry = {
            "assets": [
                {"id": "sample", "render_pivot_px": [16, 32]},
                {
                    "id": "large",
                    "render_pivot_px": [16, 32],
                    "allowed_scales": [2.0],
                },
            ]
        }
        self.scene = {
            "objects": [
                {
                    "instance_id": "object_" + str(index),
                    "asset_id": "sample",
                    "layer": layer,
                    "position": [0, index * 10],
                    "anchor": [16, 32],
                    "scale": 1.0,
                    "display_z": index * 10,
                }
                for index, layer in enumerate((
                    "background", "ground", "walls",
                    "furniture_decor", "shadows_overlays",
                ))
            ]
        }

    def codes(self, scene=None):
        report = verify_layers(self.scene if scene is None else scene, self.registry)
        self.assertFalse(report["ok"])
        self.assertEqual(report["counts"]["violations"], len(report["violations"]))
        return {item["code"] for item in report["violations"]}

    def test_valid_map_and_inputs_unchanged(self):
        before = deepcopy((self.scene, self.registry))
        report = verify_layers(self.scene, self.registry)
        self.assertTrue(report["ok"], report)
        self.assertEqual(report["counts"]["objects"], 5)
        self.assertEqual(report["counts"]["violations"], 0)
        self.assertEqual((self.scene, self.registry), before)

    def test_unknown_layer(self):
        self.scene["objects"][0]["layer"] = "unknown"
        self.assertIn("layer", self.codes())

    def test_layer_order(self):
        self.scene["objects"][1:3] = reversed(self.scene["objects"][1:3])
        self.assertIn("layer_order", self.codes())

    def test_depth_order(self):
        self.scene["objects"][4]["display_z"] = 15
        self.assertIn("z_order", self.codes())

    def test_base_y_order_and_ties(self):
        item = deepcopy(self.scene["objects"][3])
        item["instance_id"] = "second_prop"
        item["base_y"] = 29
        self.scene["objects"].insert(4, item)
        self.assertIn("y_sort", self.codes())
        item["base_y"] = 30
        self.assertTrue(verify_layers(self.scene, self.registry)["ok"])

    def test_missing_or_wrong_anchor(self):
        for value in (None, [0, 0], [16, float("nan")]):
            with self.subTest(anchor=value):
                self.scene["objects"][0]["anchor"] = value
                self.assertIn("anchor", self.codes())

    def test_scale_requires_registry_declaration(self):
        item = self.scene["objects"][0]
        for value in (2.0, 0, -1, True, float("inf"), [1, 2]):
            with self.subTest(scale=value):
                item["scale"] = value
                self.assertIn("scale", self.codes())
        item["asset_id"] = "large"
        item["scale"] = [2, 2]
        self.assertTrue(verify_layers(self.scene, self.registry)["ok"])

    def test_unknown_asset(self):
        self.scene["objects"][0]["asset_id"] = "missing"
        self.assertIn("registry", self.codes())

    def test_compiled_pass_aliases_and_origin(self):
        passes = {}
        depths = {}
        for item in deepcopy(self.scene["objects"]):
            layer = {
                "furniture_decor": "decorations",
                "shadows_overlays": "shadows",
            }.get(item["layer"], item["layer"])
            item["render_layer"] = layer
            item["origin"] = item.pop("anchor")
            depths[layer] = item.pop("display_z")
            passes[layer] = [item]
        scene = {"layer_stack": {"passes": passes, "display_z": depths}}
        self.assertTrue(verify_layers(scene, self.registry)["ok"])
        depths["shadows"] = 20
        self.assertIn("z_order", self.codes(scene))

    def test_containing_layer_mismatch(self):
        scene = {
            "layer_stack": [
                {"name": "ground", "objects": [self.scene["objects"][0]]}
            ]
        }
        self.assertIn("layer", self.codes(scene))

    def test_invalid_base_y(self):
        self.scene["objects"][0]["position"] = [0, float("nan")]
        self.assertIn("y_sort", self.codes())

    def test_latest_room_reports_counts(self):
        root = TOOLS.parent
        data_root = root / "_".join(("map", "factory"))
        registry_path = data_root / "metadata" / (
            "_".join(("environment", "assets", "v2")) + ".json"
        )
        room = data_root / "maps" / "_".join(("hero", "room", "01"))
        latest_path = room / ("latest" + ".json")
        self.assertTrue(registry_path.is_file(), "Expected repository registry")
        self.assertTrue(latest_path.is_file(), "Expected latest room data")
        registry = json.loads(registry_path.read_text(encoding="utf-8-sig"))
        scene = json.loads(latest_path.read_text(encoding="utf-8-sig"))
        # A latest pointer may name a version instead of embedding its snapshot.
        if not any(key in scene for key in (
            "layer_stack", "objects", "background_objects", "back_objects",
        )):
            version = scene.get("latest_version", scene.get("version"))
            self.assertIsNotNone(version, "Latest pointer must identify a version")
            if isinstance(version, int):
                version = "v" + str(version).zfill(4)
            candidates = sorted(room.rglob(str(version) + "*.json"))
            self.assertTrue(candidates, "Expected a snapshot for the latest version")
            snapshots = [
                json.loads(path.read_text(encoding="utf-8-sig"))
                for path in candidates
            ]
            scene = next(
                (item for item in snapshots if any(key in item for key in (
                    "layer_stack", "objects", "background_objects", "back_objects",
                ))),
                None,
            )
            self.assertIsNotNone(scene, "Latest version must contain a map snapshot")
        report = verify_layers(scene, registry)
        self.assertIsInstance(report["ok"], bool)
        self.assertGreater(report["counts"]["objects"], 0)
        self.assertEqual(report["counts"]["violations"], len(report["violations"]))
        for layer in (
            "background", "ground", "walls",
            "furniture_decor", "shadows_overlays",
        ):
            self.assertIsInstance(report["counts"][layer], int)


if __name__ == "__main__":
    unittest.main()
