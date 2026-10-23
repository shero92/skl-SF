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

func _paint_ground(data: Dictionary, target: Node2D) -> void:
    var size: Array = data.get("size", [17, 10])
    var offset: Array = data.get("ground_offset", [220, 225])
    var tile_size := int(data.get("tile_size", 64))
    var floor_ids: Array = data.get("floor_ids", ["F001", "F002"])
    var override_map: Dictionary = {}
    for entry in data.get("tile_overrides", []):
        # JSON numeric cells must be normalized before forming dictionary keys.
        # Godot can parse JSON 7 as float 7.0; "7.0:5.0" never equals "7:5".
        override_map["%d:%d" % [int(entry.get("x", 0)), int(entry.get("y", 0))]] = String(entry.get("id", "F001"))
    for y in int(size[1]):
        for x in int(size[0]):
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
                    var sprite := Sprite2D.new()
                    sprite.name = "Floor_" + str(x) + "_" + str(y) + "_" + asset_id
                    sprite.centered = false
                    sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
                    sprite.texture = texture
                    sprite.position = pos
                    sprite.scale = Vector2(float(tile_size) / texture.get_width(), float(tile_size) / texture.get_height())
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
        node.position = Vector2(float(item.get("x", 0)), float(item.get("y", 0)))
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
