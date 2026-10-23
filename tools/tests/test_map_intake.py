"""AI manifest intake integration, including new reusable environmental artwork."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import map_factory_cli as mf
from import_map_assets import import_assets
from process_map_intake import process
from test_map_factory import fixture

class Intake(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        fixture(self.root)
        mf.bootstrap(self.root,"hero_room_01",Path("map_factory/rooms/hero_room.json"))
        self.new_asset=self.root/"map_factory/intake/assets/P023_New_Coastal_Chair.png"
        self.new_asset.parent.mkdir(parents=True,exist_ok=True)
        image=Image.new("RGBA",(48,64),(0,0,0,0))
        for y in range(10,62):
            for x in range(5,41):
                image.putpixel((x,y),(141,82,43,255))
        image.save(self.new_asset)
        self.manifest_path=self.root/"map_factory/intake/pending/room_upgrade_001.json"
        self.manifest_path.parent.mkdir(parents=True,exist_ok=True)
        self.manifest={
          "mode":"patch","map_id":"hero_room_01","base_version":1,
          "note":"AI room image shows an extra chair; make only the new chair a reusable block.",
          "assets":[{
            "id":"P023","category":"furniture","name":"New Coastal Chair",
            "subtype":"chair",
            "file":"map_factory/intake/assets/P023_New_Coastal_Chair.png",
            "origin":[24,64],"tags":["wood","chair","coastal"],
            "collision":{"enabled":True,"size":[24,12],"offset":[0,-6]},
            "shadow":{"type":"chair","opacity":0.4,"offset_x":2,"offset_y":3}
          }],
          "changes":[{"op":"add_block","layer":"objects",
                      "block":{"id":"P023","instance_id":"AIChair_01",
                               "x":170,"y":178,"scale":0.85}}]
        }
        self.manifest_path.write_text(json.dumps(self.manifest))
    def tearDown(self):
        self.tmp.cleanup()
    def test_map_and_new_image_are_ingested_once(self):
        receipts=process(self.root)
        self.assertEqual(len(receipts),1)
        latest=mf.get_latest(self.root,"hero_room_01")
        self.assertEqual(latest["version"],2)
        self.assertEqual(latest["objects"][-1]["id"],"P023")
        m=mf.read(self.root,mf.map_base("hero_room_01")/"blocks"/"latest.json")
        chair=m["placed_blocks"][-1]
        self.assertEqual(chair["category"],"furniture")
        self.assertEqual(chair["pixel_size"],[48,64])
        self.assertTrue((self.root/"map_factory/parts/furniture/P023_New_Coastal_Chair.png").is_file())
        self.assertEqual(len(process(self.root)),0)
        self.assertEqual(mf.validate_repository(self.root),[("hero_room_01",2)])
    def test_same_filename_with_edits_cannot_rerun(self):
        process(self.root)
        self.manifest["note"]="Tampered old patch"
        self.manifest_path.write_text(json.dumps(self.manifest))
        with self.assertRaisesRegex(ValueError,"edited"):
            process(self.root)
    def test_existing_id_candidate_does_not_overwrite(self):
        process(self.root)
        actual=self.root/"map_factory/parts/furniture/P023_New_Coastal_Chair.png"
        original=actual.read_bytes()
        repl=Image.new("RGBA",(48,64),(0,0,0,0))
        repl.putpixel((13,13),(255,0,0,255))
        repl.save(self.new_asset)
        result=import_assets(self.root,self.manifest["assets"])
        self.assertEqual(len(result["candidates"]),1)
        self.assertEqual(actual.read_bytes(),original)
    def test_reject_character_pngs(self):
        self.manifest["assets"][0]["category"]="characters"
        with self.assertRaisesRegex(ValueError,"Map-only"):
            import_assets(self.root,self.manifest["assets"])

if __name__=="__main__":
    unittest.main()
