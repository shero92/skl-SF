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

    def test_candidate_specs_load(self):
        specs = sorted((bf.SPECS / "candidates").glob("*.json"))
        self.assertTrue(specs)
        for spec_path in specs:
            with self.subTest(spec=spec_path.name):
                spec = bf.load_spec(spec_path)
                self.assertTrue(spec.get("candidate"))

    def test_connected_shell_options_are_enabled(self):
        # TASK-0063: connected caps/quoins, cliff contacts, stair newels, cobalt-gold dial and post plinths.
        wanted = {"ART-0004": ("connect_caps", "quoins"), "ART-0014": ("cliff",), "ART-0022": ("cobalt_ticks",),
                  "ART-0024": ("plinth",), "ART-0025": ("newel",)}
        for art_id, keys in wanted.items():
            params = bf.load_spec(bf.SPECS / f"{art_id}.json")["params"]
            for key in keys:
                with self.subTest(art=art_id, key=key):
                    self.assertTrue(params.get(key), key)
        v5 = bf.load_spec(bf.SPECS / "candidates/hero_room_01_v5_side_walls.json")
        self.assertTrue(v5["params"]["coping"])
        self.assertTrue((bf.SPECS / "candidates/hero_room_01_v4_side_walls.json").exists(), "previous version kept")

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


class Downscale(unittest.TestCase):
    def test_native_downscale_has_no_dark_halo(self):
        # Transparent pixels carry black RGB; resampling must not bleed it into anti-aliased edges.
        with tempfile.TemporaryDirectory() as tmp:
            master = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
            ImageDraw.Draw(master).ellipse((30, 30, 226, 226), fill=(230, 190, 120, 255))
            master.save(Path(tmp) / "m.png")
            bf.downscale(Path(tmp) / "m.png", Path(tmp) / "n.png", 4)
            native = Image.open(Path(tmp) / "n.png")
            self.assertEqual(native.size, (64, 64))
            soft = [p for p in native.getdata() if 32 <= p[3] < 200]  # below ~32 alpha colour is unrecoverable
            self.assertTrue(soft, "anti-aliased edge expected")
            self.assertGreater(min(p[0] for p in soft), 200, "edge pixels keep the shape colour, no dark fringe")
            self.assertEqual(art_qa.check(tmp, ["n.png"])["files"][0]["halo_fraction"], 0.0)

    def test_halo_means_contrast_with_neighbours_not_dark_geometry(self):
        with tempfile.TemporaryDirectory() as tmp:
            dark = Image.new("RGBA", (40, 40), (0, 0, 0, 0))
            d = ImageDraw.Draw(dark)
            d.rectangle((10, 10, 29, 29), fill=(30, 22, 15, 255))   # dark shaded face
            d.rectangle((9, 9, 30, 30), outline=(5, 4, 3, 120))     # soft edge as dark as its face
            dark.save(Path(tmp) / "dark.png")
            halo = Image.new("RGBA", (40, 40), (0, 0, 0, 0))
            d = ImageDraw.Draw(halo)
            d.rectangle((10, 10, 29, 29), fill=(220, 180, 110, 255))  # bright stone
            d.rectangle((9, 9, 30, 30), outline=(0, 0, 0, 120))       # black fringe around it
            halo.save(Path(tmp) / "halo.png")
            report = art_qa.check(tmp, ["dark.png", "halo.png"])
            files = {Path(f["path"]).name: f for f in report["files"]}
            self.assertEqual(files["dark.png"]["problems"], [])
            self.assertTrue(any("halo" in p for p in files["halo.png"]["problems"]))


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


