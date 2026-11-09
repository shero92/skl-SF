"""Record the layout data of the low-quality twins, then retire the twins (TASK-0117).

Usage: python tools/migrate_low_to_hd.py            # plan: verify every twin and print what would change
       python tools/migrate_low_to_hd.py --apply    # write layout fields into assets_hd/hd_map.json
       python tools/migrate_low_to_hd.py --apply --remove   # also delete the low PNGs and their .import files

Each entry of assets_hd/hd_map.json maps a low-quality `assets_generated/<category>/<file>.png` to an
owner HD master. The HD runtime texture is built by fitting the master onto the low image's visible
bounds, so the low file only supplies layout numbers. This tool copies those numbers into hd_map.json
(`native_size`, `visible_bbox`, `low_sha256`, `measure`) so tools/build_hd_runtime_textures.py no longer needs the low
file, and checks that an HD runtime texture of exactly SCALE x native size exists for every entry before
it removes anything. Immutable map snapshots keep their old texture paths; HdAssets.resolve maps them to
the runtime texture by file name.

Execution provenance: Agent: claude (Claude Code); model: Sonnet 5.5.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
HD_MAP = ROOT / "assets_hd" / "hd_map.json"
LOW_DIR = ROOT / "assets_generated"
RUNTIME = ROOT / "assets_hd" / "runtime"


def visible_bbox(image: Image.Image) -> list[int] | None:
    box = image.split()[3].point(lambda v: 255 if v > 16 else 0).getbbox()
    return list(box) if box else None


def measure(image: Image.Image) -> dict:
    """Same numbers as tools/build_hero_room_blueprint.measure_png (alpha threshold 24)."""
    box = image.split()[3].point(lambda v: 255 if v > 24 else 0).getbbox()
    width, height = image.size
    if box is None:
        return {"size": [width, height], "content": [0, 0, 0, 0], "bottom_gap": height, "content_cx": width / 2.0}
    x0, y0, x1, y1 = box
    return {"size": [width, height], "content": [x0, y0, x1 - x0, y1 - y0],
            "bottom_gap": height - y1, "content_cx": (x0 + x1) / 2.0}


def inspect(relative: str, scale: int) -> dict:
    """Layout fields of one low image plus the verification of its HD runtime twin."""
    low_path = LOW_DIR / relative
    low = Image.open(low_path).convert("RGBA")
    box = visible_bbox(low)
    if box is None:
        raise ValueError(f"empty alpha: {relative}")
    twin = RUNTIME / Path(relative).name
    if not twin.is_file():
        raise ValueError(f"no HD runtime texture for {relative}")
    size = Image.open(twin).size
    if size != (low.width * scale, low.height * scale):
        raise ValueError(f"HD runtime size {size} is not {scale}x the native {low.size} for {relative}")
    return {"native_size": [low.width, low.height], "visible_bbox": box,
            "low_sha256": hashlib.sha256(low_path.read_bytes()).hexdigest(),
            "measure": measure(low)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write the layout fields into hd_map.json")
    parser.add_argument("--remove", action="store_true", help="delete the low PNGs and .import files (needs --apply)")
    args = parser.parse_args()
    if args.remove and not args.apply:
        parser.error("--remove needs --apply")
    config = json.loads(HD_MAP.read_text(encoding="utf-8"))
    scale = int(config["scale"])
    problems = []
    for relative, record in config["map"].items():
        if "measure" in record:
            continue  # already migrated (the low file may be gone)
        try:
            record.update(inspect(relative, scale))
        except (OSError, ValueError) as error:
            problems.append(str(error))
    if problems:
        for line in problems:
            print("PROBLEM:", line)
        return 1
    print(f"{len(config['map'])} twins verified (layout data ready)")
    if not args.apply:
        return 0
    config["note"] = ("low asset (relative to assets_generated/) -> HD master (relative to the masters dir; masters are local, not in git). "
                      "native_size, visible_bbox, low_sha256 and measure are the layout numbers of the retired low image.")
    HD_MAP.write_text(json.dumps(config, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("hd_map.json updated")
    if args.remove:
        removed = 0
        for relative in config["map"]:
            for path in (LOW_DIR / relative, Path(str(LOW_DIR / relative) + ".import")):
                if path.exists():
                    path.unlink()
                    removed += 1
        print(f"removed {removed} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
