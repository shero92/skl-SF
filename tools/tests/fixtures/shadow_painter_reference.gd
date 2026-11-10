extends RefCounted
## GOLDEN REFERENCE (TASK-0131): the unoptimised ShadowPainter.paint of TASK-0109/0110, kept verbatim so tests can
## prove the optimised painter produces byte-identical shadow images. Not loaded by the game.
## Agent: claude (Claude Code); model: Sonnet 5.5.
##
## Each object's shadow is painted from the object's REAL alpha silhouette, projected
## along the map light direction onto the ground plane, with height fade, a soft blur
## and a contact occlusion ellipse under the footprint. It is generated at runtime, so no
## art is added; the shadow level is its own node (Level4_PaintedShadows) that can be toggled,
## and every shadow is linked to its owner placement. The light pools live in a second level
## (Level5_Light) that is also independent.

const SHADOW_LAYER := "Level4_PaintedShadows"
const LIGHT_LAYER := "Level5_Light"
const SHADOW_Z := 20
const LIGHT_Z := 60
const MAX_SOURCE_SIDE := 256
# Pieces that are flat on the ground, hang on a wall or are light effects cast no floor shadow.
const SKIP_TOKENS := ["rug", "emblem", "overlay", "glow", "flame", "banner", "lantern", "ivy_hanging", "light", "shadow", "foam", "water", "cloud"]
const LIGHT_TOKENS := ["lantern", "candle"]


static func default_light() -> Dictionary:
	# Warm daylight from the upper left: shadows fall toward the lower right.
	return {
		"direction": [0.9, 0.3],
		"length": 0.55,
		"opacity": 0.42,
		"height_fade": 0.55,
		"blur": 1,
		"color": [0.10, 0.12, 0.26],
		"contact_opacity": 0.38,
		"contact_height": 0.10,
	}


static func merged_light(config: Dictionary) -> Dictionary:
	var light := default_light()
	for key in config:
		light[key] = config[key]
	return light


