#!/usr/bin/env python3
"""Versioned, reusable map-only factory for Godot 4.

This tool never creates, imports, updates or renders characters or game UI.
A source image is NOT automatically segmented: an AI/user supplies a reviewed
room placement manifest and optionally independently generated PNG assets.
Each revision is based on the verified latest version, not a stale screenshot.
"""
from __future__ import annotations
from map_factory_layers import create_layer_stack, validate_layer_stack
from map_factory_orientation import resolve_orientation
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
MAPS = Path("map_factory/maps")
INDEX = MAPS / "index.json"
CATALOG = Path("map_factory/metadata/asset_index.json")
LAYERS = ("background_objects", "ground_overlays", "back_objects",
          "objects", "front_objects")
BLOCKED_CATEGORIES = frozenset(("characters", "ui"))
EXCLUDED_GAMEPLAY = frozenset(("npcs", "player_spawn", "interactions"))
SLUG = re.compile(r"^[a-z][a-z0-9_]{1,63}$")


def read(root: Path, relative: Path):
    return json.loads((root / relative).read_text(encoding="utf-8"))


def dump(root: Path, relative: Path, payload):
    dest = root / relative
    dest.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    dest.write_text(text, encoding="utf-8")


def asset_catalog(root: Path):
    records = read(root, CATALOG)["assets"]
    by_id = {str(item["id"]): item for item in records}
    if len(by_id) != len(records):
        raise ValueError("Duplicate asset ID in catalog")
    return by_id


def check_id(value: str, kind="map"):
    if not isinstance(value, str) or not SLUG.fullmatch(value):
        raise ValueError(f"Invalid {kind} ID: {value!r}")
    return value


def map_base(map_id: str):
    return MAPS / check_id(map_id)


def registry(root: Path):
    target = root / INDEX
    return read(root, INDEX) if target.exists() else {"schema_version": 1, "maps": {}}


