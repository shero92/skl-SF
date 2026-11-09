"""Region-by-region comparison of a room render against the owner target (TASK-0106).

Usage: python tools/map_reference_compare.py --render R.png --target T.png --out-dir DIR

Splits both images into the review zones, measures colour and edge differences and writes
`compare.json` and a side-by-side `compare.png` with zone boxes. The status per zone is an
automatic hint (matched / partial / missing); it is NOT a visual approval and the JSON always
carries `visual_approval: false`.

Execution provenance: Agent: claude (Claude Code); model: Sonnet 5.5.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageStat

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from hero_room_capture_evidence import CANVAS, ZONES

# Heuristic thresholds on the 0..1 combined distance. Tuned for hints only.
MATCHED_BELOW = 0.12
MISSING_ABOVE = 0.28


def _edge_density(image: Image.Image) -> float:
    edges = image.convert("L").filter(ImageFilter.FIND_EDGES)
    return ImageStat.Stat(edges).mean[0] / 255.0


def _histogram_distance(a: Image.Image, b: Image.Image, bins: int = 8) -> float:
    total = 0.0
    for channel in range(3):
        ha = a.getchannel(channel).histogram()
        hb = b.getchannel(channel).histogram()
        step = 256 // bins
        pa = [sum(ha[i:i + step]) for i in range(0, 256, step)]
        pb = [sum(hb[i:i + step]) for i in range(0, 256, step)]
        na, nb = sum(pa) or 1, sum(pb) or 1
        total += sum(abs(x / na - y / nb) for x, y in zip(pa, pb)) / 2.0
    return total / 3.0


def compare_zone(render: Image.Image, target: Image.Image, box: list[int]) -> dict:
    region = (box[0], box[1], box[2], box[3])
    crop_r, crop_t = render.crop(region), target.crop(region)
    mean_diff = sum(abs(x - y) for x, y in zip(ImageStat.Stat(crop_r).mean, ImageStat.Stat(crop_t).mean)) / (3 * 255.0)
    pixel_diff = ImageStat.Stat(ImageChops.difference(crop_r, crop_t).convert("L")).mean[0] / 255.0
    histogram = _histogram_distance(crop_r, crop_t)
    er, et = _edge_density(crop_r), _edge_density(crop_t)
    edge_ratio = abs(er - et) / max(er, et, 1e-6)
    score = round(0.25 * mean_diff * 4 + 0.25 * pixel_diff + 0.3 * histogram + 0.2 * edge_ratio, 4)
    status = "matched" if score < MATCHED_BELOW else ("missing" if score > MISSING_ABOVE else "partial")
    return {
        "box": box,
        "score": score,
        "status_hint": status,
        "mean_colour_diff": round(mean_diff, 4),
        "histogram_distance": round(histogram, 4),
        "edge_density_render": round(er, 4),
        "edge_density_target": round(et, 4),
    }


def compare(render_path: Path, target_path: Path) -> dict:
    render = Image.open(render_path).convert("RGB")
    target = Image.open(target_path).convert("RGB")
    if list(render.size) != CANVAS or list(target.size) != CANVAS:
        raise ValueError(f"both images must be {CANVAS}: render {render.size}, target {target.size}")
    zones = {name: compare_zone(render, target, box) for name, box in ZONES.items()}
    return {"canvas": CANVAS, "zones": zones, "visual_approval": False,
            "note": "Automatic hints only; a human visual review is required."}


def side_by_side(render_path: Path, target_path: Path, report: dict, out: Path) -> None:
    render = Image.open(render_path).convert("RGB")
    target = Image.open(target_path).convert("RGB")
    colours = {"matched": (60, 200, 90), "partial": (240, 190, 40), "missing": (230, 70, 60)}
    for image in (render, target):
        draw = ImageDraw.Draw(image)
        for name, zone in report["zones"].items():
            if name == "lighting_and_shadows":
                continue
            draw.rectangle(zone["box"], outline=colours[zone["status_hint"]], width=3)
            draw.text((zone["box"][0] + 6, zone["box"][1] + 4), name, fill=colours[zone["status_hint"]])
    sheet = Image.new("RGB", (CANVAS[0] * 2 + 20, CANVAS[1]), (30, 30, 30))
    sheet.paste(target, (0, 0))
    sheet.paste(render, (CANVAS[0] + 20, 0))
    sheet.resize((sheet.width // 2, sheet.height // 2)).save(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render", required=True, type=Path)
    parser.add_argument("--target", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args(argv)
    report = compare(args.render, args.target)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "compare.json").write_text(json.dumps(report, indent=2), encoding="utf-8", newline="\n")
    side_by_side(args.render, args.target, report, args.out_dir / "compare.png")
    for name, zone in report["zones"].items():
        print(f"{name:28s} {zone['status_hint']:8s} score {zone['score']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