## Paints one shadow. Returns {"image": Image, "offset": Vector2} where offset is the
## top-left of the image relative to the object's foot point (bottom centre of the source).
## Returns an empty dictionary if the source has no visible pixels.
static func paint(source: Image, light_config: Dictionary = {}) -> Dictionary:
	var light := merged_light(light_config)
	var image := source.duplicate() as Image
	if image.is_compressed():
		image.decompress()
	image.convert(Image.FORMAT_RGBA8)
	var longest := maxi(image.get_width(), image.get_height())
	var original_longest := longest
	if longest > MAX_SOURCE_SIDE:
		var factor := float(MAX_SOURCE_SIDE) / float(longest)
		image.resize(maxi(1, int(image.get_width() * factor)), maxi(1, int(image.get_height() * factor)), Image.INTERPOLATE_NEAREST)
	var width := image.get_width()
	var height := image.get_height()
	var rows := _row_bounds(image)
	if rows.is_empty():
		return {}
	var foot_y: int = rows["bottom"]
	var top_y: int = rows["top"]
	var object_height := maxf(1.0, float(foot_y - top_y + 1))

	var direction := Vector2(float(light["direction"][0]), float(light["direction"][1]))
	var length := float(light["length"])
	var dx := direction.x * length
	var dy := maxf(0.05, direction.y * length)
	var fade := clampf(float(light["height_fade"]), 0.0, 1.0)
	var opacity := clampf(float(light["opacity"]), 0.0, 1.0)
	var blur := clampi(int(light["blur"]), 0, 4)
	var color_array: Array = light["color"]
	var tint := Color(float(color_array[0]), float(color_array[1]), float(color_array[2]), 1.0)

	# Contact band: the widest alpha extent in the lowest rows of the object.
	var band_rows := maxi(1, int(object_height * float(light["contact_height"])))
	var contact_x0 := width
	var contact_x1 := -1
	for y in range(maxi(top_y, foot_y - band_rows + 1), foot_y + 1):
		for x in width:
			if image.get_pixel(x, y).a > 0.3:
				contact_x0 = mini(contact_x0, x)
				contact_x1 = maxi(contact_x1, x)
	var contact_center := (contact_x0 + contact_x1 + 1) * 0.5
	var contact_rx := maxf(1.0, (contact_x1 - contact_x0 + 1) * 0.5 * 1.08)
	var contact_ry := maxf(2.0, contact_rx * 0.22)

	# Destination space: x relative to the foot x (image centre), y relative to the foot line.
	var foot_x := width * 0.5
	var pad := blur + 2
	var min_x := minf(-foot_x, minf(contact_center - foot_x - contact_rx, -foot_x + dx * object_height))
	var max_x := maxf(width - foot_x, maxf(contact_center - foot_x + contact_rx, width - foot_x + dx * object_height))
	var min_y := -contact_ry
	var max_y := maxf(contact_ry, dy * object_height)
	var out_w := int(ceil(max_x - min_x)) + pad * 2
	var out_h := int(ceil(max_y - min_y)) + pad * 2
	var origin := Vector2(floor(min_x) - pad, floor(min_y) - pad)
	var alpha := PackedFloat32Array()
	alpha.resize(out_w * out_h)

	for oy in out_h:
		var sy := origin.y + oy + 0.5
		# Inverse of: sx = x - foot_x + dx*h, sy = dy*h, with h = foot_y - y (height above foot).
		var h := sy / dy
		var inside_cast := h >= 0.0 and h <= object_height
		var src_y := int(round(foot_y - h))
		for ox in out_w:
			var sx := origin.x + ox + 0.5
			var value := 0.0
			if inside_cast and src_y >= 0 and src_y < height:
				var src_x := int(round(sx + foot_x - dx * h))
				if src_x >= 0 and src_x < width:
					value = image.get_pixel(src_x, src_y).a
					value *= 1.0 - fade * clampf(h / object_height, 0.0, 1.0)
					value *= opacity
			# Contact occlusion ellipse under the footprint.
			if contact_x1 >= contact_x0:
				var ex := (sx - (contact_center - foot_x)) / contact_rx
				var ey := sy / contact_ry
				var radius := ex * ex + ey * ey
				if radius < 1.0:
					var soft := 1.0 - radius
					value = maxf(value, soft * float(light["contact_opacity"]))
			alpha[oy * out_w + ox] = value

	for _pass in blur:
		alpha = _box_blur(alpha, out_w, out_h)

	var result := Image.create(out_w, out_h, false, Image.FORMAT_RGBA8)
	for oy in out_h:
		for ox in out_w:
			var a := alpha[oy * out_w + ox]
			if a > 0.003:
				result.set_pixel(ox, oy, Color(tint.r, tint.g, tint.b, clampf(a, 0.0, 1.0)))
	var used_longest := maxi(width, height)
	# Rows of transparent padding below the lowest opaque pixel: the shadow must start at the
	# object's real base, not at the bottom edge of the texture (objects looked like they hovered).
	var foot_gap := float(height) - float(foot_y) - 0.5
	return {"image": result, "offset": origin, "source_scale": float(original_longest) / float(used_longest), "foot_gap": foot_gap}


static func _row_bounds(image: Image) -> Dictionary:
	var top := -1
	var bottom := -1
	for y in image.get_height():
		for x in image.get_width():
			if image.get_pixel(x, y).a > 0.1:
				if top < 0:
					top = y
				bottom = y
				break
	if top < 0:
		return {}
	return {"top": top, "bottom": bottom}


static func _box_blur(values: PackedFloat32Array, w: int, h: int) -> PackedFloat32Array:
	var out := PackedFloat32Array()
	out.resize(values.size())
	for y in h:
		for x in w:
			var total := 0.0
			var count := 0
			for yy in range(maxi(0, y - 1), mini(h, y + 2)):
				for xx in range(maxi(0, x - 1), mini(w, x + 2)):
					total += values[yy * w + xx]
					count += 1
			out[y * w + x] = total / float(count)
	return out
