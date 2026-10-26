"""Deterministic, fail-closed ground-cell placement for reusable environment art.

One canonical contract belongs to catalog asset IDs, not PNG filenames.
Legacy v0001-v0010 coordinate-only maps retain their historical layout.
New strict maps must provide explicit cell anchors for all free-standing furniture.
No image generation, analysis or sprite mutation happens here.
"""
from __future__ import annotations

import math

SOURCE_LAYERS = ("background_objects", "ground_overlays", "back_objects",
                 "objects", "front_objects")
VALID_GROUPS = frozenset(("solid", "overlay"))
FACINGS = ("north", "east", "south", "west")


def _int(value):
    return type(value) is int


def validate_contract(record):
    cfg = record.get("placement_contract")
    if cfg is None:
        return None
    if not isinstance(cfg, dict) or cfg.get("schema_version") != 1:
        raise ValueError(f'{record.get("id")}: placement_contract requires schema_version=1')
    if cfg.get("mode") == "mounted":
        if cfg.get("mount_on_categories") is None or not isinstance(cfg["mount_on_categories"], list):
            raise ValueError(f'{record.get("id")}: mounted contract needs mount_on_categories')
        return cfg
    if cfg.get("mode") != "floor":
        raise ValueError(f'{record.get("id")}: placement_contract mode must be floor or mounted')
    dims = cfg.get("footprint_cells")
    if not isinstance(dims, list) or len(dims) != 2 or any(not _int(x) or x <= 0 or x > 16 for x in dims):
        raise ValueError(f'{record.get("id")}: footprint_cells must be two positive tile counts (max 16)')
    if cfg.get("occupancy_group") not in VALID_GROUPS:
        raise ValueError(f'{record.get("id")}: occupancy_group must be solid or overlay')
    allow = cfg.get("allowed_floor_tags")
    if not isinstance(allow, list) or not allow or any(not isinstance(x, str) or not x for x in allow):
        raise ValueError(f'{record.get("id")}: allowed_floor_tags is required')
    deny = cfg.get("forbidden_floor_tags", [])
    if not isinstance(deny, list) or any(not isinstance(x, str) for x in deny):
        raise ValueError("forbidden_floor_tags must be a string list")
    mask = cfg.get("occupied_cells")
    if mask is not None:
        if not isinstance(mask, list) or not mask or any(
            not isinstance(cell, list) or len(cell) != 2 or
            not all(_int(v) for v in cell) or
            not (0 <= cell[0] < dims[0] and 0 <= cell[1] < dims[1])
            for cell in mask
        ):
            raise ValueError(f'{record.get("id")}: occupied_cells must lie inside footprint')
        if len({tuple(x) for x in mask}) != len(mask):
            raise ValueError(f'{record.get("id")}: duplicate occupied_cells')
    if cfg.get("measurement_status") not in ("provisional", "reviewed"):
        raise ValueError(f'{record.get("id")}: measurement_status must be provisional or reviewed')
    return cfg


def resolved_cells(cfg, cell_x, cell_y, facing):
    """Compute exact floor cells; east/west exchange width and depth."""
    w, h = cfg["footprint_cells"]
    mask = cfg.get("occupied_cells") or [[x, y] for y in range(h) for x in range(w)]
    if facing not in FACINGS:
        raise ValueError("Unsupported cardinal facing: " + str(facing))
    if facing == "north":
        out = mask
    elif facing == "east":
        out = [[h - 1 - y, x] for x, y in mask]
    elif facing == "south":
        out = [[w - 1 - x, h - 1 - y] for x, y in mask]
    else:
        out = [[y, w - 1 - x] for x, y in mask]
    return [(cell_x + x, cell_y + y) for x, y in out]


def world_anchor(snapshot, cfg, cell_x, cell_y, facing="north"):
    """Put a bottom-center sprite pivot on the last edge of its ground footprint."""
    w, h = cfg["footprint_cells"]
    if facing in ("east", "west"):
        w, h = h, w
    cell_size = snapshot["tile_size"]
    x0, y0 = snapshot["ground_offset"]
    return [x0 + (cell_x + w / 2) * cell_size, y0 + (cell_y + h) * cell_size]


def _walkable_footprint(snapshot):
    grid = snapshot["size"]
    rows = (snapshot.get("floor_footprint") or {}).get("row_spans")
    if not rows:
        return {(x, y) for x in range(grid[0]) for y in range(grid[1])}
    return {(x, y) for y, spans in enumerate(rows)
            for start, stop in spans for x in range(start, stop + 1)}


def floor_at(snapshot, x, y):
    overrides = {(c["x"], c["y"]): c["id"] for c in snapshot.get("tile_overrides", [])}
    if (x, y) in overrides:
        return overrides[(x, y)]
    ids = snapshot["floor_ids"]
    return ids[(x * 17 + y * 11) % len(ids)]


