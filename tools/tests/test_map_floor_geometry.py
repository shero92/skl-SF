"""Irregular room footprint prevents accidental rectangular floor and invalid overrides."""
from pathlib import Path
import sys,tempfile,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import map_factory_cli as mf
from test_map_factory import fixture

class FloorGeometry(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name);fixture(self.root)
        self.room=mf.bootstrap(self.root,"test_room_01",Path("map_factory/rooms/hero_room.json"))
    def tearDown(self):self.temp.cleanup()
    def test_irregular_replaces_rectangle_and_records_version(self):
        rows=[[[1,3]],[[0,4]],[[0,4]],[[1,3]],[[2,2]]]
        import json
        path=self.root/"map_factory/intake/geometry.json"
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps({"map_id":"test_room_01","base_version":1,
          "changes":[{"op":"set_property","key":"floor_footprint","value":{"row_spans":rows}}]}))
        snap=mf.apply(self.root,path.relative_to(self.root))
        self.assertEqual(snap["layer_stack"]["ground"]["footprint"]["row_spans"],rows)
        self.assertEqual(sum(b-a+1 for row in rows for a,b in row),17)
        self.assertEqual(mf.validate_repository(self.root),[("test_room_01",2)])
    def test_no_tile_override_outside_footprint(self):
        d=dict(self.room)
        d["floor_footprint"]={"row_spans":[[[1,3]] for i in range(5)]}
        d["tile_overrides"]=[{"x":0,"y":0,"id":"F001"}]
        with self.assertRaisesRegex(ValueError,"outside painted"):
            mf.validate_room(d,mf.asset_catalog(self.root))
    def test_invalid_footprint_rows(self):
        d=dict(self.room)
        d["floor_footprint"]={"row_spans":[[[0,2]],[[2,4]]]}
        with self.assertRaisesRegex(ValueError,"match floor height"):
            mf.validate_room(d,mf.asset_catalog(self.root))
    def test_fully_inactive_floor_is_not_valid(self):
        d=dict(self.room)
        d["floor_footprint"]={"row_spans":[[] for i in range(5)]}
        with self.assertRaisesRegex(ValueError,"zero active"):
            mf.validate_room(d,mf.asset_catalog(self.root))
if __name__=="__main__":unittest.main()
