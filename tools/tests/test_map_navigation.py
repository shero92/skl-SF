"""Map navigability metadata is validated, never used to modify characters."""
import sys
from pathlib import Path
import unittest
from test_map_factory import Maps
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import map_factory_cli as mf

class MapNavigation(unittest.TestCase):
    def setUp(self):
        # Reuse one isolated map factory fixture, with no game character changes.
        self.fixture=Maps("test_bootstrap_excludes_characters_and_gameplay")
        self.fixture.setUp()
        self.root=self.fixture.root
        self.snapshot=mf.get_latest(self.root,"hero_room_01")
        self.map={
          "schema_version":1,
          "origin":[0,0],
          "grid_size":[5,5],
          "cell_size":64,
          "default":{"walk":False,"fly":False,"swim":False},
          "regions":[
            {"id":"stone_floor","rect":[0,0,4,4],"surface":"stone",
             "allow":["walk","fly"],"floor_height":0,"ceiling_height":None,
             "requires":{"fly":[]}, "review_status":"needs_review"},
            {"id":"water_edge","rect":[0,4,5,1],"surface":"water",
             "allow":["swim","fly"],"floor_height":-15,"ceiling_height":None,
             "requires":{"swim":["can_swim"]}}
          ],
          "obstacles":[
            {"instance_id":self.snapshot["objects"][0]["instance_id"],
             "blocks":["walk","fly"],"min_altitude":0,"max_altitude":80}],
          "links":[{"id":"stair_link","from":[1,1],"to":[1,2],
                    "modes":["walk"],"requires":[]}]
        }
    def tearDown(self):
        self.fixture.tearDown()
    def test_valid_map_navigation_patch_versions(self):
        path=self.fixture.make_patch([
          {"op":"set_property","key":"navigation","value":self.map},
          {"op":"set_property","key":"visual_qa","value":{"status":"needs_review"}}])
        result=mf.apply(self.root,path)
        self.assertIn("navigation",result)
        self.assertEqual(result["version"],2)
        self.assertEqual(mf.validate_repository(self.root),[("hero_room_01",2)])
    def test_rejects_unsafe_default(self):
        self.map["default"].pop("fly")
        self.snapshot["navigation"]=self.map
        with self.assertRaisesRegex(ValueError,"default"):
            mf.validate_room(self.snapshot,mf.asset_catalog(self.root))
    def test_rejects_region_beyond_grid(self):
        self.map["regions"][0]["rect"]=[4,4,5,5]
        self.snapshot["navigation"]=self.map
        with self.assertRaisesRegex(ValueError,"out of bounds"):
            mf.validate_room(self.snapshot,mf.asset_catalog(self.root))
    def test_rejects_unknown_obstacle(self):
        self.map["obstacles"][0]["instance_id"]="FakeWall_008"
        self.snapshot["navigation"]=self.map
        with self.assertRaisesRegex(ValueError,"unknown block"):
            mf.validate_room(self.snapshot,mf.asset_catalog(self.root))
    def test_rejects_unreviewed_visual_approval(self):
        self.snapshot["visual_qa"]={"status":"approved"}
        with self.assertRaisesRegex(ValueError,"requires"):
            mf.validate_room(self.snapshot,mf.asset_catalog(self.root))

if __name__ == "__main__":
    unittest.main()
