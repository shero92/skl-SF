"""Target-vs-game region report: difference numbers, change against the previous version, sheet and files.

Execution provenance: Agent: claude (Claude Code); model: Fable 5.2.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

from PIL import Image

TOOLS = Path(__file__).resolve().parents[1]
ROOT = TOOLS.parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import room_region_report as rr

SPEC = {"map_id": "demo", "target": "t.png",
        "regions": [{"id": "left", "label": "Left", "box": [0, 0, 40, 40]},
                    {"id": "right", "label": "Right", "box": [40, 0, 80, 40], "art_request": "ART-9999"}]}


def picture(left, right):
    image = Image.new("RGB", (80, 40), left)
    image.paste(Image.new("RGB", (40, 40), right), (40, 0))
    return image


class RegionReportTests(unittest.TestCase):
    def test_difference_scale(self):
        black, white = Image.new("RGB", (16, 16), (0, 0, 0)), Image.new("RGB", (16, 16), (255, 255, 255))
        self.assertEqual(rr.difference(black, black), 0.0)
        self.assertEqual(rr.difference(black, white), 100.0)

    def test_report_names_the_region_that_differs_and_the_change(self):
        target = picture((200, 180, 120), (30, 60, 200))
        game = picture((200, 180, 120), (230, 60, 0))
        report, sheet = rr.build_report(SPEC, target, game, 2, {"version": 1, "overall_difference": 50.0,
                                                                "regions": [{"id": "right", "difference": 80.0}]})
        left, right = report["regions"]
        self.assertEqual(left["difference"], 0.0)
        self.assertGreater(right["difference"], 30)
        self.assertEqual(right["change"], round(right["difference"] - 80.0, 2))
        self.assertNotIn("change", left)
        self.assertEqual(right["art_request"], "ART-9999")
        self.assertIs(report["visual_approval"], False)
        self.assertEqual(report["previous_version"], 1)
        self.assertEqual(sheet.width, 88)
        with self.assertRaises(ValueError):
            rr.build_report(SPEC, target, Image.new("RGB", (10, 10)), 2)

    def test_write_report_finds_the_capture_and_the_previous_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "map_factory/references").mkdir(parents=True)
            (root / "map_factory/references/demo_regions.json").write_text(json.dumps(SPEC), encoding="utf-8")
            picture((10, 10, 10), (10, 10, 10)).save(root / "t.png")
            for version, colour in ((1, (250, 250, 250)), (2, (60, 60, 60))):
                folder = root / rr.RENDERS / f"cap{version}"
                folder.mkdir(parents=True)
                picture((10, 10, 10), colour).save(folder / f"demo_v{version:04d}.png")
                out = rr.write_report("demo", version, root=root)
            report = json.loads((out / "report.json").read_text(encoding="utf-8"))
            self.assertTrue((out / "sheet.png").is_file())
            self.assertEqual(report["capture"], "docs/previews/map_factory_renders/cap2/demo_v0002.png")
            self.assertLess(report["overall_change"], 0)  # version 2 is closer to the target than version 1
            with self.assertRaises(FileNotFoundError):
                rr.find_capture("demo", 9, root)

    def test_hero_room_regions_fit_the_target(self):
        spec = rr.load_regions("hero_room_01")
        with Image.open(ROOT / spec["target"]) as target:
            width, height = target.size
        ids = [r["id"] for r in spec["regions"]]
        self.assertEqual(len(ids), len(set(ids)))
        for region in spec["regions"]:
            left, top, right, bottom = region["box"]
            self.assertTrue(0 <= left < right <= width and 0 <= top < bottom <= height, region["id"])


if __name__ == "__main__":
    unittest.main()
