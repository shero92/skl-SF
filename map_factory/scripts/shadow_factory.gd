extends RefCounted
class_name ShadowFactory

const SHADOW_TEXTURES := {
    "contact": "res://map_factory/parts/shadows/S002_Shadow_Contact_Medium.png",
    "contact_small": "res://map_factory/parts/shadows/S001_Shadow_Contact_Small.png",
    "contact_medium": "res://map_factory/parts/shadows/S002_Shadow_Contact_Medium.png",
    "contact_large": "res://map_factory/parts/shadows/S003_Shadow_Contact_Large.png",
    "character": "res://map_factory/parts/shadows/S004_Shadow_Character.png",
    "bed": "res://map_factory/parts/shadows/S005_Shadow_Bed.png",
    "table": "res://map_factory/parts/shadows/S006_Shadow_Table.png",
    "chair": "res://map_factory/parts/shadows/S007_Shadow_Chair.png",
    "bookshelf": "res://map_factory/parts/shadows/S008_Shadow_Bookshelf.png",
    "chest": "res://map_factory/parts/shadows/S009_Shadow_Chest.png",
    "plant": "res://map_factory/parts/shadows/S010_Shadow_Plant.png",
    "column_short": "res://map_factory/parts/shadows/S011_Shadow_Column_Short.png",
    "column_long": "res://map_factory/parts/shadows/S012_Shadow_Column_Long.png",
    "wall_base": "res://map_factory/parts/shadows/S013_Shadow_Wall_Base.png",
    "wall_corner": "res://map_factory/parts/shadows/S014_Shadow_Wall_Corner.png",
    "stairs": "res://map_factory/parts/shadows/S015_Shadow_Stairs.png",
    "soft_cast": "res://map_factory/parts/shadows/S016_Shadow_Soft_Diagonal.png"
}

static func create_shadow(config: Dictionary, sprite_size: Vector2) -> Node2D:
    var root := Node2D.new()
    root.name = "Shadow"
    var kind := String(config.get("type", "none"))
    if kind == "none":
        return root
    var path := String(config.get("texture", SHADOW_TEXTURES.get(kind, "")))
    if path != "" and ResourceLoader.exists(path):
        var sprite := Sprite2D.new()
        sprite.name = "AlphaShadow"
        sprite.texture = load(path) as Texture2D
        sprite.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
        sprite.centered = true
        sprite.position = Vector2(float(config.get("offset_x", 0)), float(config.get("offset_y", 0)))
        sprite.modulate.a = clampf(float(config.get("opacity", 0.35)), 0.0, 1.0)
        var tex_size := sprite.texture.get_size()
        if tex_size.x > 0:
            sprite.scale.x = maxf(0.5, sprite_size.x / tex_size.x)
        root.z_index = -1
        root.add_child(sprite)
        return root
    # Geometry fallback if shadow PNG is missing.
    var poly := Polygon2D.new()
    var pts := PackedVector2Array()
    for i in 24:
        var angle := TAU * float(i) / 24.0
        pts.append(Vector2(cos(angle) * maxf(8.0, sprite_size.x * 0.3), sin(angle) * 7.0))
    poly.polygon = pts
    poly.color = Color(0.08, 0.12, 0.2, float(config.get("opacity", 0.3)))
    root.z_index = -1
    root.add_child(poly)
    return root
