extends Node2D
class_name PhotoRoomLife
## Moving touches over a photo room (a room shown as one painting): rippling, glinting sea, pixel spray where
## the painted foam meets the rocks, clouds cut from the painting's own sky, drifting petals, flickering
## lantern light and floor patches. Everything comes from the painting itself or from plain pixel particles
## at run time; no art file is created or changed. Drawn creatures and breaking-wave sheets are requested
## as real art (ART-0051, ART-0052).
## Agent: claude (Claude Code); model: Fable 5.2.

const SEA_SHADER := "
shader_type canvas_item;
// Only blue water pixels move, by one or two painting pixels, so rocks, walls and foam edges stay put.
bool is_water(vec4 c) { return c.b > c.r + 0.15 && c.b > c.g + 0.04; }
void fragment() {
	vec2 px = TEXTURE_PIXEL_SIZE;
	vec2 at = UV / px;
	vec4 base = texture(TEXTURE, UV);
	vec2 shift = vec2(sin(at.y * 0.09 + TIME * 1.5) * 3.0, cos(at.x * 0.07 + TIME * 1.2) * 2.0);
	vec4 moved = texture(TEXTURE, UV + floor(shift + 0.5) * px);
	COLOR = base;
	if (is_water(base) && is_water(moved)) {
		COLOR = moved;
		COLOR.rgb += 0.04 * sin(at.x * 0.05 + at.y * 0.11 + TIME * 2.0);
		// Sun glints: single painting pixels that flash white for a moment, each on its own clock.
		vec2 cell = floor(at / 2.0);
		float seed = fract(sin(dot(cell, vec2(12.9898, 78.233))) * 43758.5453);
		float flash = smoothstep(0.985, 1.0, sin(TIME * (1.5 + seed * 2.5) + seed * 6.2832));
		COLOR.rgb = mix(COLOR.rgb, vec3(1.0), flash * step(0.9, seed));
	}
}
"

const CLOUD_SHADER := "
shader_type canvas_item;
// Keeps the bright cloud pixels of a piece of painted sky and lets the blue around them go.
void fragment() {
	vec4 c = texture(TEXTURE, UV);
	COLOR = vec4(c.rgb, smoothstep(0.48, 0.70, c.r));
}
"

const SOLID_SHADER := "
shader_type canvas_item;
// Redraws everything of the painting that is not sky or water, so drifting clouds pass behind arches and rocks.
void fragment() {
	vec4 c = texture(TEXTURE, UV);
	if (c.b > c.r + 0.28 && c.b > c.g + 0.06) { discard; }  // clear sky and open water only; bluish rock shade stays solid
	COLOR = c;
}
"

