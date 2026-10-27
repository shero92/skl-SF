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
    def _change_measurements(self):
        data=mf.read(self.root,mf.CATALOG)
        for asset in data["assets"]:
            if asset["id"]=="P001":
                asset.update(origin=[11,29],pixel_size=[120,180],
                             collision={"enabled":True,"size":[30,20]},
                             shadow={"type":"contact_medium"})
        mf.dump(self.root,mf.CATALOG,data)

    def _historical_bytes(self):
        base=self.root/mf.map_base("hero_room_01")
        return {p.relative_to(base):p.read_bytes() for folder in ("versions","layers","blocks")
                for p in (base/folder).glob("v*.json")}

    def _legacy_revision(self):
        # Simulate an existing publication: old files have no captured catalog.
        snap=mf.get_latest(self.root,"hero_room_01")
        snap.pop("resolved_assets")
        mf.dump(self.root,mf.version_file("hero_room_01",1),snap)
        mf.dump(self.root,mf.map_base("hero_room_01")/"latest.json",snap)
        reg=mf.registry(self.root)
        reg["maps"]["hero_room_01"]["snapshot_sha256"]=mf.digest_json(snap)
        mf.dump(self.root,mf.INDEX,reg)
        return snap

    def test_measurement_updates_preserve_archive_and_new_revision_uses_them(self):
        before=self._historical_bytes()
        self._change_measurements()
        self.assertEqual(mf.validate_repository(self.root),[("hero_room_01",1)])
        patch=self.make_patch([{"op":"set_property","key":"description","value":"Recalibrated"}])
        result=mf.apply(self.root,patch)
        entry=result["layer_stack"]["passes"]["decorations"][0]
        self.assertEqual(entry["origin"],[11,29])
        self.assertEqual(entry["pixel_size"],[120,180])
        self.assertEqual(result["layer_stack"]["counts"]["shadows"],1)
        for path,data in before.items():
            self.assertEqual((self.root/mf.map_base("hero_room_01")/path).read_bytes(),data)
        self.assertEqual(mf.validate_repository(self.root),[("hero_room_01",2)])

    def test_legacy_measurements_are_recovered_without_rewriting(self):
        self._legacy_revision()
        before=self._historical_bytes()
        self._change_measurements()
        self.assertEqual(mf.validate_repository(self.root),[("hero_room_01",1)])
        self.assertEqual(before,self._historical_bytes())
        result=mf.apply(self.root,self.make_patch([
            {"op":"set_property","key":"description","value":"New measurement"}]))
        self.assertEqual(result["resolved_assets"]["P001"]["origin"],[11,29])
        self.assertEqual(mf.validate_repository(self.root),[("hero_room_01",2)])

    def test_legacy_corruption_in_each_resolved_artifact_is_rejected(self):
        self._legacy_revision()
        base=mf.map_base("hero_room_01")
        cases=[(base/"blocks/v0001.json",lambda d:d["placed_blocks"][0].update(position=[9,9])),
               (base/"blocks/v0001.json",lambda d:d["placed_blocks"][0].update(asset_id="P002")),
               (base/"blocks/v0001.json",lambda d:d["placed_blocks"][0].update(anchor=[99,1])),
               (base/"layers/v0001.json",lambda d:d["passes"]["decorations"][0].update(position=[9,9]))]
        for path,corrupt in cases:
            with self.subTest(path=path,corrupt=corrupt):
                original=(self.root/path).read_bytes()
                doc=mf.read(self.root,path);corrupt(doc);mf.dump(self.root,path,doc)
                with self.assertRaises(ValueError):
                    mf.validate_repository(self.root)
                (self.root/path).write_bytes(original)

    def test_archived_source_change_and_removed_asset_are_rejected(self):
        self._legacy_revision()
        path=mf.version_file("hero_room_01",1)
        original=(self.root/path).read_bytes()
        doc=mf.read(self.root,path);doc["objects"][0]["x"]+=1;mf.dump(self.root,path,doc)
        with self.assertRaises(ValueError):
            mf.validate_repository(self.root)
        (self.root/path).write_bytes(original)
        catalog=mf.read(self.root,mf.CATALOG)
        catalog["assets"]=[x for x in catalog["assets"] if x["id"]!="P001"]
        mf.dump(self.root,mf.CATALOG,catalog)
        with self.assertRaises(ValueError):
            mf.validate_repository(self.root)

    def test_parent_snapshot_hash_detects_coherent_historical_change(self):
        mf.apply(self.root,self.make_patch([
            {"op":"set_property","key":"description","value":"Next"}]))
        path=mf.version_file("hero_room_01",1)
        doc=mf.read(self.root,path);doc["description"]="Changed historical text"
        mf.dump(self.root,path,doc)
        with self.assertRaisesRegex(ValueError,"Parent snapshot hash"):
            mf.validate_repository(self.root)

    def test_sync_only_backfills_and_does_not_recalibrate_published_files(self):
        before=self._historical_bytes()
        self._change_measurements()
        self.assertEqual(mf.sync_block_metadata(self.root),["hero_room_01@v0001"])
        self.assertEqual(before,self._historical_bytes())
        path=mf.map_base("hero_room_01")/"layers/v0001.json"
        (self.root/path).unlink()
        mf.sync_block_metadata(self.root)
        self.assertEqual(before,self._historical_bytes())
        doc=mf.read(self.root,path)
        doc["passes"]["decorations"][0]["origin"]=[999,999]
        mf.dump(self.root,path,doc)
        corrupt=(self.root/path).read_bytes()
        with self.assertRaisesRegex(ValueError,"Refusing to rewrite"):
            mf.sync_block_metadata(self.root)
        self.assertEqual((self.root/path).read_bytes(),corrupt)

    def test_snapshot_catalog_keeps_animation_frame_dependencies(self):
        patch=self.make_patch([{"op":"add_block","layer":"background_objects","block":{
            "id":"P001","instance_id":"Sea","x":0,"y":0,
            "animation":{"frames":["P001","P002"],"fps":4}}}])
        snap=mf.apply(self.root,patch)
        self.assertIn("P002",snap["resolved_assets"])
        self.assertEqual(mf.validate_repository(self.root),[("hero_room_01",2)])

    def test_frozen_snapshot_does_not_accept_removed_or_changed_identity(self):
        catalog=mf.read(self.root,mf.CATALOG)
        for record in catalog["assets"]:
            if record["id"]=="P001":
                record["category"]="characters"
        mf.dump(self.root,mf.CATALOG,catalog)
        with self.assertRaisesRegex(ValueError,"Invalid resolved asset identity"):
            mf.validate_repository(self.root)

    def test_missing_legacy_measurements_fail_explicitly(self):
        self._legacy_revision()
        path=self.root/mf.map_base("hero_room_01")/"blocks/v0001.json"
        path.unlink()
        with self.assertRaisesRegex(ValueError,"Legacy revision lacks archived measurements"):
            mf.sync_block_metadata(self.root)
        self.assertFalse(path.exists())

    def test_missing_frozen_blocks_can_be_backfilled(self):
        path=self.root/mf.map_base("hero_room_01")/"blocks/v0001.json"
        before=path.read_bytes();path.unlink()
        self._change_measurements()
        mf.sync_block_metadata(self.root)
        self.assertEqual(path.read_bytes(),before)

    def test_initial_revision_rejects_parent_hash(self):
        snap=mf.get_latest(self.root,"hero_room_01")
        snap["parent_snapshot_sha256"]="0"*64
        mf.dump(self.root,mf.version_file("hero_room_01",1),snap)
        mf.dump(self.root,mf.map_base("hero_room_01")/"latest.json",snap)
        reg=mf.registry(self.root)
        reg["maps"]["hero_room_01"]["snapshot_sha256"]=mf.digest_json(snap)
        mf.dump(self.root,mf.INDEX,reg)
        with self.assertRaisesRegex(ValueError,"Initial revision"):
            mf.validate_repository(self.root)

    def test_missing_archived_layer_is_corruption_not_skipped_validation(self):
        path=self.root/mf.map_base("hero_room_01")/"layers/v0001.json"
        path.unlink()
        with self.assertRaisesRegex(ValueError,"Versioned layer stack"):
            mf.validate_repository(self.root)

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

    def test_strict_furniture_uses_exact_ground_cells_and_no_overlap(self):
        from copy import deepcopy
        room=deepcopy(self.base)
        room.pop("layer_stack",None)
        room["placement_policy"]="strict_v1"
        room["floor_ids"]=["F001"]
        bed={"id":"P001","instance_id":"BedGrid","x":128,"y":256,"scale":1,
             "grid_placement":{"cell":[1,1],"facing":"north"}}
        room["objects"]=[bed]
        room["ground_overlays"]=[]
        catalog=mf.asset_catalog(self.root)
        for floor in ("F001","F002"):
            catalog[floor]["tags"]=["stone","floors"]
        cfg={"schema_version":1,"mode":"floor",
             "footprint_cells":[2,3],"occupancy_group":"solid",
             "allowed_floor_tags":["stone"],"allowed_floor_asset_ids":["F001"],
             "forbidden_floor_tags":["edge","corner","compass"],
             "measurement_status":"provisional"}
        catalog["P001"]["placement_contract"]=cfg
        self.assertTrue(mf.validate_room(room,catalog))
        room["objects"][0]["x"]=129
        with self.assertRaisesRegex(ValueError,"exact grid"):
            mf.validate_room(room,catalog)
        room["objects"][0]["x"]=128
        room["tile_overrides"]=[{"x":2,"y":2,"id":"F002"}]
        with self.assertRaisesRegex(ValueError,"wrong floor block"):
            mf.validate_room(room,catalog)
        room["tile_overrides"]=[]
        room["objects"].append({"id":"P001","instance_id":"BedOverlap","x":128,
                                "y":256,"scale":1,"grid_placement":{"cell":[1,1],"facing":"north"}})
        with self.assertRaisesRegex(ValueError,"occupied block"):
            mf.validate_room(room,catalog)

    def test_furniture_contract_requires_approved_footprint_for_final_map(self):
        from copy import deepcopy
        room=deepcopy(self.base)
        room.pop("layer_stack",None)
        room["floor_ids"]=["F001"]
        room["objects"]=[{"id":"P001","instance_id":"BedGrid","x":128,"y":256,
                          "grid_placement":{"cell":[1,1],"facing":"north"}}]
        catalog=mf.asset_catalog(self.root)
        catalog["F001"]["tags"]=["stone","floors"]
        catalog["P001"]["placement_contract"]={"schema_version":1,"mode":"floor",
                 "footprint_cells":[2,3],"occupancy_group":"solid",
                 "allowed_floor_tags":["stone"],"measurement_status":"provisional"}
        room["placement_policy"]="strict_v1"
        room["requires_reviewed_footprints"]=True
        with self.assertRaisesRegex(ValueError,"not been visually reviewed"):
            mf.validate_room(room,catalog)
        catalog["P001"]["placement_contract"]["measurement_status"]="reviewed"
        self.assertTrue(mf.validate_room(room,catalog))
        room["objects"][0].pop("grid_placement")
        with self.assertRaisesRegex(ValueError,"requires grid_placement"):
            mf.validate_room(room,catalog)

    def test_floor_footprint_rejects_furniture_on_missing_platform_tiles(self):
        from copy import deepcopy
        room=deepcopy(self.base)
        room.pop("layer_stack",None)
        room["floor_ids"]=["F001"]
        room["objects"]=[{"id":"P001","instance_id":"BedGrid","x":128,"y":256,
                          "grid_placement":{"cell":[1,1],"facing":"north"}}]
        catalog=mf.asset_catalog(self.root)
        catalog["F001"]["tags"]=["stone","floors"]
        catalog["P001"]["placement_contract"]={"schema_version":1,"mode":"floor",
                 "footprint_cells":[2,3],"occupancy_group":"solid",
                 "allowed_floor_tags":["stone"],"measurement_status":"provisional"}
        room["floor_footprint"]={"row_spans":[[[0,4]],[[0,4]],[[0,4]],[[0,1]],[[0,4]]]}
        with self.assertRaisesRegex(ValueError,"outside floor footprint"):
            mf.validate_room(room,catalog)

    def test_new_and_moved_furniture_snaps_to_grid_without_manual_xy(self):
        from copy import deepcopy
        snap=deepcopy(self.base)
        snap.pop("layer_stack", None)
        snap["floor_ids"]=["F001"]
        catalog=mf.asset_catalog(self.root)
        catalog["F001"]["tags"]=["stone"]
        catalog["P001"]["placement_contract"]={"schema_version":1,"mode":"floor",
                "footprint_cells":[2,3],"occupancy_group":"solid",
                "allowed_floor_tags":["stone"],"measurement_status":"provisional"}
        snap["objects"]=[]
        placed=mf.apply_changes(snap,{"changes":[
            {"op":"add_block","layer":"objects",
             "block":{"id":"P001","instance_id":"GridBed",
                      "grid_placement":{"cell":[1,1],"facing":"north"}}}]},catalog)
        self.assertEqual((placed["objects"][0]["x"],placed["objects"][0]["y"]),(128,256))
        self.assertTrue(mf.validate_room(placed,catalog))
        moved=mf.apply_changes(placed,{"changes":[
            {"op":"update_block","instance_id":"GridBed",
             "set":{"grid_placement":{"cell":[2,1],"facing":"north"}}}]},catalog)
        self.assertEqual((moved["objects"][0]["x"],moved["objects"][0]["y"]),(192,256))
        moved["objects"][0]["x"]=77
        with self.assertRaisesRegex(ValueError,"exact grid"):
            mf.validate_room(moved,catalog)

if __name__=="__main__":
    unittest.main()
