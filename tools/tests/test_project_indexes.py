"""Regression tests for tiny on-demand project file inventory."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from generate_project_indexes import render


class IndexGenerationTests(unittest.TestCase):
    def test_direct_children_and_nested_paths(self):
        generated = render([
            "README.md", "tools/build.py", "tools/tests/test_me.py",
            "map_factory/parts/floors/F001_Stone_Floor.png"])
        self.assertIn("FILES.md", generated)
        self.assertIn("tools/FILES.md", generated)
        self.assertIn("tools/tests/FILES.md", generated)
        self.assertIn("map_factory/parts/floors/FILES.md", generated)
        self.assertIn("[`tools/`](tools/FILES.md)", generated["FILES.md"])
        self.assertIn("[`build.py`](build.py)", generated["tools/FILES.md"])
        self.assertNotIn("test_me.py", generated["tools/FILES.md"])
        self.assertIn("F001_Stone_Floor.png", generated["map_factory/parts/floors/FILES.md"])
        self.assertNotIn("build.py", generated["map_factory/parts/floors/FILES.md"])

    def test_order_independent(self):
        paths = ["docs/b.md", "docs/a.md", "project.godot"]
        self.assertEqual(render(paths), render(list(reversed(paths))))


if __name__ == "__main__":
    unittest.main()
