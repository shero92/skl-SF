extends RefCounted
class_name RoomFactory

var catalog: AssetCatalog
var assets: AssetFactory

func _init() -> void:
    catalog = AssetCatalog.new()
    catalog.load_index()
    assets = AssetFactory.new(catalog)

func build_room(path: String, parent: Node2D) -> Node2D:
    var root := Node2D.new()
    root.name = "Room"
    parent.add_child(root)
    if not FileAccess.file_exists(path):
        push_error("Room layout not found: " + path)
        return root
    var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
    if typeof(data) != TYPE_DICTIONARY:
        push_error("Invalid room layout JSON")
        return root
    var tile_size := int(data.get("tile_size", 48))
    var dimensions: Array = data.get("size", [16, 12])
    var floor_layer := Node2D.new()
    floor_layer.name = "Floor"
    root.add_child(floor_layer)
    var floor_id := String(data.get("floor_asset_id", "F001"))
    var floor_data: Dictionary = catalog.get_asset(floor_id)
    var tex_path := String(floor_data.get("texture_path", ""))
    var floor_texture: Texture2D = null
    if tex_path != "" and ResourceLoader.exists(tex_path):
        floor_texture = load(tex_path) as Texture2D
    for y in int(dimensions[1]):
        for x in int(dimensions[0]):
            if floor_texture != null:
                var sprite := Sprite2D.new()
                sprite.texture = floor_texture
                sprite.centered = false
                sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
                sprite.position = Vector2(x * tile_size, y * tile_size)
                sprite.scale = Vector2(float(tile_size) / floor_texture.get_width(), float(tile_size) / floor_texture.get_height())
                floor_layer.add_child(sprite)
            else:
                var rect := Polygon2D.new()
                var t := float(tile_size)
                rect.polygon = PackedVector2Array([Vector2.ZERO, Vector2(t, 0), Vector2(t, t), Vector2(0, t)])
                rect.position = Vector2(x * tile_size, y * tile_size)
                rect.color = Color("#e8bf83") if (x + y) % 2 == 0 else Color("#dfb379")
                floor_layer.add_child(rect)
    var object_layer := Node2D.new()
    object_layer.name = "Entities"
    object_layer.y_sort_enabled = true
    root.add_child(object_layer)
    for item in data.get("objects", []):
        var node := assets.create_asset(String(item.get("id", "")))
        node.position = Vector2(float(item.get("x", 0)), float(item.get("y", 0)))
        object_layer.add_child(node)
    return root
