extends Node2D
class_name RoomNpc

@export var display_name: String = "Forest Guardian"
@export var tint: Color = Color("#469a6b")
@export var flip_sprite: bool = false
@export var character: String = ""
@export var facing: String = "down"
@export var sprite_scale: float = 0.8
var sprite: Sprite2D
var animation_time: float = 0.0

func _ready() -> void:
    # Approved poster character (Cely, Old Father, Reef Friend, Temple Archer, ...).
    if PosterCharacter.available(character):
        sprite = Sprite2D.new()
        sprite.name = character.capitalize().replace(" ", "") + "Sprite"
        sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
        PosterCharacter.apply(sprite, character, facing, sprite_scale)
        add_child(sprite)
        add_child(ShadowFactory.create_shadow({"type": "contact_small", "opacity": 0.4}, Vector2(70, 26)))
        return
    var catalog := AssetCatalog.shared()
    var record: Dictionary = catalog.get_asset("CH011")
    var path := String(record.get("texture_path", ""))
    if not ResourceLoader.exists(path):
        queue_redraw()
        return
    sprite = Sprite2D.new()
    sprite.name = "ForestFairySprite"
    sprite.texture = load(path) as Texture2D
    sprite.centered = false
    sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    sprite.hframes = maxi(1, int(record.get("animation_frames", 2)))
    sprite.flip_h = flip_sprite
    sprite.scale = Vector2.ONE * 0.55
    sprite.position = Vector2(-72, -188) * 0.55
    add_child(sprite)
    add_child(ShadowFactory.create_shadow({"type": "contact_small", "opacity": 0.4}, Vector2(70, 26)))

func _process(delta: float) -> void:
    if sprite == null:
        return
    animation_time += delta
    if character != "":
        # idle sway: frame order 0, 1, 2, 1
        sprite.frame = [0, 1, 2, 1][int(animation_time * 2.5) % 4]
        return
    sprite.frame = int(animation_time * 2.0) % sprite.hframes

func _draw() -> void:
    if sprite != null:
        return
    draw_circle(Vector2(0, -12), 18.0, tint)
    draw_circle(Vector2(0, -31), 11.0, Color("#eed2a0"))
