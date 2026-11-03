"""Build aligned HD runtime textures from the owner's HD masters.

For each assets_generated PNG listed in assets_hd/hd_map.json the matching master is cropped to its
visible bounds, fitted onto the low asset's visible bounds, and written at SCALE x the native size to
assets_hd/runtime/<same file name>. The loader scales them back to native size, so placements, anchors
and footprints are unchanged. Masters are not stored in git: pass --masters <dir containing the category folders>.
"""
import argparse, json, sys
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]


def bbox(im):
    return im.split()[3].point(lambda v: 255 if v > 16 else 0).getbbox()


def build(masters: Path, only=None):
    cfg = json.loads((ROOT / "assets_hd/hd_map.json").read_text(encoding="utf-8"))
    scale = int(cfg["scale"])
    out_dir = ROOT / "assets_hd/runtime"
    out_dir.mkdir(parents=True, exist_ok=True)
    built = []
    for rel, rec in cfg["map"].items():
        if only and not rel.startswith(only):
            continue
        low = Image.open(ROOT / "assets_generated" / rel).convert("RGBA")
        hd = Image.open(masters / rec["master"]).convert("RGBA")
        lb, hb = bbox(low), bbox(hd)
        if lb is None or hb is None:
            raise SystemExit(f"empty alpha: {rel}")
        hd = hd.crop(hb)
        if rec.get("flip_h"):
            hd = ImageOps.mirror(hd)
        tw, th = (lb[2] - lb[0]) * scale, (lb[3] - lb[1]) * scale
        hd = hd.resize((tw, th), Image.LANCZOS)
        canvas = Image.new("RGBA", (low.width * scale, low.height * scale), (0, 0, 0, 0))
        canvas.paste(hd, (lb[0] * scale, lb[1] * scale))
        canvas.save(out_dir / Path(rel).name, optimize=True)
        built.append(Path(rel).name)
    return built


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--masters", required=True)
    ap.add_argument("--only", default=None)
    a = ap.parse_args()
    names = build(Path(a.masters), a.only)
    print(f"built {len(names)} HD runtime textures")
