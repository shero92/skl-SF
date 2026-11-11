"""Publish the edits made in the in-game room editor as a new immutable Map Factory version.

    python tools/room_editor_save.py --changes <editor_changes.json> [--dry-run]

The editor (scenes/map_factory_editor.tscn) writes {"map_id", "note", "changes": [...]} where each change is
{"op": "add", "layer", "id", "instance_id", "x", "y", "scale", "rotation_degrees", "flip_h"},
{"op": "update", "instance_id", "set": {...}}, {"op": "remove", "instance_id"},
{"op": "tile", "x", "y", "id"} (id null clears the square's own tile) or
{"op": "property", "key": "floor_footprint", "value": {...}}.
`--new <map_id> --preset <name>` creates an empty map from a factory preset instead.
This tool turns them into one patch, validates it with the factory rules and applies it. A rejected edit
leaves nothing behind. --dry-run validates only. Prints ROOM_EDITOR_SAVED <map> v<NNNN> or ROOM_EDITOR_ERROR <why>.

Execution provenance: Agent: claude (Claude Code); model: Fable 5.2.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import map_factory_cli as cli  # noqa: E402
from room_design import Design  # noqa: E402

FREE_FIELDS = {"x", "y", "scale", "rotation_degrees"}
SET_FIELDS = FREE_FIELDS | {"flip_h", "layer"}
PROPERTIES = {"floor_footprint"}


def build_design(request: dict, root: Path = ROOT) -> Design:
    design = Design(str(request["map_id"]), root)
    for change in request.get("changes", []):
        op = change.get("op")
        if op == "add":
            block = {"id": str(change["id"]), "instance_id": str(change["instance_id"]),
                     "x": float(change["x"]), "y": float(change["y"]), "scale": float(change.get("scale", 1.0))}
            if float(change.get("rotation_degrees", 0)):
                block.update(rotation_degrees=float(change["rotation_degrees"]), free_transform=True)
            if change.get("flip_h"):
                block["flip_h"] = True
            design.changes.append({"op": "add_block", "layer": str(change["layer"]), "block": block})
        elif op == "update":
            updates = {k: v for k, v in change.get("set", {}).items() if k in SET_FIELDS}
            if not updates:
                continue
            if FREE_FIELDS & set(updates):
                updates["free_transform"] = True
            design.changes.append({"op": "update_block", "instance_id": str(change["instance_id"]), "set": updates})
        elif op == "remove":
            design.remove(str(change["instance_id"]))
        elif op == "tile":
            design.changes.append({"op": "set_tile", "x": int(change["x"]), "y": int(change["y"]), "id": change.get("id")})
        elif op == "property":
            if change.get("key") not in PROPERTIES:
                raise ValueError(f"The editor may not change the map property {change.get('key')}")
            design.set_property(str(change["key"]), change["value"])
        else:
            raise ValueError(f"Unknown editor change: {op}")
    return design


def save(request: dict, dry_run: bool = False, root: Path = ROOT) -> int:
    """Returns the new version number (the version it would become on a dry run)."""
    design = build_design(request, root)
    patch = design.write_patch(str(request.get("note") or "Room edited by hand in the in-game editor."))
    try:
        candidate = cli.apply(root, patch.relative_to(root), dry_run=dry_run)
    except Exception:
        patch.unlink(missing_ok=True)  # a rejected edit leaves no patch behind
        raise
    if dry_run:
        patch.unlink(missing_ok=True)
    return int(candidate["version"])


def new_map(map_id: str, preset: str, dry_run: bool = False, root: Path = ROOT) -> int:
    """Creates an empty map from a factory preset (version 1). A dry run only checks the name and the preset."""
    cli.check_id(map_id)
    if preset not in cli.PRESET_NAMES:
        raise ValueError("Unknown map preset: " + str(preset))
    if map_id in cli.registry(root)["maps"] or (root / cli.map_base(map_id)).exists():
        raise ValueError("Map already exists: " + map_id)
    if not dry_run:
        cli.create_map(root, map_id, preset, note="Created by hand in the in-game room editor from preset " + preset)
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--changes", type=Path)
    ap.add_argument("--new", dest="new_id")
    ap.add_argument("--preset", default="indoor_room")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.new_id is not None:
        try:
            version = new_map(args.new_id, args.preset, args.dry_run)
        except Exception as error:
            print(f"ROOM_EDITOR_ERROR {error}")
            return 1
        print(f"ROOM_EDITOR_SAVED {args.new_id} v{version:04d}{' (dry run)' if args.dry_run else ''}")
        return 0
    if args.changes is None:
        print("ROOM_EDITOR_ERROR --changes or --new is required")
        return 1
    try:
        request = json.loads(args.changes.read_text(encoding="utf-8"))
        version = save(request, args.dry_run)
    except Exception as error:  # the editor shows this line to the owner
        print(f"ROOM_EDITOR_ERROR {error}")
        return 1
    print(f"ROOM_EDITOR_SAVED {request['map_id']} v{version:04d}{' (dry run)' if args.dry_run else ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
