extends Node2D
class_name RoomCompanion

var follow_target: Node2D
@export var walk_speed: float = 152.0
@export var character_slug: String = "neru"
@export var sprite_scale: float = 0.7
var facing: String = "down"
var poster_mode: bool = false
var sprite: Sprite2D
var catalog: AssetCatalog
var current_animation: String = ""
var animation_time: float = 0.0
var fps: float = 2.0

func _ready() -> void:
    catalog = AssetCatalog.new()
    catalog.load_index()
    sprite = Sprite2D.new()
    sprite.name = "CrystalCompanion"
    sprite.centered = false
    sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    sprite.scale = Vector2.ONE * 0.46
    sprite.position = Vector2(-72, -188) * 0.46
    add_child(sprite)
    add_child(ShadowFactory.create_shadow({"type": "contact_small", "opacity": 0.42}, Vector2(54, 30)))
    if PosterCharacter.available(character_slug):
        poster_mode = true
        PosterCharacter.apply(sprite, character_slug, facing, sprite_scale)
        return
    _play("CH009")

func _physics_process(delta: float) -> void:
    if follow_target == null:
        return
    var desired: Vector2 = follow_target.position + Vector2(56, 16)
    var distance := position.distance_to(desired)
    var moving := distance > 70
    if poster_mode:
        if moving:
            facing = PosterCharacter.direction_for(desired - position, facing)
            position = position.move_toward(desired, walk_speed * delta)
            PosterCharacter.apply(sprite, character_slug, facing, sprite_scale)
        animation_time += delta
        sprite.frame = [0, 1, 2, 1][int(animation_time * (6.0 if moving else 2.0)) % 4]
        return
    if moving:
        position = position.move_toward(desired, walk_speed * delta)
        _play("CH010")
    else:
        _play("CH009")
    animation_time += delta
    if sprite != null:
        sprite.frame = int(animation_time * fps) % sprite.hframes

func _play(id: String) -> void:
    if current_animation == id:
        return
    current_animation = id
    animation_time = 0
    var record: Dictionary = catalog.get_asset(id)
    var path := String(record.get("texture_path", ""))
    if not ResourceLoader.exists(path):
        return
    sprite.texture = load(path) as Texture2D
    sprite.hframes = maxi(1, int(record.get("animation_frames", 2)))
    sprite.frame = 0
    fps = float(record.get("fps", 2))
