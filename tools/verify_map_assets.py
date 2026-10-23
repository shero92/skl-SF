#!/usr/bin/env python3
"""Read-only validation for reusable MAP sprites. Never mutates character/UI records."""
from pathlib import Path
import json,sys
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
BLOCKED={"characters","ui"}
TYPES={"floors","walls","architecture","stairs","environment",
       "furniture","objects","vegetation","decor","shadows"}

def main():
    records=json.loads((ROOT/"map_factory/metadata/asset_index.json").read_text(
        encoding="utf-8"))["assets"]
    errors=[]
    scanned=0
    for a in records:
        if a["category"] in BLOCKED:
            continue
        if a["category"] not in TYPES:
            errors.append("Unknown map asset category: "+str(a["category"]))
            continue
        src=ROOT/a["texture_path"].removeprefix("res://")
        if not src.is_file():
            errors.append("Missing "+a["id"])
            continue
        with Image.open(src) as img:
            if img.format!="PNG":
                errors.append("Wrong format "+a["id"])
            if [*img.size]!=a.get("pixel_size"):
                errors.append("Pixel-size mismatch "+a["id"])
            if img.convert("RGBA").getchannel("A").getbbox() is None:
                errors.append("Empty sprite "+a["id"])
        scanned+=1
    print(json.dumps({"map_assets_checked":scanned,
                      "gameplay_categories_ignored":sorted(BLOCKED),
                      "errors":errors},indent=2))
    return bool(errors)

if __name__=="__main__":
    sys.exit(main())
