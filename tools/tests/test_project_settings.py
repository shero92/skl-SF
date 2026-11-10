"""Project display and renderer settings that keep the game startable on Windows.

Execution provenance: Agent: claude (Claude Code); model: Sonnet 5.5.
"""
from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SETTINGS = (ROOT / "project.godot").read_text(encoding="utf-8")


class ProjectSettingsTests(unittest.TestCase):
    def test_windows_uses_the_angle_driver(self):
        # The native OpenGL driver stopped opening a window on the owner's PC (silent exit, no
        # window); ANGLE (OpenGL over Direct3D11) starts reliably with the same NVIDIA card.
        self.assertIn('gl_compatibility/driver.windows="opengl3_angle"', SETTINGS)

    def test_compatibility_renderer_and_windowed_mode(self):
        self.assertIn('renderer/rendering_method="gl_compatibility"', SETTINGS)
        self.assertIn("window/size/mode=0", SETTINGS)
        self.assertIn("window/size/window_width_override=1280", SETTINGS)

    def test_main_scene_exists(self):
        self.assertIn('run/main_scene="res://scenes/main.tscn"', SETTINGS)
        self.assertTrue((ROOT / "scenes" / "main.tscn").is_file())


if __name__ == "__main__":
    unittest.main()
