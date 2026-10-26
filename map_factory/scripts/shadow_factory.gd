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
    "soft_cast": "res://map_factory/parts/shadows/S016_Shadow_Soft_Diagonal.png",
    "directional_sun": "res://map_factory/parts/shadows/S017_Directional_Sun_Cast_Shadow.png"
}

const LAYER_4_Z := 20

const GLOW_TEXTURES := {
    "lantern_glow": "res://map_factory/parts/decor/D015_Lantern_Glow.png",
    "D015": "res://map_factory/parts/decor/D015_Lantern_Glow.png",
    "candle_glow": "res://map_factory/parts/decor/D016_Candle_Glow.png",
    "D016": "res://map_factory/parts/decor/D016_Candle_Glow.png"
}

# Layer 4 shadow linked to its owner placement: absolute z 20, beneath the
# owner's own layer, with owner metadata so it moves/removes with the owner.
static func create_owned_shadow(config: Dictionary, sprite_size: Vector2, owner_id: String, owner_position: Vector2 = Vector2.ZERO) -> Node2D:
    var node := create_shadow(config, sprite_size)
    _link_to_owner(node, owner_id, owner_position)
    return node

# Lantern/candle glow (D015/D016) and light-shaft entries for layer 4.
static func create_light(config: Dictionary, sprite_size: Vector2, owner_id: String = "", owner_position: Vector2 = Vector2.ZERO) -> Node2D:
    var root := Node2D.new()
    var kind := String(config.get("type", "none"))
    var opacity := clampf(float(config.get("opacity", 0.6)), 0.0, 1.0)
    var offset := Vector2(float(config.get("offset_x", 0)), float(config.get("offset_y", 0)))
    var path := String(config.get("texture", GLOW_TEXTURES.get(kind, "")))
    if kind == "light_shaft":
        root.name = "LightShaft"
    else:
        root.name = "Glow"
    if kind == "none":
        return root
    var additive := CanvasItemMaterial.new()
    additive.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
    if path != "" and ResourceLoader.exists(path):
        var sprite := Sprite2D.new()
        sprite.name = "LightSprite"
        sprite.texture = load(path) as Texture2D
        sprite.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
        sprite.centered = true
        sprite.position = offset
        sprite.rotation_degrees = float(config.get("angle", 0))
        sprite.modulate.a = opacity
        sprite.material = additive
        root.add_child(sprite)
    elif kind == "light_shaft":
        # Geometry fallback: slanted translucent quad.
        var poly := Polygon2D.new()
        var w := maxf(8.0, float(config.get("width", sprite_size.x)))
        var h := maxf(8.0, float(config.get("length", sprite_size.y)))
        var slant := float(config.get("slant", w * 0.5))
        poly.polygon = PackedVector2Array([Vector2(0, 0), Vector2(w, 0), Vector2(w + slant, h), Vector2(slant, h)])
        poly.position = offset
        poly.color = Color(1.0, 0.95, 0.8, opacity * 0.35)
        poly.material = additive
        root.add_child(poly)
    else:
        return root
    if owner_id != "":
        _link_to_owner(root, owner_id, owner_position)
    else:
        root.z_as_relative = false
        root.z_index = LAYER_4_Z
    return root

static func _link_to_owner(node: Node2D, owner_id: String, owner_position: Vector2) -> void:
    node.z_as_relative = false
    node.z_index = LAYER_4_Z
    node.position += owner_position
    node.set_meta("owner_id", owner_id)
    node.set_meta("layer", 4)
    node.add_to_group("layer4_owned")

static func create_shadow(config: Dictionary, sprite_size: Vector2) -> Node2D:
    var root := Node2D.new()
    root.name = "Shadow"
    var kind := String(config.get("type", "none"))
    if kind == "none":
        return root
    if kind == "light_shaft" or GLOW_TEXTURES.has(kind):
        return create_light(config, sprite_size)
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
