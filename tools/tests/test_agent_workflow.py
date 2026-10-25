"""Unit tests for task ownership, art deduplication and delivery hash checks."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import agent_workflow as aw


class AgentWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for path in [aw.TASK_DIR, aw.ART_DIR, Path("map_factory/metadata")]:
            (self.root / path).mkdir(parents=True, exist_ok=True)
        (self.root / "map_factory/metadata/asset_index.json").write_text(
            json.dumps({"assets": [{"id": "P001"}]}))
        self.task_path = self.root / aw.TASK_DIR / "TASK-0001_test.md"
        self.task_path.write_text("""---
id: TASK-0001
status: blocked
owner: unassigned
branch: none
depends_on: none
issue: none
art_request: ART-0001
---
# Test task
""")
        self.art_path = self.root / aw.ART_DIR / "ART-0001_picture.md"
        self.art_path.write_text("""---
id: ART-0001
status: blocked_reference
owner: graphics-specialist
task: TASK-0001
dedupe_key: stable_bed_view_need
existing_asset_ids: P001
output_paths: .agents/graphics/deliveries/ART-0001/a.png
---
# Test artwork
""")

    def tearDown(self):
        self.tmp.cleanup()

    def test_boards_are_deterministic_and_short(self):
        a = aw.generated(self.root)
        b = aw.generated(self.root)
        self.assertEqual(a, b)
        self.assertIn("TASK-0001", a[aw.TASK_BOARD])
        self.assertIn("ART-0001", a[aw.ART_BOARD])
        self.assertNotIn("Test artwork", a[aw.ART_BOARD])

    def test_duplicate_output_rejected(self):
        duplicate = self.root / aw.ART_DIR / "ART-0002_duplicate.md"
        duplicate.write_text(self.art_path.read_text().replace(
            "id: ART-0001", "id: ART-0002").replace(
            "deliveries/ART-0001/", "deliveries/ART-0002/"))
        with self.assertRaisesRegex(ValueError, "duplicated art requirement dedupe_key"):
            aw.generated(self.root)

    def test_delivered_requires_real_hash_manifest(self):
        original = self.art_path.read_text()
        self.art_path.write_text(original.replace("status: blocked_reference", "status: delivered"))
        with self.assertRaisesRegex(ValueError, "missing delivery manifest"):
            aw.generated(self.root)
        folder = self.root / ".agents/graphics/deliveries/ART-0001"
        folder.mkdir(parents=True)
        png = folder / "a.png"
        png.write_bytes(b"PNG-test-placeholder-for-hash-verification")
        rel = ".agents/graphics/deliveries/ART-0001/a.png"
        manifest = {"request_id": "ART-0001", "files": [
            {"path": rel, "sha256": hashlib.sha256(png.read_bytes()).hexdigest()}]}
        (folder / "manifest.json").write_text(json.dumps(manifest))
        self.assertIn(aw.ART_BOARD, aw.generated(self.root))
        png.write_bytes(b"tampered")
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            aw.generated(self.root)

    def test_unknown_existing_asset_rejected(self):
        self.art_path.write_text(self.art_path.read_text().replace(
            "existing_asset_ids: P001", "existing_asset_ids: P999"))
        with self.assertRaisesRegex(ValueError, "catalog ID not found"):
            aw.generated(self.root)


if __name__ == "__main__":
    unittest.main()
