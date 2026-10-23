extends RefCounted
class_name RoomFactory

## Builds re-usable rooms from catalog IDs. Sprite rendering here is intentionally
## provisional until the unreviewed concept-sheet sprites pass visual QA.
var catalog: AssetCatalog
var assets: AssetFactory

func _init() -> void:
    catalog = AssetCatalog.new()
    catalog.load_index()
    assets = AssetFactory.new(catalog)

func build_latest(map_id: String, parent: Node2D) -> Node2D:
    # The registry points to the last materialized map snapshot.
    var registry_path := "res://map_factory/maps/index.json"
    if not FileAccess.file_exists(registry_path):
        push_error("Missing map registry; run map factory bootstrap")
        return Node2D.new()
    var reg: Variant = JSON.parse_string(FileAccess.get_file_as_string(registry_path))
    if typeof(reg) != TYPE_DICTIONARY:
        push_error("Invalid map registry")
        return Node2D.new()
    var maps: Dictionary = reg.get("maps", {})
    if not maps.has(map_id):
        push_error("Unknown map: " + map_id)
        return Node2D.new()
    var reference: Dictionary = maps[map_id]
    var file := "res://" + String(reference.get("latest", ""))
    return build_room(file, parent)


func build_room(path: String, parent: Node2D) -> Node2D:
    var root := Node2D.new()
    root.name = "Room"
    parent.add_child(root)
    if not FileAccess.file_exists(path):
        push_error("Room JSON not found: " + path)
        return root
    var value: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
    if typeof(value) != TYPE_DICTIONARY:
        push_error("Room JSON malformed: " + path)
        return root
    var data: Dictionary = value
    root.set_meta("map_id", String(data.get("map_id", "legacy_room")))
    root.set_meta("map_version", int(data.get("version", 0)))
    var backdrop := Polygon2D.new()
    backdrop.name = "MapBackdrop"
    var canvas: Array = data.get("canvas_size", [1536, 1024])
    backdrop.polygon = PackedVector2Array([Vector2.ZERO, Vector2(float(canvas[0]), 0),
        Vector2(float(canvas[0]), float(canvas[1])), Vector2(0, float(canvas[1]))])
    backdrop.color = Color(String(data.get("background_color", "#087ac6")))
    root.add_child(backdrop)

    # No sea in dungeons or indoor chambers unless the map explicitly requests it.
    var ocean_info: Dictionary = data.get("ocean", {})
    if not ocean_info.is_empty() and bool(ocean_info.get("enabled", true)):
        var ocean := OceanBackground.new()
        ocean.name = "OceanBackground"
        root.add_child(ocean)
        var sea_config: Dictionary = ocean_info.duplicate(true)
        sea_config["canvas_size"] = canvas
        ocean.configure(sea_config, catalog)

    # New maps have an explicit, immutable five-pass sprite/placement graph.
    # Old maps continue using their original legacy groups.
    var stack: Dictionary = data.get("layer_stack", {})
    if not stack.is_empty() and int(stack.get("schema_version", 0)) == 1:
        _build_five_levels(data, stack, root)
        _place_effects(data.get("effects", []), root)
        return root

    _place_group(data.get("background_objects", []), root, "DistantRuins", false)
    var ground := Node2D.new()
    ground.name = "Ground"
    root.add_child(ground)
    _paint_ground(data, ground)
    _place_group(data.get("ground_overlays", []), root, "GroundOverlays", false)
    _place_group(data.get("back_objects", []), root, "RearArchitecture", false)
    _place_group(data.get("objects", []), root, "Entities", true)
    _place_group(data.get("front_objects", []), root, "FrontDecorations", false)
    _place_effects(data.get("effects", []), root)
    return root

