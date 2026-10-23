extends RefCounted
class_name AssetFactory

var catalog: AssetCatalog

func _init(source: AssetCatalog) -> void:
    catalog = source

func create_asset(asset_id: String, options: Dictionary = {}) -> Node2D:
    var record: Dictionary = catalog.get_asset(asset_id)
    var root := Node2D.new()
    root.name = asset_id
    if record.is_empty():
        push_warning("Unknown asset: " + asset_id)
        _placeholder(root, asset_id, Vector2(32, 32))
        return root
    var pixel_size: Array = record.get("pixel_size", [64, 64])
    var size := Vector2(float(pixel_size[0]), float(pixel_size[1]))
    var path := String(record.get("texture_path", ""))
    if path != "" and ResourceLoader.exists(path):
        var sprite := Sprite2D.new()
        sprite.name = "Visual"
        sprite.texture = load(path) as Texture2D
        sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
        sprite.centered = false
        var origin: Array = record.get("origin", [0, 0])
        sprite.position = -Vector2(float(origin[0]), float(origin[1]))
        sprite.flip_h = bool(options.get("flip_h", false))
        root.add_child(sprite)
    else:
        _placeholder(root, asset_id, size)

    var shadow_cfg: Dictionary = record.get("shadow", {"type": "none"}).duplicate(true)
    if options.has("shadow"):
        shadow_cfg = options["shadow"]
    if not bool(options.get("_separate_shadow", false)) and String(shadow_cfg.get("type", "none")) != "none":
        root.add_child(ShadowFactory.create_shadow(shadow_cfg, size))

    var collision_cfg: Dictionary = record.get("collision", {}).duplicate(true)
    if options.has("collision"):
        collision_cfg = options["collision"]
    if collision_cfg.get("enabled", false):
        var body := StaticBody2D.new()
        body.name = "SolidFootprint"
        var shape := CollisionShape2D.new()
        shape.name = "FootprintShape"
        var rect := RectangleShape2D.new()
        var dims: Array = collision_cfg.get("size", [32, 16])
        var offset: Array = collision_cfg.get("offset", [0, 0])
        rect.size = Vector2(float(dims[0]), float(dims[1]))
        shape.position = Vector2(float(offset[0]), float(offset[1]))
        shape.shape = rect
        body.add_child(shape)
        root.add_child(body)
    root.set_meta("asset_id", asset_id)
    root.set_meta("category", String(record.get("category", "")))
    root.set_meta("review_status", String(record.get("status", "planned")))
    return root

func _placeholder(root: Node2D, asset_id: String, size: Vector2) -> void:
    var poly := Polygon2D.new()
    var w := minf(90.0, size.x)
    var h := minf(90.0, size.y)
    poly.polygon = PackedVector2Array([Vector2(-w/2.0, -h), Vector2(w/2.0, -h),
        Vector2(w/2.0, 0), Vector2(-w/2.0, 0)])
    poly.color = Color(0.80, 0.12, 0.65, 0.7)
    root.add_child(poly)
    var label := Label.new()
    label.text = asset_id + " (draft)"
    label.position = Vector2(-w / 2.0, -h / 2.0)
    label.add_theme_color_override("font_color", Color.WHITE)
    root.add_child(label)
