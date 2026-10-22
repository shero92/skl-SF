#!/usr/bin/env python3
"""Import game sprites from ZIP, retaining the best existing files.

Only first-time PNGs are copied directly into parts/. Existing differing PNGs
go into candidates/ for visual quality review and explicit replacement.
"""
import csv
import hashlib
import io
import json
import re
import sys
import zipfile
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "map_factory/metadata/asset_index.json"
QUEUE = ROOT / "map_factory/metadata/production_queue.csv"
REPORT = ROOT / "map_factory/metadata/import_report.json"
PATH_RX = re.compile(r"map_factory/parts/([a-z_]+)/([A-Z]{1,3}[0-9]{3}_[A-Za-z0-9_]+\.png)")
MAX_FILE = 12_000_000
MAX_TOTAL = 180_000_000

def run(archive_path):
    catalog = json.loads(INDEX.read_text(encoding="utf-8"))
    by_id = {a["id"]: a for a in catalog["assets"]}
    counts = {"installed": [], "candidates": [], "unchanged": [], "skipped": []}
    total = 0
    processed = set()
    with zipfile.ZipFile(archive_path) as z:
        for member in z.infolist():
            if member.is_dir() or not member.filename.lower().endswith(".png"):
                continue
            match = PATH_RX.fullmatch(member.filename)
            if not match or member.file_size > MAX_FILE:
                counts["skipped"].append({"path": member.filename, "reason": "unsafe path or oversize"})
                continue
            category, basename = match.groups()
            asset_id = basename.split("_", 1)[0]
            record = by_id.get(asset_id)
            if not record or record["category"] != category or record["texture_path"] != "res://" + member.filename:
                counts["skipped"].append({"path": member.filename, "reason": "catalog mismatch"})
                continue
            if asset_id in processed:
                counts["skipped"].append({"path": member.filename, "reason": "duplicate ID"})
                continue
            processed.add(asset_id)
            total += member.file_size
            if total > MAX_TOTAL:
                raise ValueError("Too much uncompressed image data")
            content = z.read(member)
            if not content.startswith(b"\x89PNG\r\n\x1a\n"):
                counts["skipped"].append({"path": member.filename, "reason": "invalid PNG signature"})
                continue
            try:
                with Image.open(io.BytesIO(content)) as img:
                    img.verify()
                with Image.open(io.BytesIO(content)) as img:
                    width, height = img.size
                    if img.format != "PNG" or not (1 <= width <= 4096 and 1 <= height <= 4096):
                        raise ValueError("unsupported dimensions or format")
                    alpha_min, alpha_max = img.convert("RGBA").getchannel("A").getextrema()
            except (ValueError, OSError) as error:
                counts["skipped"].append({"path": member.filename, "reason": str(error)})
                continue
            digest = hashlib.sha256(content).hexdigest()
            target = ROOT / member.filename
            if target.exists():
                if hashlib.sha256(target.read_bytes()).hexdigest() == digest:
                    counts["unchanged"].append(asset_id)
                    continue
                candidate = ROOT / "map_factory/candidates" / category / basename
                candidate.parent.mkdir(parents=True, exist_ok=True)
                candidate.write_bytes(content)
                counts["candidates"].append({
                    "id": asset_id, "path": candidate.relative_to(ROOT).as_posix(),
                    "size": [width, height], "sha256": digest,
                    "reason": "Existing asset preserved until quality comparison"
                })
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
            record["pixel_size"] = [width, height]
            record["origin"] = [0, 0] if category in ("floors", "ui") else [width // 2, height]
            record["status"] = "needs_cleanup"
            record["source"] = {"kind": "atlas_crop", "archive": archive_path.name, "sha256": digest}
            record["qa_notes"] = "Review labels/edges, native detail, lighting, seam, origin, collision and shadow."
            if category not in ("floors", "environment") and alpha_min == 255:
                record["qa_notes"] += " Warning: opaque background detected."
            counts["installed"].append({"id": asset_id, "path": member.filename, "size": [width, height]})
    catalog["generated_png_count"] = sum((ROOT / a["texture_path"].removeprefix("res://")).exists() for a in catalog["assets"])
    catalog["asset_status_note"] = "Imported concept crops are needs_cleanup; replacements are staged in candidates/."
    INDEX.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with QUEUE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "category", "name", "status", "texture_path"])
        writer.writerows((a["id"], a["category"], a["name"], a["status"], a["texture_path"]) for a in catalog["assets"])
    REPORT.write_text(json.dumps(counts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"installed": len(counts["installed"]), "candidates": len(counts["candidates"]),
                      "unchanged": len(counts["unchanged"]), "skipped": len(counts["skipped"]),
                      "total_in_parts": catalog["generated_png_count"]}))
    return 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python tools/import_asset_pack.py <zip>")
    raise SystemExit(run(Path(sys.argv[1])))
