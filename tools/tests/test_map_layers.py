"""The five-level environmental map schema and mount/shadow relationships."""
from pathlib import Path
import tempfile,unittest,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import map_factory_cli as mf
from map_factory_layers import create_layer_stack, PASS_NAMES
from test_map_factory import fixture

class FiveLevelMap(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        fixture(self.root)
        self.base=mf.bootstrap(self.root,"hero_room_01",Path("map_factory/rooms/hero_room.json"))
        self.wid=self.base["back_objects"][0]["instance_id"]
        self.pid=self.base["objects"][0]["instance_id"]
    def tearDown(self):
        self.temp.cleanup()
    def _patch(self,items):
        path=self.root/"map_factory/intake/pending/edit.json"
        path.parent.mkdir(exist_ok=True,parents=True)
        import json
        path.write_text(json.dumps({"map_id":"hero_room_01","base_version":1,"changes":items}))
        return path.relative_to(self.root)
    def test_compiled_five_passes_and_owner_shadow(self):
        self.assertEqual(tuple(self.base["layer_stack"]["processing_passes"]),PASS_NAMES)
        patch=self._patch([
          {"op":"update_block","instance_id":self.pid,"set":{
             "mount_on":self.wid,"mount_offset":[17,33],
             "shadow":{"type":"contact_medium","opacity":0.37,"offset_x":4,"offset_y":5}}},
          {"op":"update_block","instance_id":self.wid,"set":{"x":150,"y":200}}
        ])
        result=mf.apply(self.root,patch)
        stack=result["layer_stack"]
        self.assertEqual(stack["counts"]["walls"],1)
        self.assertEqual(stack["counts"]["decorations"],1)
        self.assertEqual(stack["counts"]["shadows"],1)
        prop=stack["passes"]["decorations"][0]
        self.assertEqual(prop["position"],[167.0,233.0])
        self.assertEqual(prop["attachment"]["parent_instance_id"],self.wid)
        self.assertEqual(stack["passes"]["shadows"][0]["owner_instance_id"],self.pid)
        self.assertEqual(stack["display_z"]["shadows"],20)
        self.assertEqual(mf.validate_repository(self.root),[("hero_room_01",2)])
        stored=mf.read(self.root,mf.map_base("hero_room_01")/"layers"/"latest.json")
        self.assertEqual(stored,stack)
    def test_parent_move_recalculates_attachment(self):
        path=self._patch([
         {"op":"update_block","instance_id":self.pid,"set":{"mount_on":self.wid,"mount_offset":[5,-10]}}
        ])
        mf.apply(self.root,path)
        link=self.root/"map_factory/intake/pending/move.json"
        import json
        link.write_text(json.dumps({"map_id":"hero_room_01","base_version":2,"changes":[
         {"op":"update_block","instance_id":self.wid,"set":{"x":300,"y":230}}]}))
        v3=mf.apply(self.root,link.relative_to(self.root))
        self.assertEqual(v3["layer_stack"]["passes"]["decorations"][0]["position"],[305.0,220.0])
    def test_reject_unknown_mount(self):
        p=self._patch([{"op":"update_block","instance_id":self.pid,"set":{
            "mount_on":"NoSuchWall","mount_offset":[4,4]}}])
        with self.assertRaisesRegex(ValueError,"Mount target not found"):
            mf.apply(self.root,p)
    def test_reject_cyclic_mount(self):
        p=self._patch([{"op":"add_block","layer":"objects","block":{
            "id":"P002","instance_id":"MountedShelf","x":1,"y":1,
            "mount_on":self.pid,"mount_offset":[1,1]}},
            {"op":"update_block","instance_id":self.pid,
             "set":{"mount_on":"MountedShelf","mount_offset":[2,2]}}])
        with self.assertRaisesRegex(ValueError,"Cyclic mount"):
            mf.apply(self.root,p)
    def test_reject_tampered_layer_stack(self):
        broken=dict(self.base)
        bad=dict(broken["layer_stack"])
        bad["quality_status"]="approved_without_review"
        broken["layer_stack"]=bad
        with self.assertRaisesRegex(ValueError,"layer_stack differs"):
            mf.validate_room(broken,mf.asset_catalog(self.root))
    def test_historic_versions_remain_immutable(self):
        version1=mf.read(self.root,mf.version_file("hero_room_01",1))
        patch=self._patch([{"op":"add_block","layer":"front_objects",
            "block":{"id":"P002","instance_id":"Chair","x":200,"y":200}}])
        mf.apply(self.root,patch)
        self.assertEqual(version1,mf.read(self.root,mf.version_file("hero_room_01",1)))

if __name__=="__main__":
    unittest.main()
