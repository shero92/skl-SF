"""Five-pass, environment-only room block compiler.
Shadows are the fifth DATA pass; they draw between ground and walls at z20.
"""
from __future__ import annotations
from copy import deepcopy
from math import isfinite
from map_factory_orientation import resolve_orientation, rotate_offset
from map_factory_placement import resolved_cells

PASS_NAMES=("background","ground","walls","decorations","shadows")
SOURCE_LAYERS=("background_objects","ground_overlays","back_objects","objects","front_objects")
WALL_CATEGORIES=frozenset(("walls","architecture","stairs"))
DECOR_CATEGORIES=frozenset(("furniture","objects","vegetation","decor"))
SHADOW_FILES={
 "contact":"S002","contact_small":"S001","contact_medium":"S002",
 "contact_large":"S003","bed":"S005","table":"S006","chair":"S007",
 "bookshelf":"S008","chest":"S009","plant":"S010",
 "column_short":"S011","column_long":"S012","wall_base":"S013",
 "wall_corner":"S014","stairs":"S015","soft_cast":"S016","directional_sun":"S017"}
DISPLAY_DEPTH={"background":0,"ground":10,"shadows":20,"walls":30,"decorations":40}

def classify(part,record,source):
    explicit=part.get("render_layer")
    if explicit is not None:
        if explicit not in PASS_NAMES[:-1]:
            raise ValueError("Unknown render_layer: "+str(explicit))
        if explicit=="ground" and record["category"] not in ("floors","furniture","decor","objects"):
            raise ValueError("Ground overlay must be floor/decal prop")
        return explicit
    if source=="background_objects":return "background"
    if source=="ground_overlays":return "ground"
    category=record["category"]
    if category in WALL_CATEGORIES:return "walls"
    if category in DECOR_CATEGORIES:return "decorations"
    if category=="environment":return "background"
    raise ValueError("Unexpected map category: "+str(category))

