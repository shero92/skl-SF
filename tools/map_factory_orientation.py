"""Four cardinal facings for independent environmental blocks.

Raw 90-degree rotations are suitable for flat tiles/flat props; directional
art variants are required for perspective-aware furniture and architecture.
Existing un-oriented maps compile byte-for-byte compatible layer records.
"""
from __future__ import annotations
import math
FACINGS=("north","east","south","west")
MODES=("rotate","variants")

def canonical_asset_id(asset_id, catalog):
    """Resolve a legacy alias while retaining direct catalog compatibility."""
    matches = []
    for key, candidate in catalog.items():
        aliases = candidate.get("legacy_aliases", ())
        if isinstance(aliases, str):
            aliases = (aliases,)
        if asset_id in aliases:
            matches.append(key)
    if len(matches) > 1:
        raise ValueError("Ambiguous asset alias: " + asset_id)
    if matches:
        return matches[0]
    if asset_id in catalog:
        return asset_id
    raise ValueError("Missing registered asset: " + str(asset_id))


def furniture_direction_ids(asset_id, catalog):
    """Find canonical art for all four facings, including the legacy bed."""
    base_id = asset_id.split("@", 1)[0]
    bed_ids = dict(zip(FACINGS, ("F03", "F04", "F01", "F02")))
    source = catalog[canonical_asset_id(asset_id, catalog)]
    existing = source.get("direction_asset_ids", {})
    variants = {}
    for facing in FACINGS:
        legacy_id = (
            bed_ids[facing] if base_id in bed_ids.values()
            else base_id + "_" + facing
        )
        try:
            variants[facing] = canonical_asset_id(legacy_id, catalog)
        except ValueError:
            candidate = existing.get(facing)
            if not candidate:
                raise ValueError("Missing directional art for " + facing) from None
            variants[facing] = canonical_asset_id(candidate, catalog)
    return variants


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
    source_id=canonical_asset_id(block["id"],catalog)
    source=catalog[source_id]
    result={"facing":facing,"orientation_mode":mode,
            "turn_quarters":FACINGS.index(facing),
            "resolved_asset_id":source_id}
    if mode=="variants":
        variants=block.get("direction_asset_ids",
                           source.get("direction_asset_ids"))
        if not isinstance(variants,dict) or set(variants)!=set(FACINGS):
            raise ValueError("Perspective variants require four direction_asset_ids")
        resolved_variants = {}
        for cardinal,asset_id in variants.items():
            if not isinstance(asset_id,str):
                raise ValueError("Missing directional art for "+cardinal)
            try:
                resolved_variants[cardinal] = canonical_asset_id(asset_id,catalog)
            except ValueError:
                raise ValueError("Missing directional art for "+cardinal) from None
        variants = resolved_variants
        if len(set(variants.values())) != 4:
            raise ValueError("Four perspective directions require four distinct art assets")
        for cardinal,asset_id in variants.items():
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
