extends SceneTree
## Proves the optimised ShadowPainter.paint is byte-identical to the unoptimised reference on every
## shadow-casting texture of the hero room, and reports the speed difference (informational).
## Agent: claude (Claude Code); model: Sonnet 5.5.

const Reference = preload("res://tools/tests/fixtures/shadow_painter_reference.gd")

var _failures: int = 0


func _check(condition: bool, message: String) -> void:
	if not condition:
		_failures += 1
		printerr("FAIL: " + message)


func _initialize() -> void:
	var holder := Node2D.new()
	root.add_child(holder)
	var room := RoomFactory.new().build_latest("hero_room_01", holder)
	var snapshot: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://map_factory/maps/hero_room_01/latest.json"))
	var light: Dictionary = snapshot.get("lighting", {})
	var seen := {}
	var textures: Array[Texture2D] = []
	for sprite in ShadowPainter._owner_sprites(room):
		if ShadowPainter.wants_shadow(sprite) and not seen.has(sprite.texture.get_instance_id()):
			seen[sprite.texture.get_instance_id()] = true
			textures.append(sprite.texture)
	_check(textures.size() > 30, "enough shadow-casting textures to compare (%d)" % textures.size())
	var new_us := 0
	var old_us := 0
	var compared := 0
	for texture in textures:
		var source := texture.get_image()
		if source == null:
			continue
		var t0 := Time.get_ticks_usec()
		var fast: Dictionary = ShadowPainter.paint(source, light)
		var t1 := Time.get_ticks_usec()
		var slow: Dictionary = Reference.paint(source, light)
		var t2 := Time.get_ticks_usec()
		new_us += t1 - t0
		old_us += t2 - t1
		compared += 1
		_check(fast.is_empty() == slow.is_empty(), "empty result differs for " + texture.resource_path)
		if fast.is_empty() or slow.is_empty():
			continue
		_check(fast["image"].get_data() == slow["image"].get_data(), "shadow pixels differ for " + texture.resource_path)
		_check(fast["offset"] == slow["offset"] and is_equal_approx(fast["source_scale"], slow["source_scale"])
			and is_equal_approx(fast["foot_gap"], slow["foot_gap"]), "shadow placement differs for " + texture.resource_path)
	print("SHADOW_TIMING textures=%d optimised_ms=%.1f reference_ms=%.1f" % [compared, new_us / 1000.0, old_us / 1000.0])
	if _failures == 0:
		print("SHADOW_PAINTER_OK")
	quit(0 if _failures == 0 else 1)
