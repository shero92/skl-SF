#!/usr/bin/env python3
"""Review-only Hero Room candidates (TASK-0047): assemble delivered pieces over a published map in
real Godot, capture base + candidate and compare both with the goal reference.

    py -3 tools/candidate_room.py capture map_factory/candidates/hero_room_01_blender_v1.json

Writes docs/previews/candidates/<id>_base.png, <id>_candidate.png, <id>_compare.png and
<id>_metrics.json. Never publishes a map version, never edits the catalog or map_factory/parts.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / ".agents/planner/config.json"
DELIVERIES = ROOT / ".agents/graphics/deliveries"
OUT = ROOT / "docs/previews/candidates"
REFERENCE = ROOT / ".agents/planner/goals/GOAL-0001/references/hero_room_reference.png"
POINTS = {"top_left": (0.0, 0.0), "left_center": (0.0, 0.5), "right_center": (1.0, 0.5),
          "center": (0.5, 0.5), "bottom_center": (0.5, 1.0)}
# ground: above the floor; walls: candidate wall pass (z 30); props: y-sorted with the base furniture (z 40).
LAYERS = ("ground", "walls", "props")


def godot_executable(override: str | None = None) -> str | None:
    """Windowed Godot (captures need a real display); the console build is fine too."""
    candidates = [override, os.environ.get("GODOT_EXECUTABLE")]
    if CONFIG.is_file():
        candidates.append(json.loads(CONFIG.read_text(encoding="utf-8")).get("godot_executable"))
    candidates.append("godot")
    for c in candidates:
        if c and (Path(c).is_file() or shutil.which(c)):
            return c
    return None


def resolve(layout_path: Path, root: Path = ROOT) -> dict:
    """Expand grid cells into exact pixel placements using each delivery (or staged render) manifest's anchors."""
    layout = json.loads(Path(layout_path).read_text(encoding="utf-8"))
    base = layout["base"]
    rel = f"map_factory/maps/{base['map_id']}/versions/v{int(base['version']):04d}.json"
    snapshot = json.loads((root / rel).read_text(encoding="utf-8"))
    tile = int(snapshot["tile_size"])
    ox, oy = snapshot["ground_offset"]
    manifests: dict[str, dict] = {}
    placements = []
    for piece in layout["pieces"]:
        # "art": an ART delivery; "source": a staged candidate-only render folder (blender_factory stage).
        art = piece.get("art") or piece["source"]
        if art not in manifests:
            folder = root / ".agents/graphics/deliveries" / art if "art" in piece else root / art
            manifests[art] = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
        item = next((f for f in manifests[art]["files"] if Path(f["path"]).stem == piece["file"]), None)
        if item is None:
            raise ValueError(f"{art} delivers no {piece['file']}")
        if piece["layer"] not in LAYERS:
            raise ValueError("layer must be one of " + ", ".join(LAYERS))
        anchor = item["anchors_px"][piece["anchor"]]
        fx, fy = POINTS[piece.get("point", "top_left")]
        # offset_px: calibrated contacts that do not sit on a grid point (docs/HERO_ROOM_CALIBRATION.md).
        dx, dy = piece.get("offset_px", [0, 0])
        for n, (cx, cy) in enumerate(piece["cells"]):
            placements.append({
                "name": f"{piece['file']}_{cx}_{cy}", "layer": piece["layer"], "art": art,
                "texture": str((root / item["path"]).resolve()).replace("\\", "/"),
                "shadow": str((root / item["shadow"]).resolve()).replace("\\", "/") if item.get("shadow") else "",
                "anchor_px": anchor, "pixel_size": item["pixel_size"], "sha256": item["sha256"],
                "position": [ox + (cx + fx) * tile + dx, oy + (cy + fy) * tile + dy]})
    # refloor_cells [x, y, from_x, from_y]: show a plain neighbouring floor tile instead of an override
    # (e.g. under an inlay that replaces procedural tiles); review-only, the map snapshot is unchanged.
    for cell in layout.get("refloor_cells", []):
        if len(cell) != 4:
            raise ValueError("refloor_cells entries are [x, y, from_x, from_y]")
    return {"candidate_id": layout["candidate_id"], "base_path": "res://" + rel,
            "canvas_size": snapshot.get("canvas_size", [1536, 1024]), "tile_size": tile,
            "hide_instances": layout.get("hide_instances", []), "hide_floor_cells": layout.get("hide_floor_cells", []),
            "refloor_cells": layout.get("refloor_cells", []), "placements": placements}


def piece_boxes(resolved: dict) -> list[list[int]]:
    """Screen rectangles covered by the candidate pieces (for regional comparison)."""
    boxes = []
    for p in resolved["placements"]:
        x0 = p["position"][0] - p["anchor_px"][0]
        y0 = p["position"][1] - p["anchor_px"][1]
        boxes.append([int(x0), int(y0), int(x0 + p["pixel_size"][0]), int(y0 + p["pixel_size"][1])])
    return boxes


