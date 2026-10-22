extends CharacterBody2D
class_name HeroPlayer

@export var move_speed: float = 210.0
@export var sprite_scale: float = 0.56
var movement_enabled: bool = true
var facing: Vector2 = Vector2.DOWN
var art: Sprite2D
var _anim_id: String = ""
var _elapsed: float = 0.0
var _frame_count: int = 1
var _fps: float = 2.0

const HERO = {
    "idle_down": "CH001", "idle_up": "CH002",
    "idle_left": "CH003", "idle_right": "CH004",
    "walk_down": "CH005", "walk_up": "CH006",
    "walk_left": "CH007", "walk_right": "CH008"
}

func _ready() -> void:
    var shape := CollisionShape2D.new()
    var capsule := CapsuleShape2D.new()
    capsule.radius = 12.0
    capsule.height = 30.0
    shape.position = Vector2(0, -17)
    shape.shape = capsule
    add_child(shape)

    art = Sprite2D.new()
    art.name = "HeroSprite"
    art.centered = false
    art.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    art.scale = Vector2.ONE * sprite_scale
    art.position = Vector2(-72.0, -188.0) * sprite_scale
    add_child(art)
    add_child(ShadowFactory.create_shadow(
        {"type": "character", "opacity": 0.45, "offset_x": 0, "offset_y": -7}, Vector2(76, 40)))
    _play(HERO["idle_down"])

func _physics_process(delta: float) -> void:
    var movement := Vector2.ZERO
    if movement_enabled:
        if Input.is_key_pressed(KEY_A) or Input.is_action_pressed("ui_left"):
            movement.x -= 1
        if Input.is_key_pressed(KEY_D) or Input.is_action_pressed("ui_right"):
            movement.x += 1
        if Input.is_key_pressed(KEY_W) or Input.is_action_pressed("ui_up"):
            movement.y -= 1
        if Input.is_key_pressed(KEY_S) or Input.is_action_pressed("ui_down"):
            movement.y += 1
    velocity = movement.normalized() * move_speed
    move_and_slide()
    if movement.length_squared() > 0:
        facing = movement.normalized()
    var direction := "down"
    if absf(facing.x) > absf(facing.y):
        direction = "right" if facing.x > 0 else "left"
    elif facing.y < 0:
        direction = "up"
    var state := "walk" if movement.length_squared() > 0 else "idle"
    _play(HERO[state + "_" + direction])
    _elapsed += delta
    if art != null:
        art.frame = int(_elapsed * _fps) % _frame_count

func _play(id: String) -> void:
    if id == _anim_id:
        return
    _anim_id = id
    _elapsed = 0.0
    var catalog := AssetCatalog.new()
    if not catalog.load_index():
        return
    var record: Dictionary = catalog.get_asset(id)
    var path := String(record.get("texture_path", ""))
    if not ResourceLoader.exists(path):
        push_warning("Hero animation missing: " + id)
        return
    art.texture = load(path) as Texture2D
    _frame_count = maxi(1, int(record.get("animation_frames", 1)))
    _fps = float(record.get("fps", 2))
    art.hframes = _frame_count
    art.frame = 0
