"""Tests for atomic, reusable map metadata. No characters/UI involved."""
import json
from pathlib import Path
import tempfile
import unittest
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import map_factory_cli as mf

def fixture(root):
    (root/"map_factory/metadata").mkdir(parents=True,exist_ok=True)
    assets=[]
    for ident,category in [("F001","floors"),("F002","floors"),("P001","furniture"),
                           ("P002","furniture"),("W001","walls"),("CH001","characters"),
                           ("UI001","ui"),("S002","shadows"),("S007","shadows")]:
        assets.append({"id":ident,"category":category,"texture_path":"res://invalid/"+ident+".png"})
    (root/mf.CATALOG).write_text(json.dumps({"assets":assets}))
    (root/"map_factory/rooms").mkdir(parents=True,exist_ok=True)
    room={"room_id":"old","size":[5,5],"canvas_size":[320,320],
          "tile_size":64,"ground_offset":[0,0],"floor_ids":["F001"],
          "tile_overrides":[],"objects":[{"id":"P001","x":100,"y":100,"scale":1}],
          "back_objects":[{"id":"W001","x":0,"y":0}],"npcs":[{"name":"Should disappear"}],
          "player_spawn":[0,0],"interactions":[],"effects":[]}
    (root/"map_factory/rooms/hero_room.json").write_text(json.dumps(room))

class Maps(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        fixture(self.root)
        self.base=mf.bootstrap(self.root,"hero_room_01",Path("map_factory/rooms/hero_room.json"))
    def tearDown(self):
        self.tmp.cleanup()
    def make_patch(self,changes,version=1,map_id="hero_room_01"):
        p=self.root/"map_factory/intake/mychange.json"
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps({"map_id":map_id,"base_version":version,"changes":changes}))
        return p.relative_to(self.root)
    def test_bootstrap_excludes_characters_and_gameplay(self):
        self.assertNotIn("npcs",self.base)
        self.assertNotIn("player_spawn",self.base)
        self.assertIn("instance_id",self.base["objects"][0])
        self.assertEqual(mf.validate_repository(self.root),[("hero_room_01",1)])
    def test_revision_resolves_last_snapshot(self):
        name=self.base["objects"][0]["instance_id"]
        patch=self.make_patch([
          {"op":"update_block","instance_id":name,"set":{"x":128}},
          {"op":"add_block","layer":"objects",
           "block":{"id":"P002","instance_id":"BlueDesk","x":256,"y":120,"scale":.8}},
          {"op":"set_tile","x":2,"y":1,"id":"F002"}])
        candidate=mf.apply(self.root,patch,dry_run=True)
        self.assertEqual(candidate["version"],2)
        self.assertFalse((self.root/mf.version_file("hero_room_01",2)).exists())
        result=mf.apply(self.root,patch)
        self.assertEqual(result["tile_overrides"][0]["id"],"F002")
        self.assertEqual(result["objects"][0]["x"],128)
        self.assertEqual(mf.get_latest(self.root,"hero_room_01")["version"],2)
        self.assertEqual(mf.validate_repository(self.root),[("hero_room_01",2)])
        with self.assertRaisesRegex(ValueError,"Stale patch"):
            mf.apply(self.root,patch)
    def test_reject_character_and_duplicated_block(self):
        p=self.make_patch([{"op":"add_block","layer":"objects",
            "block":{"id":"CH001","instance_id":"BadActor","x":1,"y":2}}])
        with self.assertRaisesRegex(ValueError,"Forbidden block category"):
            mf.apply(self.root,p)
        ident=self.base["objects"][0]["instance_id"]
        p=self.make_patch([{"op":"add_block","layer":"objects",
            "block":{"id":"P002","instance_id":ident,"x":1,"y":2}}])
        with self.assertRaisesRegex(ValueError,"Duplicate instance_id"):
            mf.apply(self.root,p)
    def test_clone_reuses_latest_but_does_not_mutate_parent(self):
        parent=mf.get_latest(self.root,"hero_room_01")
        sub=mf.clone_map(self.root,"sea_library_02","hero_room_01")
        self.assertEqual(sub["version"],1)
        self.assertEqual(sub["derived_from"]["map_id"],"hero_room_01")
        self.assertEqual(sub["derived_from"]["snapshot_sha256"],mf.digest_json(parent))
        patch=self.make_patch([{"op":"remove_block",
           "instance_id":sub["objects"][0]["instance_id"]}],map_id="sea_library_02")
        mf.apply(self.root,patch)
        self.assertEqual(len(mf.get_latest(self.root,"hero_room_01")["objects"]),1)
        self.assertEqual(len(mf.get_latest(self.root,"sea_library_02")["objects"]),0)
    def test_stale_sha_rejected(self):
        path=self.make_patch([{"op":"set_tile","x":1,"y":1,"id":"F001"}])
        doc=json.loads((self.root/path).read_text())
        doc["base_sha256"]="0"*64
        (self.root/path).write_text(json.dumps(doc))
        with self.assertRaisesRegex(ValueError,"base_sha256"):
            mf.apply(self.root,path)
    def test_duplicate_tile_override_rejected(self):
        snap=dict(self.base)
        snap["tile_overrides"]=[{"x":0,"y":0,"id":"F001"},
                                {"x":0,"y":0,"id":"F002"}]
        with self.assertRaisesRegex(ValueError,"Duplicate tile"):
            mf.validate_room(snap,mf.asset_catalog(self.root))

if __name__=="__main__":
    unittest.main()
