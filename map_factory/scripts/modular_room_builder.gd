extends RefCounted
class_name ModularRoomBuilder

## Builds a room from an explicit object layout (schema skl.reference_room_layout.v1,
## also emitted by the procedural generator) using the corrected registry v2.
## Placement: every object is pinned by its registry render_pivot to its ground
## anchor (footprint cell + anchor offset). Depth: one Y-sorted world keyed on ground
## contact Y (+ render_order bias). Children (props, banners, lanterns) are attached
## to named attachment points of their host and draw directly after it.
## Stages: 1 background+floor, 2 +architecture, 3 +rugs/furniture, 4 +decorations, 5 +shadows/lighting.
const REGISTRY_PATH := "res://map_factory/metadata/environment_assets_v2.json"
const FURNITURE_ROLES := ["bed", "bedside_table", "bookcase", "work_table", "bench_horizontal", "bench_vertical", "crate_small", "crate_medium"]

var registry: Dictionary = {}
var layout: Dictionary = {}
var tile := 64
var canvas_size := Vector2(1280, 832)
var issues: Array[String] = []
var placed: Dictionary = {}          # object_id -> Node2D
var objects_by_id: Dictionary = {}   # object_id -> layout object
var _textures: Dictionary = {}

func _init() -> void:
    var raw: Variant = JSON.parse_string(FileAccess.get_file_as_string(REGISTRY_PATH))
    if typeof(raw) == TYPE_DICTIONARY:
        registry = raw.get("assets", {})
    else:
        push_error("Environment registry v2 missing: " + REGISTRY_PATH)

func build(layout_path: String, parent: Node, stage: int = 5) -> Node2D:
    var root := Node2D.new()
    root.name = "Room"
    parent.add_child(root)
    var raw: Variant = JSON.parse_string(FileAccess.get_file_as_string(layout_path))
    if typeof(raw) != TYPE_DICTIONARY:
        push_error("Room layout malformed: " + layout_path)
        return root
    layout = raw
    var grid: Dictionary = layout.get("grid", {})
    tile = int(grid.get("tile_size", 64))
    var cells: Array = grid.get("canvas_cells", [20, 13])
    canvas_size = Vector2(float(cells[0]), float(cells[1])) * float(tile)

    var backdrop := Polygon2D.new()
    backdrop.name = "Backdrop"
    backdrop.color = Color("#0a7cd0")
    backdrop.polygon = PackedVector2Array([Vector2.ZERO, Vector2(canvas_size.x, 0), canvas_size, Vector2(0, canvas_size.y)])
    root.add_child(backdrop)

    var bg := Node2D.new()
    bg.name = "Level0_Background"
    root.add_child(bg)
    _build_background(layout.get("background", []), bg)

    var ground := Node2D.new()
    ground.name = "Level1_Ground"
    ground.z_index = 10
    root.add_child(ground)
    var floor_tiles := Node2D.new()
    floor_tiles.name = "FloorTiles"
    ground.add_child(floor_tiles)
    _build_floor(layout.get("ground", {}), floor_tiles)
    var overlays := Node2D.new()
    overlays.name = "RugsAndEmblem"
    ground.add_child(overlays)

    var world := Node2D.new()
    world.name = "World_YSort"
    world.y_sort_enabled = true
    world.z_index = 30
    root.add_child(world)

    var all: Array = layout.get("objects", [])
    for o in all:
        objects_by_id[String(o["object_id"])] = o
    # pass 1: top-level objects admitted by stage; pass 2: children whose parent exists
    for o in all:
        if o.get("parent") != null:
            continue
        if not _admitted(o, stage):
            continue
        _place_top_level(o, world, overlays)
    var pending: Array = []
    for o in all:
        if o.get("parent") != null and _admitted(o, stage):
            pending.append(o)
    var progress := true
    while not pending.is_empty() and progress:
        progress = false
        var rest: Array = []
        for o in pending:
            var host: Node2D = placed.get(String(o["parent"]))
            if host == null:
                rest.append(o)
                continue
            _place_child(o, host)
            progress = true
        pending = rest
    for o in pending:
        if _admitted(o, stage) and String(o["parent"]) in objects_by_id and _admitted(objects_by_id[String(o["parent"])], stage):
            issues.append("attachment parent not built for " + String(o["object_id"]))
    if stage >= 2:
        _validate()
    if stage >= 5:
        _build_shadows(layout.get("shadows", {}), root)
    root.set_meta("issues", issues)
    return root

