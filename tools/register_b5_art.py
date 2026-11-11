"""Package Codex's finished east wall lantern master as the ART-0040 delivery, then register it and the
four ART-0003 cliff foam phases as Map Factory runtime parts (TASK-0163).

Usage: python tools/register_b5_art.py [--dry-run]

- ART-0040: the master `assets_hd/lighting/east_wall_lantern/v001/hero_wall_lantern_east.png` was drawn by
  Codex (built-in image_gen) and left uncommitted in the main checkout on 2026-11-11. It is copied byte for
  byte to the delivery path with a manifest; nothing is redrawn or edited here.
- Lantern part L07: trimmed BOX downscale into the 29x53 canvas of the request (same method as L06).
- Foam parts B15-B18: the fixed 96x48 native frames from the delivery are used unchanged, because trimming
  each frame separately would break their registration.

Execution provenance: Agent: claude (Claude Code); model: Fable 5.2.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil

from PIL import Image

import register_b3_art as b3
from register_b4_art import APPROVAL

ROOT = Path(__file__).resolve().parents[1]
LANTERN_MASTER = "assets_hd/lighting/east_wall_lantern/v001/hero_wall_lantern_east.png"
LANTERN_DELIVERY = ".agents/graphics/deliveries/ART-0040/hero_wall_lantern_east.png"
LANTERN_REQUEST = ".agents/graphics/requests/ART-0040_hero_room_wall_lantern_east.md"
FOAM_IDS = {"hero_cliff_foam_01": "B15", "hero_cliff_foam_02": "B16", "hero_cliff_foam_03": "B17", "hero_cliff_foam_04": "B18"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def package_lantern() -> dict:
    """Writes the ART-0040 delivery (copy + manifest) and marks the request delivered. Returns the manifest item."""
    master, delivery = ROOT / LANTERN_MASTER, ROOT / LANTERN_DELIVERY
    delivery.parent.mkdir(parents=True, exist_ok=True)
    if not delivery.is_file():
        shutil.copyfile(master, delivery)
    with Image.open(master) as image:
        size, mode = list(image.size), image.mode
        bounds = list(image.getchannel("A").point(lambda v: 255 if v >= 128 else 0).getbbox())
    item = {"id": "hero_wall_lantern_east", "request_id": "ART-0040", "master_path": LANTERN_MASTER,
            "delivery_path": LANTERN_DELIVERY, "sha256": sha(master), "pixel_size": size, "mode": mode,
            "bounds_alpha_128": bounds, "facing": "east", "rod_projection": "bracket_on_left_arm_extends_right",
            "native_canvas": [29, 53], "tool": "built-in image_gen", "model": "unknown",
            "independent_generation": True, "bitmap_flip_or_rotation": False,
            "quality_status": "needs_map_calibration", "owner_approved": True,
            "approval_basis": "owner_automatic_20261111"}
    manifest = {"request_id": "ART-0040", "task_id": "TASK-0163", "agent": "codex (master); claude (delivery packaging only)",
                "tool": "built-in image_gen", "model": "unknown",
                "note": "Master drawn by Codex and found uncommitted in the main checkout on 2026-11-11 "
                        "(preserved in branch backup/local-changes-20261111c). Packaged unchanged by Claude while Codex was paused.",
                "items": [item],
                "rejected_attempts": ["assets_hd/lighting/east_wall_lantern/v001/rejected/hero_wall_lantern_east_attempt_01.png"],
                "files": [{"path": LANTERN_DELIVERY, "sha256": sha(delivery)}]}
    (delivery.parent / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
                                                   encoding="utf-8", newline="\n")
    request = ROOT / LANTERN_REQUEST
    text = request.read_text(encoding="utf-8")
    text = re.sub(r"^status: requested$", "status: delivered", text, count=1, flags=re.M)
    text = text.replace("- [ ] Clean PNG produced (ONLY graphics specialist); SHA-256 manifest written; mark `delivered`.",
                        "- [x] Clean PNG produced (ONLY graphics specialist); SHA-256 manifest written; mark `delivered`.")
    request.write_text(text, encoding="utf-8", newline="\n")
    return item


def foam_record(name: str, identifier: str, item: dict) -> tuple[dict, Path]:
    native = ROOT / item["native_review_path"]
    with Image.open(native) as image:
        width, height = image.size
    rel = f"map_factory/parts/environment/{identifier}_Cliff_Foam_{name[-2:]}.png"
    record = {
        "id": identifier, "name": f"Cliff Foam {name[-2:]}", "category": "environment", "subtype": "seascape",
        "texture_path": "res://" + rel, "status": "ready", "pixel_size": [width, height], "origin": [width // 2, height],
        "collision": {"enabled": False, "size": [32, 16], "offset": [0, 0]}, "y_sort": False,
        "shadow": {"type": "none", "opacity": 0.25, "offset_x": 4, "offset_y": 2},
        "tags": ["cliff", "environment", "foam", "water"], "reusable": True,
        "source": {"kind": "image_gen_master", "master": item["master_path"],
                   "master_sha256": sha(ROOT / item["master_path"]), "request_id": "ART-0003"},
        "qa_notes": "Codex image_gen master (ART-0003); runtime part is the delivery's fixed 96x48 native frame, unchanged, "
                    "so the four phases stay registered. Map contact offset is provisional.",
        "qa_approval": dict(APPROVAL),
    }
    return record, native


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    catalog = json.loads(b3.INDEX.read_text(encoding="utf-8"))
    known = {a["id"] for a in catalog["assets"]}
    added = 0
    if "L07" not in known:
        if args.dry_run:
            print("L07 hero_wall_lantern_east (delivery would be packaged)")
        else:
            item = dict(package_lantern(), intended_native_canvas=[29, 53], native_review_path=LANTERN_MASTER)
            record, image = b3.build("hero_wall_lantern_east", ("L07", "lighting", "lantern", True, ["lantern", "wall", "east"]), item)
            record["qa_approval"] = dict(APPROVAL)
            record["qa_notes"] = "Codex image_gen master (ART-0040); runtime part is a trimmed BOX downscale. Wall mount offset needs scene calibration."
            target = ROOT / record["texture_path"].removeprefix("res://")
            image.save(target)
            catalog["assets"].append(record)
            print(record["id"], record["pixel_size"])
            added += 1
    foam = json.loads((ROOT / ".agents/graphics/deliveries/ART-0003/manifest.json").read_text(encoding="utf-8"))["items"]
    for item in sorted(foam, key=lambda i: i["frame_order"]):
        identifier = FOAM_IDS[item["id"]]
        if identifier in known:
            continue
        record, native = foam_record(item["id"], identifier, item)
        print(record["id"], item["id"], record["pixel_size"])
        if args.dry_run:
            continue
        target = ROOT / record["texture_path"].removeprefix("res://")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(native, target)
        catalog["assets"].append(record)
        added += 1
    if added:
        catalog["asset_count"] = len(catalog["assets"])
        b3.INDEX.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"registered {added}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
