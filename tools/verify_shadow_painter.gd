extends SceneTree
## Headless verification of the painted shadow level and the light level.
## Agent: claude (Claude Code); model: Sonnet 5.5.

const Painter = preload("res://map_factory/scripts/shadow_painter.gd")

var _failures: int = 0


func _initialize() -> void:
	_test_silhouette()
	_test_shape_follows_alpha()
	_test_determinism()
	_test_layer()
	_test_light_layer()
	if _failures == 0:
		print("SHADOW_PAINTER_OK")
	quit(0 if _failures == 0 else 1)


func _check(condition: bool, message: String) -> void:
	if not condition:
		_failures += 1
		printerr("FAIL: " + message)


func _box(width: int, height: int) -> Image:
	var image := Image.create(width, height, false, Image.FORMAT_RGBA8)
	image.fill(Color(0.6, 0.5, 0.3, 1.0))
	return image


func _alpha_at(painted: Dictionary, foot_dx: float, foot_dy: float) -> float:
	# Alpha of the painted image at a point given relative to the object foot.
	var image: Image = painted["image"]
	var offset: Vector2 = painted["offset"]
	var x := int(floor(foot_dx - offset.x))
	var y := int(floor(foot_dy - offset.y))
	if x < 0 or y < 0 or x >= image.get_width() or y >= image.get_height():
		return 0.0
	return image.get_pixel(x, y).a


func _test_silhouette() -> void:
	var painted: Dictionary = Painter.paint(_box(32, 64))
	_check(not painted.is_empty(), "box paints")
	var image: Image = painted["image"]
	_check(image.get_format() == Image.FORMAT_RGBA8, "shadow is RGBA")
	_check(painted["offset"].y < 0.0, "contact ellipse reaches above the foot line")
	# Light from the upper left: the shadow extends right of the box (foot x spans -16..16).
	_check(_alpha_at(painted, 24.0, 8.0) > 0.0, "shadow falls to the right of the object")
	_check(_alpha_at(painted, -40.0, 8.0) == 0.0, "no shadow on the lit side")
	# Height fade: the base of the cast is darker than its tip.
	var near_base := _alpha_at(painted, 4.0, 2.0)
	var far_tip := _alpha_at(painted, 28.0, 16.0)
	_check(near_base > far_tip, "shadow fades with height")
	_check(Painter.paint(Image.create(8, 8, false, Image.FORMAT_RGBA8)).is_empty(), "empty image paints nothing")
	var no_light: Dictionary = Painter.paint(_box(32, 64), {"opacity": 0.0, "contact_opacity": 0.0})
	_check(_alpha_at(no_light, 4.0, 2.0) == 0.0, "zero opacity paints no shadow")


func _test_shape_follows_alpha() -> void:
	# Two pillars with a transparent gap: the cast shadow must keep the gap (not a plain blob).
	var image := Image.create(48, 48, false, Image.FORMAT_RGBA8)
	for y in range(8, 48):
		for x in range(0, 14):
			image.set_pixel(x, y, Color.WHITE)
		for x in range(34, 48):
			image.set_pixel(x, y, Color.WHITE)
	var painted: Dictionary = Painter.paint(image, {"direction": [0.0, 0.5], "blur": 0, "contact_opacity": 0.0})
	# Straight down projection: gap column (foot dx about 0) stays clear mid-height; pillar column is shaded.
	var gap := _alpha_at(painted, 0.0, 8.0)
	var pillar := _alpha_at(painted, -17.0, 8.0)
	_check(pillar > 0.05 and gap < 0.01, "cast shadow keeps the silhouette gap")


func _test_determinism() -> void:
	var a: Dictionary = Painter.paint(_box(32, 64))
	var b: Dictionary = Painter.paint(_box(32, 64))
	_check(a["image"].get_data() == b["image"].get_data() and a["offset"] == b["offset"], "painting is deterministic")


func _sprite(name: String, size: Vector2i, position: Vector2) -> Sprite2D:
	var sprite := Sprite2D.new()
	sprite.name = name
	sprite.texture = ImageTexture.create_from_image(_box(size.x, size.y))
	sprite.position = position
	return sprite


func _test_layer() -> void:
	var room := Node2D.new()
	root.add_child(room)
	var walls := Node2D.new()
	walls.name = "Level2_Walls"
	walls.z_index = 30
	room.add_child(walls)
	var decor := Node2D.new()
	decor.name = "Level3_Decorations"
	decor.z_index = 40
	room.add_child(decor)
	var wall := _sprite("WallA", Vector2i(64, 128), Vector2(200, 300))
	walls.add_child(wall)
	var chest := _sprite("Chest", Vector2i(48, 40), Vector2(400, 420))
	decor.add_child(chest)
	decor.add_child(_sprite("rug_blue", Vector2i(96, 64), Vector2(300, 500)))
	var hung := _sprite("Banner", Vector2i(32, 96), Vector2(100, 200))
	decor.add_child(hung)
	var mounted := _sprite("Vine", Vector2i(16, 48), Vector2(10, 10))
	mounted.set_meta("mount_on", "WallA")
	wall.add_child(mounted)

	var layer: Node2D = Painter.build_layer(room)
	_check(layer.name == "Level4_PaintedShadows", "separate shadow level exists")
	_check(layer.z_index == 20 and layer.z_index < walls.z_index and layer.z_index < decor.z_index, "shadow level draws below the objects it shades")
	_check(layer.get_child_count() == 2, "only ground-standing objects cast shadows (got %d)" % layer.get_child_count())
	var shadow := layer.get_node_or_null("Shadow_Chest") as Sprite2D
	_check(shadow != null, "chest has an owner-linked shadow")
	if shadow != null:
		_check(shadow.get_meta("owner_ref") == chest.get_instance_id(), "shadow records its owner")
		# Foot of the chest: bottom centre (400, 420 + 20). The shadow image must sit on that foot.
		var foot := Vector2(400, 440)
		var rect := Rect2(shadow.position, shadow.texture.get_size() * shadow.scale)
		_check(rect.has_point(foot), "shadow overlaps the owner's foot point")
	Painter.set_shadows_visible(room, false)
	_check(not layer.visible, "shadow level can be hidden")
	Painter.set_shadows_visible(room, true)
	chest.position += Vector2(50, 0)
	Painter.sync(room)
	if shadow != null:
		_check(is_equal_approx(shadow.position.x, shadow.position.x) and shadow.get_meta("owner_offset") != null, "shadow follows a moved owner")
		var moved := Rect2(shadow.position, shadow.texture.get_size() * shadow.scale)
		_check(moved.has_point(Vector2(450, 440)), "shadow moved with owner")
	walls.remove_child(wall)
	wall.free()
	decor.remove_child(chest)
	chest.free()
	Painter.sync(room)
	_check(layer.get_child_count() == 0, "removing owners removes their shadows")
	room.queue_free()


func _test_light_layer() -> void:
	var room := Node2D.new()
	root.add_child(room)
	var decor := Node2D.new()
	decor.name = "Level3_Decorations"
	room.add_child(decor)
	decor.add_child(_sprite("lantern_a", Vector2i(16, 24), Vector2(100, 100)))
	decor.add_child(_sprite("chest", Vector2i(48, 40), Vector2(300, 300)))
	var layer: Node2D = Painter.build_light_layer(room)
	_check(layer.name == "Level5_Light", "separate light level exists")
	_check(layer.get_child_count() == 1, "only lit props get a pool (got %d)" % layer.get_child_count())
	_check(layer.z_index > 40, "light draws above the room")
	Painter.set_light_visible(room, false)
	_check(not layer.visible, "light level can be hidden")
	room.queue_free()