# ------------------------------------------------------------------ stage filter
func _admitted(o: Dictionary, stage: int) -> bool:
    var rec: Dictionary = registry.get(String(o["asset_id"]), {})
    if rec.is_empty():
        return false
    var level := int(o.get("logical_level", rec["logical_level"]))
    var role := String(rec["asset_role"])
    if level == 3:
        return stage >= 4
    if level == 1:
        return stage >= 3
    if level == 2:
        return stage >= 3 if role in FURNITURE_ROLES else stage >= 2
    return stage >= 1

# ------------------------------------------------------------------ helpers
func _rec(key: String) -> Dictionary:
    var rec: Dictionary = registry.get(key, {})
    if rec.is_empty():
        issues.append("unknown asset " + key)
    return rec

func _tex(rec: Dictionary) -> Texture2D:
    var path := String(rec.get("source_texture_path", ""))
    if not _textures.has(path):
        _textures[path] = load(path) as Texture2D
    return _textures[path]

func _vec(a: Array) -> Vector2:
    return Vector2(float(a[0]), float(a[1]))

func _sprite_for(rec: Dictionary) -> Sprite2D:
    var sprite := Sprite2D.new()
    sprite.name = "Visual"
    sprite.centered = false
    sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    sprite.texture = _tex(rec)
    sprite.position = -_vec(rec["render_pivot_px"])
    return sprite

func _node_name(id: String) -> String:
    return id.replace(".", "_")

func ground_anchor(o: Dictionary, rec: Dictionary) -> Vector2:
    var a := _vec(rec["ground_anchor_px"])
    var off := _vec(o.get("anchor_offset", [0, 0]))
    return Vector2(float(o["grid_x"]), float(o["grid_y"])) * float(tile) + a + off

func visual_rect(node: Node2D, rec: Dictionary, root: Node) -> Rect2:
    var b: Array = rec["visual_bounds"]
    var pivot := _vec(rec["render_pivot_px"])
    var origin := _room_pos(node, root)
    return Rect2(origin + Vector2(float(b[0]), float(b[1])) - pivot, Vector2(float(b[2] - b[0]), float(b[3] - b[1])))

func _room_pos(node: Node2D, root: Node) -> Vector2:
    var xf := Transform2D.IDENTITY
    var cur: Node = node
    while cur != null and cur != root:
        if cur is Node2D:
            xf = (cur as Node2D).transform * xf
        cur = cur.get_parent()
    return xf.origin

# ------------------------------------------------------------------ level 0
func _build_background(entries: Array, group: Node2D) -> void:
    for e in entries:
        var rec := _rec(String(e["asset"]))
        if rec.is_empty():
            continue
        var size := _vec(rec["sprite_dimensions"])
        var origin := _vec(e["px"])
        var repeat := Vector2i(1, 1)
        if e.has("tile"):
            repeat = Vector2i(int(e["tile"][0]), int(e["tile"][1]))
        for ty in repeat.y:
            for tx in repeat.x:
                var sprite := Sprite2D.new()
                sprite.centered = false
                sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
                sprite.texture = _tex(rec)
                sprite.position = origin + Vector2(tx, ty) * size
                group.add_child(sprite)

