"""Audit a Map Factory snapshot (TASK-0112).

Usage: python tools/map_audit.py --map hero_room_01 [--version 14] [--json out.json]

Reports duplicate/missing instance ids, unknown asset ids, registered assets that are
never used, per-asset instance counts, instances without a usable anchor and overlapping
footprints of furniture. It reads data only and never edits a map.

Execution provenance: Agent: claude (Claude Code); model: Sonnet 5.5.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from map_data import ROOT, iter_instances, load_catalog, load_map

FURNITURE_LIST = "objects"
DIRECTION_SUFFIX = re.compile(r"_(north|south|east|west)$")


def base_id(asset: str) -> str:
    """Directional variants (F05_south) belong to their base catalog asset (F05)."""
    return DIRECTION_SUFFIX.sub("", asset)


def footprint(record: dict, catalog: dict, tile: int) -> tuple[float, float, float, float] | None:
    info = catalog.get(base_id(str(record.get("id"))))
    if not info:
        return None
    scale = float(record.get("scale", 1.0))
    width = float(info.get("footprint_tiles_x", 1)) * tile * scale
    depth = float(info.get("footprint_tiles_y", 1)) * tile * scale
    x, y = float(record.get("x", 0)), float(record.get("y", 0))
    return (x - width / 2, y - depth, x + width / 2, y)


def overlap_area(a: tuple, b: tuple) -> float:
    w = min(a[2], b[2]) - max(a[0], b[0])
    h = min(a[3], b[3]) - max(a[1], b[1])
    return w * h if w > 0 and h > 0 else 0.0


def audit(data: dict, catalog: dict, min_overlap: float = 64.0) -> dict:
    tile = int(data.get("tile_size", 64))
    ids = Counter()
    asset_counts = Counter()
    problems: dict[str, list] = {"duplicate_instance_ids": [], "missing_instance_ids": [], "unknown_assets": [], "bad_position": [], "overlaps": []}
    furniture = []
    for list_name, record in iter_instances(data):
        instance = record.get("instance_id")
        asset = base_id(str(record.get("id", "")))
        asset_counts[asset] += 1
        if not instance:
            problems["missing_instance_ids"].append({"list": list_name, "asset": asset})
        else:
            ids[instance] += 1
        if asset not in catalog:
            problems["unknown_assets"].append({"list": list_name, "asset": asset, "instance_id": instance})
        if not isinstance(record.get("x"), (int, float)) or not isinstance(record.get("y"), (int, float)):
            problems["bad_position"].append({"list": list_name, "instance_id": instance})
        if list_name == FURNITURE_LIST:
            box = footprint(record, catalog, tile)
            if box:
                furniture.append((instance, box))
    problems["duplicate_instance_ids"] = sorted(name for name, count in ids.items() if count > 1)
    for i, (name_a, box_a) in enumerate(furniture):
        for name_b, box_b in furniture[i + 1:]:
            area = overlap_area(box_a, box_b)
            if area >= min_overlap:
                problems["overlaps"].append({"a": name_a, "b": name_b, "area": round(area, 1)})
    unused = sorted(set(catalog) - set(asset_counts))
    return {
        "instances": sum(asset_counts.values()),
        "distinct_assets": len(asset_counts),
        "asset_counts": dict(sorted(asset_counts.items())),
        "unused_registered_assets": unused,
        "problems": problems,
        "problem_count": sum(len(v) for v in problems.values()),
    }


def render_text(report: dict) -> str:
    lines = [f"instances: {report['instances']}  distinct assets: {report['distinct_assets']}  unused registered: {len(report['unused_registered_assets'])}"]
    for name, items in report["problems"].items():
        lines.append(f"{name}: {len(items)}")
        for item in items[:10]:
            lines.append(f"  - {item}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--map", required=True)
    parser.add_argument("--version", type=int)
    parser.add_argument("--json")
    args = parser.parse_args(argv)
    report = audit(load_map(args.map, args.version), load_catalog())
    print(render_text(report))
    if args.json:
        Path(args.json).write_text(json.dumps(report, indent=2), encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
