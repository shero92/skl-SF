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
## Painted shadows are a pure function of (source pixels, light, algorithm), so they are cached: in memory for
## rebuilds inside one run and on disk (user://, never in the repo) across runs. Bump CACHE_VERSION when paint() changes.
const CACHE_VERSION := 1
static var cache_dir := "user://shadow_cache/"
static var cache_enabled := true
static var cache_hits: int = 0
static var cache_misses: int = 0
static var _memory_cache: Dictionary = {}


static func clear_cache(disk: bool = true) -> void:
	_memory_cache.clear()
	cache_hits = 0
	cache_misses = 0
	if disk and DirAccess.dir_exists_absolute(cache_dir):
		for file_name in DirAccess.get_files_at(cache_dir):
			DirAccess.remove_absolute(cache_dir.path_join(file_name))


static func cache_key(source: Image, light_config: Dictionary) -> String:
	var hashing := HashingContext.new()
	hashing.start(HashingContext.HASH_SHA256)
	hashing.update(source.get_data())
	var light_text := JSON.stringify(merged_light(light_config), "", true)
	hashing.update(("v%d|%d|%d|%s" % [CACHE_VERSION, source.get_width(), source.get_height(), light_text]).to_utf8_buffer())
	return hashing.finish().hex_encode()


## paint() with the in-memory and disk cache. Same result as paint(); a corrupt or missing entry is repainted.
static func paint_cached(source: Image, light_config: Dictionary = {}) -> Dictionary:
	if not cache_enabled:
		return paint(source, light_config)
	var key := cache_key(source, light_config)
	if _memory_cache.has(key):
		cache_hits += 1
		return _memory_cache[key]
	var loaded := _load_cached(key)
	if loaded.has("hit"):
		cache_hits += 1
		_memory_cache[key] = loaded["value"]
		return loaded["value"]
	cache_misses += 1
	var painted := paint(source, light_config)
	_memory_cache[key] = painted
	_store_cached(key, painted)
	return painted


static func _load_cached(key: String) -> Dictionary:
	var meta_path := cache_dir.path_join(key + ".json")
	if not FileAccess.file_exists(meta_path):
		return {}
	var meta: Variant = JSON.parse_string(FileAccess.get_file_as_string(meta_path))
	if typeof(meta) != TYPE_DICTIONARY or int(meta.get("version", -1)) != CACHE_VERSION:
		return {}
	if bool(meta.get("empty", false)):
		return {"hit": true, "value": {}}
	var image := Image.load_from_file(ProjectSettings.globalize_path(cache_dir.path_join(key + ".png")))
	if image == null or image.is_empty():
		return {}
	image.convert(Image.FORMAT_RGBA8)
	var offset: Array = meta.get("offset", [0, 0])
	return {"hit": true, "value": {"image": image, "offset": Vector2(float(offset[0]), float(offset[1])),
		"source_scale": float(meta.get("source_scale", 1.0)), "foot_gap": float(meta.get("foot_gap", 0.0))}}


