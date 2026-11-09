"""Build the hero_room_01 reference-reconstruction blueprint and emit the v0012 patch manifest.

This script is the deterministic source of truth for the rebuilt room. It:
  1. Measures every pack PNG it uses (alpha bbox, gaps, origin) so no asset is
     stretched or auto-rotated; the correct directional image is chosen per facing.
  2. Converts visual layout targets (content centre x, content base y, grid cell,
     mount offsets) into exact sprite x/y using the registered bottom-centre origin
     contract (world_anchor / map_factory_placement).
  3. Writes map_factory/blueprints/hero_room_01_reference_v1.json (the design doc).
  4. Writes map_factory/maps/hero_room_01/patches/v0012.json (remove all v0011
     blocks, add the new layout, set ground/effects/navigation/metadata properties).

Run:  py -3 tools/build_hero_room_blueprint.py
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from PIL import Image

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from .map_factory_orientation import (
        canonical_asset_id, furniture_direction_ids, resolve_orientation,
    )
except ImportError:
    from map_factory_orientation import (
        canonical_asset_id, furniture_direction_ids, resolve_orientation,
    )

try:
    from .room_assembly import content_bounds, fit_registered_block
except ImportError:
    from room_assembly import content_bounds, fit_registered_block

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "assets_generated"
CATALOG_PATH = ROOT / "map_factory" / "metadata" / "asset_index.json"
LATEST = ROOT / "map_factory" / "maps" / "hero_room_01" / "latest.json"
BLUEPRINT = ROOT / "map_factory" / "blueprints" / "hero_room_01_reference_v1.json"
PATCH_DIR = ROOT / "map_factory" / "maps" / "hero_room_01" / "patches"
PATCH = PATCH_DIR / "v0012.json"

TILE = 64
GROUND_OFFSET = (226, 225)  # (x0, y0)
CANVAS = (1536, 1024)

# ---------------------------------------------------------------------------
# Asset measurement
# ---------------------------------------------------------------------------


def merge_directional_catalog(catalog, registry):
    """Overlay canonical directional records on legacy placement metadata."""
    assets = {asset["id"]: dict(asset) for asset in catalog["assets"]}
    registered = registry.get("assets", registry.get("items", []))
    if isinstance(registered, dict):
        registered = [
            dict(value, id=key) for key, value in registered.items()
        ]
    for asset in registered:
        asset_id = asset.get("id", asset.get("key"))
        aliases = asset.get("legacy_aliases", [])
        if isinstance(aliases, str):
            aliases = [aliases]
        if not asset_id or "@" not in asset_id:
            continue
        aliases = list(aliases)
        base_id, facing = asset_id.split("@", 1)
        bed_aliases = {
            "north": "F03", "east": "F04", "south": "F01", "west": "F02",
        }
        if base_id == "F01" and facing in bed_aliases:
            legacy_id = bed_aliases[facing]
            if legacy_id not in aliases:
                aliases.append(legacy_id)
        legacy = next((assets[a] for a in aliases if a in assets), {})
        assets[asset_id] = {
            **legacy, **asset, "id": asset_id, "legacy_aliases": list(aliases),
        }
        # Keep placement categories consistent across directional variants.
        # Registry categories describe art and may use a different taxonomy.
        if "category" in legacy:
            assets[asset_id]["category"] = legacy["category"]
    return {**catalog, "assets": list(assets.values())}


def load_catalog():
    with open(CATALOG_PATH, encoding="utf-8") as f:
        catalog = json.load(f)
    registry_path = CATALOG_PATH.with_name(
        "environment_" + "assets_v2" + ".json"
    )
    with open(registry_path, encoding="utf-8") as f:
        return merge_directional_catalog(catalog, json.load(f))


def catalog_lookup(catalog, asset_id):
    assets = {asset["id"]: asset for asset in catalog["assets"]}
    try:
        return assets[canonical_asset_id(asset_id, assets)]
    except ValueError:
        return None


def sidecar_png(catalog, asset_id):
    record = catalog_lookup(catalog, asset_id)
    if record is None:
        raise KeyError(f"unknown asset id {asset_id}")
    rel = record["texture_path"].replace("res://", "")
    return ROOT / rel


def retired_measure(png_path):
    """Layout numbers of a retired low-quality PNG, recorded in assets_hd/hd_map.json."""
    try:
        relative = Path(png_path).resolve().relative_to((ROOT / "assets_generated").resolve()).as_posix()
    except ValueError:
        return None
    hd_map = json.loads((ROOT / "assets_hd" / "hd_map.json").read_text(encoding="utf-8"))["map"]
    return hd_map.get(relative, {}).get("measure")


def texture_available(png_path):
    """The registered PNG exists, or it was retired and its HD runtime twin exists (assets_hd/hd_map.json)."""
    if Path(png_path).is_file():
        return True
    if retired_measure(png_path) is None:
        return False
    return (ROOT / "assets_hd" / "runtime" / Path(png_path).name).is_file()


def measure_png(png_path):
    if not Path(png_path).is_file():
        recorded = retired_measure(png_path)
        if recorded is not None:
            return recorded
    return measure_png_image(Image.open(png_path).convert("RGBA"))


def measure_png_image(im):
    alpha = im.split()[3]
    mask = alpha.point(lambda v: 255 if v > 24 else 0)
    bb = mask.getbbox()
    W, H = im.size
    if bb is None:
        return {"size": [W, H], "content": [0, 0, 0, 0],
                "bottom_gap": H, "content_cx": W / 2.0}
    x0, y0, x1, y1 = bb
    return {"size": [W, H], "content": [x0, y0, x1 - x0, y1 - y0],
            "bottom_gap": H - y1, "content_cx": (x0 + x1) / 2.0}


_MEASURE_CACHE = {}


def measurement(catalog, asset_id):
    if asset_id not in _MEASURE_CACHE:
        _MEASURE_CACHE[asset_id] = measure_png(sidecar_png(catalog, asset_id))
    return _MEASURE_CACHE[asset_id]


def record(catalog, asset_id):
    rec = catalog_lookup(catalog, asset_id)
    if rec is None:
        raise KeyError(f"asset id {asset_id} not in catalog")
    return rec


# ---------------------------------------------------------------------------
# Geometry
#
# Registered origin = bottom-centre of canvas for non-flat assets. Node placed at
# (x, y) so origin sits there.
#   content world bottom  = y - scale * bottom_gap
#   content world centre x = x + scale * (content_cx - origin_x)
# Given desired content base Y and content centre X:
#   y = base_Y + scale * bottom_gap
#   x = centre_X - scale * (content_cx - origin_x)
# ---------------------------------------------------------------------------


def position_from_target(catalog, asset_id, scale, content_center_x, content_base_y):
    rec = record(catalog, asset_id)
    ox, _ = rec["origin"]
    m = measurement(catalog, asset_id)
    y = content_base_y + scale * m["bottom_gap"]
    x = content_center_x - scale * (m["content_cx"] - ox)
    return [round(x, 3), round(y, 3)]


def wall_position(catalog, asset_id, scale, cell_x, content_base_y):
    """Architecture block whose content base sits at content_base_y, centred on a
    grid cell's horizontal centre."""
    rec = record(catalog, asset_id)
    ox, _ = rec["origin"]
    m = measurement(catalog, asset_id)
    cell_cx = GROUND_OFFSET[0] + (cell_x + 0.5) * TILE
    y = content_base_y + scale * m["bottom_gap"]
    x = cell_cx - scale * (m["content_cx"] - ox)
    return [round(x, 3), round(y, 3)]