def create_layer_stack(snapshot,catalog):
    placed={}; raw=[]
    for source in SOURCE_LAYERS:
        for block in snapshot.get(source,[]):
            record=catalog[block["id"]];ident=block["instance_id"]
            if ident in placed:raise ValueError("Duplicate rendered block "+ident)
            orientation=resolve_orientation(block,catalog)
            resolved=catalog[orientation["resolved_asset_id"]] if orientation else record
            entry={
                "instance_id":ident,"asset_id":block["id"],"source_layer":source,
                "render_layer":classify(block,record,source),
                "position":[float(block["x"]),float(block["y"])],
                "scale":float(block.get("scale",1.0)),
                "rotation_degrees":float(block.get("rotation_degrees",0)),
                "flip_h":bool(block.get("flip_h",False)),
                "z_index":int(block.get("z_index",0)),
                "texture_path":resolved["texture_path"],
                "pixel_size":resolved.get("pixel_size",[64,64]),"origin":resolved.get("origin",[0,0]),
                "status":record.get("status","planned"),
                "collision":deepcopy(block.get("collision",resolved.get("collision",{}))),
                "shadow":deepcopy(block.get("shadow",resolved.get("shadow",{"type":"none"}))),
                "attachment":None,**({"orientation":orientation} if orientation else {}),
                **({"grid_placement":deepcopy(block["grid_placement"]),
                    "placement_contract":deepcopy(record["placement_contract"]),
                    "occupied_floor_cells":[list(x) for x in resolved_cells(
                       record["placement_contract"],*block["grid_placement"]["cell"],
                       block["grid_placement"].get("facing","north"))]}
                   if "grid_placement" in block else {})}
            # Runtime layer 0 must receive the validated motion contract. Copies
            # keep compiled snapshots independent of mutable source metadata.
            for field in ("animation", "scroll"):
                if field in block:
                    entry[field] = deepcopy(block[field])
            placed[ident]=entry;raw.append((block,entry))
    resolved={}
    def resolve(ident,trail=()):
        if ident in resolved:return resolved[ident]
        if ident in trail:raise ValueError("Cyclic mount: "+" -> ".join(trail+(ident,)))
        entry=placed[ident]
        block=next(b for b,e in raw if e["instance_id"]==ident)
        host=block.get("mount_on")
        if host:
            if host not in placed:raise ValueError("Mount target not found: "+str(host))
            if entry["render_layer"]!="decorations":
                raise ValueError("Only decorative parts may mount on another block")
            offset=block.get("mount_offset")
            if (not isinstance(offset,list) or len(offset)!=2 or
                any(not isinstance(n,(int,float)) or isinstance(n,bool) for n in offset)):
                raise ValueError("Mounted part requires numeric mount_offset")
            parent=resolve(host,trail+(ident,))
            parent_orientation=placed[host].get("orientation")
            local_offset=rotate_offset(offset,parent_orientation["turn_quarters"]) if parent_orientation else [float(offset[0]),float(offset[1])]
            pos=[parent[0]+local_offset[0],parent[1]+local_offset[1]]
            entry["attachment"]={"parent_instance_id":host,
                "host_render_layer":placed[host]["render_layer"],
                "mount_offset":[float(offset[0]),float(offset[1])]}
        else:
            pos=entry["position"]
        resolved[ident]=pos
        return pos
    passes={key:[] for key in PASS_NAMES}
    for block,entry in raw:
        entry["position"]=resolve(entry["instance_id"])
        passes[entry["render_layer"]].append(entry)
    for key in PASS_NAMES[:-1]:
        for entry in passes[key]:
            sh=entry["shadow"];kind=str(sh.get("type","none"))
            if kind=="none":continue
            shadow_id=SHADOW_FILES.get(kind)
            source=catalog.get(shadow_id) if shadow_id else None
            texture=sh.get("texture") or (source or {}).get("texture_path")
            if not texture:raise ValueError("Shadow texture missing for "+kind)
            passes["shadows"].append({
                "instance_id":entry["instance_id"]+"__shadow",
                "owner_instance_id":entry["instance_id"],
                "owner_asset_id":entry["asset_id"],
                "asset_id":shadow_id,
                "texture_path":texture,
                "position":entry["position"],"scale":entry["scale"],
                "sprite_pixel_size":entry["pixel_size"],
                "settings":deepcopy(sh),"render_layer":"shadows",
                "display_z":DISPLAY_DEPTH["shadows"]})
    used=set(snapshot.get("floor_ids",[]))
    used.update(x["id"] for x in snapshot.get("tile_overrides",[]))
    for entries in passes.values():
        used.update(x["asset_id"] for x in entries if x.get("asset_id"))
        used.update(x["orientation"]["resolved_asset_id"] for x in entries if x.get("orientation"))
    return {"schema_version":1,"map_id":snapshot["map_id"],
      "version":snapshot["version"],
      "processing_passes":list(PASS_NAMES),
      **({"occlusion_mode":snapshot["occlusion_mode"]} if "occlusion_mode" in snapshot else {}),
      "display_z":DISPLAY_DEPTH,
      "passes":passes,
      "ground":{
        "tile_size":snapshot["tile_size"],"size":snapshot["size"],
        "origin":snapshot["ground_offset"],
        "floor_pattern_ids":snapshot.get("floor_ids",[]),
        **({"floor_tile_style":deepcopy(snapshot["floor_tile_style"])} if "floor_tile_style" in snapshot else {}),
        "overrides":deepcopy(snapshot.get("tile_overrides",[])),
        **({"footprint":deepcopy(snapshot["floor_footprint"])} if "floor_footprint" in snapshot else {})
      },
      "counts":{k:len(v) for k,v in passes.items()},
      "unique_asset_ids":sorted(used),
      "lighting_effects":deepcopy(snapshot.get("effects",[])),
      "quality_status":"needs_review",
      "note":"Shadows are last DATA pass, rendered z20 below walls z30 and props z40."}

VERIFY_LEVELS = (
    "background", "ground", "walls", "furniture_decor", "shadows_overlays"
)
VERIFY_ALIASES = {
    "decorations": "furniture_decor",
    "shadows": "shadows_overlays",
}