func _build_five_levels(data: Dictionary, stack: Dictionary, root: Node2D) -> void:
    var passes: Dictionary = stack.get("passes", {})
    var background := Node2D.new()
    background.name = "Level0_Background"
    background.z_index = 0
    root.add_child(background)
    _place_compiled_entries(passes.get("background", []), background)

    var floor_level := Node2D.new()
    floor_level.name = "Level1_Ground"
    floor_level.z_index = 10
    root.add_child(floor_level)
    var tiles := Node2D.new()
    tiles.name = "Ground"
    floor_level.add_child(tiles)
    _paint_ground(data, tiles)
    var overlays := Node2D.new()
    overlays.name = "GroundOverlays"
    floor_level.add_child(overlays)
    _place_compiled_entries(passes.get("ground", []), overlays)

    var walls := Node2D.new()
    walls.name = "Level2_Walls"
    walls.z_index = 30
    walls.y_sort_enabled = true
    root.add_child(walls)
    _place_compiled_entries(passes.get("walls", []), walls)

    var decor := Node2D.new()
    decor.name = "Level3_Decorations"
    decor.z_index = 40
    decor.y_sort_enabled = true
    root.add_child(decor)
    _place_compiled_entries(passes.get("decorations", []), decor)

    # Pass five: separate shadow instances, composited above floor but below
    # walls and decor. Processing last must NOT obscure their casting objects.
    var shadows := Node2D.new()
    shadows.name = "Level4_Shadows"
    shadows.z_index = 20
    root.add_child(shadows)
    for record in passes.get("shadows", []):
        if typeof(record) != TYPE_DICTIONARY:
            continue
        var cfg: Dictionary = record.get("settings", {})
        var dimensions: Array = record.get("sprite_pixel_size", [64, 64])
        var native_size := Vector2(float(dimensions[0]), float(dimensions[1]))
        var layer_shadow := ShadowFactory.create_shadow(cfg, native_size)
        layer_shadow.name = String(record.get("instance_id", "UnnamedShadow"))
        var xy: Array = record.get("position", [0, 0])
        layer_shadow.position = Vector2(float(xy[0]), float(xy[1]))
        var scale_value := float(record.get("scale", 1))
        layer_shadow.scale = Vector2.ONE * scale_value
        layer_shadow.set_meta("owner_instance_id", String(record.get("owner_instance_id", "")))
        shadows.add_child(layer_shadow)

func _place_compiled_entries(entries: Array, group: Node2D) -> void:
    for record in entries:
        if typeof(record) != TYPE_DICTIONARY:
            continue
        var asset_id := String(record.get("asset_id", ""))
        var orientation: Dictionary = record.get("orientation", {})
        var render_id: String = String(orientation.get("resolved_asset_id", asset_id))
        var info: Dictionary = catalog.get_asset(render_id)
        if info.is_empty() or String(info.get("category", "")) in ["characters", "ui", "shadows"]:
            push_error("Invalid map-only block: " + asset_id)
            continue
        var opts: Dictionary = {
            "_separate_shadow": true,
            "shadow": record.get("shadow", {"type":"none"}),
            "collision": record.get("collision", {"enabled":false}),
            "flip_h": record.get("flip_h", false)
        }
        var node := assets.create_asset(render_id, opts)
        node.name = String(record.get("instance_id", asset_id))
        # Four cardinal facings. Flat sprites rotate the root AND collision.
        # Perspective-aware props use four independent upright art variants.
        if not orientation.is_empty():
            var facing: String = String(orientation.get("facing", "north"))
            var turn: int = int(orientation.get("turn_quarters", 0))
            if String(orientation.get("orientation_mode", "rotate")) == "rotate":
                node.rotation_degrees = 90.0 * float(turn)
            else:
                node.rotation_degrees = 0.0
            node.set_meta("facing", facing)
            node.set_meta("orientation_mode", String(orientation.get("orientation_mode", "rotate")))
            node.set_meta("source_asset_id", asset_id)
        var xy: Array = record.get("position", [0, 0])
        node.position = Vector2(float(xy[0]), float(xy[1]))
        if orientation.is_empty():
            node.rotation_degrees = float(record.get("rotation_degrees", 0))
        var scale_value := float(record.get("scale", 1))
        node.scale = Vector2.ONE * scale_value
        # A negative or unusually high local z must not escape its semantic pass.
        node.z_index = clampi(int(record.get("z_index", 0)), -2, 2)
        var attachment: Variant = record.get("attachment")
        if typeof(attachment) == TYPE_DICTIONARY:
            node.set_meta("mount_on", String(attachment.get("parent_instance_id", "")))
            node.set_meta("mount_offset", attachment.get("mount_offset", [0,0]))
        group.add_child(node)

