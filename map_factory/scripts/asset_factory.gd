extends RefCounted
class_name AssetFactory

var catalog: AssetCatalog

func _init(source: AssetCatalog) -> void:
    catalog = source

func create_asset(asset_id: String) -> Node2D:
    var record := catalog.get_asset(asset_id)
    var root := Node2D.new()
    root.name = asset_id
    if record.is_empty():
        push_warning("Unknown asset: " + asset_id)
        _placeholder(root, asset_id, Vector2(32, 32))
        return root
    var size_data: Array = record.get("pixel_size", [32, 32])
    var size := Vector2(float(size_data[0]), float(size_data[1]))
    var path := String(record.get("texture_path", ""))
    if path != "" and ResourceLoader.exists(path):
        var sprite := Sprite2D.new()
        sprite.name = "Visual"
        sprite.texture = load(path)
        sprite.centered = false
        var origin: Array = record.get("origin", [0, 0])
        sprite.position = -Vector2(float(origin[0]), float(origin[1]))
        root.add_child(sprite)
    else:
        _placeholder(root, asset_id, size)
    var shadow_cfg: Dictionary = record.get("shadow", {"type": "none"})
    if String(shadow_cfg.get("type", "none")) != "none":
        root.add_child(ShadowFactory.create_shadow(shadow_cfg, size))
    var collision_cfg: Dictionary = record.get("collision", {})
    if collision_cfg.get("enabled", false):
        var body := StaticBody2D.new()
        body.name = "Collision"
        var shape := CollisionShape2D.new()
        var rect := RectangleShape2D.new()
        var dimensions: Array = collision_cfg.get("size", [32, 16])
        var offset: Array = collision_cfg.get("offset", [0, 0])
        rect.size = Vector2(float(dimensions[0]), float(dimensions[1]))
        shape.shape = rect
        shape.position = Vector2(float(offset[0]), float(offset[1]))
        body.add_child(shape)
        root.add_child(body)
    root.set_meta("asset_id", asset_id)
    root.set_meta("category", String(record.get("category", "")))
    return root

func _placeholder(root: Node2D, asset_id: String, size: Vector2) -> void:
    var poly := Polygon2D.new()
    poly.polygon = PackedVector2Array([Vector2.ZERO, Vector2(size.x, 0), size, Vector2(0, size.y)])
    poly.color = Color(0.8, 0.1, 0.65, 0.58)
    root.add_child(poly)
    var label := Label.new()
    label.text = asset_id
    label.add_theme_color_override("font_color", Color.WHITE)
    root.add_child(label)
