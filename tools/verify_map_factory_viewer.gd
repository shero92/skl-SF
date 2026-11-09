extends SceneTree
## Headless verification of the live Map Factory viewer.
## Agent: claude (Claude Code); model: Sonnet 5.5.

const Viewer = preload("res://scenes/map_factory_viewer.gd")
const TEMP_MAP := "user://viewer_test_map.json"

var _failures: int = 0


func _initialize() -> void:
	call_deferred("_run")


func _check(condition: bool, message: String) -> void:
	if not condition:
		_failures += 1
		printerr("FAIL: " + message)


func _write_map(note: String) -> void:
	var source := FileAccess.get_file_as_string("res://map_factory/maps/hero_room_01/versions/v0014.json")
	var data: Dictionary = JSON.parse_string(source)
	data["change_note"] = note
	var file := FileAccess.open(TEMP_MAP, FileAccess.WRITE)
	file.store_string(JSON.stringify(data))
	file.close()


func _run() -> void:
	_write_map("first")
	var viewer = Viewer.new()
	viewer.map_path = TEMP_MAP
	viewer.poll_seconds = 0.0
	root.add_child(viewer)
	await process_frame
	_check(viewer.room != null, "viewer builds the room")
	_check(viewer.reload_count == 1, "loaded once")
	for key in ["background", "ground", "walls", "decor", "shadows", "light"]:
		_check(viewer.set_level_visible(key, false), "level exists: " + key)
		_check(not viewer.is_level_visible(key), "level hidden: " + key)
		viewer.set_level_visible(key, true)
	_check(not viewer.set_level_visible("nonsense", true), "unknown level rejected")
	_check(viewer.room.get_node_or_null("Level4_PaintedShadows") != null, "painted shadow level built on demand")
	_check(viewer.room.get_node_or_null("Level5_Light") != null, "light level built on demand")
	viewer.set_painted_shadows(false)
	_check(not viewer.room.get_node("Level4_PaintedShadows").visible, "painted shadows off")
	_check(viewer.room.get_node("Level4_Shadows").visible, "strip shadows back on")
	viewer.set_painted_shadows(true)
	_check(viewer.room.get_node("Level4_PaintedShadows").visible, "painted shadows on")
	_check(not viewer.file_changed(), "no change yet")
	# Touch the file with a different modification time and content: the viewer reloads.
	OS.delay_msec(1100)
	_write_map("second")
	_check(viewer.file_changed(), "file change detected")
	_check(viewer.reload_if_changed(), "reload performed")
	_check(viewer.reload_count == 2 and viewer.room != null, "reloaded once more")
	_check(not viewer.reload_if_changed(), "no reload when unchanged")
	DirAccess.remove_absolute(ProjectSettings.globalize_path(TEMP_MAP))
	if _failures == 0:
		print("MAP_VIEWER_OK")
	quit(0 if _failures == 0 else 1)
