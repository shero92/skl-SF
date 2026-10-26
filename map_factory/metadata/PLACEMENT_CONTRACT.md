# Exact Multi-Tile Placement Contract v1

**Production contract, not an approval of the current art.** An asset is addressed by the unchanged catalog ID, for example `P001`, `P009`, `P014`. A filename alone does not grant a tile footprint or make a sprite factory-ready.

## Fields on `map_factory/metadata/asset_index.json` records

```json
{
  "id": "P001",
  "placement_contract": {
    "schema_version": 1,
    "mode": "floor",
    "footprint_cells": [2, 3],
    "occupancy_group": "solid",
    "allowed_floor_tags": ["stone"],
    "allowed_floor_asset_ids": ["F001", "F002", "F003", "F004", "F005"],
    "forbidden_floor_tags": ["edge", "corner", "compass"],
    "ground_anchor": "bottom_center",
    "measurement_status": "provisional"
  }
}
```

- `footprint_cells: [width, depth]` means the exact number of whole, logically occupied `tile_size` ground blocks, **not** the PNG pixel dimensions. A mask `occupied_cells: [[0,0],...]` allows a nonrectangular shape; entries outside declared bounds or duplicates fail validation. Every cell must exist inside the real `floor_footprint.row_spans`, not in the surrounding sea/void.
- Each occupied block's final floor ID is computed with the **same** floor sequence as Godot: override when present, else `floor_ids[(x*17+y*11)%len(floor_ids)]`. Allowed floor IDs and tags **both** must pass. A bed cannot silently cover the compass mosaic or a broken stone edge.
- `occupancy_group: solid` reserves each occupied cell and forbids another solid object from using it; `overlay` can coexist on cells as an underlay, e.g. a rug. Treat walkability/collision separately: visual footprint is not a physics shape.
- `measurement_status: provisional` means this occupied area was estimated, **not** measured from approved art. A final map sets `requires_reviewed_footprints: true` and refuses any provisional asset. An authorized visual reviewer must verify the bed's actual ground contacts in Godot before changing it to `reviewed`.
- For accessories use `mode: mounted`, `mount_on_categories` AND `mount_on_asset_ids`, e.g. blanket `P002` can attach to `P001` or `P004` only, never to any arbitrary table or floor.

## New strict map placements

```json
{
  "placement_policy": "strict_v1",
  "requires_reviewed_footprints": false,
  "size": [17, 10],
  "tile_size": 64,
  "ground_offset": [226, 225],
  "objects": [{
    "id": "P001", "instance_id": "HeroBedNew",
    "grid_placement": {"cell": [2, 2], "facing": "north"},
    "x": 418, "y": 545,
    "scale": 1
  }]
}
```

This example uses a provisional `P001` 2×3 contract: the occupied floor cells are x=2..3, y=2..4; the sprite anchor is `[226+(2+2/2)*64,225+(2+3)*64]=[418,545]`. An incorrect pixel x/y is **rejected**, not rounded. `scale` must be exactly 1 because untracked scaling breaks declared tile occupancy.

Facings are `north/east/south/west`. East/west exchange the width and depth, and the validator rotates any occupied-cell mask. Upright beds, tables, shelves and walls need distinct independently authored art IDs for all four facings (`orientation_mode=variants`) before non-north placement; NEVER substitute a rotated screenshot. Ground-flat rugs can rotate only with truthful `orientation_mode=rotate`. Data `grid_placement.facing` must match the rendered facing.

A free-standing furniture asset with a contract requires a `grid_placement` in `strict_v1`; no arbitrary subcell shifting. Existing immutable Hero Room v0001–v0010 use `legacy` pixel placements and remain readable, but **must not** be advertised as correctly footprint-aligned until migrated and visually checked in a new version. Never silently retag old revisions.

## Production acceptance

1. Specialist produces independent high-detail RGBA sprites in a real 3/4 viewpoint; separately drawn views, correct light direction, and contact-edge origin.
2. Compare original high-detail art, screenshot reference and Godot at actual size. Measure actual support contacts, intended tile footprint and interaction/collision footprint separately. The 22 furniture contracts in the current catalog are **provisional examples**, not approved measurements.
3. Confirm floor compatibility, mounting anchors, shadows and obstacle footprint. Mark contract `measurement_status=reviewed` with external reviewer evidence, then set `requires_reviewed_footprints=true` for the production map.
4. Run `python tools/map_factory_cli.py validate`, `python tools/run_tests.py --all` and Godot map smoke and screenshot comparison. No characters/UI modifications.
