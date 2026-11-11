extends SceneTree
## Headless check of the hands-on room editor: load, pick, place, move, resize, turn, flip, delete, undo,
## the change list, and a dry-run save through tools/room_editor_save.py (no version is published).
## Agent: claude (Claude Code); model: Fable 5.2.

var _failures := 0


func _check(ok: bool, what: String) -> void:
	if not ok:
		_failures += 1
		print("FAIL: " + what)


func _initialize() -> void:
	var editor: Node = load("res://scenes/map_factory_editor.tscn").instantiate()
	editor.save_dry_run = true
	var python := OS.get_environment("ROOM_EDITOR_PYTHON")
	if python != "":
		editor.python_executable = python
	root.add_child(editor)
	await process_frame
	_check(editor.room != null, "editor builds the room")
	_check(editor.blocks.size() > 50, "editor lists the placed pieces")
	_check(editor.pending_changes().is_empty(), "nothing is pending after loading")
	if editor.room == null:
		quit(1)
		return

	# Pick an existing piece by clicking inside its sprite.
	var bed := "RoyalBed"
	_check(editor.blocks.has(bed), "the bed is editable")
	editor.set_active_layer("objects")
	_check(editor.select_at(editor.rect_of(bed).get_center()) == bed, "clicking the bed selects it")
	_check(editor.select_at(Vector2(-500, -500)) == "", "clicking empty space selects nothing")

	# Move, resize, turn, flip.
	editor.selected = bed
	var start := Vector2(editor.blocks[bed]["x"], editor.blocks[bed]["y"])
	_check(editor.move_selected(start + Vector2(40.4, -12.2)), "move works")
	_check(editor.nodes[bed].position == start + Vector2(40, -12), "the node follows the move, rounded to pixels")
	editor.scale_selected(2)
	_check(is_equal_approx(editor.nodes[bed].scale.x, 1.1), "two wheel steps resize by 0.10")
	var turn_before: float = editor.nodes[bed].rotation_degrees
	editor.rotate_selected(15.0)
	_check(is_equal_approx(editor.nodes[bed].rotation_degrees, turn_before + 15.0), "E turns by 15 degrees")
	editor.flip_selected()
	var bed_change: Dictionary = editor.pending_changes()[0]
	_check(bed_change["op"] == "update" and bed_change["instance_id"] == bed, "the bed edit is one update")
	_check(bed_change["set"].keys().size() == 5, "x, y, size, turn and flip are recorded")

	# Place a new independent piece off the grid, then on the grid.
	editor.set_active_layer("objects")
	var fern: String = editor.place("P05", Vector2(700.3, 500.7))
	_check(fern != "" and editor.nodes.has(fern), "placing adds a piece")
	_check(editor.blocks[fern]["x"] == 700.0 and editor.blocks[fern]["layer"] == "objects", "free placement keeps the clicked pixel")
	_check(editor.place("NO_SUCH_PART", Vector2.ZERO) == "", "an unknown part is refused")
	editor.toggle_snap()
	var tile := float(editor.map_data["tile_size"])
	var origin := Vector2(editor.map_data["ground_offset"][0], editor.map_data["ground_offset"][1])
	var snapped: Vector2 = editor.snapped_point(origin + Vector2(tile * 2.2, tile * 3.7))
	_check(snapped == origin + Vector2(tile * 2.5, tile * 4.0), "grid snap lands on the bottom centre of the square")
	editor.toggle_snap()

	# Delete an existing piece and undo it.
	editor.selected = "FrontBlueVase"
	_check(editor.delete_selected(), "delete works")
	_check(not editor.nodes["FrontBlueVase"].visible, "a deleted piece disappears")
	_check(editor.pending_changes().any(func(c): return c["op"] == "remove" and c["instance_id"] == "FrontBlueVase"), "delete is recorded")
	_check(editor.undo(), "undo works")
	_check(editor.blocks.has("FrontBlueVase") and editor.nodes["FrontBlueVase"].visible, "undo brings the piece back")

	# Undo all the way back restores the loaded room.
	var guard := 0
	while editor.undo() and guard < 50:
		guard += 1
	_check(editor.pending_changes().is_empty(), "undoing everything leaves no change")
	_check(not editor.nodes.has(fern), "the added piece is gone after undo")
	_check(editor.nodes[bed].position == start, "the bed is back where it was")

	# A real edit passes the factory rules (dry run: nothing is published).
	var version_before := int(editor.map_data["version"])
	editor.selected = bed
	editor.move_selected(start + Vector2(10, 0))
	editor.place("P05", Vector2(640, 420))
	var saved: Dictionary = editor.save()
	_check(saved["ok"], "the factory accepts the edit: " + String(saved["message"]))
	_check(String(saved["message"]).begins_with("ROOM_EDITOR_SAVED %s v%04d" % [editor.map_id, version_before + 1]), "save reports the next version")
	var latest: Variant = JSON.parse_string(FileAccess.get_file_as_string("res://map_factory/maps/%s/latest.json" % editor.map_id))
	_check(int(latest["version"]) == version_before, "a dry run publishes nothing")

	# ---- Stage two: ground, levels, copies, redo, maps.
	editor.load_map()
	_check(editor.pending_changes().is_empty(), "reloading clears pending edits")
	var floor_cell := Vector2i(3, 3)
	_check(editor.cell_at(editor.cell_rect(floor_cell).get_center()) == floor_cell, "a point maps back to its square")
	_check(editor.paint_tile(floor_cell, "G05") or String(editor.tiles.get("3:3", "")) == "G05", "painting a floor square works")
	editor.paint_tile(floor_cell, "G09")
	_check(String(editor.tiles["3:3"]) == "G09", "the square carries the painted tile")
	_check(not editor.paint_tile(floor_cell, "P05"), "a non-floor part cannot be painted as ground")
	_check(not editor.paint_tile(Vector2i(-1, 0), "G05"), "painting outside the grid is refused")
	_check(editor.pending_changes().any(func(c): return c["op"] == "tile" and c["x"] == 3 and c["y"] == 3 and c["id"] == "G09"), "the tile edit is recorded")
	var hole := Vector2i(0, 5)
	_check(editor.cells.has("0:5") and editor.erase_cell(hole), "erasing a floor square works")
	_check(editor.pending_changes().any(func(c): return c["op"] == "property" and c["key"] == "floor_footprint"), "the floor shape edit is recorded")
	var spans: Array = editor._row_spans()
	_check(spans.size() == int(editor.map_data["size"][1]) and int(spans[5][0][0]) == 1, "row 5 now starts at square 1")
	var ground_save: Dictionary = editor.save()
	_check(ground_save["ok"], "the factory accepts the ground edit: " + String(ground_save["message"]))
	_check(editor.undo() and editor.cells.has("0:5"), "undo restores the erased square")
	_check(editor.redo() and not editor.cells.has("0:5"), "redo erases it again")
	editor.load_map()

	editor.selected = "FrontBlueVase"
	var copy: String = editor.duplicate_selected()
	_check(copy != "" and editor.blocks[copy]["id"] == editor.blocks["FrontBlueVase"]["id"], "duplicate copies the part")
	_check(is_equal_approx(editor.blocks[copy]["scale"], editor.blocks["FrontBlueVase"]["scale"]), "the copy keeps the size")
	_check(editor.blocks[copy]["x"] == editor.blocks["FrontBlueVase"]["x"] + 24.0, "the copy sits beside the source")
	editor.selected = "FrontBlueVase"
	_check(editor.move_selected_to_layer("front_objects"), "a piece can change level")
	_check(editor.pending_changes().any(func(c): return c["op"] == "update" and c["set"].get("layer") == "front_objects"), "the level change is recorded")
	editor.set_layer_hidden("objects", true)
	_check(not editor.nodes[bed].visible, "hiding a level hides its pieces")
	editor.set_layer_hidden("objects", false)
	_check(editor.nodes[bed].visible, "showing a level shows them again")
	var level_save: Dictionary = editor.save()
	_check(level_save["ok"], "the factory accepts the copy and level change: " + String(level_save["message"]))

	var ids: Array[String] = editor.map_ids()
	_check(ids.has("hero_room_01") and ids.size() >= 2, "the registry lists the maps")
	var other: String = ids[0] if ids[0] != "hero_room_01" else ids[1]
	_check(editor.open_map(other) and editor.map_id == other and editor.room != null, "another map opens")
	_check(not editor.open_map("no_such_map"), "an unknown map is refused")
	_check(editor.create_map("editor_test_map", "courtyard")["ok"], "a new map name and preset are accepted (dry run)")
	_check(not editor.create_map("hero_room_01", "courtyard")["ok"], "an existing map name is refused")
	_check(not editor.create_map("Bad Name", "courtyard")["ok"], "an invalid map name is refused")
	_check(not editor.map_ids().has("editor_test_map"), "a dry run creates nothing")

	# ---- Mouse presses: one placement per pick, Ctrl grabs a piece while a part is armed.
	editor.snap_to_grid = false
	editor.set_active_layer("objects")
	editor.placing_part = "P05"
	var count_before: int = editor.blocks.size()
	editor.press(Vector2(300.0, 300.0))
	_check(editor.blocks.size() == count_before + 1 and editor.placing_part == "", "a click places one piece and disarms the part")
	var laid: String = editor.selected
	_check(laid != "", "the placed piece stays selected")
	editor.placing_part = "P05"
	var centre: Vector2 = editor.rect_of(laid).get_center()
	editor.press(centre, true)
	_check(editor.blocks.size() == count_before + 1 and editor.selected == laid and editor._dragging, "Ctrl+click grabs the piece instead of placing another")
	var x_before: float = editor.blocks[laid]["x"]
	editor.move_selected(Vector2(x_before + 50.0, float(editor.blocks[laid]["y"])))
	_check(editor.blocks[laid]["x"] != x_before, "the grabbed piece moves")
	editor._dragging = false
	editor.press(Vector2(900.0, 100.0), false, true)
	_check(editor.placing_part == "P05" and editor.blocks.size() == count_before + 2, "Shift keeps the part armed for more copies")
	editor.placing_part = ""
	editor.undo()
	editor.undo()
	editor.undo()

	# ---- Battle setup on the map's own squares.
	editor.open_map("hero_room_01")
	editor.battles_dir = "user://test_battles"
	DirAccess.remove_absolute(ProjectSettings.globalize_path(editor.battle_file()))
	editor.load_battle_setup()
	_check(editor.battle_units.is_empty() and editor.battle_blocked.is_empty(), "a map without a battle file starts empty")
	_check(not editor.save_battle()["ok"], "a battle without units is refused")
	editor.set_battle_tool("player")
	_check(editor.battle_click(Vector2i(2, 4)) and editor.battle_click(Vector2i(2, 5)), "player start squares are placed")
	_check(not editor.battle_click(Vector2i(2, 4)), "a taken square is refused")
	_check(not editor.battle_click(Vector2i(5, 0)), "a square without floor cannot hold a unit")
	_check(editor.battle_units[0]["id"] == "hero" and editor.battle_units[0]["character"] == "CHAR001", "the first player unit is the hero")
	_check(not editor.save_battle()["ok"], "a battle without enemies is refused")
	editor.set_battle_tool("enemy")
	_check(editor.battle_click(Vector2i(12, 4)) and editor.battle_click(Vector2i(13, 5)), "enemy start squares are placed")
	editor.set_battle_tool("blocked")
	_check(editor.battle_click(Vector2i(7, 4)) and editor.is_battle_blocked(Vector2i(7, 4)), "a square can be blocked by hand")
	_check(not editor.battle_click(Vector2i(2, 4)), "a unit's square cannot be blocked")
	_check(editor.battle_click(Vector2i(8, 4)) and editor.battle_click(Vector2i(8, 4)) and not editor.is_battle_blocked(Vector2i(8, 4)), "clicking again unblocks")
	editor.set_battle_tool("clear")
	_check(editor.battle_click(Vector2i(13, 5)) and editor.battle_units.size() == 3, "clear removes a unit")
	var battle: Dictionary = editor.battle_definition()
	_check(battle["cols"] == int(editor.map_data["size"][0]) and battle["rows"] == int(editor.map_data["size"][1]), "the battle uses the map's grid")
	_check(battle["blocked"].has([5, 0]) and battle["blocked"].has([7, 4]) and not battle["blocked"].has([2, 4]), "squares without floor and hand-blocked squares are blocked")
	_check(battle["blocked_by_hand"] == [[7, 4]], "hand-blocked squares are kept apart")
	var stored: Dictionary = editor.save_battle()
	_check(stored["ok"] and FileAccess.file_exists(editor.battle_file()), "the battle file is written")
	editor.battle_units.clear()
	editor.battle_blocked.clear()
	_check(editor.load_battle_setup() and editor.battle_units.size() == 3 and editor.battle_blocked.has("7:4"), "the battle file loads back")

	# The skirmish scene plays that file over the map.
	var arena: Node = load("res://scenes/battle/tactical_battle.tscn").instantiate()
	arena.save_path = "user://test_battles/hero.json"
	arena.battle_path = editor.battle_file()
	root.add_child(arena)
	await process_frame
	_check(arena.battle_path == editor.battle_file() and arena._room != null, "the scene loads the battle and builds its map")
	_check(arena.session.size == Vector2i(int(battle["cols"]), int(battle["rows"])), "the session uses the battle's field")
	_check(arena.session.manager.combatants.size() == 3, "the battle's units fight")
	_check(arena.session.manager.blocked.has(Vector2i(7, 4)), "blocked squares block movement")
	_check(arena.cell_rect(Vector2i(0, 0)).position == editor.grid_origin(), "battle squares sit on the map's squares")
	_check(arena.cell_at(editor.cell_rect(Vector2i(2, 4)).get_center()) == Vector2i(2, 4), "a click on the map finds its square")
	var turns := 0
	while not arena.session.is_over() and turns < 600:
		if arena.is_animating():
			arena._process(0.05)
		elif arena.session.is_player_turn():
			var targets: Array[String] = arena.session.target_ids()
			if not targets.is_empty():
				arena.session.attack(targets[0])
			else:
				var options: Array[Vector2i] = arena.session.move_cells()
				var foe = arena.session.manager.alive("enemy")[0]
				options.sort_custom(func(a: Vector2i, b: Vector2i) -> bool: return (a - foe.cell).length_squared() < (b - foe.cell).length_squared())
				if not options.is_empty():
					arena.session.move(options[0])
				var after: Array[String] = arena.session.target_ids()
				if not after.is_empty():
					arena.session.attack(after[0])
				else:
					arena.session.wait()
		else:
			arena.session.step_enemy()
		turns += 1
	_check(arena.session.is_over(), "the edited battle can be fought to the end")
	_check(not arena.load_battle("user://test_battles/missing.json") and arena.session.size == arena.Session.SIZE, "a missing battle falls back to the practice field")
	arena.queue_free()
	DirAccess.remove_absolute(ProjectSettings.globalize_path(editor.battle_file()))

	editor.queue_free()
	if _failures == 0:
		print("ROOM_EDITOR_OK")
	quit(1 if _failures > 0 else 0)
