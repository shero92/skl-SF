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

import hashlib
import json
from pathlib import Path

from PIL import Image

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


def load_catalog():
    with open(CATALOG_PATH, encoding="utf-8") as f:
        return json.load(f)


def catalog_lookup(catalog, asset_id):
    for a in catalog["assets"]:
        if a["id"] == asset_id:
            return a
    return None


def sidecar_png(catalog, asset_id):
    record = catalog_lookup(catalog, asset_id)
    if record is None:
        raise KeyError(f"unknown asset id {asset_id}")
    rel = record["texture_path"].replace("res://", "")
    return ROOT / rel


def measure_png(png_path):
    im = Image.open(png_path).convert("RGBA")
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

    return E


# ---------------------------------------------------------------------------
# Resolve entries -> exact block list
# ---------------------------------------------------------------------------


def resolve_entries(catalog, entries):
    computed = {}  # instance_id -> [x, y]

    for e in entries:
        if e["kind"] == "background":
            computed[e["instance_id"]] = [round(e["x"], 3), round(e["y"], 3)]
            continue
        if e["kind"] in ("grid", "overlay"):
            rec = record(catalog, e["id"])
            cfg = rec.get("placement_contract")
            fw, fh = cfg["footprint_cells"]
            if e.get("facing", "north") in ("east", "west"):
                fw, fh = fh, fw
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

    host_pos = dict(computed)
    for e in entries:
        if e["kind"] == "mount":
            hx, hy = host_pos[e["mount_on"]]
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
            if facing != "north":
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
        rec = record(catalog, e["id"])
        m = measurement(catalog, e["id"])
        entry = {"instance_id": iid, "asset_id": e["id"], "category": rec["category"],
                 "kind": e["kind"], "position": [x, y], "scale": entry_scale(catalog, e),
                 "pixel_size": rec["pixel_size"], "content_bbox": m["content"],
                 "layer": e["layer"]}
        if e["kind"] in ("grid", "overlay"):
            entry["grid_placement"] = {"cell": list(e["cell"]),
                                       "facing": e.get("facing", "north")}
            entry["footprint_cells"] = record(catalog, e["id"])[
                "placement_contract"]["footprint_cells"]
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


def write_patch(catalog, blocks):
    with open(LATEST, encoding="utf-8") as f:
        latest = json.load(f)
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
        layer = b.pop("_layer", "objects")
        op_block = {k: v for k, v in b.items()}
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
    PATCH_DIR.mkdir(parents=True, exist_ok=True)
    with open(PATCH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"wrote patch: {PATCH} ({len(changes)} changes; {len(blocks)} blocks added, "
          f"{len(set(v0011_ids))} v0011 blocks removed)")
    return manifest


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
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
