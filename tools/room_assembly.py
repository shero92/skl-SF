"""Shared assembly helpers: expand architecture blueprints and furniture composites
into explicit objects. Used by BOTH the exact reference reconstruction and the
procedural generator, so both rely on the same corrected registry (v2)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
T = 64


def load_registry():
    return json.loads((ROOT / "map_factory/metadata/environment_assets_v2.json").read_text(encoding="utf-8"))["assets"]


def load_blueprints():
    return json.loads((ROOT / "map_factory/blueprints/architecture_blueprints.json").read_text(encoding="utf-8"))["blueprints"]


def load_composites():
    return json.loads((ROOT / "map_factory/blueprints/furniture_composites.json").read_text(encoding="utf-8"))["composites"]


def key_of(asset, facing=None):
    return asset if not facing else f"{asset}@{facing}"


def make_object(reg, object_id, asset, facing=None, *, ground_anchor_px=None, cell=None, offset=(0, 0),
                level=None, bias=0, parent=None, attach_point=None, attach_offset=(0, 0), blueprint=None, collision=True):
    """Build an explicit layout object. Either `cell` (footprint top-left) or an absolute
    `ground_anchor_px` (converted to the nearest cell + sub-cell offset) is given."""
    key = key_of(asset, facing)
    r = reg[key]
    fw, fd = r["logical_footprint"]
    ax, ay = r["ground_anchor_px"]
    if ground_anchor_px is not None:
        gx = round((ground_anchor_px[0] - ax) / T)
        gy = round((ground_anchor_px[1] - ay) / T)
        offset = (round(ground_anchor_px[0] - (gx * T + ax)), round(ground_anchor_px[1] - (gy * T + ay)))
    else:
        gx, gy = cell
    return {
        "object_id": object_id,
        "asset_id": key,
        "grid_x": gx,
        "grid_y": gy,
        "facing": facing or r["facing_direction"],
        "ground_footprint": [fw, fd],
        "anchor_offset": [offset[0], offset[1]],
        "logical_level": level if level is not None else r["logical_level"],
        "render_order": bias,
        "parent": parent,
        "attach_point": attach_point,
        "attach_offset": list(attach_offset),
        "blueprint": blueprint,
        **({} if collision else {"collision_override": "none"}),
    }


def expand_blueprint(reg, bps, name, prefix, *, anchor_px=None, anchor_cell=None, overrides=None):
    bp = bps[name]
    out = []
    for comp in bp["components"]:
        cid = f"{prefix}.{comp['id']}"
        facing = comp.get("facing")
        bias = comp.get("bias", 0)
        if bp["kind"] == "px":
            ap = (anchor_px[0] + comp["dx"], anchor_px[1] + comp["dy"])
            out.append(make_object(reg, cid, comp["asset"], facing, ground_anchor_px=ap, bias=bias, blueprint=name, collision=comp.get("collision", True)))
        else:
            cell = (anchor_cell[0] + comp["cell"][0], anchor_cell[1] + comp["cell"][1])
            out.append(make_object(reg, cid, comp["asset"], facing, cell=cell, offset=tuple(comp.get("offset", (0, 0))), bias=bias, blueprint=name, collision=comp.get("collision", True)))
    return out


def expand_composite(reg, comps, name, prefix, origin_cell, offsets=None):
    """origin_cell = footprint top-left of the main piece. `offsets` maps part id -> (dx,dy) px nudges."""
    offsets = offsets or {}
    cp = comps[name]
    out = []
    for part in cp["parts"]:
        pid = f"{prefix}.{part['id']}"
        off = offsets.get(part["id"], (0, 0))
        facing = part.get("facing")
        if "centre_cell" in part:
            r = reg[key_of(part["asset"], facing)]
            fw, fd = r["logical_footprint"]
            ax = (origin_cell[0] + part["centre_cell"][0]) * T
            ay = (origin_cell[1] + part["centre_cell"][1]) * T
            out.append(make_object(reg, pid, part["asset"], facing, ground_anchor_px=(ax + off[0], ay + off[1]),
                                   level=part.get("logical_level"), blueprint=name))
        else:
            cell = (origin_cell[0] + part["cell"][0], origin_cell[1] + part["cell"][1])
            out.append(make_object(reg, pid, part["asset"], facing, cell=cell, offset=off,
                                   level=part.get("logical_level"), blueprint=name))
    for prop in cp.get("props", []):
        out.append(make_object(reg, f"{prefix}.{prop['id']}", prop["asset"], None, cell=(0, 0), level=3,
                               parent=f"{prefix}.{prop['parent']}", attach_point=prop["point"],
                               attach_offset=tuple(prop.get("offset", (0, 0))), blueprint=name))
    return out
