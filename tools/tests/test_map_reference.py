"""Map reference intake is never allowed to auto-publish an unreviewed image."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import map_factory_cli as mf
from prepare_map_reference import prepare
from process_map_intake import process
from test_map_factory import fixture

class ReferenceJobs(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        fixture(self.root)
        shutil.copytree(mf.ROOT/"map_factory/presets",self.root/"map_factory/presets")
        mf.bootstrap(self.root,"hero_room_01",Path("map_factory/rooms/hero_room.json"))
        self.image=self.root/"uploaded_room.png"
        pic=Image.new("RGB",(320,256),(48,107,171))
        pic.save(self.image)
    def tearDown(self):
        self.tmp.cleanup()
    def test_prepare_create_keeps_reference_but_does_not_create_map(self):
        draft,doc=prepare(self.root,self.image,"my_future_room_01","create","indoor_room")
        self.assertEqual(doc["source_image"]["pixel_size"],[320,256])
        self.assertEqual(doc["source_image"]["sha256"],hashlib.sha256(self.image.read_bytes()).hexdigest())
        self.assertTrue((self.root/doc["source_image"]["path"]).exists())
        self.assertEqual(doc["analysis_status"],"pending_review")
        self.assertNotIn("my_future_room_01",mf.registry(self.root)["maps"])
        self.assertTrue((self.root/draft).exists())
    def test_prepare_patch_pins_base_version(self):
        _,job=prepare(self.root,self.image,"hero_room_01","patch")
        snap=mf.get_latest(self.root,"hero_room_01")
        self.assertEqual(job["base_version"],1)
        self.assertEqual(job["base_sha256"],mf.digest_json(snap))
    def test_unreviewed_reference_is_rejected(self):
        draft,doc=prepare(self.root,self.image,"future_world_01","create","courtyard")
        pending=self.root/"map_factory/intake/pending"
        pending.mkdir(exist_ok=True,parents=True)
        (pending/"future.json").write_text((self.root/draft).read_text())
        with self.assertRaisesRegex(ValueError,"reviewed block analysis"):
            process(self.root)
        self.assertNotIn("future_world_01",mf.registry(self.root)["maps"])
    def test_reviewed_reference_creates_map_and_preserves_dimensions(self):
        _,job=prepare(self.root,self.image,"my_future_room_01","create","indoor_room")
        job["analysis_status"]="reviewed"
        job["changes"]=[{"op":"add_block","layer":"objects",
                          "block":{"id":"P001","instance_id":"ReferenceChair","x":100,"y":120}}]
        pending=self.root/"map_factory/intake/pending"
        pending.mkdir(exist_ok=True,parents=True)
        (pending/"approved.json").write_text(json.dumps(job))
        result=process(self.root)
        self.assertEqual(len(result),1)
        snapshot=mf.get_latest(self.root,"my_future_room_01")
        self.assertEqual(snapshot["source_image"]["pixel_size"],[320,256])
        self.assertEqual(snapshot["version"],2)
        self.assertEqual(snapshot["visual_qa"]["status"],"needs_review")
        self.assertEqual(len(process(self.root)),0)
    def test_clone_draft_rejects_old_parent(self):
        _,job=prepare(self.root,self.image,"new_cave_01","clone",from_map="hero_room_01")
        job["analysis_status"]="reviewed"
        job["source_parent_version"]=0
        pending=self.root/"map_factory/intake/pending"
        pending.mkdir(exist_ok=True,parents=True)
        (pending/"badclone.json").write_text(json.dumps(job))
        with self.assertRaisesRegex(ValueError,"Outdated source_parent_version"):
            process(self.root)

if __name__=="__main__":
    unittest.main()
