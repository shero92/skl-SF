extends RefCounted
class_name ShadowPainter
## Separate painted shadow level for Map Factory rooms (TASK-0109, TASK-0110).
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


static func wants_shadow(sprite: Sprite2D) -> bool:
	if sprite.texture == null or sprite.has_meta("no_painted_shadow") or sprite.has_meta("mount_on"):
		return false
	var key := String(sprite.texture.resource_path).get_file().to_lower() + " " + String(sprite.name).to_lower()
	for token in SKIP_TOKENS:
		if key.contains(token):
			return false
	return true


## Builds the separate painted shadow level for a room. Owners are every Sprite2D under
## the wall, decoration and world-sort groups; the level is toggled with set_shadows_visible.
static func build_layer(room: Node2D, light_config: Dictionary = {}) -> Node2D:
	var old := room.get_node_or_null(SHADOW_LAYER)
	if old != null:
		room.remove_child(old)
		old.queue_free()
	var layer := Node2D.new()
	layer.name = SHADOW_LAYER
	layer.z_as_relative = false
	layer.z_index = SHADOW_Z
	room.add_child(layer)
	var light := merged_light(light_config)
	var cache := {}
	for sprite in _owner_sprites(room):
		if not wants_shadow(sprite):
			continue
		var key := "%s|%s" % [sprite.texture.resource_path, sprite.flip_h]
		if sprite.texture.resource_path == "":
			key = "mem%d|%s" % [sprite.texture.get_instance_id(), sprite.flip_h]
		if not cache.has(key):
			var source: Image = sprite.texture.get_image()
			if source == null:
				cache[key] = {}
			else:
				if sprite.flip_h:
					source = source.duplicate()
					source.flip_x()
				var painted := paint(source, light)
				if not painted.is_empty():
					painted["texture"] = ImageTexture.create_from_image(painted["image"])
				cache[key] = painted
		var painted: Dictionary = cache[key]
		if painted.is_empty():
			continue
		var xf := room_transform(sprite, room)
		var rect: Rect2 = sprite.get_rect()
		var foot := xf * Vector2(rect.position.x + rect.size.x * 0.5, rect.end.y)
		var scale := xf.get_scale().abs()
		var shadow := Sprite2D.new()
		shadow.name = "Shadow_" + String(sprite.name)
		shadow.texture = painted["texture"]
		shadow.centered = false
		shadow.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
		# The painted image is in (possibly down-sampled) source pixels: scale it back up.
		var down := float(painted.get("source_scale", 1.0))
		shadow.scale = scale * down
		var base := foot - Vector2(0.0, float(painted.get("foot_gap", 0.0)) * shadow.scale.y)
		shadow.position = base + Vector2(painted["offset"]) * shadow.scale
		shadow.set_meta("owner_ref", sprite.get_instance_id())
		shadow.set_meta("owner_offset", shadow.position - foot)
		shadow.set_meta("layer", 4)
		shadow.set_meta("foot_y", base.y)
		layer.add_child(shadow)
	return layer


static func _owner_sprites(room: Node) -> Array:
	var found := []
	for group_name in ["Level2_Walls", "Level3_Decorations", "WorldDepthSort", "Objects"]:
		var group := room.get_node_or_null(group_name)
		if group != null:
			_collect(group, found)
	return found


static func _collect(node: Node, found: Array) -> void:
	if node is Sprite2D and node.texture != null and not found.has(node):
		found.append(node)
	for child in node.get_children():
		_collect(child, found)


static func room_transform(node: Node2D, room: Node) -> Transform2D:
	var xf := Transform2D.IDENTITY
	var current: Node = node
	while current != null and current != room:
		if current is Node2D:
			xf = (current as Node2D).transform * xf
		current = current.get_parent()
	return xf


static func set_shadows_visible(room: Node, visible: bool) -> void:
	var layer := room.get_node_or_null(SHADOW_LAYER)
	if layer != null:
		layer.visible = visible


## Keeps painted shadows attached to their owners. Removed owners remove their shadow.
static func sync(room: Node2D) -> void:
	var layer := room.get_node_or_null(SHADOW_LAYER)
	if layer == null:
		return
	for child in layer.get_children():
		var shadow := child as Node2D
		if shadow == null or not shadow.has_meta("owner_ref"):
			continue
		var owner_node := instance_from_id(int(shadow.get_meta("owner_ref"))) as Sprite2D
		if owner_node == null or not is_instance_valid(owner_node) or owner_node.is_queued_for_deletion() or not room.is_ancestor_of(owner_node):
			layer.remove_child(shadow)
			shadow.queue_free()
			continue
		var xf := room_transform(owner_node, room)
		var rect: Rect2 = owner_node.get_rect()
		var foot := xf * Vector2(rect.position.x + rect.size.x * 0.5, rect.end.y)
		shadow.position = foot + Vector2(shadow.get_meta("owner_offset", Vector2.ZERO))
		shadow.visible = owner_node.is_visible_in_tree()


## Separate light level: a soft additive pool around lanterns and candles.
static func build_light_layer(room: Node2D, radius_scale: float = 3.0, strength: float = 0.32) -> Node2D:
	var old := room.get_node_or_null(LIGHT_LAYER)
	if old != null:
		room.remove_child(old)
		old.queue_free()
	var layer := Node2D.new()
	layer.name = LIGHT_LAYER
	layer.z_as_relative = false
	layer.z_index = LIGHT_Z
	room.add_child(layer)
	var material := CanvasItemMaterial.new()
	material.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	var gradient := Gradient.new()
	gradient.set_color(0, Color(1.0, 0.78, 0.40, 1.0))
	gradient.set_color(1, Color(1.0, 0.78, 0.40, 0.0))
	var pool := GradientTexture2D.new()
	pool.gradient = gradient
	pool.fill = GradientTexture2D.FILL_RADIAL
	pool.fill_from = Vector2(0.5, 0.5)
	pool.fill_to = Vector2(1.0, 0.5)
	pool.width = 128
	pool.height = 128
	for sprite in _owner_sprites(room):
		if sprite.texture == null:
			continue
		var key := String(sprite.texture.resource_path).get_file().to_lower() + " " + String(sprite.name).to_lower()
		var lit := false
		for token in LIGHT_TOKENS:
			if key.contains(token):
				lit = true
		if not lit or key.contains("glow"):
			continue
		var xf := room_transform(sprite, room)
		var rect: Rect2 = sprite.get_rect()
		var center: Vector2 = xf * rect.get_center()
		var radius := maxf(rect.size.x, rect.size.y) * xf.get_scale().abs().x * radius_scale
		var glow := Sprite2D.new()
		glow.name = "Pool_" + String(sprite.name)
		glow.texture = pool
		glow.material = material
		glow.position = center
		glow.scale = Vector2.ONE * (radius * 2.0 / 128.0)
		glow.modulate.a = strength
		glow.set_meta("owner_ref", sprite.get_instance_id())
		layer.add_child(glow)
	return layer


static func set_light_visible(room: Node, visible: bool) -> void:
	var layer := room.get_node_or_null(LIGHT_LAYER)
	if layer != null:
		layer.visible = visible
