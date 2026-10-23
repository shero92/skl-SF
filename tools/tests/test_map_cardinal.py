"""Block facing remains stable in map JSON and rotates mounted details/collision."""
from pathlib import Path
import tempfile, unittest, sys, json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import map_factory_cli as mf
from map_factory_orientation import FACINGS, resolve_orientation, rotate_offset
from test_map_factory import fixture

class FourDirections(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        fixture(self.root)
        self.room=mf.bootstrap(self.root,"demo_01",Path("map_factory/rooms/hero_room.json"))
        self.wall=self.room["back_objects"][0]["instance_id"]
        self.bed=self.room["objects"][0]["instance_id"]
        self.catalog=mf.asset_catalog(self.root)
    def tearDown(self):
        self.temp.cleanup()
    def _patch(self,ops):
        f=self.root/"map_factory/intake/pending/turn.json"
        f.parent.mkdir(parents=True,exist_ok=True)
        f.write_text(json.dumps({"map_id":"demo_01","base_version":1,"changes":ops}))
        return f.relative_to(self.root)
    def test_all_four_rotate_quadrants(self):
        for ix,face in enumerate(FACINGS):
            obj={"id":"P001","facing":face,"orientation_mode":"rotate"}
            meta=resolve_orientation(obj,self.catalog)
            self.assertEqual(meta["turn_quarters"],ix)
            self.assertEqual(meta["resolved_asset_id"],"P001")
        self.assertEqual(rotate_offset([15,8],1),[-8.0,15.0])
        self.assertEqual(rotate_offset([15,8],2),[-15.0,-8.0])
        self.assertEqual(rotate_offset([15,8],3),[8.0,-15.0])
    def test_rotating_wall_turns_mounted_lantern_offset(self):
        patch=self._patch([
          {"op":"update_block","instance_id":self.wall,
           "set":{"facing":"east","orientation_mode":"rotate","x":140,"y":160}},
          {"op":"update_block","instance_id":self.bed,
           "set":{"mount_on":self.wall,"mount_offset":[30,10],"facing":"south","orientation_mode":"rotate"}}])
        v2=mf.apply(self.root,patch)
        stack=v2["layer_stack"]
        wall=stack["passes"]["walls"][0]
        bed=stack["passes"]["decorations"][0]
        self.assertEqual(wall["orientation"]["turn_quarters"],1)
        self.assertEqual(bed["orientation"]["turn_quarters"],2)
        self.assertEqual(bed["position"],[130.0,190.0])
        self.assertEqual(mf.validate_repository(self.root),[("demo_01",2)])
    def test_four_perspective_variant_ids(self):
        records=json.loads((self.root/mf.CATALOG).read_text())
        for i in [3,4]:
            records["assets"].append({"id":f"P00{i}","category":"furniture",
                 "texture_path":f"res://invalid/P00{i}.png","pixel_size":[88,112],"origin":[44,112]})
        (self.root/mf.CATALOG).write_text(json.dumps(records))
        variants={"north":"P001","east":"P002","south":"P003","west":"P004"}
        p=self._patch([{"op":"update_block","instance_id":self.bed,
               "set":{"facing":"west","orientation_mode":"variants","direction_asset_ids":variants}}])
        v2=mf.apply(self.root,p)
        e=v2["layer_stack"]["passes"]["decorations"][0]
        self.assertEqual(e["asset_id"],"P001")
        self.assertEqual(e["orientation"]["resolved_asset_id"],"P004")
        self.assertEqual(e["texture_path"],"res://invalid/P004.png")
        self.assertEqual(e["origin"],[44,112])
        meta=mf.build_block_manifest(v2,mf.asset_catalog(self.root))
        block=next(x for x in meta["placed_blocks"] if x["instance_id"]==self.bed)
        self.assertEqual(block["asset_id"],"P001")
        self.assertEqual(block["render_asset_id"],"P004")
        self.assertEqual(block["texture_path"],"res://invalid/P004.png")
    def test_invalid_orientation_rejected(self):
        for val in ["northeast","top","90",90]:
            with self.subTest(value=val):
                with self.assertRaisesRegex(ValueError,"facing must"):
                    resolve_orientation({"id":"P001","facing":val},self.catalog)
        with self.assertRaisesRegex(ValueError,"nonzero rotation_degrees"):
            resolve_orientation({"id":"P001","facing":"east","rotation_degrees":90},self.catalog)
    def test_perspective_without_complete_art_fails(self):
        with self.assertRaisesRegex(ValueError,"four direction_asset_ids"):
            resolve_orientation({"id":"P001","facing":"east","orientation_mode":"variants",
                                 "direction_asset_ids":{"north":"P001"}},self.catalog)
        with self.assertRaisesRegex(ValueError,"same environmental category"):
            resolve_orientation({"id":"P001","facing":"north","orientation_mode":"variants",
                "direction_asset_ids":{"north":"P001","east":"P002","south":"CH001","west":"W001"}},self.catalog)
    def test_floor_override_accepts_four_cardinal_facings(self):
        for cardinal in FACINGS:
            with self.subTest(cardinal=cardinal):
                tile={"id":"F001","facing":cardinal}
                self.assertEqual(resolve_orientation(tile,self.catalog)["facing"],cardinal)
        self.room["tile_overrides"]=[{"x":2,"y":2,"id":"F001","facing":"east"}]
        self.room.pop("layer_stack",None)
        self.assertTrue(mf.validate_room(self.room,self.catalog))
        self.room["tile_overrides"][0]["facing"]="diagonal"
        with self.assertRaisesRegex(ValueError,"facing must"):
            mf.validate_room(self.room,self.catalog)
    def test_world_occlusion_pass_selection_is_versioned(self):
        manifest=self._patch([{"op":"set_property","key":"occlusion_mode",
                              "value":"world_y_sort"}])
        v2=mf.apply(self.root,manifest)
        self.assertEqual(v2["layer_stack"]["occlusion_mode"],"world_y_sort")
        self.assertEqual(mf.validate_repository(self.root),[("demo_01",2)])

    def test_set_tile_manifest_preserves_cardinal_direction(self):
        patch=self._patch([
            {"op":"set_tile","x":3,"y":2,"id":"F001","facing":"west"}
        ])
        v2=mf.apply(self.root,patch)
        tile=v2["tile_overrides"][0]
        self.assertEqual(tile,{"x":3,"y":2,"id":"F001","facing":"west"})
        manifest=mf.build_block_manifest(v2,self.catalog)
        self.assertEqual(manifest["floor_overrides"][0]["orientation"]["turn_quarters"],3)
    def test_visual_approval_requires_committed_reference(self):
        update=self._patch([{"op":"set_property","key":"visual_qa","value":{
            "status":"approved","reference_sha256":"test-reference-sha",
            "preview_path":"docs/previews/test.png","reviewer":"Test QA"}}])
        with self.assertRaisesRegex(ValueError,"committed reference image"):
            mf.apply(self.root,update)
    def test_legacy_map_is_byte_compatible(self):
        layer=self.room["layer_stack"]["passes"]["decorations"][0]
        self.assertNotIn("orientation",layer)
        self.assertEqual(layer["rotation_degrees"],0)
        self.assertEqual(mf.validate_repository(self.root),[("demo_01",1)])

if __name__=="__main__":
    unittest.main()
