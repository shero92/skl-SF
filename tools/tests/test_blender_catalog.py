"""Tests for owner-accepted Blender deliveries: catalog records and working-tree staging.

Execution provenance: Agent: claude (Claude Code); model: Sonnet 5.5.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from PIL import Image

TOOLS = Path(__file__).resolve().parents[1]
ROOT = TOOLS.parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import art_delivery
import blender_catalog


def make_root(tmp: Path, count: int = 2) -> Path:
    (tmp / ".agents/graphics/requests").mkdir(parents=True)
    (tmp / ".agents/graphics/deliveries/ART-9001").mkdir(parents=True)
    (tmp / "map_factory/metadata").mkdir(parents=True)
    catalog = {"asset_count": 2, "assets": [{"id": "W021"}, {"id": "W022"}]}
    (tmp / "map_factory/metadata/asset_index.json").write_text(json.dumps(catalog), encoding="utf-8")
    files = []
    outputs = []
    for n in range(count):
        rel = f".agents/graphics/deliveries/ART-9001/piece_{n}.png"
        Image.new("RGBA", (40 + n, 60), (200, 100, 50, 255)).save(tmp / rel)
        data = (tmp / rel).read_bytes()
        files.append({"path": rel, "sha256": hashlib.sha256(data).hexdigest(), "pixel_size": [40 + n, 60],
                      "facing": "north", "builder": "wall_run", "anchors_px": {"foot_center_front": [20.4, 55.6]},
                      "master": rel, "master_sha256": "0" * 64})
        outputs.append(rel)
    manifest = {"request_id": "ART-9001", "task_id": "TASK-9001", "status": "rendered_unreviewed", "files": files, "review": {}}
    (tmp / ".agents/graphics/deliveries/ART-9001/manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (tmp / ".agents/graphics/requests/ART-9001_test.md").write_text(
        "---\nid: ART-9001\nstatus: delivered\nowner: graphics-specialist\ntask: TASK-9001\n"
        "output_paths: " + ", ".join(outputs) + "\n---\n# test\n", encoding="utf-8")
    return tmp


class BlenderCatalogTests(unittest.TestCase):
    def test_next_ids_continue_after_the_highest_three_digit_id(self):
        assets = [{"id": "W021"}, {"id": "W022"}, {"id": "W01"}, {"id": "F009"}]
        self.assertEqual(blender_catalog.next_ids(assets, "W", 2), ["W023", "W024"])
        self.assertEqual(blender_catalog.next_ids(assets, "F", 1), ["F010"])

    def test_accept_builds_records_from_measured_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(Path(tmp))
            assets = blender_catalog.accept("ART-9001", "owner", "ok", root)
            self.assertEqual([a["id"] for a in assets], ["W023", "W024"])
            first = assets[0]
            self.assertEqual(first["category"], "walls")
            self.assertEqual(first["origin"], [20, 56])
            self.assertTrue(first["texture_path"].startswith("res://map_factory/parts/walls/W023_"))
            self.assertEqual(first["source"]["kind"], "owner_delivery")
            self.assertEqual(first["qa_approval"]["approved_by"], "owner")
            manifest = json.loads((root / ".agents/graphics/deliveries/ART-9001/manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["status"], "owner_accepted")
            self.assertEqual(manifest["review"]["accepted_by"], "owner")

    def test_unsupported_builder_is_rejected(self):
        with self.assertRaises(ValueError):
            blender_catalog.build_assets({"files": [{"builder": "magic", "path": "x.png", "pixel_size": [1, 1], "sha256": "0"}]}, [], "o", "n")

    def test_stage_registers_exact_bytes_and_marks_integrated(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(Path(tmp))
            blender_catalog.accept("ART-9001", "owner", "ok", root)
            self.assertEqual(art_delivery.stage(["ART-9001"], root), 2)
            catalog = json.loads((root / "map_factory/metadata/asset_index.json").read_text(encoding="utf-8"))
            self.assertEqual(catalog["asset_count"], 4)
            for asset in catalog["assets"][2:]:
                part = root / asset["texture_path"].removeprefix("res://")
                self.assertTrue(part.is_file())
                self.assertEqual(hashlib.sha256(part.read_bytes()).hexdigest(), asset["source"]["sha256"])
            request = (root / ".agents/graphics/requests/ART-9001_test.md").read_text(encoding="utf-8")
            self.assertIn("status: integrated", request)

    def test_stage_refuses_unknown_and_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(Path(tmp))
            blender_catalog.accept("ART-9001", "owner", "ok", root)
            with self.assertRaises(ValueError):
                art_delivery.stage(["ART-0000"], root)
            art_delivery.stage(["ART-9001"], root)
            with self.assertRaises(ValueError):  # request is integrated now, so it is not deliverable again
                art_delivery.stage(["ART-9001"], root)

    def test_real_repository_deliveries_are_integrated(self):
        catalog = json.loads((ROOT / "map_factory/metadata/asset_index.json").read_text(encoding="utf-8"))
        ids = {a["id"] for a in catalog["assets"]}
        for expected in ("W023", "W024", "W025", "W026", "F023", "F024", "F025", "F026"):
            self.assertIn(expected, ids)

    def test_quality_guard_accepts_the_catalog_with_retired_twins_and_new_parts(self):
        result = subprocess.run([sys.executable, str(TOOLS / "quality_guard.py")], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout[-800:] + result.stderr[-400:])
        report = json.loads(result.stdout[result.stdout.index("{"):])
        self.assertEqual(report["errors"], [])

    def test_ready_blender_parts_document_their_approval(self):
        catalog = json.loads((ROOT / "map_factory/metadata/asset_index.json").read_text(encoding="utf-8"))
        for asset in catalog["assets"]:
            if asset["id"] in ("W023", "W024", "W025", "W026", "F023", "F024", "F025", "F026"):
                self.assertTrue(asset.get("qa_approval"), asset["id"])


if __name__ == "__main__":
    unittest.main()