# ---------------------------------------------------------------------------
# Layout definition (reference reconstruction, deterministic)
# ---------------------------------------------------------------------------


FLOOR_TILE_IDS = tuple(f"G{i:02d}" for i in range(1, 13))
FLOOR_ROW_SPANS = (
    ((0, 4), (11, 16)),
    *(((0, 16),) for _ in range(7)),
    ((1, 15),),
    ((6, 10),),
)


def floor_footprint_rows():
    """Return fresh copies of the existing 17x10 floor row spans."""
    return [[list(span) for span in row] for row in FLOOR_ROW_SPANS]


def floor_layout():
    """Cover the footprint with 80 percent G01/G02 and sparse accent tiles."""
    cells = []
    for y, spans in enumerate(FLOOR_ROW_SPANS):
        for start, end in spans:
            for x in range(start, end + 1):
                # Spread ten accent variants across each fifty floor cells.
                slot = (len(cells) * 17) % 50
                tile_id = (
                    FLOOR_TILE_IDS[slot + 2]
                    if slot < 10 else FLOOR_TILE_IDS[(x + y) % 2]
                )
                cells.append({"x": x, "y": y, "id": tile_id})
    return cells


def floor_settings():
    """Return the approved floor palette without sharing mutable state."""
    return {
        "floor_ids": list(FLOOR_TILE_IDS),
        "floor_tile_style": {"tile_ids": list(FLOOR_TILE_IDS)},
    }


def wall_perimeter():
    """Return boundary cells, including the cells at reentrant corners."""
    floor = {(cell["x"], cell["y"]) for cell in floor_layout()}
    return {
        (x, y) for x, y in floor
        if any(
            (x + dx, y + dy) not in floor
            for dx, dy in (
                (-1, 0), (1, 0), (0, -1), (0, 1),
                (-1, -1), (-1, 1), (1, -1), (1, 1),
            )
        )
    }


def wall_gaps():
    """The rear opening borders row 1; the stair exit crosses row 9."""
    return {
        "arch": {(x, 1) for x in range(5, 11)},
        "stairs": {(x, 9) for x in range(7, 10)},
    }


def perimeter_wall_entries():
    """Build one unrotated wall per boundary cell outside the two openings."""
    floor = {(cell["x"], cell["y"]) for cell in floor_layout()}
    gaps = set().union(*wall_gaps().values())
    front = {(x, 8) for x in (1, 2, 3, 4, 11, 12, 13, 14, 15)}
    entries = []
    body_index = 0
    for x, y in sorted(wall_perimeter() - gaps, key=lambda cell: (cell[1], cell[0])):
        exposed = {
            direction for direction in ((-1, 0), (1, 0), (0, -1), (0, 1))
            if (x + direction[0], y + direction[1]) not in floor
        }
        instance_id = f"PerimeterWall_{x:02d}_{y:02d}"
        if (x, y) in front:
            asset_id = "W10"
            side = "L" if x < 6 else "R"
            instance_id = f"FrontLowWall{side}{x:02d}"
        elif (x, y) == (4, 0):
            asset_id = "W13"
        elif (x, y) == (11, 0):
            asset_id = "W14"
        elif (x, y) == (6, 9):
            asset_id = "W11"
        elif (x, y) == (10, 9):
            asset_id = "W12"
        elif len(exposed) >= 2:
            asset_id = "W09"
        elif not exposed:
            asset_id = "W08"
        elif (0, -1) in exposed:
            asset_id = "W07"
        else:
            # Cycle only eligible body cells so every variant is represented.
            # Each accent appears once per sixteen bodies.
            slot = body_index % 16
            asset_id = {
                2: "W03", 5: "W04", 8: "W05", 11: "W06",
            }.get(slot, "W01" if body_index % 2 == 0 else "W02")
            body_index += 1
        if (x, y) in ((0, 0), (16, 0)):
            instance_id = f"BackWallR{x:02d}"
        entries.append(dict(
            kind="explicit", id=asset_id, scale=1.0,
            perimeter_cell=(x, y), cell_x=x,
            content_base_y=GROUND_OFFSET[1] + (y + 1) * TILE,
            layer="back_objects", instance_id=instance_id,
            shadow={"type": "wall_base", "opacity": 0.24,
                    "offset_x": 4, "offset_y": 4},
        ))
    return entries


def entry_scale(catalog, entry):
    """Uniformly fit walls to one cell using their registered dimensions."""
    if "perimeter_cell" not in entry:
        return entry.get("scale", 1.0)
    asset = record(catalog, entry["id"])
    contract = asset.get("placement_contract") or {}
    width, depth = contract.get("footprint_cells", (1, 1))
    return min(1.0, 1.0 / width, 1.0 / depth,
               TILE / asset["pixel_size"][0])


def lighting_decor_entries(walls):
    """Build decor on perimeter walls and furniture, followed by front glows."""
    entries = []
    wall_hosts = {
        tuple(wall["perimeter_cell"]): wall["instance_id"] for wall in walls
    }

    def mount(asset_id, host, offset, layer, name, scale=1.0):
        entries.append(dict(
            kind="mount", id=asset_id, mount_on=host,
            mount_offset=offset, layer=layer, instance_id=name, scale=scale,
        ))

    # Side-wall spacing leaves the rear and stair openings clear.
    for side, x in (("Left", 0), ("Right", 16)):
        for y in (0, 2, 4, 6):
            host = wall_hosts[(x, y)]
            name = f"{side}WallLantern{y}"
            mount("L01" if y % 4 == 0 else "L02", host, (0, -40),
                  "back_objects", name, 0.5)
            # Glow mounts on the wall host (lanterns are not valid hosts).
            mount("L05", host, (0, -52), "front_objects",
                  f"{name}Glow", 0.5)

    for asset_id, cell, name in (
        ("D04", (3, 0), "LeftWallBanner"),
        ("D05", (13, 0), "RightWallBanner"),
    ):
        mount(asset_id, wall_hosts[cell], (0, -42),
              "back_objects", name, 0.65)

    for asset_id, cell, name in (
        ("D04", (0, 3), "LeftSideWallBanner"),
        ("D05", (16, 3), "RightSideWallBanner"),
    ):
        mount(asset_id, wall_hosts[cell], (0, -42),
              "back_objects", name, 0.65)

    for index, cell in enumerate(((0, 1), (16, 1), (0, 5), (16, 5))):
        host = wall_hosts[cell]
        mount(("P01", "P02", "P03")[index % 3], host, (0, -64),
              "back_objects", f"WallTopIvy{index}", 0.5)
        mount("P04", host, (12, -64), "back_objects",
              f"WallTopFlowers{index}", 0.4)
        mount("P05" if index % 2 == 0 else "P06", host, (0, 0),
              "objects", f"WallBasePlants{index}", 0.5)

    for host, offset, name in (
        ("BedsideTable", (0, -48), "BedsideLantern"),
        ("DiningTable", (65, -151), "DiningLantern"),
    ):
        mount("L04", host, offset, "objects", name, 0.5)
        mount("L05", host, (offset[0], offset[1] - 12), "front_objects",
              f"{name}Glow", 0.5)

    for host, offset, name in (
        ("LeftBookcase", (-24, -64), "LeftShelfCandles"),
        ("RightBookcase", (24, -64), "RightShelfCandles"),
        ("DiningTable", (-65, -151), "DiningCandles"),
    ):
        mount("L03", host, offset, "objects", name, 0.5)
        mount("L05", host, (offset[0], offset[1] - 10), "front_objects",
              f"{name}Glow", 0.4)

    for asset_id, host, offset, name in (
        ("R01", "BedsideTable", (24, -48), "BedsideVase"),
        ("R02", "RightBookcase", (-24, -64), "ShelfVase"),
        ("R06", "LeftBookcase", (24, -64), "ShelfBooks"),
        ("R05", "DiningTable", (-90, -151), "TableScroll"),
        ("R09", "DiningTable", (-30, -151), "TableMap"),
        ("R06", "DiningTable", (0, -151), "TableBook"),
        ("R10", "DiningTable", (30, -151), "TableFruitBowl"),
        ("R11", "DiningTable", (95, -151), "TableJug"),
    ):
        mount(asset_id, host, offset, "objects", name, 0.4)

    return entries


