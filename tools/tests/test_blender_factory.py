"""Blender part factory: spec validation, technical QA and (where Blender exists) calibrated renders."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

from PIL import Image, ImageDraw, ImageOps

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import art_qa  # noqa: E402
import blender_factory as bf  # noqa: E402

BLENDER = bf.blender_executable()


def piece(path, shape="L", backing=None):
    im = Image.new("RGBA", (64, 96), backing or (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if shape == "L":
        d.rectangle((8, 8, 30, 88), fill=(200, 160, 100, 255))
        d.rectangle((8, 70, 56, 88), fill=(150, 110, 60, 255))
    else:
        d.ellipse((10, 10, 54, 86), fill=(180, 140, 90, 255))
        d.rectangle((14, 20, 26, 60), fill=(90, 60, 30, 255))
    im.save(path)
    return im


class Specs(unittest.TestCase):
    def test_repository_specs_match_their_art_requests(self):
        for spec_path in sorted(bf.SPECS.glob("ART-*.json")):
            with self.subTest(spec=spec_path.name):
                spec = bf.load_spec(spec_path)
                wanted = [f".agents/graphics/deliveries/{spec['art_id']}/{o['name']}.png" for o in spec["outputs"]]
                self.assertEqual(sorted(wanted), sorted(bf.request_outputs(spec["art_id"])))

    def test_invalid_specs_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.json"
            for spec in ({"outputs": [{"name": "a"}]}, {"builder": "wall_run", "outputs": []},
                         {"builder": "wall_run", "outputs": [{"name": "Bad Name"}]},
                         {"builder": "wall_run", "outputs": [{"name": "a"}, {"name": "a"}]},
                         {"builder": "wall_run", "outputs": [{"name": "a", "facing": "up"}]}):
                path.write_text(json.dumps(spec))
                with self.subTest(spec=spec), self.assertRaises(ValueError):
                    bf.load_spec(path)

    def test_projection_defaults(self):
        proj = json.loads((bf.BLENDER_DIR / "projection.json").read_text(encoding="utf-8"))
        self.assertEqual(proj["tile_px"], 64)
        self.assertGreater(proj["sun"]["azimuth_deg"], 90, "light comes from the upper left")


class ExpectedSimilar(unittest.TestCase):
    def test_only_owner_accepted_pairs_leave_the_warnings(self):
        spec = {"expected_similar": [{"pair": ["wall_east", "wall_west"], "reason": "orthographic side walls"}]}
        qa = {"warnings": ["wall_east.png vs wall_west.png: nearly identical (score 1.9); fine for variants",
                           "wall_north.png vs wall_south.png: nearly identical (score 3.3); fine for variants"]}
        warnings, accepted = bf.split_expected(qa, spec)
        self.assertEqual(warnings, [qa["warnings"][1]])
        self.assertEqual(accepted, [{"warning": qa["warnings"][0], "reason": "orthographic side walls"}])

    def test_expected_similar_needs_known_outputs_and_reason(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.json"
            base = {"builder": "wall_run", "outputs": [{"name": "a"}, {"name": "b"}]}
            for bad in ([{"pair": ["a", "zz"], "reason": "x"}], [{"pair": ["a", "b"]}], [{"pair": ["a"], "reason": "x"}]):
                path.write_text(json.dumps({**base, "expected_similar": bad}))
                with self.subTest(bad=bad), self.assertRaises(ValueError):
                    bf.load_spec(path)


class TechnicalQA(unittest.TestCase):
    def test_clean_pieces_pass_and_copies_are_caught(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = piece(Path(tmp) / "a.png", "L")
            piece(Path(tmp) / "b.png", "O")
            ImageOps.mirror(a).save(Path(tmp) / "mirror.png")
            a.save(Path(tmp) / "copy.png")
            clean = art_qa.check(tmp, ["a.png", "b.png"])
            self.assertEqual(clean["problems"], [])
            self.assertEqual(clean["warnings"], [])
            mirrored = art_qa.check(tmp, ["a.png", "mirror.png"])
            self.assertTrue(any("mirrored/rotated copy" in p for p in mirrored["problems"]), mirrored)
            same = art_qa.check(tmp, ["a.png", "copy.png"])
            self.assertTrue(any("nearly identical" in w for w in same["warnings"]))

    def test_backing_and_missing_files_are_problems(self):
        with tempfile.TemporaryDirectory() as tmp:
            piece(Path(tmp) / "backed.png", "L", backing=(255, 255, 255, 255))
            report = art_qa.check(tmp, ["backed.png", "missing.png"])
            text = " ".join(report["problems"])
            self.assertIn("corners not transparent", text)
            self.assertIn("missing", text)


@unittest.skipUnless(BLENDER, "Blender not installed (CI); runs on the owner's Windows host")
class BlenderRenders(unittest.TestCase):
    def test_calibration_tile_is_exactly_one_tile(self):
        result = bf.calibrate()
        self.assertTrue(result["ok"], result)

    def test_wall_facings_are_real_renders_not_bitmap_copies(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = Path(tmp) / "spec.json"
            spec.write_text(json.dumps({"builder": "wall_run", "projection": {"supersample": 1, "samples": 4},
                                        "params": {"length": 1.0, "height": 2.0, "thickness": 0.5, "seed": 3},
                                        "outputs": [{"name": "n", "facing": "north"}, {"name": "w", "facing": "west"}]}))
            metas = bf.render(spec, Path(tmp) / "out")
            self.assertEqual([m["facing"] for m in metas], ["north", "west"])
            self.assertTrue(all(m["shadow"] for m in metas), "separate shadow pass")
            report = art_qa.check(Path(tmp) / "out", ["n.png", "w.png"])
            self.assertEqual(report["problems"], [], report)
            self.assertNotEqual(metas[0]["frame_px"], metas[1]["frame_px"], "a side wall frames differently")


if __name__ == "__main__":
    unittest.main()
