extends CharacterBody2D
## Separate registry-driven actor. Existing gameplay controllers are preserved.
signal battle_requested(actor: CharacterBody2D)
var definition: Dictionary = {}
var art: AnimatedSprite2D
var facing: String = "down"
var movement_enabled: bool = true
var hp: int = 100
var follow_target: Node2D
var navigation: NavigationGrid # shared Map Factory validator; null means unrestricted
var _foot_offsets: Array[Vector2] = []

func _ready() -> void:
	art = AnimatedSprite2D.new()
	art.name = "Animation"
	art.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	art.centered = false
	var anchor: Array = definition.get("map_anchor", [48,90])
	art.position = -Vector2(float(anchor[0]),float(anchor[1]))
	art.sprite_frames = make_frames(definition, "map_")
	add_child(art)
	var collision := CollisionShape2D.new()
	var rectangle := RectangleShape2D.new()
	var cfg: Dictionary = definition.get("collision_shape", {})
	var dims: Array = cfg.get("size", [24,18])
	var offset: Array = cfg.get("offset", [0,-9])
	rectangle.size = Vector2(float(dims[0]),float(dims[1]))
	collision.shape = rectangle
	collision.position = Vector2(float(offset[0]),float(offset[1]))
	add_child(collision)
	for x: float in [-rectangle.size.x/2,rectangle.size.x/2]:
		for y: float in [-rectangle.size.y/2,rectangle.size.y/2]:
			_foot_offsets.append(collision.position+Vector2(x,y))
	var shadow := ShadowFactory.create_shadow({"type":"character","opacity":0.22,"offset_y":-3},Vector2(30,18))
	shadow.name = "ContactShadow"
	shadow.z_as_relative = false
	shadow.z_index = 20
	shadow.set_meta("logical_level",4)
	shadow.set_meta("owner_character_id",definition.get("character_id",""))
	add_child(shadow)
	_play("idle")

static func make_frames(record: Dictionary, prefix: String) -> SpriteFrames:
	var frames := SpriteFrames.new()
	frames.remove_animation("default")
	var animations: Dictionary = record.get("animations", {})
	for key: String in animations:
		if not key.begins_with(prefix):
			continue
		var entry: Dictionary = animations[key]
		# Partial frame sequences are inspectable, but never playable as complete animations.
		if not bool(entry.get("complete", false)):
			continue
		frames.add_animation(key)
		frames.set_animation_speed(key, 1.0 / float(entry.get("duration", 0.15)))
		frames.set_animation_loop(key, bool(entry.get("loop", false)))
		for path: String in entry.get("frames", []):
			var texture: Texture2D
			if ResourceLoader.exists(path):
				texture = load(path) as Texture2D
			if texture == null:
				var picture := Image.load_from_file(ProjectSettings.globalize_path(path))
				if picture != null:
					texture = ImageTexture.create_from_image(picture)
			if texture != null:
				frames.add_frame(key, texture)
	return frames

func _physics_process(delta: float) -> void:
	var move := Vector2.ZERO
	if movement_enabled and follow_target != null:
		var delta_position := follow_target.global_position-global_position
		if delta_position.length()>80:
			move = delta_position.normalized()
	elif movement_enabled:
		move.x = float(Input.is_key_pressed(KEY_D) or Input.is_key_pressed(KEY_RIGHT)) - float(Input.is_key_pressed(KEY_A) or Input.is_key_pressed(KEY_LEFT))
		move.y = float(Input.is_key_pressed(KEY_S) or Input.is_key_pressed(KEY_DOWN)) - float(Input.is_key_pressed(KEY_W) or Input.is_key_pressed(KEY_UP))
	velocity = move.normalized() * float(definition.get("movement_speed",180))
	if navigation != null and delta > 0.0 and velocity != Vector2.ZERO:
		velocity = navigation.allowed_motion(global_position,velocity*delta,_foot_offsets)/delta
	var previous_position := global_position
	move_and_slide()
	if move != Vector2.ZERO:
		if absf(move.x) > absf(move.y):
			facing = "right" if move.x > 0 else "left"
		else:
			facing = "down" if move.y > 0 else "up"
	_play("walk" if global_position.distance_squared_to(previous_position)>.01 else "idle")

func _unhandled_key_input(event: InputEvent) -> void:
	if movement_enabled and follow_target == null and event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_SPACE:
		battle_requested.emit(self)

func _play(state: String) -> void:
	var key := "map_"+facing+"_"+state
	if art.sprite_frames.has_animation(key):
		art.visible = true
		art.play(key)
	else:
		art.visible = false
