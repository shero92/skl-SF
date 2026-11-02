#!/usr/bin/env python3
"""A. REFERENCE ROOM RECONSTRUCTION -> map_factory/rooms/reference_room_layout.json

Explicit coordinates estimated from the reference image on ONE grid: 64px cells,
canvas 20x13 cells (1280x832), origin top-left. Reference px -> cells: x/56.2, y/56.2
(reference image 1125x750 scaled x1.138 to the canvas). Major architecture and
furniture are explicit; only floor variation uses a deterministic seed.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from room_assembly import (T, ROOT, expand_blueprint, expand_composite, load_blueprints,  # noqa: E402
                           load_composites, load_registry, make_object)

reg, bps, comps = load_registry(), load_blueprints(), load_composites()
objs = []


def add(items):
    objs.extend(items if isinstance(items, list) else [items])


# ------------------------------------------------------------ level 2: architecture (explicit anchors)
add(expand_blueprint(reg, bps, "rear_wall_left", "rwl", anchor_cell=(2, 3)))
add(expand_blueprint(reg, bps, "rear_wall_right", "rwr", anchor_cell=(12, 3)))
add(expand_blueprint(reg, bps, "central_arch", "arch", anchor_px=(10 * T, 5 * T)))
add(expand_blueprint(reg, bps, "side_wall_left", "swl", anchor_cell=(2, 4)))
add(expand_blueprint(reg, bps, "side_wall_right", "swr", anchor_cell=(17, 4)))
add(expand_blueprint(reg, bps, "front_wall_left", "fwl", anchor_cell=(2, 10)))
add(expand_blueprint(reg, bps, "front_wall_right", "fwr", anchor_cell=(12, 10)))
add(expand_blueprint(reg, bps, "entrance_stairs", "stairs", anchor_px=(10 * T, 11 * T)))

# ------------------------------------------------------------ level 1/2/3: furniture composites
add(expand_composite(reg, comps, "bookcase_left_area", "bcl", (3, 4)))
add(expand_composite(reg, comps, "bed_area", "bed", (5, 5)))
add(expand_composite(reg, comps, "bookcase_right_area", "bcr", (13, 4)))
add(expand_composite(reg, comps, "table_area", "tbl", (12, 6), offsets={"bench_left": (12, 0)}))
add(make_object(reg, "compass", "D03", ground_anchor_px=(9.75 * T, 8.1 * T), level=1))

# ------------------------------------------------------------ level 3: attached decoration (wall faces, arch, door)
def deco(oid, asset, parent, point, off=(0, 0)):
    add(make_object(reg, oid, asset, None, cell=(0, 0), level=3, parent=parent, attach_point=point, attach_offset=off))


deco("banner_left_a", "D04", "swl.w2", "banner_hang")
deco("banner_left_b", "D04", "swl.w5", "banner_hang")
deco("banner_right_a", "D04", "swr.w4", "banner_hang")
deco("banner_right_b", "D04", "swr.w0", "banner_hang")
deco("lantern_rear_left_a", "L02", "rwl.w2", "lantern_hang")
deco("lantern_rear_left_b", "L02", "rwl.w4", "lantern_hang")
deco("lantern_rear_right", "L02", "rwr.w4", "lantern_hang")
deco("lantern_door", "L01", "rwr.door", "lantern_hang_left")
deco("lantern_left", "L01", "swl.w1", "lantern_hang")
deco("lantern_right", "L01", "swr.w2", "lantern_hang")
for lid in ("lantern_rear_left_a", "lantern_rear_left_b", "lantern_rear_right"):
    deco("flame_" + lid, "L05", lid, "flame_base")
deco("ivy_arch_left", "P03", "arch.arch", "arch_drape_left")
deco("ivy_arch_right", "P03", "arch.arch", "arch_drape_right")
deco("flowers_arch_top", "P05", "arch.arch", "top_center")
deco("ivy_rear_left_a", "P02", "rwl.w1", "ivy_hang")
deco("ivy_rear_left_b", "P01", "rwl.w4", "ivy_hang")
deco("ivy_door", "P03", "rwr.door", "ivy_hang_right")
deco("ivy_rear_right", "P02", "rwr.w4", "ivy_hang")
deco("growth_left", "P12", "swl.w3", "ivy_hang")
deco("growth_right", "P13", "swr.w3", "ivy_hang")
deco("flowers_rwl_up", "P04", "rwl.up2", "wall_top_stand")
deco("flowers_rwr_up", "P05", "rwr.up2", "wall_top_stand")
deco("flowers_rwl_1", "P06", "rwl.up1", "wall_top_stand")
for oid, a, par in [("fl_fwl_1", "P05", "fwl.w2"), ("bush_fwl_2", "P08", "fwl.w4"), ("fl_fwl_3", "P06", "fwl.w1"),
                    ("bush_fwl_4", "P07", "fwl.w5"), ("fl_fwr_1", "P05", "fwr.w3"), ("bush_fwr_2", "P08", "fwr.w1"),
                    ("fl_fwr_3", "P06", "fwr.w4"), ("bush_fwr_4", "P07", "fwr.w0"), ("leaf_fwl", "P10", "fwl.w3"),
                    ("leaf_fwr", "P09", "fwr.w2")]:
    deco(oid, a, par, "wall_top_stand")

# ------------------------------------------------------------ level 3: floor-standing decoration (explicit cells)
for oid, a, cell in [("vase_left", "R02", (3, 5)), ("vase_right", "R02", (12, 5)), ("plant_right", "P11", (16, 5)),
                     ("crate", None, (16, 9)), ("conch_floor", "R13", (14, 9)), ("pot_floor", "R04", (15, 9)),
                     ("flowers_floor_l", "P14", (3, 9)), ("flowers_floor_r", "P14", (15, 4))]:
    if a is None:
        add(make_object(reg, oid, "F11", "south", cell=cell, level=2))
    else:
        add(make_object(reg, oid, a, None, cell=cell, level=3))

layout = {
    "schema": "skl.reference_room_layout.v1",
    "map_id": "reference_room_01",
    "title": "Original hero room - exact reference reconstruction",
    "grid": {"tile_size": T, "canvas_cells": [20, 13], "origin": "top-left", "units": "grid_x/grid_y = footprint top-left cell"},
    "reference_image": "map_factory/references/hero_room_01_original.png",
    "registry": "map_factory/metadata/environment_assets_v2.json",
    "seed": 7,
    "walkable_check": {"entrance_cells": [[9, 10], [10, 10]], "clear_zones": {"compass": [8, 7, 3, 3]}},
    "ground": {
        "floor_rect": [3, 4, 14, 6],
        "extra_floor_cells": [[8, 10], [9, 10], [10, 10], [11, 10], [9, 11], [10, 11], [9, 12], [10, 12]],
        "tiles": ["G01", "G02", "G03", "G04", "G05", "G06", "G07", "G08", "G09", "G10", "G11", "G12"],
        "weights": [4, 3, 1, 3, 2, 1, 2, 2, 1, 2, 1, 1],
    },
    "background": [
        {"asset": "B10", "px": [0, 0], "tile": [5, 4]},
        {"asset": "B07", "px": [0, -64], "tile": [5, 1]},
        {"asset": "B01", "px": [0, 192], "tile": [5, 3]},
        {"asset": "B11", "px": [30, 30]}, {"asset": "B06", "px": [260, 20]}, {"asset": "B05", "px": [900, 30]},
        {"asset": "B06", "px": [1020, 10]}, {"asset": "B04", "px": [520, 10]},
        {"asset": "B08", "px": [150, 0]}, {"asset": "B09", "px": [700, -50]},
        {"asset": "B03", "px": [-120, 220]}, {"asset": "B03", "px": [-120, 420]},
        {"asset": "B03", "px": [1140, 200]}, {"asset": "B03", "px": [1140, 420]},
        {"asset": "B04", "px": [40, 600]}, {"asset": "B03", "px": [260, 640]},
        {"asset": "B04", "px": [480, 700]}, {"asset": "B03", "px": [760, 660]}, {"asset": "B04", "px": [1000, 620]},
        {"asset": "B02", "px": [-30, 700]}, {"asset": "B02", "px": [1050, 700]},
    ],
    "shadows": {
        "contact": {"color": "#1a0f2a", "alpha": 0.30},
        "cast": {"color": "#1a0f2a", "alpha": 0.18, "length_per_height": 0.5, "direction": [0.7, 0.5]},
        "glow_owners": [o["object_id"] for o in objs if o["asset_id"] in ("L01", "L04", "L05") and o["asset_id"] != "L05"]
                       + [o["object_id"] for o in objs if o["asset_id"] == "L03"],
        "sun_bands": [[[400, 300], [480, 300], [700, 700], [610, 700]], [[540, 300], [580, 300], [800, 700], [760, 700]]],
    },
    "objects": objs,
}
out = ROOT / "map_factory/rooms/reference_room_layout.json"
out.write_text(json.dumps(layout, indent=1) + "\n", encoding="utf-8")
print("wrote", out, len(objs), "objects")