def digest_json(data) -> str:
    packed = json.dumps(data, sort_keys=True, separators=(",", ":"),
                        ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(packed).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def version_file(map_id, n):
    return map_base(map_id) / "versions" / f"v{n:04d}.json"


def tile_override_lookup(snapshot):
    return {(int(e["x"]), int(e["y"])): deepcopy(e)
            for e in snapshot.get("tile_overrides", [])}


TRAVERSAL_MODES = frozenset(("walk", "fly", "swim"))
SURFACES = frozenset(("stone", "wood", "sand", "grass", "water",
                      "lava", "void", "bridge", "stairs", "roof", "other"))
QA_STATUSES = frozenset(("needs_review", "approved", "rejected"))


def _number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _point(value):
    return isinstance(value, list) and len(value) == 2 and all(_number(n) for n in value)


def _ability_list(value):
    return (isinstance(value, list) and len(set(map(str, value))) == len(value)
            and all(isinstance(a, str) and re.fullmatch(r"[a-z][a-z0-9_]{0,63}", a)
                    for a in value))


def _modes(value, require_nonempty=True):
    return isinstance(value, list) and (bool(value) or not require_nonempty) and len(value) == len(set(value)) and all(
        isinstance(mode, str) and mode in TRAVERSAL_MODES for mode in value)


def validate_navigation(nav: dict, placed_instance_ids):
    """Validate map-side traversability metadata only; do not control characters."""
    if not isinstance(nav, dict) or nav.get("schema_version") != 1:
        raise ValueError("navigation must have schema_version=1")
    size = nav.get("grid_size")
    origin = nav.get("origin")
    cell_size = nav.get("cell_size")
    if (not isinstance(size, list) or len(size) != 2 or
            any(type(x) is not int or x <= 0 for x in size)):
        raise ValueError("navigation.grid_size must be two positive integers")
    if not _point(origin) or not _number(cell_size) or cell_size <= 0:
        raise ValueError("navigation origin/cell_size invalid")
    default = nav.get("default")
    if not isinstance(default, dict) or any(type(default.get(m)) is not bool
                                             for m in TRAVERSAL_MODES):
        raise ValueError("navigation.default must explicitly define walk/fly/swim booleans")
    seen = set()
    for region in nav.get("regions", []):
        if not isinstance(region, dict):
            raise ValueError("Navigation region must be object")
        ident = region.get("id")
        if not isinstance(ident,str) or not re.fullmatch(r"[a-z][a-z0-9_]{0,63}",ident) or ident in seen:
            raise ValueError("Invalid/duplicate navigation region ID")
        seen.add(ident)
        rect = region.get("rect")
        if not isinstance(rect,list) or len(rect)!=4 or any(type(x) is not int for x in rect):
            raise ValueError("navigation region rect must be [cell_x,cell_y,width,height]")
        x,y,w,h = rect
        if x<0 or y<0 or w<=0 or h<=0 or x+w>size[0] or y+h>size[1]:
            raise ValueError("Navigation region out of bounds: "+ident)
        if region.get("surface") not in SURFACES:
            raise ValueError("Invalid surface type: "+ident)
        if "allow" not in region or not _modes(region["allow"], require_nonempty=False):
            raise ValueError("Navigation region must explicitly list allowed modes (empty list means blocked): "+ident)
        if not _number(region.get("floor_height",0)):
            raise ValueError("Invalid floor_height: "+ident)
        ceiling = region.get("ceiling_height")
        if ceiling is not None and (
            not _number(ceiling) or ceiling <= region.get("floor_height",0)):
            raise ValueError("ceiling_height must be greater than floor_height: "+ident)
        required=region.get("requires",{})
        if not isinstance(required,dict) or any(
            m not in TRAVERSAL_MODES or not _ability_list(v)
            for m,v in required.items()
        ):
            raise ValueError("Invalid navigation required abilities: "+ident)
        if region.get("review_status","needs_review") not in QA_STATUSES:
            raise ValueError("Unknown navigation review_status")
    for obstacle in nav.get("obstacles", []):
        if not isinstance(obstacle,dict):
            raise ValueError("Invalid navigation obstacle")
        instance=obstacle.get("instance_id")
        if instance not in placed_instance_ids:
            raise ValueError("Navigation obstacle references unknown block: "+str(instance))
        if not _modes(obstacle.get("blocks")):
            raise ValueError("Obstacle blocks must list movement modes")
        lo,hi=obstacle.get("min_altitude",0),obstacle.get("max_altitude")
        if not _number(lo) or not _number(hi) or hi <= lo:
            raise ValueError("Obstacle altitude band is invalid")
    for link in nav.get("links", []):
        if not isinstance(link,dict) or not isinstance(link.get("id"),str):
            raise ValueError("Invalid navigation link")
        for end in ("from","to"):
            p=link.get(end)
            if (not isinstance(p,list) or len(p)!=2 or
                    any(type(v) is not int for v in p) or
                    not (0 <= p[0] < size[0] and 0 <= p[1] < size[1])):
                raise ValueError("Navigation link endpoints must be integer grid cells inside navigation grid")
        if not _modes(link.get("modes")) or not _ability_list(link.get("requires",[])):
            raise ValueError("Invalid link modes/abilities")
    return True


def validate_visual_qa(qa):
    if not isinstance(qa,dict) or qa.get("status") not in QA_STATUSES:
        raise ValueError("visual_qa requires status=needs_review/approved/rejected")
    if qa.get("status") == "approved":
        if not qa.get("reference_sha256") or not qa.get("preview_path") or not qa.get("reviewer"):
            raise ValueError("Approved visual_qa requires reference SHA, preview and reviewer")
    return True


def validate_floor_tile_style(data,catalog):
    value=data.get("floor_tile_style")
    if value is None:
        return True
    if not isinstance(value,dict):
        raise ValueError("floor_tile_style must be an object")
    if type(value.get("enabled")) is not bool:
        raise ValueError("floor_tile_style.enabled must be boolean")
    inset=value.get("crop_insets")
    if not isinstance(inset,list) or len(inset)!=4 or any(type(v)!=int or v<0 for v in inset):
        raise ValueError("floor_tile_style.crop_insets must have four nonnegative integers")
    ids=value.get("tile_ids")
    if not isinstance(ids,list) or not ids or len(set(ids))!=len(ids):
        raise ValueError("floor_tile_style.tile_ids needs distinct registered floor IDs")
    for ident in ids:
        info=catalog.get(ident)
        if not info or info["category"]!="floors":
            raise ValueError("Invalid floor style asset "+str(ident))
        size=info.get("pixel_size",[0,0])
        if size[0] <= inset[0]+inset[2] or size[1] <= inset[1]+inset[3]:
            raise ValueError("floor crop removes entire tile "+ident)
    if not isinstance(value.get("joint_opacity"),(int,float)) or not 0<=value["joint_opacity"]<=1:
        raise ValueError("Invalid floor grout opacity")
    if not isinstance(value.get("joint_width"),(int,float)) or not 0<value["joint_width"]<=5:
        raise ValueError("Invalid floor grout width")
    if not isinstance(value.get("joint_color"),str) or not re.fullmatch(r"#[0-9a-fA-F]{6}",value["joint_color"]):
        raise ValueError("Invalid grout color")
    return True


def validate_floor_footprint(data):
    """Check irregular floor occupancy, keeping all absent cells non-walkable."""
    geometry=data.get("floor_footprint")
    if geometry is None:
        return True
    if not isinstance(geometry,dict):
        raise ValueError("floor_footprint must be a dictionary")
    rows=geometry.get("row_spans")
    width,height=data["size"]
    if not isinstance(rows,list) or len(rows)!=height:
        raise ValueError("floor_footprint row_spans must match floor height")
    painted=set()
    for y,spans in enumerate(rows):
        if not isinstance(spans,list):
            raise ValueError("Each footprint row must contain spans")
        previous_end=-1
        for span in spans:
            if not isinstance(span,list) or len(span)!=2 or any(type(x)!=int for x in span):
                raise ValueError("Footprint spans must contain integer [start,end]")
            lo,hi=span
            if not (0<=lo<=hi<width) or lo<=previous_end:
                raise ValueError("Overlapping/out-of-range floor footprint row")
            painted.update((x,y) for x in range(lo,hi+1))
            previous_end=hi
    if not painted:
        raise ValueError("Floor footprint has zero active cells")
    for cell in data.get("tile_overrides",[]):
        if (cell["x"],cell["y"]) not in painted:
            raise ValueError("Floor override is outside painted room footprint")
    return True


def validate_room(data, catalog, expect_map_id=None):
    if not isinstance(data, dict):
        raise ValueError("Map must be a JSON object")
    if any(field in data for field in EXCLUDED_GAMEPLAY):
        raise ValueError("Gameplay fields (npcs/player_spawn/interactions) are forbidden in the map factory")
    if expect_map_id and data.get("map_id") != expect_map_id:
        raise ValueError("Map ID mismatch")
    check_id(str(data.get("map_id", "")))
    if int(data.get("schema_version", 0)) != 2:
        raise ValueError("Map snapshot must have schema_version=2")
    if not isinstance(data.get("version"), int) or data["version"] < 1:
        raise ValueError("Invalid map version")
    size = data.get("size", [])
    origin = data.get("ground_offset", [])
    canvas = data.get("canvas_size", [])
    if any(not isinstance(a, list) or len(a) != 2 for a in (size, origin, canvas)):
        raise ValueError("size, ground_offset and canvas_size must have 2 values")
    if not all(isinstance(z, int) and z > 0 for z in size+canvas):
        raise ValueError("Invalid map size or canvas_size")
    if not all(isinstance(z, (int, float)) for z in origin):
        raise ValueError("Invalid ground_offset")
    if not isinstance(data.get("tile_size"), int) or data["tile_size"] <= 0:
        raise ValueError("Invalid tile_size")
    if not data.get("floor_ids"):
        raise ValueError("At least one floor tile is required")
    seen = set()
    def check_asset(asset_id, floor=False):
        if asset_id not in catalog:
            raise ValueError(f"Unknown asset: {asset_id}; first import an independent PNG and metadata")
        item = catalog[asset_id]
        if item["category"] in BLOCKED_CATEGORIES or item["category"] == "shadows":
            raise ValueError(f"Forbidden block category: {asset_id} ({item['category']})")
        if floor and item["category"] != "floors":
            raise ValueError(f"Floor must use floors category: {asset_id}")
    for block in data["floor_ids"]:
        check_asset(str(block), floor=True)
    coords = set()
    for override in data.get("tile_overrides", []):
        x, y = override["x"], override["y"]
        if not all(isinstance(z, int) for z in (x, y)):
            raise ValueError("Noninteger tile coordinates")
        if not 0 <= x < size[0] or not 0 <= y < size[1]:
            raise ValueError(f"Tile out of bounds: {x},{y}")
        if (x, y) in coords:
            raise ValueError(f"Duplicate tile override: {x},{y}")
        coords.add((x,y))
        check_asset(str(override["id"]), floor=True)
        # Floor tile turns use the same four-cardinal contract as props.
        resolve_orientation(override,catalog)
    validate_floor_footprint(data)
    validate_floor_tile_style(data,catalog)
    if "occlusion_mode" in data and data["occlusion_mode"] not in ("fixed_layers","world_y_sort"):
        raise ValueError("occlusion_mode must be fixed_layers or world_y_sort")
    for layer in LAYERS:
        blocks = data.get(layer, [])
        if not isinstance(blocks, list):
            raise ValueError(f"{layer} must be a list")
        for item in blocks:
            if not isinstance(item, dict):
                raise ValueError(f"Invalid block in {layer}")
            check_asset(str(item.get("id", "")))
            ident = item.get("instance_id")
            if not isinstance(ident, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,79}", ident):
                raise ValueError(f"Every placed block needs a stable instance_id: {item!r}")
            if ident in seen:
                raise ValueError(f"Duplicate instance_id: {ident}")
            seen.add(ident)
            if any(not isinstance(item.get(k), (int,float)) for k in ("x","y")):
                raise ValueError(f"Invalid position: {ident}")
            if not isinstance(item.get("scale", 1), (int,float)) or item.get("scale", 1) <= 0:
                raise ValueError(f"Invalid scale: {ident}")
            if "rotation_degrees" in item and not isinstance(item["rotation_degrees"],(int,float)):
                raise ValueError(f"Invalid rotation: {ident}")
            # Cardinal facings may either rotate the scene node, or select
            # a complete set of four independently drawn perspective views.
            resolve_orientation(item,catalog)
            if "shadow" in item and not isinstance(item["shadow"],dict):
                raise ValueError(f"Invalid shadow: {ident}")
            if "collision" in item and not isinstance(item["collision"],dict):
                raise ValueError(f"Invalid collision: {ident}")
    for item in data.get("effects", []):
        if not isinstance(item, dict) or not all(k in item for k in ("instance_id", "x", "y", "kind")):
            raise ValueError("Invalid map lighting effect")
        if item["instance_id"] in seen:
            raise ValueError("Duplicate effect instance")
        seen.add(item["instance_id"])
    if "navigation" in data:
        validate_navigation(data["navigation"], seen)
    if "visual_qa" in data:
        validate_visual_qa(data["visual_qa"])
        if data["visual_qa"]["status"]=="approved":
            source=data.get("source_image",{})
            if not source.get("path") or not source.get("sha256"):
                raise ValueError("Cannot approve a room without a committed reference image and SHA-256")
    # Resolve attachments, detect cycles and validate optional compiled layer graph.
    create_layer_stack(data,catalog)
    validate_layer_stack(data,catalog)
    return True


def normalize_existing(data: dict, map_id: str) -> dict:
    data = deepcopy(data)
    for item in EXCLUDED_GAMEPLAY:
        data.pop(item, None)
    data.pop("room_id", None)
    for key in LAYERS:
        for i, item in enumerate(data.get(key, []), 1):
            item.setdefault("instance_id", f'{item["id"]}_{key}_{i:03d}')
    data.update({"schema_version": 2, "map_id": map_id, "version": 1,
                 "parent_version": None, "created_at": now(),
                 "source_image": {"path": None, "sha256": None,
                                  "status": "reference_in_chat_not_imported"},
                 "change_note": "Map-only baseline extracted from the pre-existing room."})
    return data


def build_block_manifest(snapshot, catalog):
    """Resolve each placed reusable map part to its full authoritative catalog metadata."""
    instances = []
    used = set()
    for layer in LAYERS:
        for part in snapshot.get(layer, []):
            record = catalog[part["id"]]
            used.add(part["id"])
            orientation=resolve_orientation(part,catalog)
            resolved=catalog[orientation["resolved_asset_id"]] if orientation else record
            instances.append({
                "instance_id": part["instance_id"],
                "asset_id": part["id"],
                **({"render_asset_id":resolved["id"]} if orientation else {}),
                "category": record["category"],
                "subtype": record.get("subtype", "general"),
                "texture_path": resolved["texture_path"],
                "asset_status": record.get("status", "planned"),
                "pixel_size": resolved.get("pixel_size", [0, 0]),
                "anchor": resolved.get("origin", [0, 0]),
                "layer": layer,
                "position": [part["x"], part["y"]],
                "scale": part.get("scale", 1.0),
                "rotation_degrees": part.get("rotation_degrees", 0),
                **({"orientation":orientation} if orientation else {}),
                "flip_h": part.get("flip_h", False),
                "z_index": part.get("z_index", 0),
                "collision": part.get("collision", resolved.get("collision", {})),
                "shadow": part.get("shadow", resolved.get("shadow", {})),
                "tags": record.get("tags", []),
                "source": record.get("source", {}),
            })
    floor = []
    for item in snapshot.get("tile_overrides", []):
        record = catalog[item["id"]]
        orientation=resolve_orientation(item,catalog)
        resolved=catalog[orientation["resolved_asset_id"]] if orientation else record
        floor.append({
            "x": item["x"], "y": item["y"],
            "asset_id": item["id"],
            **({"render_asset_id":resolved["id"]} if orientation else {}),
            "category": record["category"],
            "texture_path": resolved["texture_path"],
            "pixel_size": resolved.get("pixel_size"),
            "asset_status": record.get("status", "planned"),
            **({"orientation":orientation} if orientation else {})
        })
        used.add(item["id"])
    for ident in snapshot.get("floor_ids", []):
        used.add(ident)
    return {
        "layer_schema_version": 1,
        "five_level_map": (snapshot.get("layer_stack") or create_layer_stack(snapshot,catalog))["counts"],
        "layer_stack_path": "map_factory/maps/"+snapshot["map_id"]+"/layers/latest.json",
        "schema_version": 1, "map_id": snapshot["map_id"],
        "version": snapshot["version"], "source_image": snapshot.get("source_image"),
        "block_count": len(instances), "unique_asset_count": len(used),
        "reused_asset_ids": sorted(used), "placed_blocks": instances,
        "floor_pattern_ids": snapshot.get("floor_ids", []),
        "floor_overrides": floor, "effects": snapshot.get("effects", []),
        "note": "Resolved read-only map metadata. Edit map manifests, not this generated index."
    }


def write_revision(root, map_id, snapshot, reg, patch=None):
    base = map_base(map_id)
    n = snapshot["version"]
    dest = version_file(map_id, n)
    if (root / dest).exists():
        raise ValueError("Revision already exists; refusing to overwrite history")
    cat=asset_catalog(root)
    snapshot["layer_stack"]=create_layer_stack(snapshot,cat)
    validate_room(snapshot,cat,map_id)
    dump(root, dest, snapshot)
    dump(root, base / "latest.json", snapshot)
    dump(root, base / "layers" / f"v{n:04d}.json", snapshot["layer_stack"])
    dump(root, base / "layers" / "latest.json", snapshot["layer_stack"])
    metadata = build_block_manifest(snapshot, cat)
    dump(root, base / "blocks" / f"v{n:04d}.json", metadata)
    dump(root, base / "blocks" / "latest.json", metadata)
    reg["maps"][map_id] = {
        "map_id": map_id, "version": n,
        "latest": (base / "latest.json").as_posix(),
        "immutable_snapshot": dest.as_posix(),
        "snapshot_sha256": digest_json(snapshot),
        "updated_at": snapshot["created_at"],
        "parent_map": snapshot.get("derived_from")
    }
    dump(root, INDEX, reg)
    if patch is not None:
        dump(root, base / "changes" / f"v{n:04d}.json", patch)


def bootstrap(root, map_id, source):
    check_id(map_id)
    reg = registry(root)
    if map_id in reg["maps"]:
        raise ValueError("Map already initialized: " + map_id)
    input_path = (root / source).resolve()
    if not input_path.is_relative_to(root.resolve()):
        raise ValueError("Source path escapes repository")
    data = json.loads(input_path.read_text(encoding="utf-8"))
    snapshot = normalize_existing(data, map_id)
    validate_room(snapshot, asset_catalog(root), map_id)
    write_revision(root, map_id, snapshot, reg)
    return snapshot


def get_latest(root, map_id, reg=None):
    reg = registry(root) if reg is None else reg
    if map_id not in reg["maps"]:
        raise ValueError("Unknown map ID: " + map_id)
    item = reg["maps"][map_id]
    snap = read(root, Path(item["latest"]))
    if snap["version"] != item["version"] or digest_json(snap) != item["snapshot_sha256"]:
        raise ValueError("Map registry/latest snapshot mismatch — refusing stale update")
    validate_room(snap, asset_catalog(root), map_id)
    return snap


PRESET_NAMES = ("indoor_room", "courtyard", "dungeon", "coast", "sky_island")


def create_map(root, map_id, preset="indoor_room", source_image=None, note=None):
    """Start an independent map, never inherit unwanted Hero Room blocks."""
    check_id(map_id)
    if preset not in PRESET_NAMES:
        raise ValueError("Unknown map preset: " + str(preset))
    reg=registry(root)
    if map_id in reg["maps"] or (root/map_base(map_id)).exists():
        raise ValueError("Map already exists: " + map_id)
    template=read(root,Path("map_factory/presets")/(preset+".json"))
    snapshot=deepcopy(template)
    snapshot.update({
        "schema_version":2,"map_id":map_id,"version":1,
        "parent_version":None,"created_at":now(),"preset":preset,
        "source_image":deepcopy(source_image or {
            "path":None,"sha256":None,"status":"no_source_image_yet"}),
        "visual_qa":{"status":"needs_review"},
        "change_note":note or ("Created from reusable map preset "+preset)
    })
    validate_room(snapshot,asset_catalog(root),map_id)
    write_revision(root,map_id,snapshot,reg)
    return snapshot


def clone_map(root, new_map, from_map):
    check_id(new_map)
    reg = registry(root)
    if new_map in reg["maps"]:
        raise ValueError("Map already exists: " + new_map)
    source = get_latest(root, from_map, reg)
    copy = deepcopy(source)
    copy.pop("layer_stack", None)  # Recompile derived graph under the new map identity.
    copy["map_id"] = new_map
    copy["version"] = 1
    copy["parent_version"] = None
    copy["derived_from"] = {"map_id": from_map, "version": source["version"],
                            "snapshot_sha256": digest_json(source)}
    copy["created_at"] = now()
    copy["change_note"] = "Cloned last approved map layout, not flattened screenshot pixels."
    validate_room(copy, asset_catalog(root), new_map)
    write_revision(root, new_map, copy, reg)
    return copy


def apply_changes(snapshot, manifest, catalog):
    result = deepcopy(snapshot)
    # Derived layer metadata belongs to the OLD snapshot: rebuild it only after edits.
    result.pop("layer_stack", None)
    ops = manifest.get("changes")
    if not isinstance(ops, list) or not ops:
        raise ValueError("Patch manifest needs nonempty changes array")
    for operation in ops:
        op = operation.get("op")
        if op == "set_tile":
            x, y = operation["x"], operation["y"]
            updates = tile_override_lookup(result)
            if operation.get("id") is None:
                updates.pop((x,y), None)
            else:
                new_tile={"x":x,"y":y,"id":operation["id"]}
                for option in ("facing","orientation_mode","direction_asset_ids"):
                    if option in operation:
                        new_tile[option]=deepcopy(operation[option])
                updates[(x,y)] = new_tile
            result["tile_overrides"] = [v
                for pos, v in sorted(updates.items())]
        elif op == "add_block":
            layer = operation["layer"]
            if layer not in LAYERS:
                raise ValueError("Invalid layer: " + str(layer))
            result.setdefault(layer, []).append(deepcopy(operation["block"]))
        elif op in ("update_block","remove_block"):
            name = operation["instance_id"]
            matches = [(layer, index) for layer in LAYERS
                       for index, item in enumerate(result.get(layer, []))
                       if item.get("instance_id") == name]
            if len(matches) != 1:
                raise ValueError(f"Block not found exactly once: {name}")
            layer,i=matches[0]
            if op == "remove_block":
                result[layer].pop(i)
            else:
                updates=deepcopy(operation.get("set", {}))
                if "instance_id" in updates and updates["instance_id"] != name:
                    raise ValueError("Cannot rename instance_id; remove and add explicitly")
                if "layer" in updates:
                    new_layer=updates.pop("layer")
                    if new_layer not in LAYERS:
                        raise ValueError("Invalid layer")
                    item=result[layer].pop(i)
                    item.update(updates)
                    result[new_layer].append(item)
                else:
                    result[layer][i].update(updates)
        elif op=="set_property":
            key=operation["key"]
            allowed={"description","background_color","canvas_size","tile_size",
                     "size","ground_offset","floor_ids","floor_footprint","floor_tile_style","occlusion_mode","ocean","effects",
                     "source_image","floor_art","composition_reference", "navigation", "visual_qa"}
            if key not in allowed:
                raise ValueError("Forbidden map-only property: "+str(key))
            result[key]=deepcopy(operation["value"])
        else:
            raise ValueError("Unknown patch op: "+str(op))
    result["parent_version"]=snapshot["version"]
    result["version"]=snapshot["version"]+1
    result["created_at"]=now()
    result["change_note"]=manifest.get("note","AI-authored room layout patch")
    result["source_image"]=deepcopy(manifest.get("source_image",snapshot.get("source_image",{})))
    validate_room(result,catalog,snapshot["map_id"])
    return result


def apply(root, manifest_path, dry_run=False):
    path=(root/manifest_path).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Manifest must be inside repository")
    manifest=json.loads(path.read_text(encoding="utf-8"))
    map_id=check_id(manifest.get("map_id",""))
    reg=registry(root)
    latest=get_latest(root,map_id,reg)
    if manifest.get("base_version") != latest["version"]:
        raise ValueError(f"Stale patch: manifest base_version={manifest.get('base_version')}, latest={latest['version']}")
    if manifest.get("base_sha256") and manifest["base_sha256"] != digest_json(latest):
        raise ValueError("Stale patch base_sha256 mismatch")
    candidate=apply_changes(latest,manifest,asset_catalog(root))
    if not dry_run:
        write_revision(root,map_id,candidate,reg,manifest)
    return candidate


def validate_repository(root):
    catalog=asset_catalog(root)
    reg=registry(root)
    validated=[]
    for map_id,item in sorted(reg["maps"].items()):
        current=get_latest(root,map_id,reg)
        n=current["version"]
        for version in range(1,n+1):
            snap=read(root,version_file(map_id,version))
            validate_room(snap,catalog,map_id)
            if snap["version"]!=version:
                raise ValueError("Broken version chain "+map_id)
            if version>1 and snap.get("parent_version")!=version-1:
                raise ValueError("Broken parent revision "+map_id)
        if read(root,version_file(map_id,n))!=current:
            raise ValueError("Latest snapshot does not match immutable version")
        layer_path=map_base(map_id)/"layers"/"latest.json"
        if (root/layer_path).exists():
            if read(root,layer_path)!=create_layer_stack(current,catalog):
                raise ValueError("Latest five-level layer stack metadata mismatch")
            for version in range(1,n+1):
                source=read(root,version_file(map_id,version))
                expected=create_layer_stack(source,catalog)
                if read(root,map_base(map_id)/"layers"/f"v{version:04d}.json")!=expected:
                    raise ValueError("Versioned layer stack does not match map "+map_id)
        expected_blocks=build_block_manifest(current,catalog)
        if read(root,map_base(map_id)/"blocks"/"latest.json")!=expected_blocks:
            raise ValueError("Resolved latest blocks metadata mismatch")
        if read(root,map_base(map_id)/"blocks"/f"v{n:04d}.json")!=expected_blocks:
            raise ValueError("Versioned blocks metadata mismatch")
        validated.append((map_id,n))
    return validated


def sync_block_metadata(root):
    """Backfill derived block indices without changing immutable scene revisions."""
    reg=registry(root)
    cat=asset_catalog(root)
    rebuilt=[]
    for map_id,item in sorted(reg["maps"].items()):
        for version in range(1,item["version"]+1):
            snapshot=read(root,version_file(map_id,version))
            metadata=build_block_manifest(snapshot,cat)
            dump(root,map_base(map_id)/"blocks"/f"v{version:04d}.json",metadata)
            stack=create_layer_stack(snapshot,cat)
            dump(root,map_base(map_id)/"layers"/f"v{version:04d}.json",stack)
            if version==item["version"]:
                dump(root,map_base(map_id)/"layers"/"latest.json",stack)
            if version==item["version"]:
                dump(root,map_base(map_id)/"blocks"/"latest.json",metadata)
            rebuilt.append(f"{map_id}@v{version:04d}")
    return rebuilt


def main(argv=None,root=ROOT):
    p=argparse.ArgumentParser(description="AI-assisted versioned map blocks, excluding characters")
    sub=p.add_subparsers(dest="action",required=True)
    boot=sub.add_parser("bootstrap")
    boot.add_argument("--map-id",required=True)
    boot.add_argument("--source",default="map_factory/rooms/hero_room.json")
    create=sub.add_parser("new")
    create.add_argument("--map-id",required=True)
    create.add_argument("--preset",choices=PRESET_NAMES,default="indoor_room")
    clone=sub.add_parser("clone")
    clone.add_argument("--map-id",required=True)
    clone.add_argument("--from-map",required=True)
    for action in ("preview","apply"):
        sp=sub.add_parser(action)
        sp.add_argument("--manifest",required=True)
    sub.add_parser("sync-blocks")
    sub.add_parser("validate")
    sub.add_parser("list")
    args=p.parse_args(argv)
    if args.action=="bootstrap":
        result=bootstrap(root,args.map_id,Path(args.source))
    elif args.action=="new":
        result=create_map(root,args.map_id,args.preset)
    elif args.action=="clone":
        result=clone_map(root,args.map_id,args.from_map)
    elif args.action in ("preview","apply"):
        result=apply(root,Path(args.manifest),dry_run=args.action=="preview")
    elif args.action=="sync-blocks":
        print(json.dumps({"recreated_indices":sync_block_metadata(root)},indent=2))
        return 0
    elif args.action=="validate":
        print(json.dumps({"validated_maps":validate_repository(root)},indent=2))
        return 0
    elif args.action=="list":
        print(json.dumps(registry(root),indent=2))
        return 0
    print(json.dumps({"map_id":result["map_id"],"version":result["version"],
                      "sha256":digest_json(result),"blocks":sum(len(result.get(k,[])) for k in LAYERS)},
                     ensure_ascii=False,indent=2))
    return 0


if __name__=="__main__":
    try:
        sys.exit(main())
    except (KeyError,TypeError,ValueError,FileNotFoundError) as error:
        print("Map Factory error:",error,file=sys.stderr)
        sys.exit(1)
