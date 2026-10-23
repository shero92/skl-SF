"""Five-pass, environment-only room block compiler.
Shadows are the fifth DATA pass; they draw between ground and walls at z20.
"""
from __future__ import annotations
from copy import deepcopy

PASS_NAMES=("background","ground","walls","decorations","shadows")
SOURCE_LAYERS=("background_objects","ground_overlays","back_objects","objects","front_objects")
WALL_CATEGORIES=frozenset(("walls","architecture","stairs"))
DECOR_CATEGORIES=frozenset(("furniture","objects","vegetation","decor"))
SHADOW_FILES={
 "contact":"S002","contact_small":"S001","contact_medium":"S002",
 "contact_large":"S003","bed":"S005","table":"S006","chair":"S007",
 "bookshelf":"S008","chest":"S009","plant":"S010",
 "column_short":"S011","column_long":"S012","wall_base":"S013",
 "wall_corner":"S014","stairs":"S015","soft_cast":"S016"}
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
            entry={
                "instance_id":ident,"asset_id":block["id"],"source_layer":source,
                "render_layer":classify(block,record,source),
                "position":[float(block["x"]),float(block["y"])],
                "scale":float(block.get("scale",1.0)),
                "rotation_degrees":float(block.get("rotation_degrees",0)),
                "flip_h":bool(block.get("flip_h",False)),
                "z_index":int(block.get("z_index",0)),
                "texture_path":record["texture_path"],
                "pixel_size":record["pixel_size"],"origin":record.get("origin",[0,0]),
                "status":record.get("status","planned"),
                "collision":deepcopy(block.get("collision",record.get("collision",{}))),
                "shadow":deepcopy(block.get("shadow",record.get("shadow",{"type":"none"}))),
                "attachment":None}
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
            pos=[parent[0]+float(offset[0]),parent[1]+float(offset[1])]
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
    return {"schema_version":1,"map_id":snapshot["map_id"],
      "version":snapshot["version"],
      "processing_passes":list(PASS_NAMES),
      "display_z":DISPLAY_DEPTH,
      "passes":passes,
      "ground":{
        "tile_size":snapshot["tile_size"],"size":snapshot["size"],
        "origin":snapshot["ground_offset"],
        "floor_pattern_ids":snapshot.get("floor_ids",[]),
        "overrides":deepcopy(snapshot.get("tile_overrides",[]))},
      "counts":{k:len(v) for k,v in passes.items()},
      "unique_asset_ids":sorted(used),
      "lighting_effects":deepcopy(snapshot.get("effects",[])),
      "quality_status":"needs_review",
      "note":"Shadows are last DATA pass, rendered z20 below walls z30 and props z40."}

def validate_layer_stack(snapshot,catalog):
    current=snapshot.get("layer_stack")
    if current is None:return True
    if current!=create_layer_stack(snapshot,catalog):
        raise ValueError("layer_stack differs from actual source blocks")
    return True