def mean_abs_diff(a, b, box=None) -> float:
    from PIL import ImageChops, ImageStat
    if box:
        a, b = a.crop(box), b.crop(box)
    return round(sum(ImageStat.Stat(ImageChops.difference(a, b)).mean) / 3, 2)


def compare(base_png: Path, candidate_png: Path, reference_png: Path, resolved: dict, out_png: Path) -> dict:
    """Mean absolute RGB difference (0-255, lower = closer) to the reference, whole image and per region."""
    from PIL import Image, ImageDraw
    base = Image.open(base_png).convert("RGB")
    cand = Image.open(candidate_png).convert("RGB")
    ref = Image.open(reference_png).convert("RGB")
    if ref.size != base.size:
        ref = ref.resize(base.size, Image.Resampling.LANCZOS)
    w, h = base.size
    boxes = [[max(0, b[0]), max(0, b[1]), min(w, b[2]), min(h, b[3])] for b in piece_boxes(resolved)]
    regions = {}
    for layer in LAYERS:
        sel = [b for b, p in zip(boxes, resolved["placements"]) if p["layer"] == layer]
        if sel:
            box = [min(b[0] for b in sel), min(b[1] for b in sel), max(b[2] for b in sel), max(b[3] for b in sel)]
            regions[layer] = {"box": box, "base": mean_abs_diff(base, ref, box), "candidate": mean_abs_diff(cand, ref, box)}
    # Per placement box: which piece moves the capture toward (or away from) the reference.
    pieces = {}
    for i, (b, p) in enumerate(zip(boxes, resolved["placements"])):
        if b[2] > b[0] and b[3] > b[1]:
            pieces[p.get("name", str(i))] ={"box": b, "base": mean_abs_diff(base, ref, b), "candidate": mean_abs_diff(cand, ref, b)}
    metrics = {"metric": "mean absolute RGB difference to the reference (0-255, lower is closer)",
               "whole": {"base": mean_abs_diff(base, ref), "candidate": mean_abs_diff(cand, ref)},
               "regions": regions, "pieces": pieces, "reference_resized": ref.size != Image.open(reference_png).size}
    # Side-by-side sheet for the owner: reference | base | candidate, half size, regions outlined.
    half = (w // 2, h // 2)
    sheet = Image.new("RGB", (half[0] * 3 + 40, half[1] + 40), (24, 24, 28))
    for i, (label, im) in enumerate((("reference", ref), ("base v%04d" % int(resolved["base_path"][-9:-5]), base),
                                     ("candidate " + resolved["candidate_id"], cand))):
        tile = im.resize(half, Image.Resampling.LANCZOS)
        if i:
            draw = ImageDraw.Draw(tile)
            for region in regions.values():
                draw.rectangle([v // 2 for v in region["box"]], outline=(255, 64, 64), width=2)
        sheet.paste(tile, (10 + i * (half[0] + 10), 30))
        ImageDraw.Draw(sheet).text((12 + i * (half[0] + 10), 8), label, fill=(235, 235, 235))
    sheet.save(out_png)
    return metrics


def capture(layout_path: Path, godot: str | None = None, timeout: int = 600) -> dict:
    exe = godot_executable(godot)
    if exe is None:
        raise RuntimeError("Godot not found: set godot_executable in .agents/planner/config.json or GODOT_EXECUTABLE")
    resolved = resolve(layout_path)
    cid = resolved["candidate_id"]
    OUT.mkdir(parents=True, exist_ok=True)
    base_png, cand_png = OUT / f"{cid}_base.png", OUT / f"{cid}_candidate.png"
    with tempfile.TemporaryDirectory(prefix="candidate-") as tmp:
        spec = Path(tmp) / "resolved.json"
        spec.write_text(json.dumps(resolved, indent=2), encoding="utf-8", newline="\n")
        proc = subprocess.run([exe, "--path", str(ROOT), "--rendering-driver", "opengl3", "--script",
                               "res://tools/capture_candidate_room.gd", "--", str(spec), str(base_png), str(cand_png)],
                              capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
    log = proc.stdout + proc.stderr
    if proc.returncode or log.count("CANDIDATE_CAPTURE_OK") != 2:
        raise RuntimeError("Godot capture failed:\n" + "\n".join(log.strip().splitlines()[-15:]))
    metrics = compare(base_png, cand_png, REFERENCE, resolved, OUT / f"{cid}_compare.png")
    metrics.update({"candidate_id": cid, "layout": Path(layout_path).as_posix(), "base": resolved["base_path"],
                    "placements": len(resolved["placements"]), "godot": Path(exe).name,
                    "status": "candidate_unapproved", "approval": None})
    (OUT / f"{cid}_metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8", newline="\n")
    return metrics


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("capture")
    c.add_argument("layout", type=Path)
    c.add_argument("--godot")
    r = sub.add_parser("resolve")
    r.add_argument("layout", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.cmd == "resolve":
            print(json.dumps(resolve(args.layout), indent=2))
        else:
            print(json.dumps(capture(args.layout, args.godot), indent=2))
        return 0
    except (OSError, RuntimeError, ValueError, KeyError) as exc:
        print("candidate room:", exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
