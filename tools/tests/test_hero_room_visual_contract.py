"""Read-only contract validation and audit failure tests. Agent: codex."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "visual_contract", ROOT / "tools" / "hero_room_visual_contract.py")
audit_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit_module)


class VisualContractTests(unittest.TestCase):
    def setUp(self):
        self.contract = audit_module.read_json(audit_module.CONTRACT)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.texture = self.root / "approved.png"
        self.texture.write_bytes(b"fixture")
        self.registry = {"assets": {
            "approved": {"source_path": self.texture.name}
        }}
        self.room = {"version": 13, "blocks": [{"asset_id": "approved"}]}

    def evidence(self):
        return {
            "room_sha256": hashlib.sha256(json.dumps(
                self.room, sort_keys=True, separators=(",", ":")
            ).encode("utf-8")).hexdigest(),
            "geometry": {
                "verified": True, "provenance": "test renderer fixture",
                "image_size": [1536, 1024],
                "world_to_image": [2, 0, 0, 2, 10, 20],
            },
            "resolved_assets": [{
                "asset_id": "approved", "source_path": self.texture.name,
                "image_bounds": [635, 545, 890, 730],
                "feature_classes": ["blue_gold_compass_rose"],
            }],
        }

    def run_audit(self, evidence=None):
        return audit_module.audit(self.contract, self.registry, self.room,
                                  self.root, evidence)

    def test_all_eleven_zones(self):
        self.assertEqual(len(audit_module.validate_contract(self.contract)["zones"]), 11)

    def test_missing_zone_rejected(self):
        self.contract["zones"].pop()
        with self.assertRaises(ValueError):
            self.run_audit()

    def test_duplicate_zone_rejected(self):
        self.contract["zones"][-1] = copy.deepcopy(self.contract["zones"][0])
        with self.assertRaises(ValueError):
            self.run_audit()

    def test_invalid_contract_data_rejected(self):
        for bad in ([0, 0, 0, 10], [0, 0, 2000, 10], [0, 0, float("nan"), 10]):
            with self.subTest(box=bad):
                contract = copy.deepcopy(self.contract)
                contract["zones"][0]["box"] = bad
                with self.assertRaises(ValueError):
                    audit_module.validate_contract(contract)

    def test_nonexistent_source_rejected(self):
        self.texture.unlink()
        with self.assertRaises(ValueError):
            self.run_audit()

    def test_unknown_required_asset_rejected(self):
        self.contract["zones"][0]["required_asset_ids"] = ["missing"]
        with self.assertRaises(ValueError):
            self.run_audit()

    def test_unknown_placed_asset_rejected(self):
        self.room["blocks"][0]["asset_id"] = "missing"
        with self.assertRaises(ValueError):
            self.run_audit()

    def test_external_source_rejected(self):
        self.registry["assets"]["approved"]["source_path"] = "../outside.png"
        with self.assertRaises(ValueError):
            self.run_audit()

    def test_no_geometry_does_not_invent_coverage(self):
        report = self.run_audit()
        self.assertIsNone(report["distinct_pngs"])
        self.assertFalse(report["visual_approval"])
        self.assertFalse(report["geometry_verified"])
        self.assertTrue(all(z["world_polygon"] is None for z in report["zones"]))
        self.assertTrue(all(z["approximate_bounds_coverage"] is None
                            for z in report["zones"]))
        self.assertTrue(all(z["unverified_feature_classes"] for z in report["zones"]))

    def test_verified_geometry_counts_and_missing_art_requests(self):
        report = self.run_audit(self.evidence())
        self.assertEqual(report["placed_instances"], 1)
        self.assertEqual(report["distinct_pngs"], 1)
        compass = next(z for z in report["zones"] if z["id"] == "compass")
        self.assertEqual(compass["approximate_bounds_coverage"], 1)
        self.assertEqual(compass["world_polygon"][0], [312.5, 262.5])
        self.assertEqual(compass["absent_feature_classes"], [])
        self.assertTrue(report["potential_missing_art"])
        self.assertFalse(report["visual_approval"])

    def test_misplaced_feature(self):
        evidence = self.evidence()
        evidence["resolved_assets"][0]["image_bounds"] = [0, 0, 10, 10]
        report = self.run_audit(evidence)
        compass = next(z for z in report["zones"] if z["id"] == "compass")
        self.assertEqual(compass["misplaced_feature_classes"], ["blue_gold_compass_rose"])

    def test_unverified_or_singular_geometry_rejected(self):
        for matrix, verified in (([1, 0, 0, 1, 0, 0], False),
                                 ([0, 0, 0, 0, 0, 0], True)):
            evidence = self.evidence()
            evidence["geometry"].update(world_to_image=matrix, verified=verified)
            with self.assertRaises(ValueError):
                self.run_audit(evidence)

    def test_stale_render_evidence_rejected(self):
        evidence = self.evidence()
        evidence["room_sha256"] = "stale"
        with self.assertRaises(ValueError):
            self.run_audit(evidence)

    def test_resolved_texture_must_belong_to_asset(self):
        other = self.root / "other.png"
        other.write_bytes(b"fixture")
        evidence = self.evidence()
        evidence["resolved_assets"][0]["source_path"] = other.name
        with self.assertRaises(ValueError):
            self.run_audit(evidence)

    def test_coverage_union_does_not_double_count(self):
        self.assertEqual(audit_module.union_area(
            [[0, 0, 10, 10], [0, 0, 10, 10], [5, 0, 15, 10]]), 150)

    def test_reference_is_not_substituted(self):
        with self.assertRaises(ValueError):
            audit_module.verify_reference(self.texture,
                                          self.contract["reference_sha256"])

    def test_dedicated_router_entry(self):
        data = audit_module.read_json(ROOT / "tools" / "test_map.json")
        entries = [t for t in data["tests"] if t["id"] == "hero_room_visual_contract"]
        self.assertEqual(len(entries), 1)
        self.assertIn(Path(__file__).name, entries[0]["command"])
        self.assertEqual(len(entries[0]["paths"]), 4)


if __name__ == "__main__":
    unittest.main()
