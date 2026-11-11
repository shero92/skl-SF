"""Compare every named region of the owner's target picture with the same region of a real Godot capture.

    python tools/room_region_report.py --map hero_room_01            # latest version, its newest capture
    python tools/room_region_report.py --map hero_room_01 --version 25

Writes docs/previews/map_factory_renders/region_reports/<map>_vNNNN/ with sheet.png (target left, game
right, one row per region) and report.json (difference per region, 0 = same, 100 = opposite, and the
change against the previous report when one exists). The number is a progress hint: it never sets or
implies visual approval, and a lower number is not proof that a region looks right.

Execution provenance: Agent: claude (Claude Code); model: Fable 5.2.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageStat

ROOT = Path(__file__).resolve().parents[1]
RENDERS = Path("docs/previews/map_factory_renders")
REPORTS = RENDERS / "region_reports"
SHRINK = 4  # compare at quarter size so pixel-level noise does not dominate shape and colour


def difference(target: Image.Image, game: Image.Image) -> float:
    """Mean absolute colour difference of two same-size crops, 0 to 100, measured at 1/SHRINK size."""
    size = (max(1, target.width // SHRINK), max(1, target.height // SHRINK))
    a = target.convert("RGB").resize(size, Image.Resampling.BOX)
    b = game.convert("RGB").resize(size, Image.Resampling.BOX)
    return round(sum(ImageStat.Stat(ImageChops.difference(a, b)).mean) / 3 / 255 * 100, 2)


def load_regions(map_id: str, root: Path = ROOT) -> dict:
    return json.loads((root / f"map_factory/references/{map_id}_regions.json").read_text(encoding="utf-8"))


def find_capture(map_id: str, version: int, root: Path = ROOT) -> Path:
    name = f"{map_id}_v{version:04d}.png"
    found = sorted((p for p in (root / RENDERS).glob(f"*/{name}") if REPORTS.name not in p.parts),
                   key=lambda p: p.stat().st_mtime)
    if not found:
        raise FileNotFoundError(f"No Godot capture named {name} under {RENDERS.as_posix()}")
    return found[-1]


def build_report(spec: dict, target: Image.Image, game: Image.Image, version: int, previous: dict | None = None):
    """Returns (report dict, sheet image)."""
    if target.size != game.size:
        raise ValueError("target and game capture must have the same pixel size")
    before = {r["id"]: r["difference"] for r in (previous or {}).get("regions", [])}
    rows = []
    crops = []
    for region in spec["regions"]:
        box = tuple(region["box"])
        t, g = target.crop(box), game.crop(box)
        value = difference(t, g)
        row = {"id": region["id"], "label": region["label"], "box": list(box), "difference": value}
        if region.get("art_request"):
            row["art_request"] = region["art_request"]
        if region["id"] in before:
            row["change"] = round(value - before[region["id"]], 2)  # negative = closer to the target
        rows.append(row)
        crops.append((row, t, g))
    area = sum((r["box"][2] - r["box"][0]) * (r["box"][3] - r["box"][1]) for r in rows)
    overall = round(sum(r["difference"] * (r["box"][2] - r["box"][0]) * (r["box"][3] - r["box"][1]) for r in rows) / area, 2)
    report = {"schema_version": 1, "map_id": spec["map_id"], "version": version, "visual_approval": False,
              "note": "difference: 0 = same, 100 = opposite; a progress hint only, never a visual approval",
              "overall_difference": overall, "regions": rows}
    if previous:
        report["previous_version"] = previous.get("version")
        report["overall_change"] = round(overall - previous["overall_difference"], 2)
    label_h, gap = 18, 8
    width = max(t.width * 2 + gap for _, t, _ in crops)
    height = sum(t.height + label_h + gap for _, t, _ in crops)
    sheet = Image.new("RGB", (width, height), (24, 28, 36))
    draw = ImageDraw.Draw(sheet)
    y = 0
    for row, t, g in crops:
        text = f"{row['label']}  |  difference {row['difference']}"
        if "change" in row:
            text += f"  ({row['change']:+})"
        draw.text((4, y + 3), text, fill=(235, 235, 235))
        sheet.paste(t.convert("RGB"), (0, y + label_h))
        sheet.paste(g.convert("RGB"), (t.width + gap, y + label_h))
        y += t.height + label_h + gap
    return report, sheet


def write_report(map_id: str, version: int, capture: Path | None = None, root: Path = ROOT) -> Path:
    spec = load_regions(map_id, root)
    capture = capture or find_capture(map_id, version, root)
    earlier = sorted(p for p in (root / REPORTS).glob(f"{map_id}_v*/report.json")
                     if int(p.parent.name.rsplit("_v", 1)[1]) < version)
    previous = json.loads(earlier[-1].read_text(encoding="utf-8")) if earlier else None
    with Image.open(root / spec["target"]) as target, Image.open(capture) as game:
        report, sheet = build_report(spec, target, game, version, previous)
    report["target"] = spec["target"]
    report["capture"] = capture.relative_to(root).as_posix()
    out = root / REPORTS / f"{map_id}_v{version:04d}"
    out.mkdir(parents=True, exist_ok=True)
    sheet.resize((sheet.width // 2, sheet.height // 2), Image.Resampling.BOX).save(out / "sheet.png")  # half size keeps the repo small
    (out / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--map", default="hero_room_01")
    ap.add_argument("--version", type=int)
    ap.add_argument("--capture", type=Path, help="capture PNG; default: newest capture of that version")
    args = ap.parse_args()
    version = args.version
    if version is None:
        version = int(json.loads((ROOT / f"map_factory/maps/{args.map}/latest.json").read_text(encoding="utf-8"))["version"])
    out = write_report(args.map, version, (ROOT / args.capture) if args.capture else None)
    report = json.loads((out / "report.json").read_text(encoding="utf-8"))
    for row in report["regions"]:
        change = f"  ({row['change']:+})" if "change" in row else ""
        print(f"{row['difference']:6.2f}{change:10}  {row['label']}")
    print(f"{report['overall_difference']:6.2f}  overall (area-weighted); visual_approval stays false")
    print(out.relative_to(ROOT).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
