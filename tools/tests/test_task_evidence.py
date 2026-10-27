"""Evidence gates use synthetic PNG headers, never production artwork."""

import hashlib
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from task_evidence import check_task


class TaskEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.image = self.root / "map_factory/references/source.png"
        self.image.parent.mkdir(parents=True)
        self.image.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" + struct.pack(">II", 1448, 1086) + b"synthetic-test-only")
        self.base = {
            "kind": "reference", "status": "approved", "approved_by": "owner",
            "approved_at": "2026-10-27T10:00:00Z",
            "provenance": {"source": "owner attachment", "kind": "original"},
            "path": "map_factory/references/source.png", "pixel_size": [1448, 1086],
            "sha256": hashlib.sha256(self.image.read_bytes()).hexdigest(),
        }

    def run_gate(self, items):
        path = self.root / "evidence.json"
        path.write_text(json.dumps({"requirements": items}), encoding="utf-8", newline="\n")
        return check_task({"evidence_manifest": "evidence.json"}, self.root)

    def test_no_manifest_is_optional(self):
        self.assertEqual(check_task({}, self.root), [])

    def test_valid_reference(self):
        self.assertEqual(self.run_gate([self.base]), [])

    def test_matching_dimensions_do_not_replace_hash(self):
        self.image.write_bytes(self.image.read_bytes() + b"changed")
        self.assertIn("SHA-256", " ".join(self.run_gate([self.base])))

    def test_dimensions_checked_independently(self):
        self.base["pixel_size"] = [1, 2]
        self.assertIn("dimensions", " ".join(self.run_gate([self.base])))

    def test_approval_checked_before_any_binary_access(self):
        for field in ("status", "approved_by", "approved_at", "provenance"):
            with self.subTest(field=field):
                item = dict(self.base)
                item.pop(field)
                manifest = self.root / "evidence.json"
                manifest.write_text(json.dumps({"requirements": [item]}), encoding="utf-8", newline="\n")
                original_open = Path.open
                def guarded_open(path, mode="r", *args, **kwargs):
                    if "b" in mode:
                        raise AssertionError("binary access forbidden")
                    return original_open(path, mode, *args, **kwargs)
                with patch.object(Path, "open", guarded_open):
                    self.assertTrue(check_task({"evidence_manifest": "evidence.json"}, self.root))

    def test_missing_and_malformed_manifest(self):
        self.assertTrue(check_task({"evidence_manifest": "missing.json"}, self.root))
        path = self.root / "bad.json"
        for value in ("{", "[]", '{"requirements": []}', '{"requirements": [null]}'):
            path.write_text(value, encoding="utf-8", newline="\n")
            self.assertTrue(check_task({"evidence_manifest": "bad.json"}, self.root))

    def test_traversal_absolute_and_production_paths_rejected(self):
        for value in ("../source.png", "/tmp/source.png", "C:/source.png", "map_factory/parts/source.png", "map_factory/references/../source.png"):
            with self.subTest(path=value):
                self.assertTrue(self.run_gate([{**self.base, "path": value}]))
        self.assertTrue(check_task({"evidence_manifest": "../evidence.json"}, self.root))

    def test_symlink_escape_rejected(self):
        with tempfile.TemporaryDirectory() as external:
            target = Path(external) / "source.png"
            target.write_bytes(b"external")
            link = self.image.parent / "link.png"
            try:
                link.symlink_to(target)
            except OSError:
                self.skipTest("OS does not allow symlink creation")
            result = self.run_gate([{**self.base, "path": "map_factory/references/link.png"}])
            self.assertIn("escapes", " ".join(result))

    def test_bad_header_and_metadata(self):
        for changes in ({"sha256": "bad"}, {"pixel_size": [True, 1]}, {"pixel_size": [0, 1]}, {"path": "map_factory/references//source.png"}):
            self.assertTrue(self.run_gate([{**self.base, **changes}]))
        self.image.write_bytes(b"not PNG")
        self.assertIn("header", " ".join(self.run_gate([self.base])))

    def test_symlink_to_production_inside_repository_rejected(self):
        production = self.root / "map_factory/parts/closed.png"
        production.parent.mkdir()
        production.write_bytes(b"closed-production-fixture")
        link = self.image.parent / "internal.png"
        try:
            link.symlink_to(production)
        except OSError:
            self.skipTest("OS does not allow symlink creation")
        self.assertIn("approved reference directory", " ".join(self.run_gate([
            {**self.base, "path": "map_factory/references/internal.png"}
        ])))

    def test_measurement_independent_from_missing_reference(self):
        measured = {**self.base, "kind": "measurement", "scope": "wall", "target": "W021"}
        measured.pop("path")
        self.image.unlink()
        self.assertEqual(self.run_gate([measured]), [])
        measured.pop("scope")
        self.assertIn("scope", " ".join(self.run_gate([measured])))

    def test_visual_approval_requires_owner_independent_reviewer_and_binding(self):
        item = {**self.base, "kind": "visual_approval", "scope": "room", "target": "hero_room_01/v0012",
                "owner_approved": True, "producer": "codex", "producer_session": "produce-1",
                "reviewer_session": "review-1", "target_commit": "a" * 40}
        self.assertEqual(self.run_gate([item]), [])
        for changes in ({"owner_approved": False}, {"producer": "OWNER"}, {"reviewer_session": "produce-1"}, {"target_commit": "short"}, {"producer_session": ""}):
            with self.subTest(changes=changes):
                self.assertTrue(self.run_gate([{**item, **changes}]))


if __name__ == "__main__":
    unittest.main()
