#!/usr/bin/env python3
"""Stage real ChatGPT-created PNG bytes from owner's ZIP, without generating art.

Codex and Claude Code may verify/import bytes only. Do not mark art approved.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import struct
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / ".agents/graphics/chatgpt_drafts/2026-10-26"
SIGNATURE = bytes.fromhex("89504e470d0a1a0a")

def safe(name):
    p = PurePosixPath(name)
    return (bool(name) and "\\" not in name and not p.is_absolute() and
            not any(x in ("..", ".", "") for x in p.parts) and "\x00" not in name)

def stage(zip_path, destination=DEST, dry_run=False):
    with zipfile.ZipFile(zip_path) as z:
        info = [i for i in z.infolist() if not i.is_dir()]
        members = {i.filename: i for i in info}
        if len(members) != len(info) or not all(safe(n) for n in members):
            raise ValueError("invalid or duplicate archive path")
        if any(i.file_size > 10_000_000 for i in info) or sum(i.file_size for i in info) > 35_000_000:
            raise ValueError("excessive archive size")
        m = json.loads(z.read("manifest.json"))
        if m.get("status") != "DRAFT_REVIEW_REQUIRED":
            raise ValueError("unexpected approval state")
        drafts = m["assets"]
        crops = m["original_source_crops"]
        if len(drafts) != 22 or len(crops) != 4:
            raise ValueError("expected 22 drafts and 4 original source crops")
        declared = set()
        for entry in drafts + crops:
            name = entry["path"]
            if name in declared or name not in members or not safe(name) or not name.endswith(".png"):
                raise ValueError("missing, duplicate, or unsafe PNG: " + name)
            if not name.startswith(("draft_specialist/", "source_reference_crops/")):
                raise ValueError("invalid artwork directory: " + name)
            if entry.get("status") not in ("draft_unreviewed", "source_crop_unreviewed"):
                raise ValueError("unreviewed art must not be pre-approved: " + name)
            declared.add(name)
            b = z.read(name)
            if len(b) < 33 or b[:8] != SIGNATURE or b[12:16] != b"IHDR":
                raise ValueError("invalid PNG header: " + name)
            if list(struct.unpack(">II", b[16:24])) != entry["pixel_size"]:
                raise ValueError("invalid PNG dimensions: " + name)
            if b[24] != 8 or b[25] not in (4, 6):
                raise ValueError("expected 8-bit alpha PNG: " + name)
            if hashlib.sha256(b).hexdigest() != entry["sha256"]:
                raise ValueError("PNG hash mismatch: " + name)
        previews = {"source_crops_preview.png", "drafts_review_contact_sheet.png"}
        extra = [n for n in members if n.endswith(".png") and n not in declared | previews]
        if extra:
            raise ValueError("unlisted PNGs: " + repr(extra))
        if destination.exists():
            raise FileExistsError(str(destination))
        summary = {"validated": 26, "drafts": 22, "original_crops": 4,
                   "destination": str(destination), "copied": not dry_run}
        if dry_run:
            return summary
        destination.mkdir(parents=True)
        try:
            for name in sorted(members):
                out = destination / name
                out.parent.mkdir(parents=True, exist_ok=True)
                with out.open("xb") as handle:
                    handle.write(z.read(name))
        except BaseException:
            import shutil
            shutil.rmtree(destination)
            raise
        return summary

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("zip_path", type=Path, help="The ZIP downloaded from the ChatGPT conversation")
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()
    print(json.dumps(stage(a.zip_path, dry_run=a.dry_run), ensure_ascii=False, indent=2))
    print("Only staged. No PNG generated, no production catalog or ART states modified.")

if __name__ == "__main__":
    main()
