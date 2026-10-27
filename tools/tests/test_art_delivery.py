"""Art metadata validation is byte/PNG-header based, not image viewing."""
from pathlib import Path
import json
import hashlib
import importlib.util
import zipfile
import struct
import sys
import tempfile
import unittest

TOOLS=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(TOOLS))
from art_delivery import png_properties, audit_goal_reference

class ArtDeliveryGuards(unittest.TestCase):
    def test_native_png_dimensions_without_decoding_pixels(self):
        with tempfile.TemporaryDirectory() as tmp:
            file=Path(tmp)/"owner.png"
            # Valid PNG signature, IHDR length+name+dimensions/depth/color; no pixel decoding.
            h=b"\x89PNG\r\n\x1a\n"+b"\x00\x00\x00\x0dIHDR"
            file.write_bytes(h+struct.pack(">IIBBBBB",64,128,8,6,0,0,0)+b"\0\0\0\0")
            self.assertEqual(png_properties(file),[64,128])
    def test_non_alpha_png_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            file=Path(tmp)/"noalpha.png"
            h=b"\x89PNG\r\n\x1a\n"+b"\x00\x00\x00\x0dIHDR"
            file.write_bytes(h+struct.pack(">IIBBBBB",64,128,8,2,0,0,0)+b"\0\0\0\0")
            with self.assertRaisesRegex(ValueError,"RGBA"):
                png_properties(file)
    def test_reference_audit_checks_bytes_and_dimensions_without_claiming_pixel_equivalence(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/".agents/planner/goals/GOAL-0001/references/hero_room_reference.png"
            path.parent.mkdir(parents=True)
            path.write_bytes(b"\x89PNG\r\n\x1a\n"+b"\x00\x00\x00\x0dIHDR"+struct.pack(">II",1448,1086))
            report=audit_goal_reference(Path(tmp))
            self.assertEqual(report["committed_pixel_size"],[1448,1086])
            self.assertEqual(len(report["committed_sha256"]),64)
            self.assertFalse(report["byte_identical_to_chat_upload"])
            self.assertFalse(report["specialist_production_unblocked"])
            self.assertEqual(report["pixel_equivalence_when_hash_differs"],"not_assessed")

    def test_goal_qa_is_manual_and_owner_signoff(self):
        text=(TOOLS/"goal_qa.py").read_text(encoding="utf8")
        self.assertIn("final_comparison_run_at",text)
        self.assertIn('"--sandbox","read-only"',text)
        self.assertIn("owner_final_signoff",text)
        self.assertIn("capture_map_previews.gd",text)
        self.assertNotIn('state["final_verified"]=True',text)


FILE=TOOLS/"import_chatgpt_art_pack.py"
SPEC=importlib.util.spec_from_file_location("chatgpt_art_importer",FILE)
MODULE=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

class ChatGPTArtImportTests(unittest.TestCase):
    def make_zip(self, root):
        art = bytes.fromhex("89504e470d0a1a0a")+b"\0\0\0\rIHDR"+struct.pack(">IIBBBBB",32,32,8,6,0,0,0)+b"\0\0\0\0"
        assets = []
        crops = []
        file = root/"art.zip"
        with zipfile.ZipFile(file,"w") as z:
            for i in range(26):
                kind = "draft_specialist" if i < 22 else "source_reference_crops"
                path = f"{kind}/ART-{i:04d}/sprite_{i:02d}.png"
                row = {"path":path,"pixel_size":[32,32],
                       "sha256":hashlib.sha256(art).hexdigest(),
                       "status":"draft_unreviewed" if i<22 else "source_crop_unreviewed"}
                (assets if i<22 else crops).append(row)
                z.writestr(path,art)
            z.writestr("manifest.json",json.dumps({
                "status":"DRAFT_REVIEW_REQUIRED","assets":assets,
                "original_source_crops":crops}))
        return file

    def test_import_only_existing_exact_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            archive=self.make_zip(root)
            dest=root/"staging"
            result=MODULE.stage(archive,dest,dry_run=True)
            self.assertEqual(result["validated"],26)
            self.assertFalse(dest.exists())
            result=MODULE.stage(archive,dest)
            self.assertEqual(result["drafts"],22)
            self.assertTrue((dest/"manifest.json").exists())
            with self.assertRaises(FileExistsError):
                MODULE.stage(archive,dest)

    def test_rejects_untrusted_archive_state(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            archive=self.make_zip(root)
            with zipfile.ZipFile(archive) as z:
                data={name:z.read(name) for name in z.namelist()}
            manifest=json.loads(data["manifest.json"])
            manifest["status"]="integrated"
            data["manifest.json"]=json.dumps(manifest).encode()
            with zipfile.ZipFile(archive,"w") as z:
                for k,v in data.items(): z.writestr(k,v)
            with self.assertRaisesRegex(ValueError,"approval"):
                MODULE.stage(archive,root/"staging")


class HDPackImportGuards(unittest.TestCase):
    def test_verified_exact_named_pngs_are_registered_without_painting(self):
        import hashlib
        import importlib.util
        import zipfile
        import unittest.mock
        spec=importlib.util.spec_from_file_location(
            "hd_factory_import", TOOLS/"install_hd_factory_pack.py")
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        # Synthetic PNG headers stand in for the actual high-quality art:
        # test validates byte identity, IDs, safe paths and no overwrites.
        png=(bytes.fromhex("89504e470d0a1a0a")+b"\x00\x00\x00\x0dIHDR"+
             struct.pack(">IIBBBBB",128,128,8,6,0,0,0)+b"\x00\x00\x00\x00")
        mapping={
            "W021":("walls","Vine Covered Compass Ruin Wall"),
            "W022":("walls","Isometric Ivy Fantasy Wall"),
            "A017":("architecture","Ivy Covered Compass Shrine Pillar"),
            "A018":("architecture","Sapphire Compass Doorway"),
            "D019":("decor","Royal Blue Compass Banner"),
            "P023":("furniture","Cobalt Compass Treasure Chest"),
            "P024":("furniture","Compass Rose Fantasy Bed Frame"),
            "P025":("furniture","Royal Blue Compass Bedspread"),
            "P026":("furniture","Nautical Compass Study Desk"),
        }
        assets=[]
        for ident,(category,name) in mapping.items():
            base=ident+"_"+name.replace(" ","_")+".png"
            assets.append({"id":ident,"name":name,"category":category,
             "subtype":"test","path":"sprites/"+category+"/"+base,
             "factory_path":"map_factory/parts/"+category+"/"+base,
             "source_file":"original.png","pixel_size":[128,128],
             "origin":[64,128],"sha256":hashlib.sha256(png).hexdigest()})
        raw=json.dumps({"assets":assets}).encode("utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            catalog=root/module.CATALOG
            catalog.parent.mkdir(parents=True)
            catalog.write_text(json.dumps({"assets":[{"id":"F001","category":"floors"}],"asset_count":1}))
            archive=root/"hd.zip"
            with zipfile.ZipFile(archive,"w") as z:
                z.writestr("manifest.json",raw)
                for a in assets:
                    z.writestr(a["path"],png)
            with unittest.mock.patch.object(module,"MANIFEST_SHA",hashlib.sha256(raw).hexdigest()):
                self.assertEqual(len(module.verify(archive)["assets"]),9)
                module.install(archive,root,integrate=False)
                result=json.loads(catalog.read_text())
                self.assertEqual(result["asset_count"],10)
                self.assertTrue(all(a["status"]=="needs_cleanup" for a in result["assets"][1:]))
                for a in assets:
                    self.assertEqual((root/a["factory_path"]).read_bytes(),png)
                with self.assertRaisesRegex(ValueError,"existing catalog IDs"):
                    module.install(archive,root,integrate=False)
                # Refuse a changed payload: hashes are mandatory.
                with zipfile.ZipFile(archive,"w") as z:
                    z.writestr("manifest.json",raw)
                    for a in assets:
                        z.writestr(a["path"],png+b"tampered" if a["id"]=="P024" else png)
                with self.assertRaisesRegex(ValueError,"SHA256"):
                    module.verify(archive)

if __name__=="__main__":
    unittest.main()


from unittest.mock import patch
import goal_qa as qa

class GoalCaptureTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)
        for name,value in {"ROOT":self.root,"GOALS":self.root/".agents/planner/goals"}.items():
            context=patch.object(qa,name,value);context.start();self.addCleanup(context.stop)
        self.write(".agents/planner/goals/GOAL-0001/state.json",{"status":"active","milestones_approved":True,"final_verified":False})
        self.snapshot={"map_id":"hero_room_01","version":11,"canvas_size":[1536,1024]}
        digest=hashlib.sha256(json.dumps(self.snapshot,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
        self.write("map_factory/maps/hero_room_01/versions/v0011.json",self.snapshot)
        self.write("map_factory/maps/index.json",{"maps":{"hero_room_01":{"version":11,"snapshot_sha256":digest}}})

    def write(self,name,value):
        p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps(value),encoding="utf-8",newline="\n")
        return p

    def test_registry_resolves_current_immutable_revision(self):
        spec=qa.capture_spec()
        self.assertEqual(spec["version"],11)
        self.assertEqual(spec["file"],"hero_room_01_v0011.png")
        self.assertEqual(spec["snapshot"],"map_factory/maps/hero_room_01/versions/v0011.json")

    def test_later_revision_does_not_need_code_change(self):
        spec=qa.capture_spec()
        self.snapshot["version"]=12
        digest=hashlib.sha256(json.dumps(self.snapshot,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
        self.write("map_factory/maps/hero_room_01/versions/v0012.json",self.snapshot)
        self.write("map_factory/maps/index.json",{"maps":{"hero_room_01":{"version":12,"snapshot_sha256":digest}}})
        self.assertEqual(qa.capture_spec()["version"],12)
        self.assertNotEqual(qa.capture_spec()["file"],spec["file"])

    def test_mismatched_snapshot_fails(self):
        self.snapshot["canvas_size"]=[64,64]
        self.write("map_factory/maps/hero_room_01/versions/v0011.json",self.snapshot)
        with self.assertRaisesRegex(ValueError,"identity/hash"):
            qa.capture_spec()

    def test_invalid_map_path_fails_before_access(self):
        with self.assertRaisesRegex(ValueError,"Invalid map"):
            qa.capture_spec("../escape")

    def test_intermediate_goal_gate_allows_unfinished_tasks(self):
        self.write(".agents/tasks/TASK-0001_fixture.md",{})
        (self.root/".agents/tasks/TASK-0001_fixture.md").write_text("**Goal:** GOAL-0001\nstatus: blocked\n",newline="\n")
        self.assertFalse(qa.goal_state("GOAL-0001")[1]["final_verified"])
        with self.assertRaisesRegex(ValueError,"unfinished"):
            qa.eligible("GOAL-0001")

    def test_inactive_goal_still_blocks_capture(self):
        self.write(".agents/planner/goals/GOAL-0001/state.json",{"status":"draft","milestones_approved":False})
        with self.assertRaisesRegex(ValueError,"not approved"):
            qa.goal_state("GOAL-0001")

    def test_approved_explicit_prerequisites_do_not_include_the_qa_task_itself(self):
        self.write(".agents/planner/goals/GOAL-0001/state.json",{"status":"active","milestones_approved":True,
            "qa_required_tasks":["TASK-0001"],"qa_required_tasks_approved":True})
        path=self.write(".agents/tasks/TASK-0001_fixture.md",{})
        path.write_text("status: done\n",newline="\n")
        other=self.write(".agents/tasks/TASK-0044_fixture.md",{})
        other.write_text("**Goal:** GOAL-0001\nstatus: in_progress\n",newline="\n")
        self.assertEqual(qa.eligible("GOAL-0001")[1]["qa_required_tasks"],["TASK-0001"])

    def test_unapproved_empty_or_missing_prerequisites_fail_closed(self):
        for required,approved in [([],True),(["TASK-0001"],False),(["TASK-0001"],True)]:
            self.write(".agents/planner/goals/GOAL-0001/state.json",{"status":"active","milestones_approved":True,
                "qa_required_tasks":required,"qa_required_tasks_approved":approved})
            with self.assertRaises(ValueError):qa.eligible("GOAL-0001")

    def capture_fixture(self):
        spec=qa.capture_spec();source=self.root/"capture.png"
        source.write_bytes(b"\x89PNG\r\n\x1a\n"+b"\x00\x00\x00\x0dIHDR"+struct.pack(">II",1536,1024))
        proof={"capture_id":"nonce","map_id":spec["id"],"version":11,
               "snapshot_sha256":spec["snapshot_sha256"],"canvas_size":[1536,1024],
               "camera_position":[768,512],"camera_zoom":[1,1],
               "render_sha256":hashlib.sha256(source.read_bytes()).hexdigest()}
        receipt=self.write("capture.json",proof)
        return spec,source,receipt,proof

    def test_capture_receipt_binds_exact_run_version_hash_and_viewport(self):
        spec,source,receipt,proof=self.capture_fixture()
        self.assertEqual(qa.verify_capture(source,receipt,spec,"nonce"),proof)

    def test_stale_capture_rejected(self):
        spec,source,receipt,_=self.capture_fixture()
        with self.assertRaisesRegex(ValueError,"Stale/mismatched"):
            qa.verify_capture(source,receipt,spec,"other-run")

    def test_changed_capture_rejected(self):
        spec,source,receipt,_=self.capture_fixture()
        source.write_bytes(source.read_bytes()+b"changed")
        with self.assertRaisesRegex(ValueError,"hash"):
            qa.verify_capture(source,receipt,spec,"nonce")

    def test_wrong_viewport_rejected(self):
        spec,source,receipt,_=self.capture_fixture()
        source.write_bytes(source.read_bytes()[:16]+struct.pack(">II",64,64))
        with self.assertRaisesRegex(ValueError,"dimensions"):
            qa.verify_capture(source,receipt,spec,"nonce")

    def test_missing_receipt_never_accepts_existing_image(self):
        spec,source,receipt,_=self.capture_fixture();receipt.unlink()
        with self.assertRaisesRegex(RuntimeError,"receipt missing"):
            qa.verify_capture(source,receipt,spec,"nonce")



    def test_reference_manifest_required_before_any_comparison(self):
        with self.assertRaisesRegex(ValueError,"manifest required"):
            qa.authenticated_reference("GOAL-0001")

    def test_authenticated_source_selected_instead_of_historical_goal_image(self):
        source=self.root/"map_factory/references/original.png";source.parent.mkdir(parents=True)
        source.write_bytes(b"\x89PNG\r\n\x1a\n"+b"\0\0\0\rIHDR"+struct.pack(">II",1448,1086))
        manifest={"requirements":[{"kind":"reference","status":"approved","approved_at":"2026-10-27",
            "approved_by":"owner","provenance":{"source":"owner attachment","kind":"owner_supplied_original"},
            "path":"map_factory/references/original.png","sha256":hashlib.sha256(source.read_bytes()).hexdigest(),"pixel_size":[1448,1086]}]}
        self.write("map_factory/references/original.reference.json",manifest)
        self.write(".agents/planner/goals/GOAL-0001/state.json",{"status":"active","milestones_approved":True,
            "reference_manifest":"map_factory/references/original.reference.json"})
        self.assertEqual(qa.authenticated_reference("GOAL-0001").resolve(),source.resolve())
        source.write_bytes(source.read_bytes()+b"different")
        with self.assertRaisesRegex(ValueError,"SHA-256"):
            qa.authenticated_reference("GOAL-0001")

    def test_capture_rejects_camera_mismatch_and_missing_run_id(self):
        spec,source,receipt,proof=self.capture_fixture()
        proof["camera_zoom"]=[2,2];receipt.write_text(json.dumps(proof),newline="\n")
        with self.assertRaisesRegex(ValueError,"Stale/mismatched"):
            qa.verify_capture(source,receipt,spec,"nonce")
        with self.assertRaisesRegex(ValueError,"identity required"):
            qa.verify_capture(source,receipt,spec,None)

    def test_isolated_renderer_tree_must_have_matching_committed_snapshot(self):
        other=self.root/"isolated"
        with self.assertRaises(FileNotFoundError):
            qa.capture_spec(root=other)
        self.write("isolated/map_factory/maps/index.json",json.loads((self.root/"map_factory/maps/index.json").read_text()))
        changed=dict(self.snapshot,canvas_size=[64,64])
        self.write("isolated/map_factory/maps/hero_room_01/versions/v0011.json",changed)
        with self.assertRaisesRegex(ValueError,"identity/hash"):
            qa.capture_spec(root=other)