def validate_grid_placements(snapshot, catalog):
    policy = snapshot.get("placement_policy", "legacy")
    if policy not in ("legacy", "strict_v1"):
        raise ValueError("placement_policy must be legacy or strict_v1")
    occupied_ground = _walkable_footprint(snapshot)
    reserved = {}  # solid floor cell -> instance_id
    resolved = {}
    require_review = bool(snapshot.get("requires_reviewed_footprints", False))
    if snapshot.get("requires_reviewed_footprints") not in (None, True, False):
        raise ValueError("requires_reviewed_footprints must be boolean")
    for layer in SOURCE_LAYERS:
        for item in snapshot.get(layer, []):
            record = catalog[item["id"]]
            cfg = validate_contract(record)
            ident = item["instance_id"]
            if item.get("mount_on"):
                if cfg and cfg["mode"] == "floor":
                    raise ValueError(f"{ident}: floor furniture cannot be mounted")
                if cfg and cfg["mode"] == "mounted":
                    # Host type is checked below after all map objects are indexed.
                    continue
            if cfg and cfg["mode"] == "mounted" and policy == "strict_v1":
                raise ValueError(f"{ident}: accessory must have mount_on")
            placed = item.get("grid_placement")
            if not placed:
                if policy == "strict_v1" and cfg and cfg["mode"] == "floor":
                    raise ValueError(f"{ident}: strict furniture requires grid_placement")
                if placed is not None:
                    raise ValueError(f"{ident}: grid_placement cannot be empty")
                continue
            if not cfg or cfg.get("mode") != "floor":
                raise ValueError(f"{ident}: grid_placement requires floor placement_contract")
            if layer not in ("objects", "ground_overlays", "front_objects", "back_objects"):
                raise ValueError(f"{ident}: furniture cannot be placed in {layer}")
            if not isinstance(placed, dict) or set(placed) - {"cell", "facing"}:
                raise ValueError(f"{ident}: grid_placement fields must be cell and facing")
            xy = placed.get("cell")
            facing = placed.get("facing", "north")
            if not isinstance(xy, list) or len(xy) != 2 or any(not _int(v) for v in xy):
                raise ValueError(f"{ident}: grid_placement.cell needs two integers")
            if facing not in FACINGS:
                raise ValueError(f"{ident}: invalid facing")
            if require_review and cfg["measurement_status"] != "reviewed":
                raise ValueError(f"{ident}: measured footprint has not been visually reviewed")
            if item.get("rotation_degrees", 0) not in (0, 0.0):
                raise ValueError(f"{ident}: use grid_placement.facing, not arbitrary sprite rotation")
            if float(item.get("scale", 1)) != 1.0:
                raise ValueError(f"{ident}: scaling changes grid footprint; use scale=1 and native-sized sprite art")
            actual = world_anchor(snapshot, cfg, *xy, facing)
            if any(not math.isfinite(v) or abs(float(item[k]) - v) > 0.01 for k, v in zip(("x", "y"), actual)):
                raise ValueError(f"{ident}: x/y must match exact grid bottom-center anchor {actual}")
            cells = resolved_cells(cfg, xy[0], xy[1], facing)
            for cell in cells:
                if cell not in occupied_ground:
                    raise ValueError(f"{ident}: furniture outside floor footprint at {cell}")
                tile = catalog[floor_at(snapshot, *cell)]
                tags = set(tile.get("tags", []))
                if not tags.intersection(cfg["allowed_floor_tags"]):
                    raise ValueError(f"{ident}: incompatible ground tile {tile['id']} at {cell}")
                if tags.intersection(cfg.get("forbidden_floor_tags", [])):
                    raise ValueError(f"{ident}: prohibited ground tile {tile['id']} at {cell}")
                if cfg["occupancy_group"] == "solid":
                    if cell in reserved:
                        raise ValueError(f"{ident}: occupied block {cell} already used by {reserved[cell]}")
                    reserved[cell] = ident
            resolved[ident] = {"cells": [list(x) for x in cells], "anchor": actual,
                               "facing": facing, "group": cfg["occupancy_group"]}
    # Independently enforce host categories: a blanket may go on a bed, not a wall.
    by_id = {i["instance_id"]: i for layer in SOURCE_LAYERS for i in snapshot.get(layer, [])}
    for layer in SOURCE_LAYERS:
        for item in snapshot.get(layer, []):
            cfg = catalog[item["id"]].get("placement_contract")
            if cfg and cfg.get("mode") == "mounted" and item.get("mount_on"):
                host = by_id.get(item["mount_on"])
                if not host:
                    raise ValueError(f'{item["instance_id"]}: mount target missing')
                if catalog[host["id"]]["category"] not in cfg["mount_on_categories"]:
                    raise ValueError(f'{item["instance_id"]}: accessory cannot mount on host category')
    return resolved