# ------------------------------------------------------------------ level 1 floor
func _build_floor(data: Dictionary, group: Node2D) -> void:
    var ids: Array = data.get("tiles", ["G01"])
    var weights: Array = data.get("weights", [])
    var bag: Array = []
    for i in ids.size():
        for n in int(weights[i]) if i < weights.size() else 1:
            bag.append(ids[i])
    var rng := RandomNumberGenerator.new()
    rng.seed = int(layout.get("seed", 1))
    var cells: Array = []
    var rect: Array = data.get("floor_rect", [0, 0, 0, 0])
    for cy in range(int(rect[1]), int(rect[1]) + int(rect[3])):
        for cx in range(int(rect[0]), int(rect[0]) + int(rect[2])):
            cells.append([cx, cy])
    for c in data.get("extra_floor_cells", []):
        cells.append(c)
    for c in cells:
        var rec := _rec(String(bag[rng.randi() % bag.size()]))
        var sprite := Sprite2D.new()
        sprite.name = "Floor_%d_%d" % [int(c[0]), int(c[1])]
        sprite.centered = false
        sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
        sprite.texture = _tex(rec)
        sprite.position = Vector2(float(c[0]), float(c[1])) * float(tile)
        group.add_child(sprite)

# ------------------------------------------------------------------ objects
func _make_node(o: Dictionary, rec: Dictionary) -> Node2D:
    var node := Node2D.new()
    node.name = _node_name(String(o["object_id"]))
    node.add_child(_sprite_for(rec))
    node.set_meta("object_id", String(o["object_id"]))
    node.set_meta("asset_key", String(o["asset_id"]))
    node.set_meta("role", String(rec["asset_role"]))
    node.set_meta("level", int(o.get("logical_level", rec["logical_level"])))
    return node

func _place_top_level(o: Dictionary, world: Node2D, overlays: Node2D) -> void:
    var rec := _rec(String(o["asset_id"]))
    if rec.is_empty():
        return
    var node := _make_node(o, rec)
    node.position = ground_anchor(o, rec)
    var level := int(o.get("logical_level", rec["logical_level"]))
    if rec["render_pass"] == "ground":
        overlays.add_child(node)
    else:
        node.position.y += 0.01 * float(o.get("render_order", 0))  # tie-break bias for equal ground Y
        var coll: Dictionary = rec["collision_shape"]
        if String(coll.get("type", "none")) == "cells" and String(o.get("collision_override", "")) != "none":
            var body := StaticBody2D.new()
            body.name = "SolidFootprint"
            node.add_child(body)
            var origin_local := Vector2(float(o["grid_x"]), float(o["grid_y"])) * float(tile) - node.position
            for c in coll["cells"]:
                var shape := CollisionShape2D.new()
                var r := RectangleShape2D.new()
                r.size = Vector2(tile, tile)
                shape.shape = r
                shape.position = origin_local + Vector2(float(c[0]) + 0.5, float(c[1]) + 0.5) * float(tile)
                body.add_child(shape)
        world.add_child(node)
    node.set_meta("level", level)
    placed[String(o["object_id"])] = node

func _place_child(o: Dictionary, host: Node2D) -> void:
    var rec := _rec(String(o["asset_id"]))
    var host_rec: Dictionary = registry.get(String(host.get_meta("asset_key")), {})
    if rec.is_empty() or host_rec.is_empty():
        return
    var points: Dictionary = host_rec["attachment_points"]
    var point_name := String(o.get("attach_point", ""))
    if not points.has(point_name):
        issues.append("host %s has no attachment point '%s' (%s)" % [host.get_meta("object_id"), point_name, o["object_id"]])
        return
    var p := _vec(points[point_name]) - _vec(host_rec["render_pivot_px"]) + _vec(o.get("attach_offset", [0, 0]))
    var node := _make_node(o, rec)
    node.position = p
    node.set_meta("attach_parent", String(o["parent"]))
    host.add_child(node)
    placed[String(o["object_id"])] = node

