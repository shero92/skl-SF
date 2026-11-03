#!/usr/bin/env python3
"""Read-only visual contract audit. Agent: codex.

Render evidence uses resolved_assets entries with asset_id, source_path,
image_bounds and feature_classes. Geometry must contain verified=true,
image_size, and world_to_image=[a,b,c,d,e,f], where
image_x=a*world_x+c*world_y+e and image_y=b*world_x+d*world_y+f.
Bounds must describe rendered texture bounds, not guessed sprite anchors.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "map_factory" / "blueprints" / "hero_room_01_visual_targets_20261103.json"
REGISTRY = ROOT / "map_factory" / "metadata" / ("environment_assets_" + "v2.json")
REFERENCE = ROOT / "map_factory" / "references" / ("hero_room_01_target_" + "20261103.png")
ZONE_IDS = {
    "sea_cliffs", "rear_arch", "left_walls", "right_walls", "floor",
    "bed_rug", "desk_rug", "compass", "front_parapet", "stairs", "lighting",
}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def numbers(value, count):
    return (isinstance(value, list) and len(value) == count
            and all(type(n) in (int, float) and math.isfinite(n) for n in value))


def bounds(value):
    if not numbers(value, 4) or value[2] <= value[0] or value[3] <= value[1]:
        raise ValueError("Invalid bounds")
    return value


def validate_contract(data):
    if not isinstance(data, dict):
        raise ValueError("Contract must be an object")
    if (data.get("version") != 1 or data.get("image_size") != [1536, 1024]
            or data.get("coordinate_space") != "image"
            or data.get("visual_approval") is not False
            or data.get("characters") != "optional_separate_actors"):
        raise ValueError("Invalid contract metadata")
    zones = data.get("zones")
    if not isinstance(zones, list) or len(zones) != len(ZONE_IDS):
        raise ValueError("Exactly eleven zones are required")
    if any(not isinstance(z, dict) for z in zones):
        raise ValueError("Zones must be objects")
    if {z.get("id") for z in zones} != ZONE_IDS:
        raise ValueError("Missing or duplicate required zones")
    for zone in zones:
        box = bounds(zone.get("box"))
        if not (0 <= box[0] < box[2] <= 1536 and 0 <= box[1] < box[3] <= 1024):
            raise ValueError("Zone outside reference")
        features = zone.get("features")
        if (not isinstance(features, list) or not features
                or any(not isinstance(f, str) or not f for f in features)
                or len(features) != len(set(features))):
            raise ValueError("Invalid feature classes")
        ids = zone.get("required_asset_ids")
        if (not isinstance(ids, list)
                or any(not isinstance(i, str) or not i for i in ids)
                or len(ids) != len(set(ids))
                or not isinstance(zone.get("notes"), str) or not zone["notes"]):
            raise ValueError("Invalid zone requirements")
    return data


def source_file(root, source):
    if not isinstance(source, str) or not source:
        raise ValueError("Missing source texture path")
    relative = source.removeprefix("res://").replace("\\", "/")
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError("Nonexistent or external source texture: " + source)
    if path.suffix.lower() != ".png":
        raise ValueError("Source texture is not a PNG: " + source)
    return path


def asset_index(data, root):
    """Accept explicit keyed or list registries; fail closed on unknown layouts."""
    rows = data.get("assets") if isinstance(data, dict) else None
    if isinstance(rows, dict):
        rows = [dict(value, id=key) for key, value in rows.items()
                if isinstance(value, dict)]
        if len(rows) != len(data["assets"]):
            raise ValueError("Invalid registry asset")
    if not isinstance(rows, list) or not rows:
        raise ValueError("Unsupported or empty registry assets")
    result = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Invalid registry row")
        identifier = row.get("id", row.get("asset_id"))
        if not isinstance(identifier, str) or not identifier or identifier in result:
            raise ValueError("Invalid or duplicate registry ID")
        source = row.get("source_path", row.get("texture_path", row.get("texture")))
        sources = []
        if source is not None:
            sources.append(source)
        variants = row.get("variants", {})
        if not isinstance(variants, dict):
            raise ValueError("Unsupported variant layout")
        for variant in variants.values():
            if isinstance(variant, str):
                sources.append(variant)
            elif isinstance(variant, dict):
                sources.append(variant.get("source_path", variant.get("texture_path",
                                                                       variant.get("texture"))))
            else:
                raise ValueError("Invalid variant")
        if not sources:
            raise ValueError("No source textures for asset " + identifier)
        result[identifier] = {source_file(root, value) for value in sources}
    return result


def room_instances(room):
    if not isinstance(room, dict):
        raise ValueError("Invalid room state")
    version = room.get("version")
    if type(version) is not int or version < 13:
        raise ValueError("Room must identify an existing version >= 13")
    blocks = room.get("blocks")
    if not isinstance(blocks, list) or not blocks:
        raise ValueError("Unsupported or empty room blocks")
    if any(not isinstance(b, dict) or not isinstance(b.get("asset_id"), str)
           for b in blocks):
        raise ValueError("Room blocks must identify assets explicitly")
    return blocks


def verified_geometry(evidence, image_size):
    geometry = evidence.get("geometry")
    if geometry is None:
        return None
    if (not isinstance(geometry, dict) or geometry.get("verified") is not True
            or geometry.get("image_size") != image_size
            or not isinstance(geometry.get("provenance"), str)
            or not geometry["provenance"]):
        raise ValueError("Render geometry lacks verification or provenance")
    matrix = geometry.get("world_to_image")
    if not numbers(matrix, 6):
        raise ValueError("Invalid affine render geometry")
    a, b, c, d, _, _ = matrix
    if abs(a * d - b * c) < 1e-12:
        raise ValueError("Singular render geometry")
    return matrix


def world_polygon(box, matrix):
    a, b, c, d, e, f = matrix
    determinant = a * d - b * c
    return [[(d * (x - e) - c * (y - f)) / determinant,
             (-b * (x - e) + a * (y - f)) / determinant]
            for x, y in ((box[0], box[1]), (box[2], box[1]),
                         (box[2], box[3]), (box[0], box[3]))]


def intersection(left, right):
    x0, y0 = max(left[0], right[0]), max(left[1], right[1])
    x1, y1 = min(left[2], right[2]), min(left[3], right[3])
    return [x0, y0, x1, y1] if x1 > x0 and y1 > y0 else None


def union_area(rectangles):
    edges = sorted({x for r in rectangles for x in (r[0], r[2])})
    area = 0.0
    for left, right in zip(edges, edges[1:]):
        spans = sorted((r[1], r[3]) for r in rectangles
                       if r[0] < right and r[2] > left)
        end = -math.inf
        height = 0.0
        for bottom, top in spans:
            height += max(0, top - max(bottom, end))
            end = max(end, top)
        area += (right - left) * height
    return area


def audit(contract, registry, room, root, evidence=None):
    validate_contract(contract)
    assets = asset_index(registry, root)
    blocks = room_instances(room)
    used = [block["asset_id"] for block in blocks]
    for identifier in used:
        if identifier not in assets:
            raise ValueError("Unknown placed asset ID: " + identifier)
    for zone in contract["zones"]:
        for identifier in zone["required_asset_ids"]:
            if identifier not in assets:
                raise ValueError("Unknown required asset ID: " + identifier)
    evidence = {} if evidence is None else evidence
    if not isinstance(evidence, dict):
        raise ValueError("Invalid render evidence")
    matrix = verified_geometry(evidence, contract["image_size"])
    resolved = evidence.get("resolved_assets")
    textures = set()
    if resolved is not None:
        if matrix is None or not isinstance(resolved, list) or len(resolved) != len(blocks):
            raise ValueError("Resolved instances require geometry and complete room coverage")
        if evidence.get("room_sha256") != hashlib.sha256(
                json.dumps(room, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest():
            raise ValueError("Render evidence does not identify this room state")
        remaining = list(used)
        for item in resolved:
            if not isinstance(item, dict):
                raise ValueError("Invalid resolved instance")
            identifier = item.get("asset_id")
            if identifier not in remaining:
                raise ValueError("Render instances differ from room")
            remaining.remove(identifier)
            texture = source_file(root, item.get("source_path"))
            if texture not in assets[identifier]:
                raise ValueError("Resolved source is not registered for asset")
            bounds(item.get("image_bounds"))
            features = item.get("feature_classes")
            if (not isinstance(features, list)
                    or any(not isinstance(f, str) or not f for f in features)):
                raise ValueError("Invalid resolved feature classes")
            textures.add(texture)
    reports = []
    requests = []
    for zone in contract["zones"]:
        required = set(zone["features"])
        local = set()
        elsewhere = set()
        rectangles = []
        for item in resolved or []:
            features = required.intersection(item["feature_classes"])
            elsewhere.update(features)
            clipped = intersection(zone["box"], item["image_bounds"])
            if features and clipped:
                local.update(features)
                rectangles.append(clipped)
        missing = sorted(required - elsewhere) if resolved is not None else []
        misplaced = sorted((required & elsewhere) - local)
        absent_ids = sorted(set(zone["required_asset_ids"]) - set(used))
        unverified = sorted(required) if resolved is None else []
        reports.append({
            "id": zone["id"], "image_box": zone["box"],
            "world_polygon": world_polygon(zone["box"], matrix) if matrix else None,
            "approximate_bounds_coverage": (
                union_area(rectangles) / ((zone["box"][2] - zone["box"][0])
                                          * (zone["box"][3] - zone["box"][1]))
                if resolved is not None else None),
            "absent_feature_classes": missing,
            "misplaced_feature_classes": misplaced,
            "unverified_feature_classes": unverified,
            "required_asset_ids_not_placed": absent_ids,
        })
        if missing:
            requests.append({
                "zone": zone["id"], "features": missing,
                "status": "potential_missing_art_requires_library_review",
                "request": "Codex/Claude: review approved library and approve any art request.",
            })
    return {
        "agent": "codex", "visual_approval": False,
        "asset_ids_used": sorted(set(used)), "placed_instances": len(blocks),
        "distinct_pngs": len(textures) if resolved is not None else None,
        "registered_candidate_pngs": len(set().union(*(assets[i] for i in set(used)))),
        "geometry_verified": matrix is not None, "zones": reports,
        "potential_missing_art": requests,
        "limitations": [
            "Bounds coverage includes transparent pixels and ignores occlusion.",
            "Feature classes require reviewed render evidence; asset names are not proof.",
            "Absent render features do not prove that approved library art is missing.",
            "Counts and hashes do not measure visual similarity.",
            "Without resolved evidence, real missing-art gaps remain unverified.",
        ],
    }


def verify_reference(path, expected_hash):
    raw = path.read_bytes()
    if (len(raw) < 24 or raw[:8] != b"\x89PNG\r\n\x1a\n"
            or raw[12:16] != b"IHDR"
            or struct.unpack(">II", raw[16:24]) != (1536, 1024)
            or hashlib.sha256(raw).hexdigest() != expected_hash):
        raise ValueError("Reference identity or dimensions do not match")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--room", required=True, type=Path)
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    parser.add_argument("--contract", type=Path, default=CONTRACT)
    parser.add_argument("--reference", type=Path, default=REFERENCE)
    parser.add_argument("--render-evidence", type=Path)
    args = parser.parse_args(argv)
    try:
        contract = validate_contract(read_json(args.contract))
        verify_reference(args.reference, contract["reference_sha256"])
        report = audit(contract, read_json(args.registry), read_json(args.room), ROOT,
                       read_json(args.render_evidence) if args.render_evidence else None)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("Audit blocked: " + str(exc), file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
