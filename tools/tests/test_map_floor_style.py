"""Stone tile crop retains source PNGs while improving floor texture placement."""
from pathlib import Path
import sys,tempfile,unittest,json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import map_factory_cli as mf
from test_map_factory import fixture

class FloorStyle(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        fixture(self.root)
        records=json.loads((self.root/mf.CATALOG).read_text())
        for r in records["assets"]:
            if r["category"]=="floors":r["pixel_size"]=[162,161]
        (self.root/mf.CATALOG).write_text(json.dumps(records))
        self.snap=mf.bootstrap(self.root,"test_room_01",Path("map_factory/rooms/hero_room.json"))
    def tearDown(self):self.temp.cleanup()
    def test_floor_style_compiles_without_mutating_pngs(self):
        config={"enabled":True,"tile_ids":["F001","F002"],"crop_insets":[9,9,9,16],
           "joint_color":"#817264","joint_opacity":0.2,"joint_width":1.1}
        self.snap["floor_tile_style"]=config
        self.snap.pop("layer_stack",None)
        mf.validate_room(self.snap,mf.asset_catalog(self.root))
        from map_factory_layers import create_layer_stack
        self.assertEqual(create_layer_stack(self.snap,mf.asset_catalog(self.root))["ground"]["floor_tile_style"],config)
    def test_reject_aggressive_crop(self):
        self.snap["floor_tile_style"]={"enabled":True,"tile_ids":["F001"],"crop_insets":[100,20,100,20],
            "joint_color":"#888888","joint_opacity":.2,"joint_width":1.0}
        with self.assertRaisesRegex(ValueError,"entire tile"):
            mf.validate_room(self.snap,mf.asset_catalog(self.root))
if __name__=="__main__":unittest.main()