# ------------------------------------------------------------------ validation
func _validate() -> void:
    var occupied: Dictionary = {}
    var furniture: Array = []
    for id in objects_by_id:
        if not placed.has(id):
            continue
        var o: Dictionary = objects_by_id[id]
        if o.get("parent") != null:
            continue
        var rec: Dictionary = registry[String(o["asset_id"])]
        var coll: Dictionary = rec["collision_shape"]
        if String(coll.get("type", "none")) == "cells" and String(o.get("collision_override", "")) != "none":
            for c in coll["cells"]:
                var key := "%d:%d" % [int(o["grid_x"]) + int(c[0]), int(o["grid_y"]) + int(c[1])]
                if occupied.has(key):
                    issues.append("collision footprint overlap %s vs %s at %s" % [id, occupied[key], key])
                else:
                    occupied[key] = id
        if String(rec["asset_role"]) in FURNITURE_ROLES:
            furniture.append(id)
    # furniture visual-bounds overlap (excluding rugs: they are ground overlays)
    for i in furniture.size():
        for j in range(i + 1, furniture.size()):
            var a: Node2D = placed[furniture[i]]
            var b: Node2D = placed[furniture[j]]
            var ra := visual_rect(a, registry[String(a.get_meta("asset_key"))], a.get_parent().get_parent())
            var rb := visual_rect(b, registry[String(b.get_meta("asset_key"))], b.get_parent().get_parent())
            var inter := ra.intersection(rb)
            if inter.size.x > 6.0 and inter.size.y > 6.0:
                issues.append("furniture visual overlap %s / %s (%dx%d px)" % [furniture[i], furniture[j], inter.size.x, inter.size.y])
    # clear zones (compass) and entrance walkability
    var check: Dictionary = layout.get("walkable_check", {})
    for zone_name in check.get("clear_zones", {}):
        var z: Array = check["clear_zones"][zone_name]
        for cy in range(int(z[1]), int(z[1]) + int(z[3])):
            for cx in range(int(z[0]), int(z[0]) + int(z[2])):
                if occupied.has("%d:%d" % [cx, cy]):
                    issues.append("clear zone '%s' blocked by %s" % [zone_name, occupied["%d:%d" % [cx, cy]]])
    var floor_cells: Dictionary = {}
    var data: Dictionary = layout.get("ground", {})
    var rect: Array = data.get("floor_rect", [0, 0, 0, 0])
    for cy in range(int(rect[1]), int(rect[1]) + int(rect[3])):
        for cx in range(int(rect[0]), int(rect[0]) + int(rect[2])):
            floor_cells["%d:%d" % [cx, cy]] = true
    for c in data.get("extra_floor_cells", []):
        floor_cells["%d:%d" % [int(c[0]), int(c[1])]] = true
    var starts: Array = check.get("entrance_cells", [])
    var seen: Dictionary = {}
    var queue: Array = []
    for s in starts:
        var k := "%d:%d" % [int(s[0]), int(s[1])]
        if floor_cells.has(k) and not occupied.has(k):
            queue.append(Vector2i(int(s[0]), int(s[1])))
            seen[k] = true
    while not queue.is_empty():
        var cur: Vector2i = queue.pop_back()
        for d in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
            var n: Vector2i = cur + d
            var nk := "%d:%d" % [n.x, n.y]
            if floor_cells.has(nk) and not occupied.has(nk) and not seen.has(nk):
                seen[nk] = true
                queue.append(n)
    var free := 0
    for k in floor_cells:
        if not occupied.has(k):
            free += 1
    if not starts.is_empty() and seen.size() < free:
        var lost: Array = []
        for k in floor_cells:
            if not occupied.has(k) and not seen.has(k):
                lost.append(k)
        issues.append("walkable area: %d of %d free floor cells reachable (unreachable: %s)" % [seen.size(), free, ", ".join(lost)])
    layout["_report"] = {"free_floor_cells": free, "reachable_from_entrance": seen.size(), "solid_cells": occupied.size()}

