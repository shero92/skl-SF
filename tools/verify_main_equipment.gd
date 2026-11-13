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
	for spot: Dictionary in _main.interactions:
		if spot.get("id", "") == "ReefFriend":
			_check(walk.point_open(Vector2(spot["x"], spot["y"])), "a moved NPC stands on a walk square")
	var life: PhotoRoomLife = _main._life
	_check(life != null and life.glows.size() == 8, "lanterns glow over the painting")
	_check(life.get_children().filter(func(n: Node) -> bool: return n is Polygon2D and n.name != "CloudCover").size() == 6 and life.get_node_or_null("Patch") != null, "the sea shimmers and the painted figures are covered")
	_check(life.clouds.size() == 4 and life.get_node_or_null("CloudCover") != null and life.splashes.size() == 11 and life.petals != null, "clouds, spray and petals are set up")
	var cloud_x: float = life.clouds[0].position.x
	life._process(1.0)
	_check(life.clouds[0].position.x > cloud_x and life.splashes[0].emitting, "clouds drift and spray bursts")
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
	_main._unhandled_input(_key(KEY_F3))
	_check(not _main.photo_mode and not photo.visible and _main._room.get_node("Level1_Ground").visible, "F3 brings the map pieces back")
	_check(_main.player.navigation != walk and _main.player.navigation.cell_size == 64.0, "the map's own walk grid returns")
	_check(_main._companion.visible and _main._moved["Cely"].visible, "the map room keeps its characters")
	_main._unhandled_input(_key(KEY_F3))
	_check(_main.photo_mode and photo.visible, "F3 again shows the painting")
	_main.dialogue.open_dialogue("Test", ["hello"])
	_main._unhandled_input(_key(KEY_I))
	_check(not _main.is_equipment_open(), "I is ignored while a dialogue is open")
	_check(FileAccess.file_exists(TEST_SAVE), "equipping wrote the hero save")
	DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))
	if _failures == 0:
		print("MAIN_EQUIPMENT_OK")
	quit(0 if _failures == 0 else 1)