def layout_entries():
    E = []

    # ---- Level 0: background (distant isles, sea stacks) ----
    E.append(dict(kind="background", id="B05", x=288, y=130, scale=0.32,
                  layer="background_objects", instance_id="DistantIsleLeft"))
    E.append(dict(kind="background", id="B06", x=1120, y=145, scale=0.25,
                  layer="background_objects", instance_id="DistantIsleRight"))
    E.append(dict(kind="background", id="B11", x=1012, y=106, scale=0.14,
                  layer="background_objects", instance_id="DistantIsleArch"))
    E.append(dict(kind="background", id="B05", x=90, y=110, scale=0.27,
                  layer="background_objects", instance_id="LeftIslandDistantExtra"))
    E.append(dict(kind="background", id="B06", x=1452, y=126, scale=0.19,
                  layer="background_objects", instance_id="RightIslandDistantExtra"))
    E.append(dict(kind="background", id="B05", x=40, y=100, scale=0.60,
                  layer="background_objects", instance_id="SeaStackLeft"))
    E.append(dict(kind="background", id="B06", x=1350, y=120, scale=0.50,
                  layer="background_objects", instance_id="SeaStackRight"))

    # ---- Level 2: furniture (grid, scale 1.0) ----
    E.append(dict(kind="grid", id="F01", facing="south",
                  cell=(2, 1), layer="objects", instance_id="RoyalBed",
                  shadow={"type": "bed", "opacity": 0.30, "offset_x": 0, "offset_y": 0}))
    E.append(dict(kind="grid", id="F05", facing="south",
                  cell=(0, 2), layer="objects", instance_id="BedsideTable",
                  shadow={"type": "contact_medium", "opacity": 0.26, "offset_x": 0, "offset_y": 0}))
    E.append(dict(kind="grid", id="F06", facing="north",
                  cell=(1, 0), layer="objects", instance_id="LeftBookcase",
                  shadow={"type": "bookshelf", "opacity": 0.28, "offset_x": 0, "offset_y": 0}))
    E.append(dict(kind="grid", id="F07", facing="north",
                  cell=(10, 1), layer="objects", instance_id="RightBookcase",
                  shadow={"type": "bookshelf", "opacity": 0.28, "offset_x": 0, "offset_y": 0}))
    E.append(dict(kind="grid", id="F08", facing="north",
                  cell=(12, 3), layer="objects", instance_id="DiningTable",
                  shadow={"type": "table", "opacity": 0.30, "offset_x": 4, "offset_y": 0}))
    E.append(dict(kind="grid", id="F09", facing="south",
                  cell=(12, 6), layer="objects", instance_id="TableBenchLeft",
                  shadow={"type": "chair", "opacity": 0.22, "offset_x": 0, "offset_y": 0}))
    E.append(dict(kind="grid", id="F09", facing="south",
                  cell=(14, 6), layer="objects", instance_id="TableBenchRight",
                  shadow={"type": "chair", "opacity": 0.22, "offset_x": 0, "offset_y": 0}))

    for asset_id, cell in (("F10", (15, 7)), ("F11", (1, 7)), ("F12", (3, 7))):
        E.append(dict(
            kind="grid", id=asset_id, facing="south", cell=cell,
            layer="objects", instance_id="Crate" + asset_id,
            shadow={"type": "contact_medium", "opacity": 0.22,
                    "offset_x": 0, "offset_y": 0},
        ))

    # ---- Level 1: ground overlays (grid, scale 1.0) ----
    E.append(dict(kind="overlay", id="D01", cell=(2, 2), layer="ground_overlays",
                  instance_id="BedRug",
                  shadow={"type": "contact_medium", "opacity": 0.22, "offset_x": 0, "offset_y": 0}))
    E.append(dict(kind="overlay", id="D02", cell=(12, 3), layer="ground_overlays",
                  instance_id="TableRug",
                  shadow={"type": "contact_medium", "opacity": 0.22, "offset_x": 0, "offset_y": 0}))
    E.append(dict(kind="overlay", id="D03", cell=(6, 4), layer="ground_overlays",
                  instance_id="CompassFloorEmblem",
                  shadow={"type": "contact_medium", "opacity": 0.20, "offset_x": 0, "offset_y": 0}))

    # ---- Level 2: architecture (explicit, scale free) ----
    # Dominant open rear arch: content centre x=707, content base y=289, scale 2.4.
    E.append(dict(kind="explicit", id="A05", scale=2.4,
                  content_center_x=707, content_base_y=289, layer="back_objects",
                  instance_id="RearArch",
                  shadow={"type": "soft_cast", "opacity": 0.24, "offset_x": 6, "offset_y": 5}))
    # Two supporting columns flanking the arch, content base y=289, scale 1.0.
    E.append(dict(kind="explicit", id="A01", scale=1.0,
                  content_center_x=532, content_base_y=289, layer="back_objects",
                  instance_id="ArchColumnLeft",
                  shadow={"type": "column_long", "opacity": 0.24, "offset_x": 4, "offset_y": 4}))
    E.append(dict(kind="explicit", id="A01", scale=1.0,
                  content_center_x=890, content_base_y=289, layer="back_objects",
                  instance_id="ArchColumnRight",
                  shadow={"type": "column_long", "opacity": 0.24, "offset_x": 4, "offset_y": 4}))
    # Decorative ruined stone door at rear right: content centre x=1112, base y=289, scale 1.75.
    E.append(dict(kind="explicit", id="A09", scale=1.75,
                  content_center_x=1112, content_base_y=289, layer="back_objects",
                  instance_id="RearRightDoor",
                  shadow={"type": "soft_cast", "opacity": 0.24, "offset_x": 6, "offset_y": 5}))
    # Includes the nine named front low walls; no duplicate legacy wall run.
    E.extend(perimeter_wall_entries())
    # Front staircase: 4 step tiles descending toward camera, centre x=750.
    for i, base_y in enumerate([880, 916, 952, 988]):
        E.append(dict(kind="explicit", id="A10", scale=1.6,
                      content_center_x=750, content_base_y=base_y, layer="back_objects",
                      instance_id="StairStep%d" % (i + 1),
                      shadow={"type": "stairs", "opacity": 0.24, "offset_x": 4, "offset_y": 5}))
    # Entrance pillars at front, base y=865, scale 1.1.
    E.append(dict(kind="explicit", id="A13", scale=1.1,
                  content_center_x=602, content_base_y=865, layer="back_objects",
                  instance_id="EntrancePillarLeft",
                  shadow={"type": "column_short", "opacity": 0.26, "offset_x": 4, "offset_y": 4}))
    E.append(dict(kind="explicit", id="A13", scale=1.1,
                  content_center_x=894, content_base_y=865, layer="back_objects",
                  instance_id="EntrancePillarRight",
                  shadow={"type": "column_short", "opacity": 0.26, "offset_x": 4, "offset_y": 4}))
    # Stair side supports flanking the stringers.
    E.append(dict(kind="explicit", id="A11", scale=1.0,
                  content_center_x=630, content_base_y=916, layer="back_objects",
                  instance_id="StairSupportLeft",
                  shadow={"type": "wall_base", "opacity": 0.20, "offset_x": 3, "offset_y": 3}))
    E.append(dict(kind="explicit", id="A12", scale=1.0,
                  content_center_x=870, content_base_y=916, layer="back_objects",
                  instance_id="StairSupportRight",
                  shadow={"type": "wall_base", "opacity": 0.20, "offset_x": 3, "offset_y": 3}))

    # ---- Level 2: front coastal foundations (environment, rendered as walls) ----
    # Allow for the registered origin so full canvases fit below the lower walls.
    E.append(dict(kind="background", id="B03", x=394, y=970, scale=0.20,
                  layer="front_objects", render_layer="walls",
                  instance_id="TerraceRockFrontLeft",
                  shadow={"type": "wall_base", "opacity": 0.18, "offset_x": 5, "offset_y": 8}))
    E.append(dict(kind="background", id="B03", x=1145, y=970, scale=0.20,
                  layer="front_objects", render_layer="walls",
                  instance_id="TerraceRockFrontRight",
                  shadow={"type": "wall_base", "opacity": 0.18, "offset_x": 5, "offset_y": 8}))

    # ---- Level 2: floor plants in front of the arch (grid, scale 1.0) ----
    E.append(dict(kind="grid", id="P05", facing="north",
                  cell=(5, 1), layer="objects", instance_id="ArchFlowersLeft",
                  shadow={"type": "plant", "opacity": 0.16, "offset_x": 2, "offset_y": 2}))
    E.append(dict(kind="grid", id="P06", facing="north",
                  cell=(8, 1), layer="objects", instance_id="ArchFlowersRight",
                  shadow={"type": "plant", "opacity": 0.16, "offset_x": 2, "offset_y": 2}))
    E.append(dict(kind="grid", id="P04", facing="north",
                  cell=(6, 2), layer="objects", instance_id="ArchFlowersCenter",
                  shadow={"type": "plant", "opacity": 0.16, "offset_x": 2, "offset_y": 2}))

    # ---- Level 3: decorations mounted on the arch ----
    E.append(dict(kind="mount", id="P03", mount_on="RearArch",
                  mount_offset=(-105, -170), layer="back_objects",
                  instance_id="ArchIvyLeft"))
    E.append(dict(kind="mount", id="P03", mount_on="RearArch",
                  mount_offset=(105, -170), layer="back_objects",
                  instance_id="ArchIvyRight"))
    E.append(dict(kind="mount", id="P12", mount_on="RearArch",
                  mount_offset=(-114, -9), layer="back_objects",
                  instance_id="ArchFloralLeft"))
    E.append(dict(kind="mount", id="P13", mount_on="RearArch",
                  mount_offset=(124, -9), layer="back_objects",
                  instance_id="ArchFloralRight"))

    # ---- Level 3: wall-mounted lanterns & banners ----
    E.append(dict(kind="mount", id="L01", mount_on="BackWallR00",
                  mount_offset=(-14, -55), layer="back_objects",
                  instance_id="LeftWallLantern"))
    E.append(dict(kind="mount", id="L01", mount_on="BackWallR16",
                  mount_offset=(14, -55), layer="back_objects",
                  instance_id="RightWallLantern"))
    E.append(dict(kind="mount", id="D04", mount_on="RearArch",
                  mount_offset=(62, -90), layer="back_objects",
                  instance_id="ArchBannerRight"))
    E.append(dict(kind="mount", id="D05", mount_on="RearArch",
                  mount_offset=(-62, -90), layer="back_objects",
                  instance_id="ArchBannerLeft"))

    # ---- Level 3: tabletop props mounted on the dining table ----
    E.append(dict(kind="mount", id="R05", mount_on="DiningTable",
                  mount_offset=(-92, -151), layer="objects",
                  instance_id="TableScroll"))
    E.append(dict(kind="mount", id="R09", mount_on="DiningTable",
                  mount_offset=(-42, -151), layer="objects",
                  instance_id="TableMap"))
    E.append(dict(kind="mount", id="R06", mount_on="DiningTable",
                  mount_offset=(-2, -151), layer="objects",
                  instance_id="TableBook"))
    E.append(dict(kind="mount", id="R10", mount_on="DiningTable",
                  mount_offset=(38, -151), layer="objects",
                  instance_id="TableFruitBowl"))
    E.append(dict(kind="mount", id="R11", mount_on="DiningTable",
                  mount_offset=(88, -151), layer="objects",
                  instance_id="TableJug"))

    # ---- Level 3: floor vases flanking the arch base ----
    E.append(dict(kind="grid", id="R01", facing="north",
                  cell=(0, 1), layer="objects", instance_id="ArchVaseLeft",
                  shadow={"type": "contact_small", "opacity": 0.20, "offset_x": 2, "offset_y": 2}))
    E.append(dict(kind="grid", id="R02", facing="north",
                  cell=(9, 1), layer="objects", instance_id="ArchVaseRight",
                  shadow={"type": "contact_small", "opacity": 0.20, "offset_x": 2, "offset_y": 2}))

    # Replace legacy decor with mounts on perimeter walls or parent furniture.
    E = [
        entry for entry in E
        if not entry["id"].startswith(("L", "P", "R"))
        and entry["id"] not in ("D04", "D05")
    ]
    E.extend(lighting_decor_entries(
        [entry for entry in E if "perimeter_cell" in entry]
    ))
    return E


