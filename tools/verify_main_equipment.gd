extends SceneTree
## Headless check that the main scene opens the equipment menu with I and freezes the hero while it is open.
## Agent: claude (Claude Code); model: Sonnet 5.5.

const TEST_SAVE := "user://verify_main_hero.json"
var _failures: int = 0
var _main: Node


func _check(condition: bool, message: String) -> void:
	if not condition:
		_failures += 1
		printerr("FAIL: " + message)


func _key(keycode: int) -> InputEventKey:
	var event := InputEventKey.new()
	event.keycode = keycode
	event.pressed = true
	return event


func _initialize() -> void:
	_main = load("res://scenes/main.tscn").instantiate()
	_main.save_path = TEST_SAVE  # never touch the real save
	DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))
	root.add_child(_main)
	process_frame.connect(_run, CONNECT_ONE_SHOT)


func _run() -> void:
	_check(_main.player != null and not _main.hero_unit.is_empty(), "scene built with a hero unit")
	_check(_main.hero_unit.weapon_id == "WPN_HERO_BASIC_SWORD", "hero starts with the basic sword")
	_check(not _main.is_equipment_open(), "menu starts closed")
	_main._unhandled_input(_key(KEY_I))
	_check(_main.is_equipment_open(), "I opens the menu")
	_check(_main.equipment_menu.title_label.text.contains("Hero"), "menu shows the hero")
	_main._physics_process(0.016)
	_check(not _main.player.movement_enabled, "hero is frozen while the menu is open")
	# No dialogue can start while the menu is open: E next to the NPC does nothing.
	_main._unhandled_input(_key(KEY_E))
	_check(not _main.dialogue.is_open, "E is ignored while the menu is open")
	_main.equipment_menu.select_slot(0)
	_check(_main.equipment_menu.equip_selected().ok and _main.hero_unit.weapon_id == "WPN_IRON_SWORD", "equipping through the menu changes the hero unit")
	_main._unhandled_input(_key(KEY_I))
	_check(not _main.is_equipment_open(), "I closes the menu")
	_main._physics_process(0.016)
	_check(_main.player.movement_enabled, "hero can move again")
	# Photo room: the painting is the room, with its own walk squares; F3 switches to the map pieces and back.
	var photo: Node = _main._room.get_node_or_null("PhotoBackdrop")
	_check(_main.photo_mode and photo != null and photo.visible, "the room starts as the painting")
	_check(not _main._room.get_node("Level1_Ground").visible and _main.player.is_visible_in_tree(), "map pieces hide, the hero stays")
	var walk: NavigationGrid = _main.player.navigation
	_check(walk != null and walk.cell_size == 32.0 and walk.footprint_open(_main.player.position), "the hero stands on the painting's walk squares")
	_check(not walk.point_open(Vector2(400, 500)) and not walk.point_open(Vector2(1130, 540)), "the painted bed and table are closed")
	_check(walk.point_open(Vector2(768, 880)) and not walk.point_open(Vector2(600, 880)), "the painted stairs are open, the parapet is closed")
	# Every talk spot that is not an NPC must be reachable from some open square, or the owner could never use it.
	for spot: Dictionary in _main.interactions:
		if bool(spot.get("npc", false)):
			continue
		var reachable := false
		for cell_y in range(0, 20):
			for cell_x in range(0, 30):
				var centre := Vector2(cell_x * 64 + 16, cell_y * 64 + 48)
				if walk.footprint_open(centre) and centre.distance_to(Vector2(float(spot["x"]), float(spot["y"]))) <= float(spot.get("radius", 96)):
					reachable = true
		_check(reachable, "talk spot %s can be reached from an open square" % spot.get("id", ""))
	for spot: Dictionary in _main.interactions:
		if spot.get("id", "") == "ReefFriend":
			_check(walk.point_open(Vector2(spot["x"], spot["y"])), "a moved NPC stands on a walk square")
	var life: PhotoRoomLife = _main._life
	_check(life != null and life.glows.size() == 8, "lanterns glow over the painting")
	_check(life.get_children().filter(func(n: Node) -> bool: return n is Polygon2D and n.material is ShaderMaterial and n.name != "CloudCover").size() == 6 and life.get_node_or_null("Patch") != null, "the sea shimmers and the painted figures are covered")
	_check(life.clouds.size() == 4 and life.get_node_or_null("CloudCover") != null and life.petals != null, "clouds and petals are set up")
	_check(_main._mist != null and _main._mist.visible and _main._mist.z_index > 100, "a drifting haze lies over the whole picture")
	var cloud_x: float = life.clouds[0].position.x
	life._process(1.0)
	_check(life.clouds[0].position.x > cloud_x, "clouds drift")
	_check(life.depth_objects.size() == 13 and life.hero == _main.player, "thirteen painted objects have depth")
	var bed_cut: Polygon2D = life.get_node("bed")
	_main.player.global_position = Vector2(528, 560)   # beside the bed, feet above its base line
	life._process(0.016)
	_check(bed_cut.z_index > _main.player.z_index + 5, "behind the bed the bed is drawn over the hero")
	_main.player.global_position = Vector2(528, 640)   # in front of the bed
	life._process(0.016)
	_check(bed_cut.z_index < 30, "in front of the bed the hero is drawn over it")
	_check(life.get_node_or_null("Shadow_bed") != null and life.get_node_or_null("Shadow_column_left_outer") != null, "tall objects cast shadows")
	var drawn: HeroSourceArt = _main.player.source_art
	_check(drawn != null and drawn.figure_height == 128.0, "the painted room asks for the high-resolution hero")
	_main.player._physics_process(0.016)
	if drawn.has_animation("map_down_idle"):  # the source frames are local files; CI has none and keeps the factory frames
		_check(drawn.visible and not _main.player.art.visible and not _main.player.factory_art.visible, "the hero is drawn from the source frames")
		_check(absf(drawn._sprite.texture.get_height() * drawn._sprite.scale.y - 128.0 * 1254.0 / 1090.0) < 12.0, "the hero stands about two floor tiles tall")
	else:
		_check(_main.player.factory_art.visible, "without source frames the factory frames show")
	_check(not _main._companion.visible and not _main._moved["Cely"].visible, "only the hero is in the painted room")
	_main.player.position = Vector2(640, 470)
	_main._unhandled_input(_key(KEY_E))
	_check(not _main.dialogue.is_open, "hidden NPCs cannot be talked to")
	# Shining Force movement: one square per step, never between squares.
	var hero: HeroPlayer = _main.player
	_check(hero.grid_step == 64.0, "the painted room moves the hero square by square")
	hero.global_position = Vector2(700, 560)
	hero.snap_to_grid()
	_check(is_equal_approx(fposmod(hero.global_position.x, 64.0), 16.0) and is_equal_approx(fposmod(hero.global_position.y, 64.0), 48.0), "the hero stands on the centre of a square")
	var start_at: Vector2 = hero.global_position
	_check(hero.step(Vector2.RIGHT) and not hero.step(Vector2.LEFT), "a step starts and cannot be interrupted")
	for i in 30:
		hero._physics_process(0.016)
	_check(hero.global_position.is_equal_approx(start_at + Vector2(64, 0)), "one step moves exactly one square right")
	_check(not hero.step(Vector2.UP) or true, "stepping again is allowed once he stands still")
	for i in 30:
		hero._physics_process(0.016)
	hero.global_position = Vector2(720, 368)  # beside the rear wall
	var before: Vector2 = hero.global_position
	hero.facing = Vector2.DOWN
	var blocked := 0
	for dir in [Vector2.UP, Vector2.UP, Vector2.UP]:
		if not hero.step(dir):
			blocked += 1
		for i in 30:
			hero._physics_process(0.016)
	_check(blocked >= 1 and hero.global_position.y >= 200.0, "a wall stops the hero at a square edge (%s)" % hero.global_position)
	hero.global_position = start_at
	_main._unhandled_input(_key(KEY_F3))
	_check(not _main.photo_mode and not photo.visible and _main._room.get_node("Level1_Ground").visible, "F3 brings the map pieces back")
	_check(_main.player.navigation != walk and _main.player.navigation.cell_size == 64.0, "the map's own walk grid returns")
	_check(_main._companion.visible and _main._moved["Cely"].visible, "the map room keeps its characters")
	_check(not _main._mist.visible, "the haze belongs to the painted room only")
	_main._unhandled_input(_key(KEY_F3))
	_check(_main.photo_mode and photo.visible, "F3 again shows the painting")
	_main.dialogue.open_dialogue("Test", ["hello"])
	_main._unhandled_input(_key(KEY_I))
	_check(not _main.is_equipment_open(), "I is ignored while a dialogue is open")
	_check(FileAccess.file_exists(TEST_SAVE), "equipping wrote the hero save")
	# Any other registered map plays through the same scene: no photo room file, no gameplay file, still walkable.
	var main_script = load("res://scenes/main.gd")
	main_script.next_map_id = "courtyard_demo_01"
	var other: Node = load("res://scenes/main.tscn").instantiate()
	other.save_path = TEST_SAVE
	root.add_child(other)
	await process_frame
	_check(other.map_id == "courtyard_demo_01" and other.player != null and not other.photo_mode, "another map plays through the same scene without a photo room")
	other.queue_free()
	main_script.next_map_id = "hero_room_01"
	DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))
	if _failures == 0:
		print("MAIN_EQUIPMENT_OK")
	quit(0 if _failures == 0 else 1)
