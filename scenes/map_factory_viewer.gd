extends Node2D
## Live Map Factory viewer (TASK-0111): loads a map snapshot, reloads it when the JSON file
## changes and toggles each level independently. Keys 1-6 toggle the levels, R reloads,
## P switches between strip shadows and painted shadows.
## Agent: claude (Claude Code); model: Sonnet 5.5.

const LEVELS := {
	"background": "Level0_Background",
	"ground": "Level1_Ground",
	"walls": "Level2_Walls",
	"decor": "Level3_Decorations",
	"shadows": "Level4_PaintedShadows",
	"light": "Level5_Light",
}
const KEY_ORDER := ["background", "ground", "walls", "decor", "shadows", "light"]

@export var map_path: String = "res://map_factory/maps/hero_room_01/latest.json"
@export var poll_seconds: float = 0.5

var room: Node2D
var painted_shadows: bool = true
var light_pools: bool = true
var reload_count: int = 0
var _visible := {"background": true, "ground": true, "walls": true, "decor": true, "shadows": true, "light": true}
var _stamp: int = 0
var _elapsed: float = 0.0


func _ready() -> void:
	load_map(map_path)


func load_map(path: String) -> bool:
	map_path = path
	if room != null:
		remove_child(room)
		room.free()
		room = null
	if not FileAccess.file_exists(path):
		push_error("Map file missing: " + path)
		return false
	var built: Node2D = RoomFactory.new().build_room(path, self)
	if built == null:
		return false
	room = built
	_stamp = FileAccess.get_modified_time(path)
	reload_count += 1
	_apply_shadow_mode()
	for key in _visible:
		set_level_visible(key, _visible[key])
	return true


func _apply_shadow_mode() -> void:
	if room == null:
		return
	var strips := room.get_node_or_null("Level4_Shadows")
	if strips != null:
		strips.visible = not painted_shadows
	var lighting: Dictionary = {}
	var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(map_path))
	if typeof(data) == TYPE_DICTIONARY:
		lighting = data.get("lighting", {})
	if painted_shadows and room.get_node_or_null(ShadowPainter.SHADOW_LAYER) == null:
		ShadowPainter.build_layer(room, lighting)
	if light_pools and room.get_node_or_null(ShadowPainter.LIGHT_LAYER) == null:
		ShadowPainter.build_light_layer(room)


func set_level_visible(key: String, shown: bool) -> bool:
	if not LEVELS.has(key):
		return false
	_visible[key] = shown
	if room == null:
		return false
	var node := room.get_node_or_null(LEVELS[key])
	if node == null:
		return false
	node.visible = shown
	return true


func is_level_visible(key: String) -> bool:
	return bool(_visible.get(key, false))


func set_painted_shadows(enabled: bool) -> void:
	painted_shadows = enabled
	if room == null:
		return
	var strips := room.get_node_or_null("Level4_Shadows")
	if strips != null:
		strips.visible = not enabled
	if enabled and room.get_node_or_null(ShadowPainter.SHADOW_LAYER) == null:
		_apply_shadow_mode()
	ShadowPainter.set_shadows_visible(room, enabled and _visible["shadows"])


## True when the map file changed on disk since it was loaded.
func file_changed() -> bool:
	return FileAccess.file_exists(map_path) and FileAccess.get_modified_time(map_path) != _stamp


func reload_if_changed() -> bool:
	if file_changed():
		return load_map(map_path)
	return false


func _process(delta: float) -> void:
	_elapsed += delta
	if _elapsed >= poll_seconds:
		_elapsed = 0.0
		reload_if_changed()


func _unhandled_key_input(event: InputEvent) -> void:
	var key := event as InputEventKey
	if key == null or not key.pressed or key.echo:
		return
	var index := key.keycode - KEY_1
	if index >= 0 and index < KEY_ORDER.size():
		var name: String = KEY_ORDER[index]
		set_level_visible(name, not is_level_visible(name))
	elif key.keycode == KEY_R:
		load_map(map_path)
	elif key.keycode == KEY_P:
		set_painted_shadows(not painted_shadows)
