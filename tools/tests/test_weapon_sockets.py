"""Socket contract, malformed input and read-only CLI regression tests."""
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
SCRIPT = ROOT / "tools" / "weapon_sockets.py"
SCHEMA = ROOT / "game_factory" / "battle" / "weapon_sockets.schema.json"
SPEC = importlib.util.spec_from_file_location("weapon_sockets", SCRIPT)
weapon_sockets = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(weapon_sockets)


def fixture() -> dict:
    return {
        "attack_id": "hero_slash",
        "frames": [
            {
                "frame_name": "slash_00",
                "weapon_id": "WPN_HERO_BASIC_SWORD",
                "socket": {"x": 12, "y": -3.5, "rotation_deg": 45},
                "layer": "in_hand",
                "provenance": {
                    "method": "annotation",
                    "reference": "annotations/hero_slash.json#slash_00",
                },
            },
            {
                "frame_name": "slash_01",
                "weapon_id": "WPN_IRON_SWORD",
                "socket": {"x": 14, "y": 2, "rotation_deg": -180},
                "layer": "behind_hand",
                "provenance": {
                    "method": "measurement",
                    "reference": "measurements/hero_slash.csv:2",
                },
            },
        ],
    }


class WeaponSocketTests(unittest.TestCase):
    def assert_invalid(self, data: object, reason: str) -> None:
        errors = weapon_sockets.validate(data)
        self.assertTrue(errors)
        self.assertIn(reason, "\n".join(errors))

    def test_valid_fixture(self):
        self.assertEqual(weapon_sockets.validate(fixture()), [])

    def test_missing_fields(self):
        for key in ("attack_id", "frames"):
            with self.subTest(root=key):
                data = fixture()
                del data[key]
                self.assert_invalid(data, f"$.{key}: missing required field")
        for key in ("frame_name", "weapon_id", "socket", "layer", "provenance"):
            with self.subTest(frame=key):
                data = fixture()
                del data["frames"][1][key]
                self.assert_invalid(data, f"$.frames[1].{key}: missing required field")
        for key in ("x", "y", "rotation_deg"):
            with self.subTest(socket=key):
                data = fixture()
                del data["frames"][0]["socket"][key]
                self.assert_invalid(data, f"socket.{key}: missing required field")

    def test_duplicate_frame(self):
        data = fixture()
        data["frames"].append(copy.deepcopy(data["frames"][0]))
        self.assert_invalid(data, "duplicate frame 'slash_00'")

    def test_rotation_bounds(self):
        for value in (-180, 180, 0):
            with self.subTest(valid=value):
                data = fixture()
                data["frames"][0]["socket"]["rotation_deg"] = value
                self.assertEqual(weapon_sockets.validate(data), [])
        for value in (-180.01, 180.01, 1000):
            with self.subTest(invalid=value):
                data = fixture()
                data["frames"][0]["socket"]["rotation_deg"] = value
                self.assert_invalid(data, "rotation_deg: out of range")

    def test_invalid_numbers(self):
        for key in ("x", "y", "rotation_deg"):
            for value in (float("nan"), float("inf"), -float("inf"),
                          True, False, "1", None):
                with self.subTest(key=key, value=value):
                    data = fixture()
                    data["frames"][0]["socket"][key] = value
                    self.assert_invalid(data, f"socket.{key}: expected finite number")

    def test_supported_layers_and_weapons(self):
        for layer in weapon_sockets.LAYERS:
            for weapon in weapon_sockets.WEAPON_IDS:
                data = fixture()
                data["frames"][0].update(layer=layer, weapon_id=weapon)
                self.assertEqual(weapon_sockets.validate(data), [])
        for key, value in (("layer", "behind_body"), ("weapon_id", "WPN_UNKNOWN"),
                           ("layer", []), ("weapon_id", {})):
            with self.subTest(key=key, value=value):
                data = fixture()
                data["frames"][0][key] = value
                self.assert_invalid(data, f"{key}: expected one of")

    def test_provenance_required(self):
        for source, reason in (
            (None, "provenance: expected object"),
            ({}, "provenance.method: missing required field"),
            ({"method": "generated", "reference": "guess"},
             "provenance.method: expected one of"),
            ({"method": "annotation", "reference": "  "},
             "provenance.reference: expected non-empty string"),
            ({"method": "measurement"},
             "provenance.reference: missing required field"),
        ):
            with self.subTest(source=source):
                data = fixture()
                data["frames"][0]["provenance"] = source
                self.assert_invalid(data, reason)

    def test_bad_structure(self):
        for value in (None, [], 1, "socket"):
            self.assert_invalid(value, "$: expected object")
        for value in ([], {}, None, "frame"):
            data = fixture()
            data["frames"] = value
            self.assert_invalid(data, "frames: expected non-empty array")
        data = fixture()
        data["frames"][0] = None
        self.assert_invalid(data, "frames[0]: expected object")
        data = fixture()
        data["frames"][0]["socket"] = []
        self.assert_invalid(data, "socket: expected object")

    def test_blank_identifiers(self):
        data = fixture()
        data["attack_id"] = " "
        data["frames"][0]["frame_name"] = ""
        errors = "\n".join(weapon_sockets.validate(data))
        self.assertIn("attack_id: expected non-empty string", errors)
        self.assertIn("frame_name: expected non-empty string", errors)

    def test_unknown_fields(self):
        for location in ("root", "frame", "socket", "provenance"):
            with self.subTest(location=location):
                data = fixture()
                target = data if location == "root" else data["frames"][0]
                if location in ("socket", "provenance"):
                    target = target[location]
                target["unexpected"] = True
                self.assert_invalid(data, "unexpected: unknown field")

    def test_schema_contract(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(set(schema["required"]), {"attack_id", "frames"})
        frame = schema["$defs"]["frame"]
        properties = frame["properties"]
        self.assertEqual(set(frame["required"]), set(fixture()["frames"][0]))
        self.assertEqual(properties["weapon_id"]["enum"], list(weapon_sockets.WEAPON_IDS))
        self.assertEqual(properties["layer"]["enum"], list(weapon_sockets.LAYERS))
        source = properties["provenance"]["properties"]
        self.assertEqual(source["method"]["enum"], list(weapon_sockets.SOURCE_METHODS))
        rotation = properties["socket"]["properties"]["rotation_deg"]
        self.assertEqual((rotation["minimum"], rotation["maximum"]), (-180, 180))

    def test_file_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sockets.json"
            self.assertIn("cannot read", weapon_sockets.validate_file(path)[0])
            for text, reason in (
                ("{", "cannot read valid socket JSON"),
                ('{"attack_id":"a","attack_id":"b","frames":[]}', "duplicate JSON key"),
                ('{"frames":[NaN]}', "non-finite JSON number NaN"),
                ('{"frames":[Infinity]}', "non-finite JSON number Infinity"),
                ('{"frames":[-Infinity]}', "non-finite JSON number -Infinity"),
            ):
                with self.subTest(text=text):
                    path.write_text(text, encoding="utf-8")
                    self.assertIn(reason, "\n".join(weapon_sockets.validate_file(path)))
            data = fixture()
            text = json.dumps(data).replace('"x": 12', '"x": 1e999')
            path.write_text(text, encoding="utf-8")
            self.assertIn("expected finite number",
                          "\n".join(weapon_sockets.validate_file(path)))
            path.write_bytes(b"\xff")
            self.assertIn("cannot read", weapon_sockets.validate_file(path)[0])

    def test_cli_reports_status_and_preserves_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            valid = root / "valid.json"
            invalid = root / "invalid.json"
            valid.write_text(json.dumps(fixture()), encoding="utf-8")
            data = fixture()
            del data["frames"][0]["socket"]
            invalid.write_text(json.dumps(data), encoding="utf-8")
            before = {p.name: p.read_bytes() for p in root.iterdir()}
            for paths, code, summary in (
                ([valid], 0, "1/1 files passed"),
                ([invalid], 1, "0/1 files passed"),
                ([valid, invalid], 1, "1/2 files passed"),
                ([root / "missing.json"], 1, "0/1 files passed"),
            ):
                with self.subTest(paths=paths):
                    result = subprocess.run(
                        [sys.executable, str(SCRIPT), *map(str, paths)],
                        capture_output=True, text=True, timeout=30,
                    )
                    self.assertEqual(result.returncode, code, result.stderr)
                    self.assertIn(summary, result.stdout)
                    if invalid in paths:
                        self.assertIn("socket: missing required field", result.stdout)
            self.assertEqual(
                {p.name: p.read_bytes() for p in root.iterdir()}, before
            )

    def test_cli_requires_a_file(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
