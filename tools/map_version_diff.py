"""Diff two immutable Map Factory versions (TASK-0113).

Usage: python tools/map_version_diff.py --map hero_room_01 --from 13 --to 14 [--json out.json]

Lists instances that were added, removed, moved or changed by instance_id. Read only.

Execution provenance: Agent: claude (Claude Code); model: Sonnet 5.5.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from map_data import iter_instances, load_map

CHANGE_FIELDS = ("id", "scale", "facing", "render_layer", "shadow", "mount_on", "rotation")


def index(data: dict) -> dict[str, tuple[str, dict]]:
    return {str(r["instance_id"]): (name, r) for name, r in iter_instances(data) if r.get("instance_id")}


def diff(old: dict, new: dict, move_tolerance: float = 0.5) -> dict:
    a, b = index(old), index(new)
    added = sorted(set(b) - set(a))
    removed = sorted(set(a) - set(b))
    moved, changed = [], []
    for key in sorted(set(a) & set(b)):
        (list_a, rec_a), (list_b, rec_b) = a[key], b[key]
        dx = float(rec_b.get("x", 0)) - float(rec_a.get("x", 0))
        dy = float(rec_b.get("y", 0)) - float(rec_a.get("y", 0))
        if abs(dx) > move_tolerance or abs(dy) > move_tolerance:
            moved.append({"instance_id": key, "dx": round(dx, 2), "dy": round(dy, 2)})
        fields = {f: [rec_a.get(f), rec_b.get(f)] for f in CHANGE_FIELDS if rec_a.get(f) != rec_b.get(f)}
        if list_a != list_b:
            fields["list"] = [list_a, list_b]
        if fields:
            changed.append({"instance_id": key, "fields": fields})
    return {
        "from_version": old.get("version"),
        "to_version": new.get("version"),
        "added": added,
        "removed": removed,
        "moved": moved,
        "changed": changed,
        "summary": {"added": len(added), "removed": len(removed), "moved": len(moved), "changed": len(changed)},
    }


def render_text(report: dict) -> str:
    s = report["summary"]
    lines = [f"v{report['from_version']} -> v{report['to_version']}: +{s['added']} -{s['removed']} moved {s['moved']} changed {s['changed']}"]
    for name in report["added"][:20]:
        lines.append(f"  + {name}")
    for name in report["removed"][:20]:
        lines.append(f"  - {name}")
    for item in report["moved"][:20]:
        lines.append(f"  ~ {item['instance_id']} ({item['dx']:+}, {item['dy']:+})")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--map", required=True)
    parser.add_argument("--from", dest="old", type=int, required=True)
    parser.add_argument("--to", dest="new", type=int, required=True)
    parser.add_argument("--json")
    args = parser.parse_args(argv)
    report = diff(load_map(args.map, args.old), load_map(args.map, args.new))
    print(render_text(report))
    if args.json:
        Path(args.json).write_text(json.dumps(report, indent=2), encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
