extends CharacterBody2D
class_name HeroPlayer

@export var move_speed: float = 210.0
@export var sprite_scale: float = 0.56
var movement_enabled: bool = true
var navigation: NavigationGrid # optional Map Factory walk validator; null keeps movement unrestricted
## Opt-in: draw the hero from the Game Factory manifest (approved map idle/walk frames). Off by default so the
## shipped look is unchanged; incomplete or missing animations always fall back to the legacy sprite.
@export var use_factory_art: bool = false
var factory_art: AnimatedSprite2D
## Above 0: Shining Force style movement. The hero stands on the centre of a square of this size and every key press
## (or held key) moves him exactly one square, up, down, left or right, never between squares and never diagonally.
var grid_step: float = 0.0
## Shifts the squares so that their centres sit in the middle of the walk grid's cells, away from cell edges.
var grid_offset: Vector2 = Vector2.ZERO
var step_seconds: float = 0.2
var _step_from: Vector2 = Vector2.ZERO
var _step_to: Vector2 = Vector2.ZERO
var _step_time: float = -1.0  # negative: standing still
## Optional high-resolution drawing of the hero (painted rooms). When set and its sources exist it replaces both sprites.
var source_art: HeroSourceArt
const FACTORY_ACTOR = preload("res://scenes/game_factory_actor.gd")
const FACTORY_MANIFEST := "res://game_factory/character_manifest.json"
static var _factory_frames: SpriteFrames
static var _factory_anchor: Array = [48, 90]
var facing: Vector2 = Vector2.DOWN

## True while he is walking (a step in progress, or free movement this frame); the camera leads in his direction.
func is_moving() -> bool:
    return _step_time >= 0.0 or velocity != Vector2.ZERO
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
    if use_factory_art:
        _setup_factory_art()
    _play(HERO["idle_down"])

## Centre of the square that holds a point.
func square_centre(point: Vector2) -> Vector2:
    return grid_offset + ((point - grid_offset) / grid_step).floor() * grid_step + Vector2.ONE * grid_step * 0.5


## Puts the hero on the square that holds him, or on the nearest open square next to it.
func snap_to_grid() -> void:
    _step_time = -1.0
    var best := square_centre(global_position)
    if navigation != null and not navigation.footprint_open(best):
        var found := false
        for ring in range(1, 4):
            for dy in range(-ring, ring + 1):
                for dx in range(-ring, ring + 1):
                    var candidate := best + Vector2(dx, dy) * grid_step
                    if not found and navigation.footprint_open(candidate):
                        best = candidate
                        found = true
    global_position = best


## One square in a direction (Vector2.LEFT/RIGHT/UP/DOWN) if the square is open and he is standing still.
func step(direction: Vector2) -> bool:
    facing = direction
    if grid_step <= 0.0 or _step_time >= 0.0:
        return false
    var target := global_position + direction * grid_step
    if navigation != null and not navigation.footprint_open(target):
        return false  # bumps into the wall: he only turns to face it
    _step_from = global_position
    _step_to = target
    _step_time = 0.0
    return true


func _grid_input() -> Vector2:
    if not movement_enabled:
        return Vector2.ZERO
    if Input.is_key_pressed(KEY_A) or Input.is_action_pressed("ui_left"):
        return Vector2.LEFT
    if Input.is_key_pressed(KEY_D) or Input.is_action_pressed("ui_right"):
        return Vector2.RIGHT
    if Input.is_key_pressed(KEY_W) or Input.is_action_pressed("ui_up"):
        return Vector2.UP
    if Input.is_key_pressed(KEY_S) or Input.is_action_pressed("ui_down"):
        return Vector2.DOWN
    return Vector2.ZERO


func _physics_process(delta: float) -> void:
    var movement := Vector2.ZERO
    if grid_step > 0.0:
        if _step_time >= 0.0:
            _step_time += delta
            var done := clampf(_step_time / step_seconds, 0.0, 1.0)
            global_position = _step_from.lerp(_step_to, done)
            movement = _step_to - _step_from
            if _step_time >= step_seconds:
                global_position = _step_to
                _step_time = -1.0
        if _step_time < 0.0:
            var wanted := _grid_input()
            if wanted != Vector2.ZERO and step(wanted):
                movement = wanted
            elif wanted != Vector2.ZERO:
                facing = wanted
    elif movement_enabled:
        if Input.is_key_pressed(KEY_A) or Input.is_action_pressed("ui_left"):
            movement.x -= 1
        if Input.is_key_pressed(KEY_D) or Input.is_action_pressed("ui_right"):
            movement.x += 1
        if Input.is_key_pressed(KEY_W) or Input.is_action_pressed("ui_up"):
            movement.y -= 1
        if Input.is_key_pressed(KEY_S) or Input.is_action_pressed("ui_down"):
            movement.y += 1
    if grid_step <= 0.0:
        velocity = movement.normalized() * move_speed
        if navigation != null and delta > 0.0 and velocity != Vector2.ZERO:
            # Only apply the part of the step whose footprint stays on open cells (slides along edges).
            velocity = navigation.allowed_motion(global_position, velocity * delta) / delta
        move_and_slide()
    if movement.length_squared() > 0:
        facing = movement.normalized()
    var direction := "down"
    if absf(facing.x) > absf(facing.y):
        direction = "right" if facing.x > 0 else "left"
    elif facing.y < 0:
        direction = "up"
    var state := "walk" if movement.length_squared() > 0 else "idle"
    if source_art != null and source_art.play(state, direction, delta):
        art.visible = false
        if factory_art != null:
            factory_art.visible = false
    elif factory_art != null and _play_factory(state, direction):
        art.visible = false
    else:
        if factory_art != null:
            factory_art.visible = false
            art.visible = true
        _play(HERO[state + "_" + direction])
    _elapsed += delta
    if art != null:
        art.frame = int(_elapsed * _fps) % _frame_count

func _setup_factory_art() -> void:
    if _factory_frames == null:
        var manifest: Variant = JSON.parse_string(FileAccess.get_file_as_string(FACTORY_MANIFEST))
        if typeof(manifest) != TYPE_DICTIONARY:
            return
        for record: Dictionary in manifest.get("characters", []):
            if String(record.get("slug", "")) == "hero":
                _factory_frames = FACTORY_ACTOR.make_frames(record, "map_") # complete animations only
                _factory_anchor = record.get("map_anchor", [48, 90])
    if _factory_frames == null:
        return
    factory_art = AnimatedSprite2D.new()
    factory_art.name = "FactoryAnimation"
    factory_art.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    factory_art.centered = false
    factory_art.sprite_frames = _factory_frames
    factory_art.position = -Vector2(float(_factory_anchor[0]), float(_factory_anchor[1]))
    factory_art.visible = false
    add_child(factory_art)


func _play_factory(state: String, direction: String) -> bool:
    var key := "map_%s_%s" % [direction, state]
    if not _factory_frames.has_animation(key) or _factory_frames.get_frame_count(key) == 0:
        return false
    factory_art.visible = true
    if factory_art.animation != key or not factory_art.is_playing():
        factory_art.play(key)
    return true


func _play(id: String) -> void:
    if id == _anim_id:
        return
    _anim_id = id
    _elapsed = 0.0
    var catalog := AssetCatalog.shared()
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