def verify_layers(map_json, v2):
    """Return an independent validation report without modifying either input.

    Anchors use pixel coordinates. Scale exceptions must be declared by the
    registry's allowed_scales list. Legacy compiled pass names are accepted,
    but their display depths must still follow the five-level rule.
    """
    violations = []
    counts = {"objects": 0, **dict.fromkeys(VERIFY_LEVELS, 0)}

    def fail(code, ident, message):
        violations.append({"code": code, "instance_id": ident, "message": message})

    def number(value):
        return (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and isfinite(value)
        )

    def pair(value):
        if isinstance(value, dict):
            value = [value.get("x"), value.get("y")]
        if (isinstance(value, (list, tuple)) and len(value) == 2
                and all(number(item) for item in value)):
            return list(value)
        return None

    records = v2.get("assets", v2)
    if isinstance(records, list):
        records = {
            record.get("id", record.get("asset_id")): record
            for record in records if isinstance(record, dict)
        }
    if not isinstance(records, dict):
        raise ValueError("Registry must contain keyed records or an assets list")

    stack = map_json.get("layer_stack", map_json)
    groups = []
    depths = {}
    if isinstance(stack, dict) and isinstance(stack.get("passes"), dict):
        depths = stack.get("display_z", {})
        groups = list(stack["passes"].items())
    elif isinstance(stack, list):
        for entry in stack:
            if not isinstance(entry, dict):
                fail("layer", None, "Layer stack entry must be an object")
                continue
            children = entry.get("objects", entry.get("entries"))
            if children is not None:
                layer = entry.get("render_layer", entry.get("name", entry.get("layer")))
                groups.append((layer, children))
                if "z_index" in entry:
                    depths[layer] = entry["z_index"]
            else:
                groups.append((None, [entry]))
    elif isinstance(stack, dict) and isinstance(stack.get("objects"), list):
        groups = [(None, stack["objects"])]
    else:
        # Source maps can be checked without compiling or changing a snapshot.
        for source, layer in zip(
            SOURCE_LAYERS,
            ("background", "ground", "walls", "furniture_decor", "shadows_overlays"),
        ):
            if source in map_json:
                groups.append((layer, map_json[source]))
        if not groups:
            fail("layer", None, "No object collection found")

    previous_rank = -1
    previous_y = {}
    layer_depths = {}
    for group_layer, objects in groups:
        if not isinstance(objects, list):
            fail("layer", None, "Layer objects must be a list")
            continue
        for obj in objects:
            counts["objects"] += 1
            if not isinstance(obj, dict):
                fail("layer", None, "Placed object must be an object")
                continue
            ident = obj.get("instance_id", obj.get("id"))
            raw_layer = obj.get("render_layer", obj.get("layer", group_layer))
            layer = VERIFY_ALIASES.get(raw_layer, raw_layer)
            group = VERIFY_ALIASES.get(group_layer, group_layer)
            if layer not in VERIFY_LEVELS:
                fail("layer", ident, "Unknown render layer: " + str(raw_layer))
            else:
                counts[layer] += 1
                if group is not None and layer != group:
                    fail("layer", ident, "Object does not belong to its containing layer")
                rank = VERIFY_LEVELS.index(layer)
                if rank < previous_rank:
                    fail("layer_order", ident, "Layers are not in five-level order")
                previous_rank = max(previous_rank, rank)
                position = pair(obj.get("position"))
                base_y = obj.get("base_y", position[1] if position else obj.get("y"))
                if not number(base_y):
                    fail("y_sort", ident, "Missing or invalid base y")
                else:
                    if layer in previous_y and base_y < previous_y[layer]:
                        fail("y_sort", ident, "Objects must be ordered by base y")
                    previous_y[layer] = base_y
                depth = obj.get("display_z", depths.get(raw_layer))
                if depth is not None:
                    if not number(depth):
                        fail("z_order", ident, "Display depth must be finite")
                    else:
                        layer_depths.setdefault(layer, []).append(depth)

            orientation = obj.get("orientation") or {}
            asset_id = orientation.get(
                "resolved_asset_id", obj.get("asset_id", obj.get("id"))
            )
            record = records.get(asset_id)
            if not isinstance(record, dict):
                fail("registry", ident, "Asset has no registry record")
                continue
            expected = pair(record.get("render_pivot_px"))
            anchor = pair(obj.get("anchor_px", obj.get("anchor", obj.get("origin"))))
            if expected is None or anchor != expected:
                fail("anchor", ident, "Anchor must match registered render_pivot_px")

            scale = obj.get("scale", 1.0)
            scale_pair = [scale, scale] if number(scale) else pair(scale)
            allowed = [[1.0, 1.0]]
            declarations = record.get("allowed_scales", [])
            if isinstance(declarations, list):
                for declared in declarations:
                    candidate = [declared, declared] if number(declared) else pair(declared)
                    if candidate is not None:
                        allowed.append(candidate)
            if (scale_pair is None or any(value <= 0 for value in scale_pair)
                    or scale_pair not in allowed):
                fail("scale", ident, "Scale must be 1.0 or registered in allowed_scales")

    for lower_index, lower in enumerate(VERIFY_LEVELS):
        for upper in VERIFY_LEVELS[lower_index + 1:]:
            if (lower in layer_depths and upper in layer_depths
                    and max(layer_depths[lower]) >= min(layer_depths[upper])):
                fail("z_order", None, lower + " must draw below " + upper)

    counts["violations"] = len(violations)
    return {"ok": not violations, "counts": counts, "violations": violations}


def validate_layer_stack(snapshot,catalog):
    current=snapshot.get("layer_stack")
    if current is None:return True
    if current!=create_layer_stack(snapshot,catalog):
        raise ValueError("layer_stack differs from actual source blocks")
    return True
