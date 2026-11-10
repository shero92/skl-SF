"""Independent-source validation, lossless atlas and honest animation export contracts."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import golden_cyclone_assets as assets
from battle_godot_harness import run_godot


def _configured_godot_exists() -> bool:
    try:
        path = json.loads((Path(__file__).resolve().parents[2] / ".agents/planner/config.json").read_text(encoding="utf-8")).get("godot_executable")
    except (OSError, ValueError):
        return False
    return isinstance(path, str) and Path(path).is_file()


class ExportContracts(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)
        self.frames = []
        annotations = {"uniform_source_scale": .22, "game_canvas_size": [384, 384],
                       "game_ground_anchor": [192, 352], "frames": {}}
        for index in range(1, 23):
            ident = f"hero_golden_cyclone_{index:03}"
            path = self.root / "masters" / (ident + ".png")
            path.parent.mkdir(exist_ok=True)
            image = Image.new("RGBA", (1024, 1024))
            ImageDraw.Draw(image).rectangle((250, 150, 700, 900), fill=(index * 9, 80, 120, 255))
            image.save(path)
            request = self.root / "requests" / (ident + ".txt")
            request.parent.mkdir(exist_ok=True)
            request.write_text("Synthetic test fixture; never a production asset.")
            self.frames.append({"frame_id": ident, "source_image_path": path.relative_to(self.root).as_posix(),
                                "sha256": assets.sha(path), "source_generation_mode": "individual_request",
                                "generation_request_path": request.relative_to(self.root).as_posix(),
                                "quality_status": "needs_review", "frame_duration": 45})
            annotations["frames"][ident] = {"method": "manual_source_review",
                "character_ground_anchor": [475, 900], "weapon_hand_anchor": [350, 400],
                "hand_rotation": -45, "weapon_render_order": "front", "weapon_scale": .9}
        self.manifest = {"production_source_mode": "INDIVIDUAL_FRAME", "generated_frame_count": 22,
                         "frames": self.frames}
        assets.write(self.root / assets.MANIFEST, self.manifest)
        assets.write(self.root / assets.ANNOTATIONS, annotations)

    def test_rejects_copied_source_even_with_updated_hash(self):
        first, second = self.frames[:2]
        shutil.copyfile(self.root / first["source_image_path"], self.root / second["source_image_path"])
        second["sha256"] = first["sha256"]
        assets.write(self.root / assets.MANIFEST, self.manifest)
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            assets.validate(self.root)

    def test_rejects_missing_and_collage_provenance(self):
        self.frames[0]["source_generation_mode"] = "cropped_storyboard"
        assets.write(self.root / assets.MANIFEST, self.manifest)
        with self.assertRaisesRegex(ValueError, "independent"):
            assets.validate(self.root)
        self.frames[0]["source_generation_mode"] = "individual_request"
        self.frames[0]["source_image_path"] = None
        assets.write(self.root / assets.MANIFEST, self.manifest)
        with self.assertRaisesRegex(ValueError, "Missing source"):
            assets.validate(self.root)

    def test_rejects_clipped_silhouette(self):
        image = Image.new("RGBA", (1024, 1024))
        ImageDraw.Draw(image).rectangle((0, 200, 500, 900), fill="white")
        path = self.root / "clipped.png"
        image.save(path)
        with self.assertRaisesRegex(ValueError, "edge"):
            assets.inspect_png(path)

    def test_export_keeps_sources_and_atlas_pixels(self):
        before = [assets.sha(self.root / f["source_image_path"]) for f in self.frames]
        result = assets.build(self.root)
        self.assertTrue(result["original_hashes_unchanged"])
        self.assertEqual(before, [assets.sha(self.root / f["source_image_path"]) for f in self.frames])
        first = Image.open(self.root / assets.OUTPUT / "hero_golden_cyclone_001.png")
        sheet = Image.open(self.root / assets.REVIEW / "hero_golden_cyclone_sprite_sheet.png")
        self.assertEqual(first.tobytes(), sheet.crop((0, 0, 384, 384)).tobytes())
        meta = assets.read(self.root / "game_factory/golden_cyclone/v001/metadata/review_assets.json")
        self.assertFalse(meta["owner_approved"])
        self.assertFalse(meta["production_activation"])
        self.assertEqual(meta["uniform_source_scale"], .22)
        self.assertEqual(sum(f["hit"] for f in meta["frames"]), 1)

    def test_gif_rounding_preserves_total_without_drift(self):
        timing = assets.quantize_durations([45] * 22)
        self.assertEqual(sum(timing), 990)
        self.assertEqual(set(timing), {40, 50})
        with self.assertRaises(ValueError):
            assets.quantize_durations([float("nan")])

    def test_paths_cannot_escape_package(self):
        with self.assertRaisesRegex(ValueError, "escapes"):
            assets.local(self.root, "../outside.png")

    def test_godot_export_rejects_stale_scene_receipt(self):
        assets.write(self.root / "game_factory/golden_cyclone/v001/metadata/review_assets.json", {})
        assets.write(self.root / assets.REVIEW / "godot_capture_receipt.json", {
            "actual_viewport": True, "candidate_only": True, "review_assets_sha256": "stale", "modes": {}})
        with self.assertRaisesRegex(ValueError, "Stale Godot capture"):
            assets.encode_godot(self.root)


class PreviewContracts(unittest.TestCase):
    # Python-only CI has no Godot at the owner's path; runs wherever it is installed.
    @unittest.skipUnless(_configured_godot_exists(), "configured godot_executable is not installed here")
    def test_headless_candidate_preview(self):
        code, output = run_godot("res://tools/verify_golden_cyclone_preview.gd", timeout=90)
        self.assertEqual(code, 0, output)
        self.assertIn("GOLDEN_CYCLONE_PREVIEW_OK", output)
        self.assertNotIn("SCRIPT ERROR", output)


if __name__ == "__main__":
    unittest.main()
