"""Seeded scale and rotation variation for placed Map Factory blocks.

Usage: python tools/map_variation.py --map hero_room_01 --seed 7 --out PATCH.json
                                     [--scale-jitter 0.15] [--rotation-range 360]
                                     [--scale-only ID,ID]

Only rotation-safe pieces (map_factory/metadata/transform_rules.json) get a free rotation.
Upright pieces are never turned. `--scale-only` lets named ids vary in size only. Results
are deterministic per (seed, instance_id), so the order of placements never changes the
outcome. Scale and rotation snap to the steps in the rules file to keep pixel density
consistent. The output is a patch manifest of `update_block` operations for
tools/map_factory_cli.py apply.

Execution provenance: Agent: claude (Claude Code); model: Sonnet 5.5.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from map_data import ROOT, iter_instances, load_json, load_map


def load_rules(root: Path = ROOT) -> dict:
    return load_json(root / "map_factory" / "metadata" / "transform_rules.json")


def unit(seed: int, instance_id: str, salt: str) -> float:
    """Deterministic number in [0, 1) for one instance and purpose."""
    digest = hashlib.sha256(f"{seed}:{instance_id}:{salt}".encode()).digest()
    return int.from_bytes(digest[:8], "big") / 2 ** 64


def snap(value: float, step: float) -> float:
    return round(round(value / step) * step, 4) if step else value


def vary_record(record: dict, rules: dict, seed: int, scale_jitter: float = 0.15,
                rotation_range: float = 360.0, scale_only: frozenset = frozenset()) -> dict:
    """Return the changed fields (empty if the record is not eligible)."""
    asset = str(record.get("id", ""))
    instance = str(record.get("instance_id", ""))
    safe = asset in set(rules.get("rotation_safe", []))
    if not safe and asset not in scale_only:
        return {}
    changes = {}
    base = float(record.get("scale", 1.0))
    factor = 1.0 + (unit(seed, instance, "scale") * 2 - 1) * scale_jitter
    scale = snap(base * factor, float(rules.get("scale_snap", 0.05)))
    scale = min(max(scale, float(rules.get("scale_min", 0.1))), float(rules.get("scale_max", 4.0)))
    if abs(scale - base) > 1e-9:
        changes["scale"] = scale
    limit = float(rules.get("rotation_range_degrees", {}).get(asset, rotation_range))
    span = min(rotation_range, limit)
    if safe and span > 0:
        angle = (unit(seed, instance, "rotation") - 0.5) * span
        angle = snap(angle, float(rules.get("rotation_snap_degrees", 15))) % 360
        if angle != float(record.get("rotation_degrees", 0)) % 360:
            changes["rotation_degrees"] = angle
    return changes


def vary(data: dict, rules: dict, seed: int, **options) -> list[dict]:
    """update_block operations for every eligible instance of a map snapshot."""
    operations = []
    for _list_name, record in iter_instances(data):
        changes = vary_record(record, rules, seed, **options)
        if changes:
            operations.append({"op": "update_block", "instance_id": record["instance_id"], "set": changes})
    return operations


def build_manifest(data: dict, operations: list[dict], seed: int) -> dict:
    return {
        "manifest_version": 1,
        "map_id": data["map_id"],
        "base_version": data["version"],
        "base_sha256": None,
        "note": f"Seeded scale and rotation variation (seed {seed}) on rotation-safe pieces.",
        "source_image": data.get("source_image", {}),
        "changes": operations,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--map", required=True)
    parser.add_argument("--version", type=int)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--scale-jitter", type=float, default=0.15)
    parser.add_argument("--rotation-range", type=float, default=360.0)
    parser.add_argument("--scale-only", default="")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    data = load_map(args.map, args.version)
    options = {"scale_jitter": args.scale_jitter, "rotation_range": args.rotation_range,
               "scale_only": frozenset(x for x in args.scale_only.split(",") if x)}
    operations = vary(data, load_rules(), args.seed, **options)
    manifest = build_manifest(data, operations, args.seed)
    index = load_json(ROOT / "map_factory" / "maps" / "index.json")["maps"][args.map]
    manifest["base_version"] = index["version"]
    manifest["base_sha256"] = index["snapshot_sha256"]
    print(f"{len(operations)} instances varied")
    if args.out:
        Path(args.out).write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