static func _store_cached(key: String, painted: Dictionary) -> void:
	DirAccess.make_dir_recursive_absolute(cache_dir)
	var meta := {"version": CACHE_VERSION, "empty": painted.is_empty()}
	if not painted.is_empty():
		var offset: Vector2 = painted["offset"]
		meta["offset"] = [offset.x, offset.y]
		meta["source_scale"] = painted["source_scale"]
		meta["foot_gap"] = painted["foot_gap"]
		if (painted["image"] as Image).save_png(cache_dir.path_join(key + ".png")) != OK:
			return
	var file := FileAccess.open(cache_dir.path_join(key + ".json"), FileAccess.WRITE) # written last: marks a complete entry
	if file != null:
		file.store_string(JSON.stringify(meta))


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
	var pixels := image.get_data() # RGBA8 bytes; reading them directly avoids a get_pixel call per sample
	var rows := _row_bounds(pixels, width, height)
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
			if pixels[(y * width + x) * 4 + 3] > CONTACT_ALPHA_BYTE: # byte/255 > 0.3
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
	var alpha_lut := _alpha_lut()
	var contact_opacity := float(light["contact_opacity"]) # hoisted: a Dictionary lookup per pixel was measurable
	var has_contact := contact_x1 >= contact_x0
	var contact_shift := contact_center - foot_x

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
					value = alpha_lut[pixels[(src_y * width + src_x) * 4 + 3]]
					value *= 1.0 - fade * clampf(h / object_height, 0.0, 1.0)
					value *= opacity
			# Contact occlusion ellipse under the footprint.
			if has_contact:
				var ex := (sx - contact_shift) / contact_rx
				var ey := sy / contact_ry
				var radius := ex * ex + ey * ey
				if radius < 1.0:
					var soft := 1.0 - radius
					value = maxf(value, soft * contact_opacity)
			alpha[oy * out_w + ox] = value

	for _pass in blur:
		alpha = _box_blur(alpha, out_w, out_h)

	# Same 8-bit conversion Image.set_pixel uses (truncation), written straight into the byte buffer.
	var tint8 := Color(tint.r, tint.g, tint.b, 1.0)
	var red := int(tint8.r * 255.0)
	var green := int(tint8.g * 255.0)
	var blue := int(tint8.b * 255.0)
	var bytes := PackedByteArray()
	bytes.resize(out_w * out_h * 4)
	for i in out_w * out_h:
		var a := alpha[i]
		if a > 0.003:
			var o := i * 4
			bytes[o] = red
			bytes[o + 1] = green
			bytes[o + 2] = blue
			bytes[o + 3] = int(clampf(a, 0.0, 1.0) * 255.0)
	var result := Image.create_from_data(out_w, out_h, false, Image.FORMAT_RGBA8, bytes)
	var used_longest := maxi(width, height)
	# Rows of transparent padding below the lowest opaque pixel: the shadow must start at the
	# object's real base, not at the bottom edge of the texture (objects looked like they hovered).
	var foot_gap := float(height) - float(foot_y) - 0.5
	return {"image": result, "offset": origin, "source_scale": float(original_longest) / float(used_longest), "foot_gap": foot_gap}


const CONTACT_ALPHA_BYTE := 76 # byte/255 > 0.3
const ROW_ALPHA_BYTE := 25 # byte/255 > 0.1
static var _lut: PackedFloat32Array


## byte -> float32 alpha exactly as a per-pixel Image read returns it.
static func _alpha_lut() -> PackedFloat32Array:
	if _lut.is_empty():
		_lut.resize(256)
		for b in 256:
			_lut[b] = Color(0.0, 0.0, 0.0, b / 255.0).a
	return _lut


static func _row_bounds(pixels: PackedByteArray, width: int, height: int) -> Dictionary:
	var top := -1
	var bottom := -1
	for y in height:
		var row := y * width * 4 + 3
		for x in width:
			if pixels[row + x * 4] > ROW_ALPHA_BYTE:
				if top < 0:
					top = y
				bottom = y
				break
	if top < 0:
		return {}
	return {"top": top, "bottom": bottom}


## 3x3 box average with edge clamping. Interior pixels sum their nine neighbours in the original
## order (bit-identical result); only the border uses the generic loop.
static func _box_blur(values: PackedFloat32Array, w: int, h: int) -> PackedFloat32Array:
	var out := PackedFloat32Array()
	out.resize(values.size())
	for y in h:
		var border_row := y == 0 or y == h - 1
		for x in w:
			var index := y * w + x
			if not border_row and x > 0 and x < w - 1:
				var up := index - w
				var down := index + w
				var total := 0.0
				total += values[up - 1]
				total += values[up]
				total += values[up + 1]
				total += values[index - 1]
				total += values[index]
				total += values[index + 1]
				total += values[down - 1]
				total += values[down]
				total += values[down + 1]
				out[index] = total / 9.0
				continue
			var edge_total := 0.0
			var count := 0
			for yy in range(maxi(0, y - 1), mini(h, y + 2)):
				for xx in range(maxi(0, x - 1), mini(w, x + 2)):
					edge_total += values[yy * w + xx]
					count += 1
			out[index] = edge_total / float(count)
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
				var painted := paint_cached(source, light)
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
