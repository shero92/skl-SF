import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import map_factory_cli as cli


class CameraLightShaftTests(unittest.TestCase):
    def test_camera_valid_and_invalid(self):
        cli.validate_camera({"x": 768, "y": 512, "zoom": 1.5})
        for bad in ({"x": 1}, {"x": 1, "y": 1, "zoom": 9}, {"x": "a", "y": 1}, []):
            with self.assertRaises(ValueError):
                cli.validate_camera(bad)

    def test_light_shafts_rules(self):
        good = {"instance_id": "S1", "points": [[0, 0], [10, 0], [5, 9]], "color": "#fff0b0", "opacity": 0.1, "blend": "add"}
        cli.validate_light_shafts([good], set())
        for patch in ({"points": [[0, 0], [1, 1]]}, {"color": "red"}, {"opacity": 2}, {"blend": "screen"}):
            with self.assertRaises(ValueError):
                cli.validate_light_shafts([{**good, **patch}], set())
        with self.assertRaises(ValueError):
            cli.validate_light_shafts([good], {"S1"})

    def test_shadow_mode_and_lighting_rules(self):
        cli.validate_shadow_mode("painted")
        cli.validate_shadow_mode("strips")
        with self.assertRaises(ValueError):
            cli.validate_shadow_mode("fancy")
        cli.validate_lighting({"direction": [0.9, 0.3], "length": 0.5, "opacity": 0.4, "blur": 1,
                               "color": [0.1, 0.1, 0.3], "light_pools": True})
        for bad in ([], {"nope": 1}, {"opacity": 2}, {"blur": 9}, {"direction": [0, 0]},
                    {"direction": [1]}, {"color": [2, 0, 0]}, {"light_pools": "yes"}, {"length": True}):
            with self.assertRaises(ValueError):
                cli.validate_lighting(bad)


if __name__ == "__main__":
    unittest.main()
