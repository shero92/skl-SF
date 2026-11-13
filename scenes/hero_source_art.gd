extends Node2D
class_name HeroSourceArt
## Draws the hero from the high-resolution map source frames (1254 px each) instead of the 96 px game frames.
## The sources are local files that Godot does not import, so they are read from disk, reduced once in memory
## and never written back. When a source is missing the caller keeps its normal sprite.
## Agent: claude (Claude Code); model: Fable 5.2.

const INDEX := "res://game_factory/hero_map_source_frames.json"
const WORK_HEIGHT := 320.0  # figure height of the in-memory copy; drawn smaller with mipmaps for a clean edge

const OUTLINE_SHADER := "
shader_type canvas_item;
// A dark one-pixel rim around the figure, the way classic tactical RPG sprites stand out from the floor.
uniform float reach = 2.5;  // rim width in texture pixels (one room pixel)
void fragment() {
	vec4 c = texture(TEXTURE, UV);
	float near = 0.0;
	for (int i = 0; i < 8; i++) {
		float a = float(i) * 0.7853982;
		near = max(near, texture(TEXTURE, UV + vec2(cos(a), sin(a)) * reach * TEXTURE_PIXEL_SIZE).a);
	}
	vec4 rim = vec4(0.13, 0.08, 0.07, near);
	COLOR = mix(rim, vec4(c.rgb, 1.0), c.a);
	COLOR.a = max(c.a, near * 0.95);
}
"

var figure_height: float = 128.0  # height on screen in room pixels
## Vertical squash toward the room's three-quarter camera (about 50 degrees down): the drawing is a straight-on view,
## so a floor view foreshortens it. 1.0 leaves the drawing as it is.
var view_squash: float = 1.0
var _index: Dictionary = {}
var _frames: Dictionary = {}  # animation key -> Array of {texture, offset}
var _sprite: Sprite2D
var _key: String = ""
var _elapsed: float = 0.0


func _ready() -> void:
	var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(INDEX)) if FileAccess.file_exists(INDEX) else null
	if data is Dictionary:
		_index = data
	var shadow := Polygon2D.new()  # soft ground shadow so the figure stands on the floor
	shadow.name = "GroundShadow"
	var ring := PackedVector2Array()
	for step in 20:
		var turn := TAU * step / 20.0
		ring.append(Vector2(cos(turn) * figure_height * 0.27, sin(turn) * figure_height * 0.085 - 3.0))
	shadow.polygon = ring
	shadow.color = Color(0.1, 0.06, 0.02, 0.38)
	add_child(shadow)
	# A long soft shadow thrown to the lower right (the light comes from the upper left): he is tall, so it is long.
	var cast := Polygon2D.new()
	cast.name = "CastShadow"
	var tall := figure_height
	cast.polygon = PackedVector2Array([Vector2(-tall * 0.16, -3), Vector2(tall * 0.16, -3), Vector2(tall * 0.16 + tall * 0.55, tall * 0.2), Vector2(-tall * 0.16 + tall * 0.55, tall * 0.2)])
	cast.vertex_colors = PackedColorArray([Color(0.05, 0.03, 0.1, 0.4), Color(0.05, 0.03, 0.1, 0.4), Color(0.05, 0.03, 0.1, 0.0), Color(0.05, 0.03, 0.1, 0.0)])
	add_child(cast)
	_sprite = Sprite2D.new()
	_sprite.name = "SourceFrame"
	_sprite.centered = false
	_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	var rim := ShaderMaterial.new()
	rim.shader = Shader.new()
	rim.shader.code = OUTLINE_SHADER
	rim.set_shader_parameter("reach", WORK_HEIGHT / figure_height)
	_sprite.material = rim
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
	_sprite.scale = Vector2(size, size * view_squash)
	_sprite.position = -Vector2(frame["offset"].x * size, frame["offset"].y * size * view_squash)
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