class PaletteQA(unittest.TestCase):
    def test_grey_stone_is_a_problem_and_golden_stone_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            check = {"min_saturation": 0.3, "hue_deg": [20, 50]}
            for colour, bad in (((150, 146, 140), True), ((176, 128, 62), False), ((60, 90, 170), True)):
                path = Path(tmp) / "p.png"
                Image.new("RGBA", (8, 8), (*colour, 255)).save(path)
                stats = bf.palette(path)
                with self.subTest(colour=colour):
                    self.assertEqual(bool(bf.palette_problems("p.png", stats, check)), bad, stats)
            self.assertEqual(bf.palette_problems("p.png", stats, None), [])

    def test_two_colour_piece_uses_pixel_saturation(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "inlay.png"
            im = Image.new("RGBA", (8, 8), (40, 60, 200, 255))
            ImageDraw.Draw(im).rectangle((0, 0, 7, 3), fill=(200, 160, 40, 255))
            im.save(path)
            stats = bf.palette(path)
            self.assertLess(stats["saturation"], stats["pixel_saturation"], "blue + gold average toward grey")
            self.assertEqual(bf.palette_problems("inlay.png", stats, {"min_pixel_saturation": 0.35}), [])
            self.assertEqual(stats["opaque_size"], [8, 8])


@unittest.skipUnless(BLENDER, "Blender not installed (CI); runs on the owner's Windows host")
class BlenderRenders(unittest.TestCase):
    def test_calibration_tile_is_exactly_one_tile(self):
        result = bf.calibrate()
        self.assertTrue(result["ok"], result)

    def test_side_wall_lean_keeps_the_foot_and_shifts_the_top_outward(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = Path(tmp) / "spec.json"
            spec.write_text(json.dumps({"builder": "wall_run", "projection": {"supersample": 1, "samples": 4},
                                        "params": {"length": 1.0, "height": 2.0, "thickness": 0.5, "seed": 3, "ivy": False},
                                        "outputs": [{"name": "w", "facing": "west", "params": {"lean": -0.4}},
                                                    {"name": "e", "facing": "east", "params": {"lean": 0.4}}]}))
            west, east = bf.render(spec, Path(tmp) / "out")
            for meta, sign in ((west, -1), (east, 1)):
                foot, top = meta["anchors_px"]["foot_center_front"], meta["anchors_px"]["top_center_front"]
                self.assertAlmostEqual((top[0] - foot[0]) * sign, 0.4 * 2.0 * 64, delta=2.0, msg=meta["name"])
            report = art_qa.check(Path(tmp) / "out", ["w.png", "e.png"])
            self.assertEqual(report["problems"], [], report)
            self.assertEqual(report["warnings"], [], "leaning side walls show different inner faces")

    def test_side_wall_path_is_one_mesh_standing_on_every_floor_step(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = Path(tmp) / "spec.json"
            path = [[1, 0], [1, -1], [0, -1], [0, -2]]
            spec.write_text(json.dumps({"builder": "side_wall_path", "projection": {"supersample": 1, "samples": 4},
                                        "params": {"path": path, "inside": "left", "height": 0.8, "thickness": 0.3,
                                                   "lean": -0.2, "seed": 2, "ivy": False, "rubble": 0},
                                        "outputs": [{"name": "s", "facing": "west"}]}))
            meta = bf.render(spec, Path(tmp) / "out")[0]
            ox, oy = meta["anchors_px"]["grid_origin"]
            alpha = Image.open(Path(tmp) / "out/s.png").getchannel("A")
            # Just outside each segment's floor-edge midpoint, a little above the floor, there is wall.
            for (x0, y0), (x1, y1), out in zip(path, path[1:], ((-1, 0), (0, 1), (-1, 0))):
                mx, my = (x0 + x1) / 2 + out[0] * 0.15, (y0 + y1) / 2 + out[1] * 0.15
                px, py = ox + mx * 64 - 0.2 * 0.3 * 64, oy - my * 64 - 0.3 * 64
                self.assertGreater(alpha.getpixel((round(px), round(py))), 200, (x0, y0, x1, y1))

    def test_v4_pieces_match_their_calibrated_sizes_and_anchors(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = Path(tmp) / "spec.json"
            spec.write_text(json.dumps({"builder": "compass_inlay", "projection": {"supersample": 1, "samples": 4},
                                        "outputs": [{"name": "inlay", "shadow": False},
                                                    {"name": "stairs", "builder": "entrance_stairs", "shadow": False},
                                                    {"name": "fence", "builder": "rope_fence",
                                                     "params": {"posts": [[0, 0], [-1.0, 1.5]]}}]}))
            inlay, stairs, fence = bf.render(spec, Path(tmp) / "out")
            box = Image.open(Path(tmp) / "out/inlay.png").getchannel("A").point(lambda v: 255 if v > 24 else 0).getbbox()
            self.assertAlmostEqual(box[2] - box[0], 267, delta=4, msg="ART-0022 rhombus width")
            self.assertAlmostEqual(box[3] - box[1], 259, delta=4, msg="ART-0022 rhombus height")
            cx, cy = inlay["anchors_px"]["center"]
            self.assertAlmostEqual(cx, (box[0] + box[2]) / 2, delta=2)
            alpha = Image.open(Path(tmp) / "out/stairs.png").getchannel("A")
            top = stairs["anchors_px"]["top_center"]
            self.assertGreater(alpha.getpixel((round(top[0]), round(top[1]) + 100)), 200, "3 steps reach ~105 px below the edge")
            front, back = fence["anchors_px"]["front_post_foot"], fence["anchors_px"]["back_post_foot"]
            self.assertAlmostEqual(front[0] - back[0], 64, delta=1)
            self.assertAlmostEqual(front[1] - back[1], 96, delta=1)
            self.assertLess(fence["frame_px"][0], 200, "rope curve bounds do not bloat the frame")

    def test_cliff_depth_variants_and_stair_newel_anchors(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = Path(tmp) / "spec.json"
            spec.write_text(json.dumps({"builder": "broken_floor_edge", "projection": {"supersample": 1, "samples": 4},
                                        "params": {"kind": "edge", "seed": 11},
                                        "outputs": [{"name": "c8", "params": {"cliff": 0.8}},
                                                    {"name": "c10", "params": {"cliff": 1.0}},
                                                    {"name": "stairs", "builder": "entrance_stairs", "shadow": False,
                                                     "params": {"newel": 0.36}}]}))
            c8, c10, stairs = bf.render(spec, Path(tmp) / "out")
            h8 = Image.open(Path(tmp) / "out/c8.png").getchannel("A").getbbox()
            h10 = Image.open(Path(tmp) / "out/c10.png").getchannel("A").getbbox()
            self.assertGreater(h10[3] - h10[1], h8[3] - h8[1], "10-deep cliff is taller than the 8-deep one")
            left, right = stairs["anchors_px"]["post_left"], stairs["anchors_px"]["post_right"]
            self.assertAlmostEqual(left[1], right[1], delta=1, msg="newels share one seam row")
            self.assertGreater(right[0] - left[0], 150)

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
