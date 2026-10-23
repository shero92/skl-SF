"""Generic map templates work for completely new maps, not just Hero Room."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import map_factory_cli as mf
from process_map_intake import process
from test_map_factory import fixture


class GeneralMaps(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        fixture(self.root)
        source=mf.ROOT/"map_factory/presets"
        dest=self.root/"map_factory/presets"
        shutil.copytree(source,dest)
        catalog=self.root/mf.CATALOG
        records=json.loads(catalog.read_text())
        for ident in ("F003","F004","F005"):
            records["assets"].append({
                "id":ident,"category":"floors",
                "texture_path":"res://invalid/"+ident+".png"
            })
        catalog.write_text(json.dumps(records))
    def tearDown(self):
        self.tmp.cleanup()
    def test_all_five_presets_create_independent_maps(self):
        for name in mf.PRESET_NAMES:
            with self.subTest(name=name):
                map_id=name+"_01"
                data=mf.create_map(self.root,map_id,name)
                self.assertEqual(data["preset"],name)
                self.assertEqual(data["version"],1)
                self.assertNotIn("npcs",data)
                self.assertFalse(any(data["navigation"]["default"].values()))
                self.assertEqual(data["visual_qa"]["status"],"needs_review")
                self.assertEqual(bool(data.get("ocean")),name=="coast")
                self.assertEqual(mf.get_latest(self.root,map_id)["map_id"],map_id)
        self.assertEqual(len(mf.validate_repository(self.root)),5)
    def test_create_manifest_produces_reusable_map_and_blocks(self):
        pending=self.root/"map_factory/intake/pending"
        pending.mkdir(parents=True)
        name="create_courtyard_01"
        manifest={
          "mode":"create","map_id":name,"preset":"courtyard",
          "changes":[
            {"op":"add_block","layer":"objects",
             "block":{"id":"P001","instance_id":"Bench_01","x":370,"y":480,
                      "scale":1.0,"shadow":{"type":"contact_medium","opacity":0.42}}},
            {"op":"set_tile","x":5,"y":4,"id":"F002"}],
          "note":"Independent courtyard assembled entirely from catalog IDs."
        }
        (pending/"create_demo.json").write_text(json.dumps(manifest))
        processed=process(self.root)
        self.assertEqual(len(processed),1)
        snapshot=mf.get_latest(self.root,name)
        self.assertEqual(snapshot["version"],2)
        self.assertEqual(snapshot["objects"][0]["instance_id"],"Bench_01")
        resolved=mf.read(self.root,mf.map_base(name)/"blocks"/"latest.json")
        self.assertEqual(resolved["placed_blocks"][0]["asset_id"],"P001")
        self.assertEqual(resolved["placed_blocks"][0]["shadow"]["opacity"],0.42)
        self.assertEqual(len(process(self.root)),0)
        self.assertEqual(mf.validate_repository(self.root),[(name,2)])
    def test_invalid_template_and_duplicate_name_are_rejected(self):
        with self.assertRaisesRegex(ValueError,"Unknown map preset"):
            mf.create_map(self.root,"bad_room_01","made_up_world")
        mf.create_map(self.root,"new_room_01","indoor_room")
        with self.assertRaisesRegex(ValueError,"already exists"):
            mf.create_map(self.root,"new_room_01","dungeon")
    def test_subsequent_changes_use_last_revision(self):
        data=mf.create_map(self.root,"indoor_demo_01","indoor_room")
        path=self.root/"map_factory/intake"/"edit.json"
        path.parent.mkdir(exist_ok=True,parents=True)
        patch={
            "map_id":"indoor_demo_01",
            "base_version":1,
            "base_sha256":mf.digest_json(data),
            "changes":[{"op":"add_block","layer":"back_objects",
                       "block":{"id":"W001","instance_id":"BackWall","x":80,"y":90}}]}
        path.write_text(json.dumps(patch))
        mf.apply(self.root,path.relative_to(self.root))
        with self.assertRaisesRegex(ValueError,"Stale patch"):
            mf.apply(self.root,path.relative_to(self.root))
        newer=mf.get_latest(self.root,"indoor_demo_01")
        self.assertEqual(newer["version"],2)
        self.assertEqual(newer["back_objects"][0]["instance_id"],"BackWall")

if __name__=="__main__":
    unittest.main()