# ---------------------------------------------------------------------------
# Resolve entries -> exact block list
# ---------------------------------------------------------------------------


def is_furniture(entry):
    return entry["id"].split("@", 1)[0] in {
        "F01", "F02", "F03", "F04", "F05", "F06",
        "F07", "F08", "F09", "F10", "F11", "F12",
    }


def furniture_orientation(catalog, entry):
    assets = {asset["id"]: asset for asset in catalog["assets"]}
    variants = furniture_direction_ids(entry["id"], assets)
    block = {
        "id": entry["id"], "facing": entry.get("facing", "north"),
        "orientation_mode": "variants", "direction_asset_ids": variants,
    }
    return resolve_orientation(block, assets)


def entry_footprint(catalog, entry):
    """Use the north footprint once, swapping axes for east and west."""
    if is_furniture(entry):
        assets = {asset["id"]: asset for asset in catalog["assets"]}
        north_id = furniture_direction_ids(entry["id"], assets)["north"]
        rec = assets[north_id]
    else:
        rec = record(catalog, entry["id"])
    width, depth = rec["placement_contract"]["footprint_cells"]
    if entry.get("facing", "north") in ("east", "west"):
        width, depth = depth, width
    return [width, depth]


def resolve_entries(catalog, entries):
    computed = {}  # instance_id -> [x, y]

    for e in entries:
        if e["kind"] == "background":
            computed[e["instance_id"]] = [round(e["x"], 3), round(e["y"], 3)]
            continue
        if e["kind"] in ("grid", "overlay"):
            fw, fh = entry_footprint(catalog, e)
            cell_x, cell_y = e["cell"]
            x = GROUND_OFFSET[0] + (cell_x + fw / 2.0) * TILE
            y = GROUND_OFFSET[1] + (cell_y + fh) * TILE
            computed[e["instance_id"]] = [round(x, 3), round(y, 3)]
        elif e["kind"] == "explicit":
            if "perimeter_cell" in e:
                # Use the registered bottom-centre pivot, without sprite rotation.
                cell_x, cell_y = e["perimeter_cell"]
                computed[e["instance_id"]] = [
                    GROUND_OFFSET[0] + (cell_x + 0.5) * TILE,
                    GROUND_OFFSET[1] + (cell_y + 1) * TILE,
                ]
            elif e.get("content_center_x") is not None:
                computed[e["instance_id"]] = position_from_target(
                    catalog, e["id"], e["scale"], e["content_center_x"],
                    e["content_base_y"])
            else:
                computed[e["instance_id"]] = wall_position(
                    catalog, e["id"], e["scale"], e["cell_x"], e["content_base_y"])

    # Mounts follow their hosts, including lantern-mounted glow overlays.
    for e in entries:
        if e["kind"] == "mount":
            hx, hy = computed[e["mount_on"]]
            ox, oy = e["mount_offset"]
            computed[e["instance_id"]] = [round(hx + ox, 3), round(hy + oy, 3)]

    blocks = []
    for e in entries:
        iid = e["instance_id"]
        x, y = computed[iid]
        block = {"id": e["id"], "instance_id": iid, "x": x, "y": y,
                 "scale": entry_scale(catalog, e), "_layer": e["layer"]}
        if e["kind"] in ("grid", "overlay"):
            facing = e.get("facing", "north")
            block["grid_placement"] = {"cell": list(e["cell"]), "facing": facing}
            if is_furniture(e):
                orientation = furniture_orientation(catalog, e)
                block["id"] = orientation["resolved_asset_id"]
                block["facing"] = facing
                block["orientation_mode"] = "variants"
                block["direction_asset_ids"] = orientation["direction_asset_ids"]
            elif facing != "north":
                block["facing"] = facing
                block["orientation_mode"] = "variants"
                block["direction_asset_ids"] = record(catalog, e["id"]).get(
                    "direction_asset_ids", {})
            if e.get("shadow"):
                block["shadow"] = e["shadow"]
        elif e["kind"] == "mount":
            block["render_layer"] = "decorations"
            block["mount_on"] = e["mount_on"]
            block["mount_offset"] = list(e["mount_offset"])
            if e.get("shadow"):
                block["shadow"] = e["shadow"]
        elif e["kind"] == "background":
            if e.get("render_layer"):
                block["render_layer"] = e["render_layer"]
            if e.get("shadow"):
                block["shadow"] = e["shadow"]
        else:  # explicit architecture
            if e.get("shadow"):
                block["shadow"] = e["shadow"]
        blocks.append(block)
    return blocks, computed


