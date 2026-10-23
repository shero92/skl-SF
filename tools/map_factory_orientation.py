"""Four cardinal facings for independent environmental blocks.

Raw 90-degree rotations are suitable for flat tiles/flat props; directional
art variants are required for perspective-aware furniture and architecture.
Existing un-oriented maps compile byte-for-byte compatible layer records.
"""
from __future__ import annotations
import math
FACINGS=("north","east","south","west")
MODES=("rotate","variants")

def resolve_orientation(block,catalog):
    if not any(k in block for k in ("facing","orientation_mode","direction_asset_ids")):
        return None
    if "facing" not in block:
        raise ValueError("Oriented block requires facing")
    facing=block["facing"]
    if not isinstance(facing,str) or facing not in FACINGS:
        raise ValueError("facing must be north/east/south/west")
    mode=block.get("orientation_mode","rotate")
    if mode not in MODES:
        raise ValueError("orientation_mode must be rotate or variants")
    old_rot=block.get("rotation_degrees",0)
    if not isinstance(old_rot,(int,float)) or isinstance(old_rot,bool) or not math.isfinite(old_rot) or old_rot!=0:
        raise ValueError("facing cannot be combined with nonzero rotation_degrees")
    source=catalog[block["id"]]
    result={"facing":facing,"orientation_mode":mode,
            "turn_quarters":FACINGS.index(facing),
            "resolved_asset_id":block["id"]}
    if mode=="variants":
        variants=block.get("direction_asset_ids",
                           source.get("direction_asset_ids"))
        if not isinstance(variants,dict) or set(variants)!=set(FACINGS):
            raise ValueError("Perspective variants require four direction_asset_ids")
        if len(set(variants.values())) != 4:
            raise ValueError("Four perspective directions require four distinct art assets")
        for cardinal,asset_id in variants.items():
            if not isinstance(asset_id,str) or asset_id not in catalog:
                raise ValueError("Missing directional art for "+cardinal)
            candidate=catalog[asset_id]
            if candidate["category"]!=source["category"] or candidate["category"] in ("characters","ui","shadows"):
                raise ValueError("Directional asset must remain in same environmental category")
        result["resolved_asset_id"]=variants[facing]
        result["direction_asset_ids"]={d:variants[d] for d in FACINGS}
    elif "direction_asset_ids" in block:
        raise ValueError("direction_asset_ids requires orientation_mode=variants")
    return result

def rotate_offset(point,quarters):
    x,y=point
    if quarters%4==1:return [-float(y),float(x)]
    if quarters%4==2:return [-float(x),-float(y)]
    if quarters%4==3:return [float(y),-float(x)]
    return [float(x),float(y)]
