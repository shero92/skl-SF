"""Socket validation fixtures and CLI regressions; no images are read or written."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools/weapon_sockets.py"
spec = importlib.util.spec_from_file_location("weapon_sockets", SCRIPT)
weapon_sockets = importlib.util.module_from_spec(spec)
spec.loader.exec_module(weapon_sockets)


def fixture() -> dict:
    return {
        "attack_id": "hero_slash",
        "frames": [{
            "frame_name": "slash_00",
            "socket": {"x": 12, "y": -4.5, "rotation_deg": 90},
            "layer": "in_hand",
            "weapon_ids": ["WPN_HERO_BASIC_SWORD", "WPN_IRON_SWORD"],
            "provenance": {
                "method": "annotation",
                "reference": "annotations/hero_slash.json#slash_00",
            },
        }],
    }


class WeaponSocketsTests(unittest.TestCase):
    def assert_invalid(self, data: object, reason: str) -> None:
        self.assertIn(reason, "\n".join(weapon_sockets.validate(data)))

    def test_valid_layers_methods_and_rotation_boundaries(self):
        for layer in weapon_sockets.LAYERS:
            for method in weapon_sockets.METHODS:
                for rotation in (-180, 0, 180):
                    with self.subTest(layer=layer, method=method, rotation=rotation):
                        data = fixture()
                        frame = data["frames"][0]
                        frame["layer"] = layer
                        frame["provenance"]["method"] = method
                        frame["socket"]["rotation_deg"] = rotation
                        self.assertEqual(weapon_sockets.validate(data), [])

    def test_missing_fields(self):
        for key in fixture():
            data = fixture()
            del data[key]
            self.assert_invalid(data, f"$.{key}: missing required field")
        for key in fixture()["frames"][0]:
            data = fixture()
            del data["frames"][0][key]
            self.assert_invalid(data, f"$.frames[0].{key}: missing required field")
        for key in ("x", "y", "rotation_deg"):
            data = fixture()
            del data["frames"][0]["socket"][key]
            self.assert_invalid(data, f"socket.{key}: missing required field")

    def test_duplicate_frames(self):
        data = fixture()
        data["frames"].append(copy.deepcopy(data["frames"][0]))
        self.assert_invalid(data, "duplicate frame")
        data["frames"][1]["frame_name"] = "slash_01"
        self.assertEqual(weapon_sockets.validate(data), [])

    def test_bad_numbers(self):
        for key in ("x", "y", "rotation_deg"):
            for value in (float("nan"), float("inf"), -float("inf"), True, "12", None):
                with self.subTest(key=key, value=value):
                    data = fixture()
                    data["frames"][0]["socket"][key] = value
                    self.assert_invalid(data, f"socket.{key}: expected finite number")
        for value in (-180.01, 180.01):
            data = fixture()
            data["frames"][0]["socket"]["rotation_deg"] = value
            self.assert_invalid(data, "rotation out of range")

    def test_layer_weapons_and_provenance(self):
        cases = [
            ("layer", "body", "invalid layer"),
            ("weapon_ids", [], "expected nonempty array"),
            ("weapon_ids", ["WPN_UNKNOWN"], "unsupported weapon id"),
            ("weapon_ids", ["WPN_IRON_SWORD"] * 2, "duplicate weapon id"),
            ("provenance", {"method": "guess", "reference": "notes"},
             "source must be annotation or measurement"),
            ("provenance", {"method": "measurement", "reference": "  "},
             "expected nonblank string"),
            ("provenance", {"method": "annotation"}, "missing required field"),
        ]
        for key, value, reason in cases:
            with self.subTest(key=key, value=value):
                data = fixture()
                data["frames"][0][key] = value
                self.assert_invalid(data, reason)

    def test_malformed_shapes_and_unknown_fields(self):
        for value in (None, [], True, "attack"):
            self.assert_invalid(value, "expected object")
        for frames in ([], {}, None, [None]):
            data = fixture()
            data["frames"] = frames
            self.assertTrue(weapon_sockets.validate(data))
        data = fixture()
        data["frames"][0]["socket"]["z"] = 0
        self.assert_invalid(data, "unknown field")
        data = fixture()
        data["attack_id"] = " "
        self.assert_invalid(data, "expected nonblank string")

    def test_schema_contract(self):
        schema = json.loads(
            (ROOT / "game_factory/battle/weapon_sockets.schema.json")
            .read_text(encoding="utf-8")
        )
        properties = schema["properties"]["frames"]["items"]["properties"]
        self.assertEqual(properties["layer"]["enum"], list(weapon_sockets.LAYERS))
        self.assertEqual(properties["weapon_ids"]["items"]["enum"],
                         list(weapon_sockets.WEAPON_IDS))
        self.assertEqual(properties["provenance"]["properties"]["method"]["enum"],
                         list(weapon_sockets.METHODS))

    def test_cli_reports_all_files_and_preserves_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            valid = root / "valid.json"
            invalid = root / "invalid.json"
            valid.write_text(json.dumps(fixture()), encoding="utf-8")
            data = fixture()
            del data["frames"][0]["socket"]
            invalid.write_text(json.dumps(data), encoding="utf-8")
            before = {path: path.read_bytes() for path in (valid, invalid)}
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), str(valid), str(invalid)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(proc.returncode, 1, proc.stderr)
            self.assertIn(f"PASS {valid}", proc.stdout)
            self.assertIn("socket: missing required field", proc.stdout)
            self.assertIn("1/2 files passed", proc.stdout)
            for path, contents in before.items():
                self.assertEqual(path.read_bytes(), contents)
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), str(valid)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_file_errors_and_nonstandard_json(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"
            self.assertIn("cannot read valid JSON", weapon_sockets.validate_file(path)[0])
            for text, reason in (
                ("{", "cannot read valid JSON"),
                ('{"attack_id": "a", "attack_id": "b"}', "duplicate JSON key"),
                ('{"value": NaN}', "non-finite JSON number"),
                ('{"value": Infinity}', "non-finite JSON number"),
            ):
                path.write_text(text, encoding="utf-8")
                self.assertIn(reason, weapon_sockets.validate_file(path)[0])
            data = fixture()
            text = json.dumps(data).replace('"x": 12', '"x": 1e999')
            path.write_text(text, encoding="utf-8")
            self.assertIn("expected finite number",
                          "\n".join(weapon_sockets.validate_file(path)))


if __name__ == "__main__":
    unittest.main()
