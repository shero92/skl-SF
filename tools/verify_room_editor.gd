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

	editor.queue_free()
	if _failures == 0:
		print("ROOM_EDITOR_OK")
	quit(1 if _failures > 0 else 0)