# ---------------------------------------------------------------------------
# Blueprint JSON (design document)
# ---------------------------------------------------------------------------


def write_blueprint(catalog, entries, resolved):
    pos_map = dict(resolved)
    instances = []
    for e in entries:
        iid = e["instance_id"]
        x, y = pos_map[iid]
        orientation = furniture_orientation(catalog, e) if is_furniture(e) else None
        asset_id = orientation["resolved_asset_id"] if orientation else e["id"]
        rec = record(catalog, asset_id)
        m = measurement(catalog, asset_id)
        entry = {"instance_id": iid, "asset_id": asset_id, "category": rec["category"],
                 "kind": e["kind"], "position": [x, y], "scale": entry_scale(catalog, e),
                 "pixel_size": rec["pixel_size"], "content_bbox": m["content"],
                 "layer": e["layer"]}
        if e["kind"] in ("grid", "overlay"):
            entry["grid_placement"] = {"cell": list(e["cell"]),
                                       "facing": e.get("facing", "north")}
            entry["footprint_cells"] = entry_footprint(catalog, e)
        if orientation:
            entry["orientation_mode"] = "variants"
            entry["direction_asset_ids"] = orientation["direction_asset_ids"]
        if e.get("facing"):
            entry["facing"] = e["facing"]
        if e["kind"] == "mount":
            entry["mount_on"] = e["mount_on"]
            entry["mount_offset"] = list(e["mount_offset"])
        if e.get("shadow"):
            entry["shadow"] = e["shadow"]
        instances.append(entry)

    blueprint = {
        "schema_version": 1,
        "map_id": "hero_room_01",
        "mode": "reference_reconstruction",
        "description": ("Deterministic reference-room blueprint for hero_room_01. "
                        "Recreates the fantasy seaside bedroom using only the approved "
                        "128-piece environment pack (assets_generated); no new artwork "
                        "and no PNG bytes modified."),
        "canvas_size": list(CANVAS),
        "tile_size": TILE,
        "size": [17, 10],
        "ground_offset": list(GROUND_OFFSET),
        "floor_footprint": {
            "row_0": [[0, 4], [11, 16]],
            "rows_1_7": [[0, 16]],
            "row_8": [[1, 15]],
            "row_9": [[6, 10]],
            "notes": ("Row 0 leaves cells 5-10 open so the rear arch opening reveals "
                      "the ocean behind it; cells 0-4 and 11-16 keep floor at the edges."),
        },
        "instances": instances,
        "notes": (
            "Documented pack limitations (not worked around by stretching): arch opening "
            "~84px wide at scale 2.4; bed rug D01 and table rug D02 are compact "
            "portrait/square assets vs the reference's landscape rugs; bookcases are "
            "low/wide vs the reference's tall shelves; no side-wall banner art exists "
            "in the pack; the 64x64 square grid cannot reproduce the reference's oblique "
            "floor projection."),
    }
    with open(BLUEPRINT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(blueprint, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"wrote blueprint: {BLUEPRINT} ({len(instances)} instances)")
    return blueprint


# ---------------------------------------------------------------------------
# Patch manifest (v0012)
# ---------------------------------------------------------------------------


def compute_sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def digest_json(data):
    packed = json.dumps(data, sort_keys=True, separators=(",", ":"),
                        ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(packed).hexdigest()


def patch_manifest(catalog, blocks, latest):
    """Build a manifest without mutating inputs or writing files."""
    base_version = latest["version"]
    base_sha = digest_json(latest)

    v0011_ids = []
    for layer in ("background_objects", "ground_overlays", "back_objects",
                  "objects", "front_objects"):
        for b in latest.get(layer, []):
            v0011_ids.append(b["instance_id"])

    changes = []
    for iid in sorted(set(v0011_ids)):
        changes.append({"op": "remove_block", "instance_id": iid})
    for b in blocks:
        layer = b.get("_layer", "objects")
        op_block = deepcopy({k: v for k, v in b.items() if k != "_layer"})
        changes.append({"op": "add_block", "layer": layer, "block": op_block})

    # Clear every v0011 tile override via set_tile (id=None removes a tile).
    # set_property does not allow tile_overrides, so we remove per-cell.
    for ov in latest.get("tile_overrides", []):
        changes.append({"op": "set_tile", "x": int(ov["x"]), "y": int(ov["y"]),
                        "id": None})

    # Apply explicit deterministic tiles after clearing the previous overrides.
    for cell in floor_layout():
        changes.append({"op": "set_tile", **cell})
    for key, value in floor_settings().items():
        if key == "floor_tile_style":
            value = {**latest.get(key, {}), **value}
        changes.append({"op": "set_property", "key": key, "value": value})

    changes.append({"op": "set_property", "key": "floor_footprint",
                    "value": {"row_spans": floor_footprint_rows(),
                              "shape": "hero_room_reference_v1",
                              "notes": ("Row 0 leaves cells 5-10 open so the rear arch "
                                        "opening reveals the ocean behind it.")}})

    changes.append({"op": "set_property", "key": "ocean",
                    "value": latest.get("ocean", {
                        "tile_size": 512, "fps": 4, "sky_height": 68,
                        "notes": "Horizon lowered to reference; layer-0 ocean/sky kept."})})

    changes.append({"op": "set_property", "key": "effects", "value": [
        {"instance_id": "LanternLeftGlow", "kind": "lantern",
         "x": 258, "y": 420, "scale": 0.45, "glow_alpha": 0.38},
        {"instance_id": "LanternRightGlow", "kind": "lantern",
         "x": 1282, "y": 420, "scale": 0.45, "glow_alpha": 0.38},
        {"instance_id": "TableCandleGlow", "kind": "candle",
         "x": 1122, "y": 440, "scale": 0.40, "glow_alpha": 0.34},
    ]})

    changes.append({"op": "set_property", "key": "navigation", "value": {
        "schema_version": 1,
        "origin": [226, 225],
        "cell_size": 64,
        "grid_size": [17, 10],
        "default": {"walk": False, "fly": False, "swim": False},
        "regions": [
            {"id": "inner_terrace_safe_walk", "rect": [1, 2, 15, 7],
             "surface": "stone", "allow": ["walk", "fly"],
             "requires": {"walk": [], "fly": []},
             "floor_height": 0, "ceiling_height": None, "review_status": "needs_review"},
            {"id": "stairs_to_ocean_entrance", "rect": [7, 9, 3, 1],
             "surface": "stairs", "allow": ["walk", "fly"],
             "requires": {"walk": [], "fly": []},
             "floor_height": -24, "ceiling_height": None, "review_status": "needs_review"},
        ],
        "obstacles": [
            {"instance_id": "RoyalBed", "blocks": ["walk", "fly"],
             "min_altitude": 0, "max_altitude": 75},
            {"instance_id": "DiningTable", "blocks": ["walk", "fly"],
             "min_altitude": 0, "max_altitude": 80},
            {"instance_id": "EntrancePillarLeft", "blocks": ["walk", "fly"],
             "min_altitude": 0, "max_altitude": 78},
            {"instance_id": "EntrancePillarRight", "blocks": ["walk", "fly"],
             "min_altitude": 0, "max_altitude": 78},
            {"instance_id": "LeftBookcase", "blocks": ["walk", "fly"],
             "min_altitude": 0, "max_altitude": 110},
            {"instance_id": "RightBookcase", "blocks": ["walk", "fly"],
             "min_altitude": 0, "max_altitude": 110},
        ],
        "links": [
            {"id": "coastal_stair_exit", "from": [8, 8], "to": [8, 9],
             "modes": ["walk", "fly"], "requires": []},
        ],
        "note": "Navigation provisional, unreviewed; no character or weapon factory changes.",
    }})

    changes.append({"op": "set_property", "key": "description", "value": (
        "Hero's Seaside Sanctuary — reference reconstruction v0012. Rebuilt from the "
        "approved 128-piece environment pack: open rear arch to ocean, royal bed left "
        "on its rug, dining table right on its rug, centred compass emblem, front "
        "staircase, four-level assembly (background/ground/walls-decorations/shadows). "
        "Visual approval pending.")})
    changes.append({"op": "set_property", "key": "visual_qa", "value": {
        "status": "needs_review",
        "notes": "Native Godot render v0012; compare against reference and v0011."}})
    changes.append({"op": "set_property", "key": "composition_reference", "value": {
        "image": "map_factory/references/hero_room_01_original.png",
        "reference_sha256": "42511e4e05176d9057775fa05562ca5b91675d32ba70ae9b8ba1012b41df25a7",
        "reference_dimensions": [1448, 1086],
        "qa": "pending visual comparison",
        "status": "needs_visual_review"}})
    changes.append({"op": "set_property", "key": "source_image", "value": {
        "path": "map_factory/references/hero_room_01_original.png",
        "sha256": "42511e4e05176d9057775fa05562ca5b91675d32ba70ae9b8ba1012b41df25a7",
        "status": "reference_imported"}})
    changes.append({"op": "set_property", "key": "floor_art", "value": {
        "design": "central compass emblem as D03 ground overlay at grid cell (6,4)",
        "tile_size": 64, "ids": ["D03"], "top_left_grid": [6, 4], "qa": "needs_review"}})

    manifest = {
        "manifest_version": 1,
        "map_id": "hero_room_01",
        "base_version": base_version,
        "base_sha256": base_sha,
        "note": ("hero_room_01 reference reconstruction v0012: replace v0011 layout with "
                 "deterministic reference-reconstruction blueprint using the approved "
                 "128-piece environment pack; PNG bytes unchanged."),
        "source_image": {
            "path": "map_factory/references/hero_room_01_original.png",
            "sha256": "42511e4e05176d9057775fa05562ca5b91675d32ba70ae9b8ba1012b41df25a7",
            "status": "reference_imported",
        },
        "changes": changes,
    }
    return manifest


def legacy_catalog_ids():
    data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))["assets"]
    return set(data) if isinstance(data, dict) else {a["id"] for a in data}


