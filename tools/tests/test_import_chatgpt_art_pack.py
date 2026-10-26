"""Import ChatGPT-produced owner art bytes; never synthesize graphics."""
from pathlib import Path
import hashlib
import importlib.util
import json
import struct
import tempfile
import unittest
import zipfile

FILE=Path(__file__).resolve().parents[1]/"import_chatgpt_art_pack.py"
SPEC=importlib.util.spec_from_file_location("chatgpt_art_importer",FILE)
MODULE=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

class ChatGPTArtImportTests(unittest.TestCase):
    def make_zip(self, root):
        art = bytes.fromhex("89504e470d0a1a0a")+b"\\0\\0\\0\\rIHDR"+struct.pack(">IIBBBBB",32,32,8,6,0,0,0)+b"\\0\\0\\0\\0"
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

if __name__=="__main__":
    unittest.main()