# ------------------------------------------------------------------ level 4
func _build_shadows(cfg: Dictionary, root: Node2D) -> void:
    var level := Node2D.new()
    level.name = "Level4_Shadows"
    level.z_index = 20
    root.add_child(level)
    var contact: Dictionary = cfg.get("contact", {})
    var cast: Dictionary = cfg.get("cast", {})
    var contact_color := Color(String(contact.get("color", "#1a0f2a")), float(contact.get("alpha", 0.3)))
    var cast_color := Color(String(cast.get("color", "#1a0f2a")), float(cast.get("alpha", 0.18)))
    var dir := _vec(cast.get("direction", [0.7, 0.5]))
    var per_h := float(cast.get("length_per_height", 0.5))
    for id in placed:
        var o: Dictionary = objects_by_id[id]
        if o.get("parent") != null:
            continue
        var rec: Dictionary = registry[String(o["asset_id"])]
        if not bool(rec.get("shadow_caster", false)):
            continue
        var fp := _vec(rec["logical_footprint"]) * float(tile)
        var base := Vector2(float(o["grid_x"]), float(o["grid_y"])) * float(tile) + _vec(o.get("anchor_offset", [0, 0]))
        var b: Array = rec["visual_bounds"]
        var height := maxf(0.0, float(b[3] - b[1]) - 24.0)
        var x0 := base.x
        var x1 := base.x + fp.x
        var yb := base.y + fp.y
        var reach := dir * height * per_h
        var cast_poly := Polygon2D.new()
        cast_poly.name = "Cast_" + _node_name(id)
        cast_poly.color = cast_color
        cast_poly.polygon = PackedVector2Array([Vector2(x0, yb), Vector2(x1, yb), Vector2(x1 + reach.x, yb + reach.y), Vector2(x0 + reach.x, yb + reach.y)])
        level.add_child(cast_poly)
        var contact_poly := Polygon2D.new()
        contact_poly.name = "Contact_" + _node_name(id)
        contact_poly.color = contact_color
        contact_poly.polygon = PackedVector2Array([Vector2(x0 - 2, yb - 10), Vector2(x1 + 2, yb - 10), Vector2(x1 + 6, yb + 4), Vector2(x0 - 6, yb + 4)])
        level.add_child(contact_poly)
    var additive := CanvasItemMaterial.new()
    additive.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
    for band in cfg.get("sun_bands", []):
        var poly := Polygon2D.new()
        poly.name = "SunBand"
        poly.color = Color(1.0, 0.82, 0.45, 0.09)
        poly.material = additive
        var pts := PackedVector2Array()
        for p in band:
            pts.append(_vec(p))
        poly.polygon = pts
        level.add_child(poly)
    for owner_id in cfg.get("glow_owners", []):
        var node: Node2D = placed.get(String(owner_id))
        if node == null:
            continue
        var rec: Dictionary = registry[String(node.get_meta("asset_key"))]
        var vb := visual_rect(node, rec, root)
        var radius := 58.0 if String(rec["asset_role"]) == "candles" else 84.0
        var color := Color("#ffb347", 0.42)
        var gradient := Gradient.new()
        gradient.set_color(0, color)
        gradient.set_color(1, Color(color, 0.0))
        var gt := GradientTexture2D.new()
        gt.gradient = gradient
        gt.fill = GradientTexture2D.FILL_RADIAL
        gt.fill_from = Vector2(0.5, 0.5)
        gt.fill_to = Vector2(1.0, 0.5)
        gt.width = int(radius * 2)
        gt.height = int(radius * 2)
        var glow := Sprite2D.new()
        glow.name = "Glow_" + _node_name(String(owner_id))
        glow.texture = gt
        glow.material = additive
        glow.position = vb.get_center()
        glow.z_index = 20
        level.add_child(glow)