def legacy_form(asset_id, legacy_ids):
    """Map a v2 key (X@facing) to the id the legacy runtime catalog knows."""
    if "@" not in asset_id or asset_id in legacy_ids:
        return asset_id
    base, facing = asset_id.split("@", 1)
    for candidate in (base + "_" + facing, base):
        if candidate in legacy_ids:
            return candidate
    return asset_id


def canonical_blocks(catalog, blocks):
    """Resolve registered v2 identities and keep full sprites inside the canvas."""
    assets = {asset["id"]: asset for asset in catalog["assets"]}
    result = deepcopy(blocks)
    positions = {}
    legacy_ids = legacy_catalog_ids()
    for block in result:
        original_id = block["id"]
        block["id"] = canonical_asset_id(block["id"], assets)
        if "direction_asset_ids" in block:
            block["direction_asset_ids"] = {
                facing: canonical_asset_id(asset_id, assets)
                for facing, asset_id in block["direction_asset_ids"].items()
            }
        asset = assets[block["id"]]
        width, height = asset["pixel_size"]
        ox, oy = asset["origin"]
        scale = min(block.get("scale", 1.0),
                    CANVAS[0] / width, CANVAS[1] / height)
        if "grid_placement" in block:
            # Grid anchors remain authoritative; reduce uniformly if necessary.
            limits = (
                (block["x"], ox), (CANVAS[0] - block["x"], width - ox),
                (block["y"], oy), (CANVAS[1] - block["y"], height - oy),
            )
            scale = min(scale, *(space / extent for space, extent in limits
                                 if extent > 0))
            if scale <= 0:
                raise ValueError(f"Grid anchor outside canvas: {block['instance_id']}")
        block["scale"] = scale
        block["x"] = min(max(block["x"], scale * ox),
                         CANVAS[0] - scale * (width - ox))
        block["y"] = min(max(block["y"], scale * oy),
                         CANVAS[1] - scale * (height - oy))
        positions[block["instance_id"]] = (block["x"], block["y"])
        # The runtime catalog is the legacy asset index: ids that only exist as
        # v2 keys (F01@south, F05@north) stay in their legacy form in the map.
        block["id"] = legacy_form(block["id"], legacy_ids)
        if "direction_asset_ids" in block:
            block["direction_asset_ids"] = {
                facing: legacy_form(asset_id, legacy_ids)
                for facing, asset_id in block["direction_asset_ids"].items()
            }

    for block in result:
        if block.get("mount_on"):
            record = assets.get(block["id"]) or assets.get(
                legacy_form(block["id"], legacy_ids), {})
            contract = record.get("placement_contract") or {}
            if contract.get("mode") == "floor":
                # Floor-contract props (plants, rugs) cannot be mounted; keep
                # their absolute position instead of a host attachment.
                block.pop("mount_on")
                block.pop("mount_offset", None)
                continue
            hx, hy = positions[block["mount_on"]]
            block["mount_offset"] = [block["x"] - hx, block["y"] - hy]
    return result


