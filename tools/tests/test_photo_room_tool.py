"""Photo room authoring tool: new, check, preview. The hero room file must stay valid.

Execution provenance: Agent: claude (Claude Code); model: Sonnet 5.5.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[1]
ROOT = TOOLS.parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import photo_room_tool as tool


class PhotoRoomToolTests(unittest.TestCase):
    def test_hero_room_file_is_valid(self):
        data = json.loads(tool.photo_path("hero_room_01").read_text(encoding="utf-8"))
        self.assertEqual(tool.check_room(data), [])

    def test_new_room_starts_empty_and_check_asks_for_walk_squares(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "pictures").mkdir()
            Image.new("RGB", (640, 480), (90, 140, 200)).save(root / "pictures" / "hall.png")
            target = tool.new_room("hall", "pictures/hall.png", root, create_map=False)
            data = json.loads(target.read_text(encoding="utf-8"))
            self.assertEqual(data["navigation"]["grid_size"], [20, 15])
            self.assertEqual(data["hero_step"], 64)
            problems = tool.check_room(data, root)
            self.assertTrue(any("nobody can walk" in line for line in problems))
            with self.assertRaises(ValueError):
                tool.new_room("hall", "pictures/hall.png", root, create_map=False)
            data["navigation"]["regions"].append({"rect": [2, 2, 5, 4], "allow": ["walk"]})
            data["depth_objects"].append({"id": "pillar", "base_y": 200, "poly": [[100, 50], [140, 50], [140, 200], [100, 200]],
                                          "shadow": [[100, 140, 200, 80]]})
            self.assertEqual(tool.check_room(data, root), [])
            picture = tool.preview(data, root / "overlay.png", root)
            self.assertEqual(Image.open(picture).size, (640, 480))

    def test_check_finds_broken_numbers(self):
        data = json.loads(tool.photo_path("hero_room_01").read_text(encoding="utf-8"))
        data["navigation"]["regions"].append({"rect": [60, 60, 5, 5], "allow": ["walk"]})
        data["depth_objects"].append({"id": "bed", "base_y": 5, "poly": [[0, 0], [10, 0]]})
        data["surprise"] = 1
        text = "\n".join(tool.check_room(data))
        self.assertIn("outside the grid", text)
        self.assertIn("repeated", text)
        self.assertIn("at least 3 points", text)
        self.assertIn("unknown key", text)


if __name__ == "__main__":
    unittest.main()
