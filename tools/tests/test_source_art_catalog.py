"""Source handoff audit: integrity, safe paths, preserved unknowns and approval scope."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import source_art_catalog as catalog


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.write_json("map_factory/maps/index.json", {"maps": {
            "room": {"latest": "map_factory/maps/room/latest.json", "version": 1}}})
        self.write_json("map_factory/maps/room/latest.json", {"texture": "res://assets_hd/test/v001/piece.png"})
        self.source = self.root / "assets_hd/test/v001/piece.png"
        self.source.parent.mkdir(parents=True)
        Image.new("RGBA", (4, 6), (10, 20, 30, 255)).save(self.source)
        self.item = {"id": "piece", "master_path": "assets_hd/test/v001/piece.png",
                     "sha256": hashlib.sha256(self.source.read_bytes()).hexdigest(),
                     "pixel_size": [4, 6], "origin": None, "quality_status": "needs_regeneration"}
        self.manifest = "game_factory/environment/ART-0099/v001/manifest.json"
        self.refresh()
        self.git = patch.object(catalog.subprocess, "run", return_value=subprocess.CompletedProcess([], 1, b"", b""))
        self.git.start()
        self.addCleanup(self.git.stop)

    def write_json(self, rel, data):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data), encoding="utf-8")

    def refresh(self, rejected=False):
        self.write_json(self.manifest, {"request_id": "ART-0099", "owner_approved": False,
                                      "items": [] if rejected else [self.item],
                                      "rejected_attempts": [self.item] if rejected else []})

    def test_approval_preserves_unknowns_defects_and_map_evidence(self):
        before = self.source.read_bytes()
        result = catalog.build(self.root)
        row = result["assets"][0]
        self.assertTrue(row["owner_approved"])
        self.assertEqual(row["quality_status"], "needs_regeneration")
        self.assertIsNone(row["metadata"]["origin"])
        self.assertFalse(row["production_active"])
        self.assertEqual(row["exact_path_map_references"], ["room"])
        self.assertEqual(self.source.read_bytes(), before)

    def test_rejected_is_never_promoted_by_owner_approval(self):
        self.refresh(rejected=True)
        result = catalog.build(self.root)
        self.assertEqual((result["selected_count"], result["rejected_count"]), (0, 1))
        self.assertEqual(result["assets"][0]["selection"], "rejected")

    def test_modified_source_fails_sha_audit(self):
        Image.new("RGBA", (4, 6), (80, 30, 20, 255)).save(self.source)
        with self.assertRaisesRegex(ValueError, "SHA mismatch"):
            catalog.build(self.root)

    def test_missing_linked_prompt_is_reported(self):
        self.item["prompt_path"] = "game_factory/environment/ART-0099/v001/requests/missing.txt"
        self.refresh()
        with self.assertRaisesRegex(ValueError, "Missing linked prompt_path"):
            catalog.build(self.root)

    def test_path_outside_project_is_rejected(self):
        self.item["master_path"] = "../../outside.png"
        self.refresh()
        with self.assertRaisesRegex(ValueError, "Path outside project"):
            catalog.build(self.root)

    def test_unregistered_image_in_source_group_blocks_complete_catalog(self):
        Image.new("RGBA", (2, 2), (40, 50, 60, 255)).save(self.source.parent / "unregistered.png")
        with self.assertRaisesRegex(ValueError, "Source PNG has no piece record"):
            catalog.build(self.root)


if __name__ == "__main__":
    unittest.main()
