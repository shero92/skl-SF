"""Discovered evidence validation tests; no Godot or image generation required."""
import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "capture_evidence", ROOT / "tools" / "hero_room_capture_evidence.py")
capture = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(capture)


class CaptureEvidenceTests(unittest.TestCase):
    def test_invalid_version_rejected_before_accessing_target(self):
        for version in (0, -1, 12, 13, True):
            with self.subTest(version=version), self.assertRaises(ValueError):
                capture.prepare(ROOT, version, Path("absent"), "review_test")

    def test_missing_png_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(OSError):
                capture.png_size(Path(directory) / ("missing" + ".png"))

    def test_invalid_png_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ("invalid" + ".png")
            path.write_bytes(b"not an image")
            with self.assertRaises(ValueError):
                capture.png_size(path)

    def test_missing_provenance_fails_before_render_access(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            capture.write_new(output / ("render" + ".json"), {})
            request = {
                "capture_id": "review_test", "commit": "abc",
                "target_sha256": capture.TARGET_HASH,
                "cases": [{"file": "render" + ".png", "id": "hero_room_01",
                           "version": 14, "snapshot_sha256": "def"}],
            }
            with self.assertRaisesRegex(ValueError, "Invalid provenance"):
                capture.verify(output, output, request)

    def test_existing_evidence_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ("receipt" + ".json")
            capture.write_new(path, {"original": True})
            with self.assertRaises(FileExistsError):
                capture.write_new(path, {})
            self.assertEqual(capture.read_json(path), {"original": True})

    def test_character_and_reference_paths_rejected(self):
        for name in ("assets/characters/example.png", "assets/neru_idle.png",
                     "references/room.png", "assets/hero.png"):
            with self.subTest(name=name):
                self.assertTrue(capture.forbidden_texture(name))
        self.assertFalse(capture.forbidden_texture("environment/bed.png"))

    def test_resource_cannot_escape_root(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                capture.resource(Path(directory), "../outside")

    def test_router_registers_discovered_suite(self):
        router = capture.read_json(ROOT / "tools" / "test_map.json")
        entry = next(t for t in router["tests"]
                     if t["id"] == "hero_room_capture_evidence")
        self.assertEqual(entry["kind"], "python")
        self.assertIn("discover", entry["command"])
        self.assertIn("test_hero_room_capture_evidence.py", entry["command"])


class AllowlistExtensionTests(unittest.TestCase):
    def test_hd_runtime_twins_follow_the_hd_map(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "assets_hd").mkdir()
            (root / "assets_hd" / "hd_map.json").write_text(
                '{"map": {"floor/G01__floor.png": {"master": "x"}}}', encoding="utf-8")
            base = {"assets_generated/floor/G01__floor.png", "assets_generated/floor/G02__floor.png",
                    "map_factory/parts/shadows/S1.png"}
            self.assertEqual(capture.hd_runtime_paths(root, base), {"assets_hd/runtime/G01__floor.png"})
            self.assertEqual(capture.hd_runtime_paths(root / "nowhere", base), set())

    def test_parts_library_paths_only_registered_parts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "map_factory" / "metadata").mkdir(parents=True)
            (root / "map_factory" / "metadata" / "asset_index.json").write_text(
                '{"assets": [{"texture_path": "res://map_factory/parts/shadows/S1.png"},'
                ' {"texture_path": "res://elsewhere/X.png"}]}', encoding="utf-8")
            self.assertEqual(capture.parts_library_paths(root), {"map_factory/parts/shadows/S1.png"})

    def test_real_registry_allows_hd_and_parts(self):
        assets = capture.read_json(ROOT / "map_factory" / "metadata" / "environment_assets_v2.json")
        base = capture.texture_paths(assets)
        self.assertGreater(len(capture.parts_library_paths(ROOT)), 50)
        if (ROOT / "assets_hd" / "hd_map.json").is_file():
            self.assertTrue(capture.hd_runtime_paths(ROOT, base))


if __name__ == "__main__":
    unittest.main()