REFERENCE_ZONES = {
    "RearArch": (555, 0, 990, 390),
    "ArchColumnLeft": (535, 150, 610, 390),
    "ArchColumnRight": (935, 150, 1010, 390),
    "RearRightDoor": (1210, 100, 1390, 340),
    "RoyalBed": (250, 335, 550, 625),
    "BedRug": (220, 430, 580, 665),
    "BedsideTable": (195, 430, 265, 530),
    "LeftBookcase": (275, 240, 510, 345),
    "RightBookcase": (1050, 245, 1275, 350),
    "DiningTable": (1030, 430, 1320, 625),
    "TableRug": (1000, 490, 1350, 675),
    "CompassFloorEmblem": (635, 545, 890, 730),
    "EntrancePillarLeft": (600, 725, 655, 850),
    "EntrancePillarRight": (875, 725, 930, 850),
    "StairSupportLeft": (610, 835, 655, 970),
    "StairSupportRight": (875, 835, 920, 970),
}


def reference_relayout_blocks(catalog):
    """Build explicit environment placements; retain the established wall run."""
    entries = [
        entry for entry in layout_entries()
        if not entry["instance_id"].startswith(("Crate", "TableBench"))
    ]
    blocks, _ = resolve_entries(catalog, entries)
    blocks = canonical_blocks(catalog, blocks)
    by_id = {block["instance_id"]: block for block in blocks}
    original = deepcopy(by_id)

    def fit(name, zone, maximum=1.0):
        block = by_id[name]
        asset = record(catalog, block["id"])
        fitted = fit_registered_block(
            asset, measurement(catalog, block["id"]), block, zone, maximum,
        )
        fitted.pop("grid_placement", None)
        by_id[name] = fitted

    for name, zone in REFERENCE_ZONES.items():
        fit(name, zone, 2.4 if name == "RearArch" else 1.0)
    for index in range(4):
        fit(f"StairStep{index + 1}",
            (655, 755 + index * 58, 875, 850 + index * 58), 1.6)

    # Keep attached props on the resized host using the same uniform transform.
    for block in blocks:
        name = block["instance_id"]
        host = block.get("mount_on")
        if host:
            before, after = original[host], by_id[host]
            ratio = after["scale"] / before["scale"]
            dx, dy = block["mount_offset"]
            by_id[name] = {
                **block, "x": after["x"] + dx * ratio,
                "y": after["y"] + dy * ratio,
                "scale": block["scale"] * ratio,
                "mount_offset": [dx * ratio, dy * ratio],
            }

    # Flower mounts flank the opening rather than covering the ocean aperture.
    for name, asset_id, dx in (
        ("RearArchFlowersLeft", "P12", -165),
        ("RearArchFlowersRight", "P13", 165),
    ):
        host = by_id["RearArch"]
        asset_id = canonical_asset_id(
            asset_id, {asset["id"]: asset for asset in catalog["assets"]},
        )
        by_id[name] = {
            "id": asset_id, "instance_id": name,
            "x": host["x"] + dx, "y": host["y"],
            "scale": 0.4, "_layer": "back_objects",
            "render_layer": "decorations", "mount_on": "RearArch",
            "mount_offset": [dx, 0],
        }
    result = list(by_id.values())
    validate_reference_relayout(catalog, result)
    return result


