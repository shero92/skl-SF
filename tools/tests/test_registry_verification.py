"""TASK-0090 registry bridge checks; no map or image writes.

Agent: codex. Model: GPT-6. Tests call audit helpers only.
"""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1]
ROOT = TOOLS.parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from audit_room_assets import audit_map_ids, verify_v2_assets


def load_json(relative):
    with (ROOT / relative).open(encoding="utf-8") as handle:
        return json.load(handle)


class RegistryVerificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.v2 = load_json("map_factory/metadata/environment_assets_v2.json")
        cls.legacy = load_json("map_factory/metadata/asset_index.json")
        cls.room = load_json(
            "map_factory/maps/hero_room_01/versions/v0012.json")

    def test_room_legacy_ids_and_status(self):
        expected = {
            "E015", "E016", "E017", "E023", "E024", "F001", "F002",
            "F05_east", "F05_north", "F05_south", "F05_west",
            "F09_east", "F09_north", "F09_south", "F09_west",
            "S001", "S002", "S005", "S006", "S007", "S008",
            "S010", "S011", "S012", "S013", "S015", "S016",
        }
        report = audit_map_ids(self.room, self.v2, self.legacy)
        self.assertEqual(set(report["legacy_only"]), expected)
        self.assertEqual(report["unresolved"], [])
        self.assertEqual(
            set(report["v2_resolved"]) | set(report["legacy_only"]),
            set(self.room["resolved_assets"]),
        )
        self.assertFalse(
            set(report["v2_resolved"]) & set(report["legacy_only"]))
        for asset_id, record in report["legacy_only"].items():
            with self.subTest(asset_id=asset_id):
                bridged = asset_id.startswith(("F05_", "F09_"))
                self.assertEqual(
                    record["status"], "ready" if bridged else "needs_cleanup")
                self.assertEqual(record["qa_approval"], bridged)
                self.assertEqual(
                    record["v2_target"],
                    asset_id.replace("_", "@") if bridged else None,
                )

    def test_all_v2_files_verify(self):
        result = verify_v2_assets(self.v2, ROOT)
        self.assertEqual(result["errors"], [])
        self.assertEqual(len(result["verified"]), 128)
        self.assertEqual(set(result["verified"]), set(self.v2["assets"]))

    def test_every_directional_alias_has_a_target(self):
        expected = {
            key.replace("@", "_"): key
            for key in self.v2["assets"] if "@" in key
        }
        self.assertEqual(self.v2["legacy_aliases"], expected)
        for target in self.v2["legacy_aliases"].values():
            self.assertIn(target, self.v2["assets"])

    def test_unknown_ids_and_missing_bridge_targets(self):
        v2 = {"assets": {}, "legacy_aliases": {"alias": "missing"}}
        report = audit_map_ids(
            {"resolved_assets": {"unknown": {}, "alias": {}}}, v2, {})
        self.assertEqual(report["unresolved"], ["alias", "unknown"])
        self.assertEqual(report["legacy_only"], {})

    def test_alias_without_legacy_record_resolves(self):
        report = audit_map_ids(
            {"resolved_assets": {"F05_north": {}}}, self.v2, {})
        self.assertEqual(report["v2_resolved"], ["F05_north"])
        self.assertEqual(report["unresolved"], [])

    def test_audit_preserves_inputs(self):
        before = copy.deepcopy((self.room, self.v2, self.legacy))
        audit_map_ids(self.room, self.v2, self.legacy)
        self.assertEqual((self.room, self.v2, self.legacy), before)

    def test_verifier_detects_bad_metadata(self):
        v2 = copy.deepcopy(self.v2)
        v2["assets"]["A01"]["sha256"] = "0" * 64
        v2["assets"]["A01"]["sprite_dimensions"] = [1, 1]
        v2["legacy_aliases"]["broken"] = "missing"
        del v2["assets"]["F05@west"]
        errors = verify_v2_assets(v2, ROOT)["errors"]
        self.assertIn("SHA-256 mismatch A01", errors)
        self.assertIn("Sprite dimensions mismatch A01", errors)
        self.assertIn("Missing alias target broken: missing", errors)
        self.assertIn("Incomplete directional group bedside_table", errors)

    def test_verifier_detects_missing_files(self):
        with patch.object(Path, "is_file", return_value=False):
            result = verify_v2_assets(self.v2, ROOT)
        self.assertEqual(result["verified"], [])
        self.assertEqual(
            sum(error.startswith("Missing v2 PNG ") for error in result["errors"]),
            128,
        )


if __name__ == "__main__":
    unittest.main()
