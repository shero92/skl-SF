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
	# F3: the target painting as one backdrop (owner test); the map pieces hide, characters stay.
	_main._unhandled_input(_key(KEY_F3))
	var photo: Node = _main._room.get_node_or_null("PhotoBackdrop")
	_check(_main.photo_mode and photo != null and photo.visible, "F3 shows the painting backdrop")
	_check(not _main._room.get_node("Level1_Ground").visible and _main.player.is_visible_in_tree(), "map pieces hide, the hero stays")
	_main._unhandled_input(_key(KEY_F3))
	_check(not _main.photo_mode and not photo.visible and _main._room.get_node("Level1_Ground").visible, "F3 again brings the map pieces back")
	_main.dialogue.open_dialogue("Test", ["hello"])
	_main._unhandled_input(_key(KEY_I))
	_check(not _main.is_equipment_open(), "I is ignored while a dialogue is open")
	_check(FileAccess.file_exists(TEST_SAVE), "equipping wrote the hero save")
	DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))
	if _failures == 0:
		print("MAIN_EQUIPMENT_OK")
	quit(0 if _failures == 0 else 1)
