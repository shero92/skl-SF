"""Art metadata validation is byte/PNG-header based, not image viewing."""
from pathlib import Path
import json
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
            path.write_bytes(b"\\x89PNG\\r\\n\\x1a\\n"+b"\\x00\\x00\\x00\\x0dIHDR"+struct.pack(">II",1448,1086))
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

if __name__=="__main__":
    unittest.main()