var clouds: Array[Sprite2D] = []
var cloud_speed: float = 6.0
var cloud_span: float = 1536.0
var splashes: Array[CPUParticles2D] = []
var petals: CPUParticles2D
var _splash_wait: Array[float] = []
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
	cloud_span = photo.get_width()
	var sky: Dictionary = definition.get("clouds", {})
	cloud_speed = float(sky.get("speed", 6.0))
	var keyed := ShaderMaterial.new()
	keyed.shader = Shader.new()
	keyed.shader.code = CLOUD_SHADER
	for cut: Dictionary in sky.get("cuts", []):
		var from: Array = cut.get("from", [0, 0, 0, 0])
		var cloud := Sprite2D.new()
		cloud.name = "Cloud"
		cloud.texture = photo
		cloud.centered = false
		cloud.region_enabled = true
		cloud.region_rect = Rect2(float(from[0]), float(from[1]), float(from[2]), float(from[3]))
		cloud.position = Vector2(float(cut.get("x", 0)), float(from[1]))  # same height above the horizon as painted
		cloud.flip_h = bool(cut.get("flip", false))
		cloud.material = keyed
		add_child(cloud)
		clouds.append(cloud)
	if not clouds.is_empty() and float(sky.get("cover_height", 0)) > 0.0:
		var solid := ShaderMaterial.new()
		solid.shader = Shader.new()
		solid.shader.code = SOLID_SHADER
		var front := Polygon2D.new()
		front.name = "CloudCover"
		var cover := float(sky["cover_height"])
		front.polygon = PackedVector2Array([Vector2.ZERO, Vector2(cloud_span, 0), Vector2(cloud_span, cover), Vector2(0, cover)])
		front.texture = photo
		front.material = solid
		add_child(front)
	# Pixel spray where the painted foam meets the rocks: short bursts of small white squares, each on its own clock.
	var fade := Gradient.new()
	fade.set_color(0, Color(1, 1, 1, 1))
	fade.set_color(1, Color(0.75, 0.93, 1.0, 0.0))
	for index in definition.get("splashes", []).size():
		var at: Array = definition["splashes"][index]
		var spray := CPUParticles2D.new()
		spray.name = "Splash"
		spray.position = Vector2(float(at[0]), float(at[1]))
		spray.emitting = false
		spray.one_shot = true
		spray.amount = 70
		spray.lifetime = 1.1
		spray.explosiveness = 0.85
		spray.emission_shape = CPUParticles2D.EMISSION_SHAPE_RECTANGLE
		spray.emission_rect_extents = Vector2(26, 6)
		spray.direction = Vector2(0, -1)
		spray.spread = 38.0
		spray.initial_velocity_min = 90.0
		spray.initial_velocity_max = 230.0
		spray.gravity = Vector2(0, 330)
		spray.scale_amount_min = 3.0
		spray.scale_amount_max = 6.0
		spray.color_ramp = fade
		add_child(spray)
		splashes.append(spray)
		_splash_wait.append(0.4 + 0.9 * index)
	var drift: Dictionary = definition.get("petals", {})
	if int(drift.get("amount", 0)) > 0:
		var area: Array = drift.get("area", [0, 0, 1536, 1024])
		var tints := Gradient.new()
		tints.set_color(0, Color(1.0, 1.0, 1.0))
		tints.set_color(1, Color(1.0, 0.78, 0.86))
		petals = CPUParticles2D.new()
		petals.name = "Petals"
		petals.position = Vector2(float(area[0]) + float(area[2]) * 0.5, float(area[1]) + float(area[3]) * 0.5)
		petals.amount = int(drift["amount"])
		petals.lifetime = 9.0
		petals.preprocess = 9.0
		petals.emission_shape = CPUParticles2D.EMISSION_SHAPE_RECTANGLE
		petals.emission_rect_extents = Vector2(float(area[2]), float(area[3])) * 0.5
		petals.direction = Vector2(1, 0.45)
		petals.spread = 25.0
		petals.initial_velocity_min = 22.0
		petals.initial_velocity_max = 48.0
		petals.gravity = Vector2(0, 5)
		petals.scale_amount_min = 2.0
		petals.scale_amount_max = 3.0
		petals.color_initial_ramp = tints
		var soft := Gradient.new()
		soft.set_color(0, Color(1, 1, 1, 0.0))
		soft.add_point(0.15, Color(1, 1, 1, 0.95))
		soft.set_color(soft.get_point_count() - 1, Color(1, 1, 1, 0.0))
		petals.color_ramp = soft
		add_child(petals)
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
	for cloud in clouds:
		cloud.position.x += cloud_speed * delta
		if cloud.position.x > cloud_span:
			cloud.position.x = -cloud.region_rect.size.x
	for index in splashes.size():
		_splash_wait[index] -= delta
		if _splash_wait[index] <= 0.0:
			splashes[index].restart()
			_splash_wait[index] = 2.2 + fmod(float(index) * 1.37 + _time * 0.61, 2.6)  # uneven, like real swell
	for index in glows.size():
		# Two slow waves and one quick one per lantern, each out of step with its neighbours.
		var phase := float(index) * 1.7
		glows[index].modulate.a = 0.72 + 0.16 * sin(_time * 2.1 + phase) + 0.08 * sin(_time * 7.3 + phase * 2.0) + 0.04 * sin(_time * 13.0 + phase)