func _paint_ground(data: Dictionary, target: Node2D) -> void:
    var size: Array = data.get("size", [17, 10])
    var offset: Array = data.get("ground_offset", [220, 225])
    var tile_size := int(data.get("tile_size", 64))
    var floor_ids: Array = data.get("floor_ids", ["F001", "F002"])
    var footprint: Dictionary = data.get("floor_footprint", {})
    var row_spans: Array = footprint.get("row_spans", [])
    var tile_style: Dictionary = data.get("floor_tile_style", {})
    var style_tile_ids: Array = tile_style.get("tile_ids", [])
    var override_map: Dictionary = {}
    for entry in data.get("tile_overrides", []):
        # JSON numeric cells must be normalized before forming dictionary keys.
        # Godot can parse JSON 7 as float 7.0; "7.0:5.0" never equals "7:5".
        override_map["%d:%d" % [int(entry.get("x", 0)), int(entry.get("y", 0))]] = String(entry.get("id", "F001"))
    for y in int(size[1]):
        for x in int(size[0]):
            if not row_spans.is_empty():
                var inside := false
                for span in row_spans[y]:
                    if x >= int(span[0]) and x <= int(span[1]):
                        inside = true
                        break
                if not inside:
                    continue
            var asset_id := String(floor_ids[(x * 17 + y * 11) % floor_ids.size()])
            var key := str(x) + ":" + str(y)
            if override_map.has(key):
                asset_id = String(override_map[key])
            var record: Dictionary = catalog.get_asset(asset_id)
            var path := String(record.get("texture_path", ""))
            var pos := Vector2(float(offset[0]) + x * tile_size, float(offset[1]) + y * tile_size)
            if path != "" and ResourceLoader.exists(path):
                var texture := load(path) as Texture2D
                if texture != null:
                    var styled_tile := bool(tile_style.get("enabled", false)) and style_tile_ids.has(asset_id)
                    if styled_tile:
                        var edges: Array = tile_style.get("crop_insets", [0, 0, 0, 0])
                        var cut := AtlasTexture.new()
                        cut.atlas = texture
                        cut.region = Rect2(
                            float(edges[0]), float(edges[1]),
                            float(texture.get_width()) - float(edges[0]) - float(edges[2]),
                            float(texture.get_height()) - float(edges[1]) - float(edges[3])
                        )
                        texture = cut
                    var sprite := Sprite2D.new()
                    sprite.name = "Floor_" + str(x) + "_" + str(y) + "_" + asset_id
                    sprite.centered = false
                    sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
                    sprite.texture = texture
                    sprite.position = pos
                    sprite.scale = Vector2(float(tile_size) / texture.get_width(), float(tile_size) / texture.get_height())
                    if styled_tile:
                        var mortar := Line2D.new()
                        mortar.name = "WarmStoneJoint"
                        mortar.width = float(tile_style.get("joint_width", 1.0)) / sprite.scale.x
                        var tint := Color(String(tile_style.get("joint_color", "#88755b")))
                        tint.a = float(tile_style.get("joint_opacity", 0.22))
                        mortar.default_color = tint
                        var w := float(texture.get_width())
                        var h := float(texture.get_height())
                        mortar.points = PackedVector2Array([
                            Vector2(0, 0), Vector2(w, 0), Vector2(w, h),
                            Vector2(0, h), Vector2(0, 0)
                        ])
                        sprite.add_child(mortar)
                    target.add_child(sprite)
                    continue
            var fallback := Polygon2D.new()
            var t := float(tile_size)
            fallback.polygon = PackedVector2Array([Vector2.ZERO, Vector2(t, 0), Vector2(t, t), Vector2(0, t)])
            fallback.color = Color("#d9ad73") if (x + y) % 2 else Color("#edc792")
            fallback.position = pos
            target.add_child(fallback)

func _place_group(entries: Array, parent: Node2D, name: String, use_y_sort: bool) -> void:
    var group := Node2D.new()
    group.name = name
    group.y_sort_enabled = use_y_sort
    parent.add_child(group)
    for item in entries:
        if typeof(item) != TYPE_DICTIONARY:
            continue
        var asset_id := String(item.get("id", ""))
        var record: Dictionary = catalog.get_asset(asset_id)
        if record.is_empty():
            push_warning("Unknown asset in room layout: " + asset_id)
            continue
        if String(record.get("category", "")) in ["characters", "ui", "shadows"]:
            push_error("Map factory rejects non-environment sprite " + asset_id)
            continue
        var node := assets.create_asset(asset_id, item)
        node.name = String(item.get("instance_id", asset_id))
        if item.has("facing"):
            var facing: String = String(item["facing"])
            var turns := ["north", "east", "south", "west"].find(facing)
            if turns >= 0:
                if String(item.get("orientation_mode", "rotate")) == "rotate":
                    node.rotation_degrees = 90.0 * float(turns)
                else:
                    var directions: Dictionary = item.get("direction_asset_ids", record.get("direction_asset_ids", {}))
                    var variant_id: String = String(directions.get(facing, ""))
                    if variant_id != "" and not catalog.get_asset(variant_id).is_empty():
                        node.queue_free()
                        node = assets.create_asset(variant_id, item)
                        node.name = String(item.get("instance_id", asset_id))
                node.set_meta("facing", facing)
        node.position = Vector2(float(item.get("x", 0)), float(item.get("y", 0)))
        if not item.has("facing"):
            node.rotation_degrees = float(item.get("rotation_degrees", 0))
        var s := float(item.get("scale", 1.0))
        node.scale = Vector2(s, s)
        node.z_index = int(item.get("z_index", 0))
        group.add_child(node)

func _place_effects(entries: Array, parent: Node2D) -> void:
    var group := Node2D.new()
    group.name = "AnimatedLighting"
    parent.add_child(group)
    for info in entries:
        if typeof(info) != TYPE_DICTIONARY:
            continue
        var light := RoomLightFX.new()
        light.name = String(info.get("instance_id", "LightFX"))
        group.add_child(light)
        light.configure(info, catalog)
