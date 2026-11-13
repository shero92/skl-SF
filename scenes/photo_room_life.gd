extends Node2D
class_name PhotoRoomLife
## Moving touches over a photo room (a room shown as one painting): a rolling, glinting sea, clouds cut from
## the painting's own sky, a drifting haze with soft cloud shadows over the whole screen, drifting petals,
## flickering lantern light and floor patches. Everything comes from the painting itself or from plain pixel particles
## at run time; no art file is created or changed. Drawn creatures and breaking-wave sheets are requested
## as real art (ART-0051, ART-0052).
## Agent: claude (Claude Code); model: Fable 5.2.

const SEA_SHADER := "
shader_type canvas_item;
// No pixel warping (it frayed the painted edges). Long swells roll through the water as slow light and dark
// bands; the painted foam lines pulse with the swell, so each wave seems to break and fall back along
// the shore, and single pixels glint in the sun. Shapes never move: only brightness.
bool is_water(vec4 c) { return c.b > c.r + 0.15 && c.b > c.g + 0.04; }
bool is_foam(vec4 c) { return min(c.r, min(c.g, c.b)) > 0.58 && c.b > c.r - 0.03; }
float hash(vec2 p) {
	vec3 q = fract(vec3(p.xyx) * 0.1031);
	q += dot(q, q.yzx + 33.33);
	return fract((q.x + q.y) * q.z);
}
void fragment() {
	vec2 at = UV / TEXTURE_PIXEL_SIZE;
	vec4 c = texture(TEXTURE, UV);
	// Two swells crossing at different angles and speeds.
	float swell = 0.5 + 0.25 * sin(dot(at, vec2(0.011, 0.016)) - TIME * 0.85) + 0.25 * sin(dot(at, vec2(-0.007, 0.013)) - TIME * 0.6 + 2.0);
	if (is_water(c)) {
		c.rgb *= 0.93 + 0.14 * swell;
		float seed = hash(floor(at / 2.0));
		float flash = smoothstep(0.985, 1.0, sin(TIME * (1.5 + seed * 2.5) + seed * 6.2832));
		c.rgb = mix(c.rgb, vec3(1.0), flash * step(0.9, seed));
	} else if (is_foam(c)) {
		// Foam gathers when the swell crests and thins out in the trough.
		float crest = smoothstep(0.45, 0.95, swell);
		c.rgb = mix(c.rgb * 0.8, vec3(1.0), crest * 0.7);
	}
	COLOR = c;
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
	float haze = smoothstep(0.54, 0.72, fbm(at * 3.6 + bend * 1.6 + vec2(-t * 0.22, t * 0.05)));
	float shade = smoothstep(0.54, 0.70, fbm(at * 2.2 + bend * 0.9 + vec2(7.3 - t * 0.13, 2.1 + t * 0.03)));
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
const BEHIND_HERO := 27   # above the painting and its shadows, below the hero
const ABOVE_HERO := 40
var depth_objects: Array[Polygon2D] = []
var hero: Node2D
var hidden_amount: float = 0.0
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
	# Painted objects with height: each is cut from the painting and drawn again above the hero while his feet are
	# behind its base line (so he walks behind it), and below him once he is in front. Each also casts a soft shadow
	# toward the lower right, as long as the object is high.
	var shade := Gradient.new()
	for object: Dictionary in definition.get("depth_objects", []):
		var cutout := Polygon2D.new()
		cutout.name = String(object.get("id", "Object"))
		cutout.z_as_relative = false
		cutout.z_index = BEHIND_HERO
		var outline := PackedVector2Array()
		for point: Array in object.get("poly", []):
			outline.append(Vector2(float(point[0]), float(point[1])))
		cutout.polygon = outline
		cutout.texture = photo
		cutout.set_meta("base_y", float(object.get("base_y", 0)))
		add_child(cutout)
		depth_objects.append(cutout)
		for edge: Array in object.get("shadow", []):
			var tall := float(edge[4]) if edge.size() > 4 else float(edge[3])
			var shape := PackedVector2Array()
			var colors := PackedColorArray()
			var dark := Color(0.04, 0.03, 0.1, 0.34)
			var clear := Color(0.04, 0.03, 0.1, 0.0)
			var reach := Vector2(tall * 0.62, tall * 0.3)
			if edge.size() == 5:  # a vertical edge: x1, y1, x2, y2, height
				shape.append(Vector2(float(edge[0]), float(edge[1])))
				shape.append(Vector2(float(edge[2]), float(edge[3])))
				shape.append(Vector2(float(edge[2]), float(edge[3])) + reach)
				shape.append(Vector2(float(edge[0]), float(edge[1])) + reach)
			else:  # a base line: x1, x2, y, height
				shape.append(Vector2(float(edge[0]), float(edge[2])))
				shape.append(Vector2(float(edge[1]), float(edge[2])))
				shape.append(Vector2(float(edge[1]), float(edge[2])) + reach)
				shape.append(Vector2(float(edge[0]), float(edge[2])) + reach)
			colors.append(dark)
			colors.append(dark)
			colors.append(clear)
			colors.append(clear)
			var cast := Polygon2D.new()
			cast.name = "Shadow_" + String(object.get("id", ""))
			cast.polygon = shape
			cast.vertex_colors = colors
			add_child(cast)
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
	if hero != null:
		for object in depth_objects:
			# Feet above the base line: he stands behind it, so the object is drawn over him.
			object.z_index = ABOVE_HERO if hero.global_position.y < float(object.get_meta("base_y")) else BEHIND_HERO
		# Hidden: a wall or plant in front of him covers at least a fifth of his body, so a faint ghost shows where he stands.
		var body := Rect2(hero.global_position + Vector2(-34, -130), Vector2(68, 130))
		var covered := 0.0
		for object in depth_objects:
			if object.z_index == ABOVE_HERO:
				var bounds := Rect2(object.polygon[0], Vector2.ZERO)
				for point in object.polygon:
					bounds = bounds.expand(point)
				covered = maxf(covered, bounds.intersection(body).get_area() / body.get_area())
		hidden_amount = covered
		var source = hero.get("source_art")
		if source != null:
			source.show_ghost(covered > 0.2)
	for cloud in clouds:
		cloud.position.x += cloud_speed * delta
		if cloud.position.x > cloud_span:
			cloud.position.x = -cloud.region_rect.size.x
	for index in glows.size():
		# Two slow waves and one quick one per lantern, each out of step with its neighbours.
		var phase := float(index) * 1.7
		glows[index].modulate.a = 0.72 + 0.16 * sin(_time * 2.1 + phase) + 0.08 * sin(_time * 7.3 + phase * 2.0) + 0.04 * sin(_time * 13.0 + phase)
