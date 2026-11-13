extends Node2D
class_name PhotoRoomLife
## Moving touches over a photo room (a room shown as one painting): rippling, glinting sea, clouds cut from
## the painting's own sky, a drifting haze with soft cloud shadows over the whole screen, drifting petals,
## flickering lantern light and floor patches. Everything comes from the painting itself or from plain pixel particles
## at run time; no art file is created or changed. Drawn creatures and breaking-wave sheets are requested
## as real art (ART-0051, ART-0052).
## Agent: claude (Claude Code); model: Fable 5.2.

const SEA_SHADER := "
shader_type canvas_item;
// Blue water pixels ripple and glint; where water meets rock a foam band surges in and falls back.
bool is_water(vec4 c) { return c.b > c.r + 0.15 && c.b > c.g + 0.04; }
// Rock, cliff or wall: neither water nor the pale painted foam.
// Open water is strongly blue; shaded rock is only bluish, so it needs the wider margin.
bool is_open_water(vec4 c) { return c.b > c.r + 0.34 && c.b > c.g + 0.04; }
bool is_rock(vec4 c) { return !is_open_water(c) && min(c.r, min(c.g, c.b)) < 0.62; }
float hash(vec2 p) {
	vec3 q = fract(vec3(p.xyx) * 0.1031);
	q += dot(q, q.yzx + 33.33);
	return fract((q.x + q.y) * q.z);
}
float noise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), f.x), mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x), f.y);
}
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
		float seed = hash(floor(at / 2.0));
		float flash = smoothstep(0.985, 1.0, sin(TIME * (1.5 + seed * 2.5) + seed * 6.2832));
		COLOR.rgb = mix(COLOR.rgb, vec3(1.0), flash * step(0.9, seed));
	}
	if (is_open_water(base)) {  // never on lit or shaded rock
		// Distance to the nearest rock, probed on five rings.
		float near = 99.0;
		for (int ring = 0; ring < 5; ring++) {
			float radius = 3.0 + float(ring) * 4.0;
			for (int i = 0; i < 8; i++) {
				float a = float(i) * 0.7853982 + float(ring) * 0.39;
				if (is_rock(texture(TEXTURE, UV + vec2(cos(a), sin(a)) * radius * px))) { near = min(near, radius); }
			}
		}
		if (near < 90.0) {
			// Each stretch of shore has its own rhythm: the swell runs in fast, lingers, then drains away.
			float beat = TIME * 0.9 + noise(at * 0.012) * 6.2832;
			float swell = pow(0.5 + 0.5 * sin(beat), 1.6);
			float reach = mix(3.0, 21.0, swell);
			float ragged = noise(at * 0.22 + vec2(TIME * 0.6, -TIME * 0.35));
			float body = smoothstep(reach, reach - 5.0, near + ragged * 6.0);
			float lip = smoothstep(2.5, 0.0, abs(near + ragged * 6.0 - reach + 2.0));  // bright leading edge
			float foam = clamp(body * (0.45 + 0.4 * ragged) + lip * 0.75, 0.0, 1.0) * (0.35 + 0.65 * swell);
			COLOR.rgb = mix(COLOR.rgb, vec3(0.93, 0.98, 1.0), foam);
		}
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

const MIST_SHADER := "
shader_type canvas_item;
// Soft haze and cloud shadows that drift over the whole picture. Value noise in chunky cells so it sits with pixel art.
uniform float strength = 0.3;
uniform float shadow = 0.16;
uniform float speed = 1.0;
uniform vec2 size = vec2(1536.0, 1024.0);
float hash(vec2 p) {  // no large sine products: those lose precision on some drivers and return a constant
	vec3 q = fract(vec3(p.xyx) * 0.1031);
	q += dot(q, q.yzx + 33.33);
	return fract((q.x + q.y) * q.z);
}
float noise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), f.x), mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x), f.y);
}
float fbm(vec2 p) {
	float v = 0.0;
	float a = 0.5;
	for (int i = 0; i < 4; i++) { v += a * noise(p); p *= 2.03; a *= 0.5; }
	return v;
}
varying vec2 spot;
void vertex() { spot = VERTEX; }  // position in picture pixels
void fragment() {
	vec2 at = floor(spot / 4.0) * 4.0 / size.y;  // 4 px cells
	float t = TIME * speed;
	// The whole field travels to the right while a second, slower field bends it, so banks roll and change shape.
	vec2 bend = vec2(fbm(at * 1.7 + vec2(0.0, t * 0.05)), fbm(at * 1.7 + vec2(5.2, -t * 0.04))) - 0.5;
	float haze = smoothstep(0.50, 0.70, fbm(at * 3.6 + bend * 1.6 + vec2(-t * 0.22, t * 0.05)));
	float shade = smoothstep(0.50, 0.68, fbm(at * 2.2 + bend * 0.9 + vec2(7.3 - t * 0.13, 2.1 + t * 0.03)));
	float alpha = max(haze * strength, shade * shadow * (1.0 - haze));
	COLOR = vec4(mix(vec3(0.05, 0.08, 0.2), vec3(1.0, 0.98, 0.94), haze * strength / max(alpha, 0.0001)), alpha);
}
"

var mist: Polygon2D
var clouds: Array[Sprite2D] = []
var cloud_speed: float = 6.0
var cloud_span: float = 1536.0
var petals: CPUParticles2D
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


## The haze lies over everything, characters included, so the caller parents it above them.
func build_mist(definition: Dictionary, size: Vector2) -> Polygon2D:
	var settings: Dictionary = definition.get("mist", {})
	if settings.is_empty():
		return null
	var material := ShaderMaterial.new()
	material.shader = Shader.new()
	material.shader.code = MIST_SHADER
	material.set_shader_parameter("strength", float(settings.get("strength", 0.3)))
	material.set_shader_parameter("shadow", float(settings.get("shadow", 0.16)))
	material.set_shader_parameter("speed", float(settings.get("speed", 1.0)))
	material.set_shader_parameter("size", size)
	mist = Polygon2D.new()
	mist.name = "Mist"
	mist.polygon = PackedVector2Array([Vector2.ZERO, Vector2(size.x, 0), size, Vector2(0, size.y)])
	mist.material = material
	return mist


func _process(delta: float) -> void:
	_time += delta
	for cloud in clouds:
		cloud.position.x += cloud_speed * delta
		if cloud.position.x > cloud_span:
			cloud.position.x = -cloud.region_rect.size.x
	for index in glows.size():
		# Two slow waves and one quick one per lantern, each out of step with its neighbours.
		var phase := float(index) * 1.7
		glows[index].modulate.a = 0.72 + 0.16 * sin(_time * 2.1 + phase) + 0.08 * sin(_time * 7.3 + phase * 2.0) + 0.04 * sin(_time * 13.0 + phase)
