extends Node2D
class_name HeroSourceArt
## Draws the hero from the high-resolution map source frames (1254 px each) instead of the 96 px game frames.
## The sources are local files that Godot does not import, so they are read from disk, reduced once in memory
## and never written back. When a source is missing the caller keeps its normal sprite.
## Agent: claude (Claude Code); model: Fable 5.2.

const INDEX := "res://game_factory/hero_map_source_frames.json"
const WORK_HEIGHT := 320.0  # figure height of the in-memory copy; drawn smaller with mipmaps for a clean edge

var figure_height: float = 128.0  # height on screen in room pixels
var _index: Dictionary = {}
var _frames: Dictionary = {}  # animation key -> Array of {texture, offset}
var _sprite: Sprite2D
var _key: String = ""
var _elapsed: float = 0.0


func _ready() -> void:
	var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(INDEX)) if FileAccess.file_exists(INDEX) else null
	if data is Dictionary:
		_index = data
	_sprite = Sprite2D.new()
	_sprite.name = "SourceFrame"
	_sprite.centered = false
	_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	add_child(_sprite)


## True when every frame of the animation could be read.
func has_animation(key: String) -> bool:
	return not _load(key).is_empty()


## Shows the animation ("map_down_idle" ...). Returns false when its sources are not on this machine.
func play(state: String, direction: String, delta: float) -> bool:
	var key := "map_%s_%s" % [direction, state]
	var frames := _load(key)
	if frames.is_empty():
		visible = false
		return false
	if key != _key:
		_key = key
		_elapsed = 0.0
	_elapsed += delta
	var frame: Dictionary = frames[int(_elapsed * float(_index.get("fps", {}).get(state, 4))) % frames.size()]
	var size := figure_height / WORK_HEIGHT
	_sprite.texture = frame["texture"]
	_sprite.scale = Vector2.ONE * size
	_sprite.position = -Vector2(frame["offset"]) * size
	visible = true
	return true


func _load(key: String) -> Array:
	if _frames.has(key):
		return _frames[key]
	var loaded: Array = []
	var height := float(_index.get("figure_heights", {}).get(key, 0))
	for record: Dictionary in _index.get("animations", {}).get(key, []):
		var image := Image.load_from_file(ProjectSettings.globalize_path(String(record["path"])))
		if image == null or image.is_empty() or height <= 0.0:
			loaded = []
			break
		var ratio := WORK_HEIGHT / height
		image.resize(maxi(1, roundi(image.get_width() * ratio)), maxi(1, roundi(image.get_height() * ratio)), Image.INTERPOLATE_LANCZOS)
		image.generate_mipmaps()
		loaded.append({"texture": ImageTexture.create_from_image(image),
			"offset": Vector2(float(record["anchor"][0]), float(record["anchor"][1])) * ratio})
	_frames[key] = loaded
	return loaded
