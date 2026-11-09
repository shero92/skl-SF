"""Turn an owner-accepted Blender delivery into catalog metadata (TASK-0015, TASK-0025).

Usage: python tools/blender_catalog.py ART-0004 --accepted-by owner --note "quote"
       python tools/art_delivery.py --stage ART-0004     # then registers the PNGs

The Blender factory writes `files` (native PNGs, hashes, measured anchors) but no catalog records. This
tool records the owner's acceptance in the manifest and builds one catalog record per delivered PNG from
the measured data (size, foot anchor, facing, builder) with the next free catalog IDs. Pixels are never
touched; separate cast-shadow PNGs stay in the delivery folder (they are not registered as parts).

Execution provenance: Agent: claude (Claude Code); model: Sonnet 5.5.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from art_delivery import ROOT, request_fields

BUILDERS = {"wall_run": ("walls", "W", "stone", ["walls", "stone", "wall", "run", "ivy"], True),
            "broken_floor_edge": ("floors", "F", "stone", ["floors", "stone", "broken", "edge", "terrace"], False)}


def next_ids(catalog_assets: list[dict], prefix: str, count: int) -> list[str]:
    numbers = [int(a["id"][1:]) for a in catalog_assets if re.fullmatch(prefix + r"\d{3,4}", a["id"])]
    start = max(numbers, default=0) + 1
    return [f"{prefix}{n:03d}" for n in range(start, start + count)]


def title(stem: str) -> str:
    return " ".join(part.capitalize() for part in re.split(r"[_ ]+", stem))


def build_assets(manifest: dict, catalog_assets: list[dict], accepted_by: str, note: str) -> list[dict]:
    files = manifest["files"]
    builders = {f.get("builder") for f in files}
    if len(builders) != 1 or next(iter(builders)) not in BUILDERS:
        raise ValueError(f"unsupported builder set: {builders}")
    category, prefix, subtype, tags, y_sort = BUILDERS[next(iter(builders))]
    ids = next_ids(catalog_assets, prefix, len(files))
    assets = []
    for identifier, record in zip(ids, files):
        stem = Path(record["path"]).stem
        name = title(stem)
        width, height = record["pixel_size"]
        anchors = record.get("anchors_px", {})
        foot = anchors.get("foot_center_front", [width / 2, height])
        assets.append({
            "id": identifier,
            "name": name,
            "category": category,
            "subtype": subtype,
            "texture_path": f"res://map_factory/parts/{category}/{identifier}_{name.replace(' ', '_')}.png",
            "status": "ready",
            "pixel_size": [width, height],
            "origin": [int(round(foot[0])), int(round(foot[1]))],
            "collision": {"enabled": False, "size": [32, 16], "offset": [0, 0]},
            "y_sort": y_sort,
            "shadow": {"type": "none", "opacity": 0.25, "offset_x": 4, "offset_y": 2},
            "tags": sorted(set(tags + [record.get("facing", "default")])),
            "reusable": True,
            "source": {"kind": "owner_delivery", "file": record["path"], "builder": record.get("builder"),
                       "master": record.get("master"), "master_sha256": record.get("master_sha256"),
                       "sha256": record["sha256"]},
            "qa_notes": f"Built with tools/blender_factory.py (no AI image generation). Accepted by {accepted_by}: {note}",
            "qa_approval": {"approved_by": accepted_by, "evidence": note,
                            "method": "built with tools/blender_factory.py, scripted QA clean, accepted by the owner"},
        })
    return assets


def accept(request_id: str, accepted_by: str, note: str, root: Path = ROOT) -> list[dict]:
    fields, _text = request_fields(root / ".agents/graphics/requests" / next(
        p.name for p in (root / ".agents/graphics/requests").glob(f"{request_id}_*.md")))
    if fields.get("status") != "delivered":
        raise ValueError(f"{request_id} is not delivered")
    folder = root / ".agents/graphics/deliveries" / request_id
    manifest_path = folder / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    catalog = json.loads((root / "map_factory/metadata/asset_index.json").read_text(encoding="utf-8"))
    if "assets" not in manifest:
        manifest["assets"] = build_assets(manifest, catalog["assets"], accepted_by, note)
    manifest["status"] = "owner_accepted"
    manifest["review"] = {**manifest.get("review", {}), "visual_approval": "owner_accepted",
                          "accepted_by": accepted_by, "note": note}
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return manifest["assets"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request_id")
    parser.add_argument("--accepted-by", required=True)
    parser.add_argument("--note", required=True)
    args = parser.parse_args()
    assets = accept(args.request_id, args.accepted_by, args.note)
    for asset in assets:
        print(asset["id"], asset["name"], asset["pixel_size"], asset["origin"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
