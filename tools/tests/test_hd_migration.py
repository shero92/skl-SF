"""Tests for the retirement of the low-quality assets_generated twins (TASK-0117).

Execution provenance: Agent: claude (Claude Code); model: Sonnet 5.5.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

from PIL import Image

TOOLS = Path(__file__).resolve().parents[1]
ROOT = TOOLS.parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import build_hero_room_blueprint as blueprint
import migrate_low_to_hd as migrate

HD_MAP = json.loads((ROOT / "assets_hd" / "hd_map.json").read_text(encoding="utf-8"))


class HdMigrationTests(unittest.TestCase):
    def test_every_entry_carries_layout_data(self):
        for relative, record in HD_MAP["map"].items():
            for field in ("native_size", "visible_bbox", "low_sha256", "measure"):
                self.assertIn(field, record, (relative, field))
            self.assertEqual(len(record["low_sha256"]), 64)
            self.assertEqual(record["measure"]["size"], record["native_size"])

    def test_runtime_twin_is_scale_times_native_size(self):
        scale = int(HD_MAP["scale"])
        for relative, record in HD_MAP["map"].items():
            twin = ROOT / "assets_hd" / "runtime" / Path(relative).name
            with Image.open(twin) as image:
                self.assertEqual(list(image.size), [v * scale for v in record["native_size"]], relative)

    def test_measure_matches_the_blueprint_measurement(self):
        image = Image.new("RGBA", (64, 128), (0, 0, 0, 0))
        for x in range(10, 40):
            for y in range(20, 100):
                image.putpixel((x, y), (200, 100, 50, 255))
        self.assertEqual(migrate.measure(image), blueprint.measure_png_image(image))

    def test_blueprint_reads_retired_files_from_hd_map(self):
        relative, record = next(iter(HD_MAP["map"].items()))
        missing = ROOT / "assets_generated" / relative
        if missing.is_file():
            self.skipTest("original still present")
        self.assertEqual(blueprint.measure_png(missing), record["measure"])
        self.assertTrue(blueprint.texture_available(missing))
        self.assertFalse(blueprint.texture_available(ROOT / "assets_generated" / "nowhere" / "x.png"))


if __name__ == "__main__":
    unittest.main()
