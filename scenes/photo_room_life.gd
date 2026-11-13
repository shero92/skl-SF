extends Node2D
class_name PhotoRoomLife
## Quiet moving touches over a photo room (a room shown as one painting): a gentle shimmer on the sea,
## flickering lantern light and floor patches. Everything is drawn from the painting itself at run time;
## no art file is created or changed. Breaking waves, clouds and flying creatures need real art
## (ART-0051, ART-0052) and are not faked here.
## Agent: claude (Claude Code); model: Fable 5.2.

const SEA_SHADER := "
shader_type canvas_item;
// Only blue water pixels move, by one or two painting pixels, so rocks, walls and foam edges stay put.
bool is_water(vec4 c) { return c.b > c.r + 0.15 && c.b > c.g + 0.04; }
void fragment() {
	vec2 px = TEXTURE_PIXEL_SIZE;
	vec2 at = UV / px;
	vec4 base = texture(TEXTURE, UV);
	vec2 shift = vec2(sin(at.y * 0.09 + TIME * 1.3) * 2.0, cos(at.x * 0.07 + TIME * 1.1) * 1.5);
	vec4 moved = texture(TEXTURE, UV + floor(shift + 0.5) * px);
	COLOR = base;
	if (is_water(base) && is_water(moved)) {
		COLOR = moved;
		COLOR.rgb += 0.04 * sin(at.x * 0.05 + at.y * 0.11 + TIME * 2.0);
	}
}
"

var glows: Array[Sprite2D] = []
var _time: float = 0.0


## `definition` is the photo room file.
func build(photo: Texture2D, definition: Dictionary) -> void:
	for patch: Dictionary in definition.get("patches", []):
		var from: Array = patch.get("from", [0, 0, 0, 0])
		var to: Array = patch.get("to", [0, 0])
		var cover := Sprite2D.new()
		cover.name = "Patch"
		cover.texture = photo
		cover.centered = false
		cover.region_enabled = true
		cover.region_rect = Rect2(float(from[0]), float(from[1]), float(from[2]), float(from[3]))
		cover.position = Vector2(float(to[0]), float(to[1]))
		add_child(cover)
	var water := ShaderMaterial.new()
	water.shader = Shader.new()
	water.shader.code = SEA_SHADER
	for points: Array in definition.get("sea", []):
		var sea := Polygon2D.new()
		sea.name = "Sea"
		var outline := PackedVector2Array()
		for point: Array in points:
			outline.append(Vector2(float(point[0]), float(point[1])))
		sea.polygon = outline
		sea.texture = photo  # without explicit UVs a polygon samples the texture at its own pixel positions
		sea.material = water
		add_child(sea)
	var gradient := Gradient.new()
	gradient.set_color(0, Color(1.0, 0.82, 0.45, 0.55))
	gradient.set_color(1, Color(1.0, 0.7, 0.3, 0.0))
	var halo := GradientTexture2D.new()
	halo.gradient = gradient
	halo.fill = GradientTexture2D.FILL_RADIAL
	halo.fill_from = Vector2(0.5, 0.5)
	halo.fill_to = Vector2(1.0, 0.5)
	halo.width = 128
	halo.height = 128
	var additive := CanvasItemMaterial.new()
	additive.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	for light: Array in definition.get("lanterns", []):
		var glow := Sprite2D.new()
		glow.name = "LanternGlow"
		glow.texture = halo
		glow.material = additive
		glow.position = Vector2(float(light[0]), float(light[1]))
		glow.scale = Vector2.ONE * float(light[2]) / 64.0
		add_child(glow)
		glows.append(glow)


func _process(delta: float) -> void:
	_time += delta
	for index in glows.size():
		# Two slow waves and one quick one per lantern, each out of step with its neighbours.
		var phase := float(index) * 1.7
		glows[index].modulate.a = 0.72 + 0.16 * sin(_time * 2.1 + phase) + 0.08 * sin(_time * 7.3 + phase * 2.0) + 0.04 * sin(_time * 13.0 + phase)