def validate_reference_relayout(catalog, blocks):
    """Reject missing textures, misplaced focal features and blocked circulation."""
    from math import isfinite

    by_id = {block["instance_id"]: block for block in blocks}
    if len(by_id) != len(blocks):
        raise ValueError("Duplicate placement identity")
    bounds = {}
    for block in blocks:
        asset = record(catalog, block["id"])
        if not texture_available(sidecar_png(catalog, block["id"])):
            raise ValueError("Missing registered texture")
        if (not all(isfinite(block[key]) for key in ("x", "y", "scale"))
                or block["scale"] <= 0
                or block.get("rotation", 0) != 0
                or block.get("flip_h") or block.get("flip_v")):
            raise ValueError("Invalid sprite transform")
        bounds[block["instance_id"]] = content_bounds(
            asset, measurement(catalog, block["id"]), block,
        )
        if block.get("mount_on") and block["mount_on"] not in by_id:
            raise ValueError("Missing mount host")
        if "direction_asset_ids" in block:
            variants = block["direction_asset_ids"]
            if set(variants) != {"north", "east", "south", "west"}:
                raise ValueError("Incomplete directional furniture")
            textures = {sidecar_png(catalog, value) for value in variants.values()}
            if len(textures) != 4 or not all(texture_available(path) for path in textures):
                raise ValueError("Directional furniture requires four textures")
            if block["id"] != variants[block["facing"]]:
                raise ValueError("Incorrect directional texture")
    for name, zone in REFERENCE_ZONES.items():
        left, top, right, bottom = bounds[name]
        if (left < zone[0] - 0.001 or top < zone[1] - 0.001
                or right > zone[2] + 0.001 or bottom > zone[3] + 0.001):
            raise ValueError(f"Feature outside target zone: {name}")

    # Rugs and mounted props intentionally overlap their hosts. Solid furniture
    # must remain separate and leave a two-cell central route to the stairs.
    solids = ("RoyalBed", "BedsideTable", "LeftBookcase",
              "RightBookcase", "DiningTable")
    def overlaps(a, b):
        return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]

    for index, name in enumerate(solids):
        if overlaps(bounds[name], (700, 390, 828, 850)):
            raise ValueError("Furniture blocks central circulation")
        for other in solids[index + 1:]:
            if overlaps(bounds[name], bounds[other]):
                raise ValueError("Solid furniture overlap")
    floor = {(cell["x"], cell["y"]) for cell in floor_layout()}
    if not all((x, y) in floor for x in (7, 8, 9) for y in range(2, 10)):
        raise ValueError("Central route lacks floor coverage")


def next_reference_version():
    """Choose the immediate successor; never skip an existing patch."""
    with open(LATEST, encoding="utf-8") as stream:
        version = json.load(stream)["version"] + 1
    if version <= 13:
        raise ValueError("Reference relayout requires a post-v0013 parent")
    if (PATCH_DIR / f"v{version:04d}.json").exists():
        raise FileExistsError("Next patch already exists")
    return version


def build_patch(version):
    """Return a deterministic patch from read-only inputs; never write outputs."""
    if type(version) is not int or version < 2:
        raise ValueError("Patch version must be an integer of at least 2")
    with open(LATEST, encoding="utf-8") as f:
        latest = json.load(f)
    if version != 12 and latest["version"] != version - 1:
        raise ValueError(
            f"Patch version {version} requires parent {version - 1}; "
            f"latest is {latest['version']}"
        )
    catalog = load_catalog()
    blocks, _ = resolve_entries(catalog, layout_entries())
    hosts = {block["instance_id"] for block in blocks}
    for block in blocks:
        if block.get("mount_on") and block["mount_on"] not in hosts:
            raise ValueError(f"Mount host missing for {block['instance_id']}")
    if version != 12:
        blocks = canonical_blocks(catalog, blocks)
    if version > 13:
        blocks = reference_relayout_blocks(catalog)
    manifest = patch_manifest(catalog, blocks, latest)
    if version != 12:
        assets = {asset["id"]: asset for asset in catalog["assets"]}

        def canonical_ids(value):
            if isinstance(value, list):
                return [canonical_ids(item) for item in value]
            if isinstance(value, dict):
                return {key: canonical_ids(item) for key, item in value.items()}
            if isinstance(value, str) and value in assets:
                return canonical_asset_id(value, assets)
            return value

        manifest = canonical_ids(manifest)
        legacy_ids = legacy_catalog_ids()

        def runtime_ids(value):
            if isinstance(value, list):
                return [runtime_ids(item) for item in value]
            if isinstance(value, dict):
                return {key: runtime_ids(item) for key, item in value.items()}
            if isinstance(value, str):
                return legacy_form(value, legacy_ids)
            return value

        # Maps are resolved by the legacy asset index at runtime, which does not
        # know v2-only keys such as F01@south.
        manifest["changes"] = runtime_ids(manifest["changes"])
        for change in manifest["changes"]:
            if change["op"] == "set_property":
                if change["key"] == "description":
                    change["value"] = (
                        f"Hero's Seaside Sanctuary - reference reconstruction "
                        f"v{version:04d}. Approved environment assets; "
                        "visual approval pending."
                    )
                elif change["key"] == "visual_qa":
                    change["value"] = {
                        "status": "needs_review",
                        "notes": (
                            f"Native render v{version:04d} pending; compare "
                            f"against reference and v{version - 1:04d}."
                        ),
                    }
        manifest["note"] = (
            f"hero_room_01 reference reconstruction v{version:04d}: "
            f"replace v{version - 1:04d} layout using approved v2 assets; "
            "PNG bytes unchanged. Visual approval pending."
        )
    if version > 13:
        # Historical source metadata does not identify the new owner target.
        manifest.pop("source_image", None)
        manifest["changes"] = [
            change for change in manifest["changes"]
            if change.get("key") not in ("source_image", "composition_reference")
        ]
        for change in manifest["changes"]:
            if change.get("key") == "visual_qa":
                change["value"].update({
                    "visual_approval": False,
                    "target_dimensions": [1536, 1024],
                    "target_sha256": (
                        "47a7855cf242302108e1a6b9eaf4bfd3422f9f8c812585fa4"
                        "da5bcaea948668b"
                    ),
                    "limitations": [
                        "Target intake and machine contract require operator verification.",
                        "Square floor tiles cannot reproduce oblique perspective.",
                        "Compact rugs and low shelves differ from the target.",
                        "Directional side-wall banners require an art audit.",
                        "Arch aperture and coastal foam require rendered comparison.",
                    ],
                })
    return manifest


def write_patch(catalog, blocks, version=12):
    """Write only the requested patch; preserve the default legacy behaviour."""
    if version == 12:
        with open(LATEST, encoding="utf-8") as f:
            manifest = patch_manifest(catalog, blocks, json.load(f))
    else:
        manifest = build_patch(version)
    destination = PATCH_DIR / f"v{version:04d}.json"
    PATCH_DIR.mkdir(parents=True, exist_ok=True)
    with open(destination, "w" if version == 12 else "x",
              encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"wrote patch: {destination} ({len(manifest['changes'])} changes)")
    return manifest


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build the hero room patch.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--patch-version", type=int, default=12)
    mode.add_argument("--reference-relayout", action="store_true")
    args = parser.parse_args(argv)
    if args.reference_relayout:
        args.patch_version = next_reference_version()
    if args.patch_version < 2:
        parser.error("--patch-version must be at least 2")
    if args.patch_version != 12:
        manifest = build_patch(args.patch_version)
        destination = PATCH_DIR / f"v{args.patch_version:04d}.json"
        PATCH_DIR.mkdir(parents=True, exist_ok=True)
        with open(destination, "x", encoding="utf-8", newline="\n") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print(f"wrote patch: {destination} ({len(manifest['changes'])} changes)")
        return
    catalog = load_catalog()
    entries = layout_entries()
    blocks, computed = resolve_entries(catalog, entries)
    hosts = {b["instance_id"] for b in blocks}
    for b in blocks:
        if b.get("mount_on") and b["mount_on"] not in hosts:
            raise SystemExit(f"mount host missing: {b['mount_on']} for {b['instance_id']}")
    write_blueprint(catalog, entries, computed)
    write_patch(catalog, blocks)


if __name__ == "__main__":
    main()
