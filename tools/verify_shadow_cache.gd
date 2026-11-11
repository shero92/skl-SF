extends SceneTree
## Verifies the painted-shadow cache: disk and memory hits are byte-identical to a fresh paint, corrupt entries are
## repainted, and a cached room build is much faster. Agent: claude (Claude Code); model: Sonnet 5.5.

const Reference = preload("res://tools/tests/fixtures/shadow_painter_reference.gd")

var _failures: int = 0


func _check(condition: bool, message: String) -> void:
	if not condition:
		_failures += 1
		printerr("FAIL: " + message)


func _build_ms(map_id: String) -> float:
	var holder := Node2D.new()
	root.add_child(holder)
	var started := Time.get_ticks_usec()
	RoomFactory.new().build_latest(map_id, holder)
	var elapsed := (Time.get_ticks_usec() - started) / 1000.0
	holder.free()
	return elapsed


func _initialize() -> void:
	ShadowPainter.cache_dir = "user://shadow_cache_test/"
	ShadowPainter.clear_cache(true)
	var snapshot: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://map_factory/maps/hero_room_01/latest.json"))
	var light: Dictionary = snapshot.get("lighting", {})

	# Identity: cold paint, memory hit and disk hit all equal the unoptimised reference.
	var holder := Node2D.new()
	root.add_child(holder)
	var room := RoomFactory.new().build_latest("hero_room_01", holder)
	var sources: Array[Image] = []
	var seen := {}
	for sprite in ShadowPainter._owner_sprites(room):
		if sources.size() < 4 and ShadowPainter.wants_shadow(sprite) and not seen.has(sprite.texture.get_instance_id()):
			seen[sprite.texture.get_instance_id()] = true
			sources.append(sprite.texture.get_image())
	holder.free()
	ShadowPainter.clear_cache(true)
	_check(sources.size() >= 1, "have at least one real texture to test")
	for source in sources:
		var expected: Dictionary = Reference.paint(source, light)
		var cold: Dictionary = ShadowPainter.paint_cached(source, light)
		_check(cold["image"].get_data() == expected["image"].get_data(), "cold result equals reference")
		ShadowPainter._memory_cache.clear()
		var disk: Dictionary = ShadowPainter.paint_cached(source, light)
		_check(disk["image"].get_data() == expected["image"].get_data(), "disk hit equals reference")
		_check(disk["offset"] == expected["offset"] and is_equal_approx(disk["source_scale"], expected["source_scale"])
			and is_equal_approx(disk["foot_gap"], expected["foot_gap"]), "disk hit keeps offset, scale and foot gap")
		var memory: Dictionary = ShadowPainter.paint_cached(source, light)
		_check(memory["image"].get_data() == expected["image"].get_data(), "memory hit equals reference")
	_check(ShadowPainter.cache_misses == sources.size() and ShadowPainter.cache_hits == sources.size() * 2,
		"hit/miss counters (%d misses, %d hits)" % [ShadowPainter.cache_misses, ShadowPainter.cache_hits])

	# A different light must not reuse the entry; a corrupt entry is repainted.
	var other_light := light.duplicate(true)
	other_light["opacity"] = 0.9
	var misses_before := ShadowPainter.cache_misses
	ShadowPainter.paint_cached(sources[0], other_light)
	_check(ShadowPainter.cache_misses == misses_before + 1, "a changed light is a miss")
	var key := ShadowPainter.cache_key(sources[0], light)
	var bad := FileAccess.open(ShadowPainter.cache_dir.path_join(key + ".png"), FileAccess.WRITE)
	bad.store_string("not a png")
	bad.close()
	ShadowPainter._memory_cache.clear()
	var repaired: Dictionary = ShadowPainter.paint_cached(sources[0], light)
	_check(repaired["image"].get_data() == Reference.paint(sources[0], light)["image"].get_data(), "corrupt entry is repainted")

	# Speed (informational + loose guard): full room build cold vs warm.
	ShadowPainter.clear_cache(true)
	var cold_ms := _build_ms("hero_room_01")
	ShadowPainter._memory_cache.clear()
	var disk_ms := _build_ms("hero_room_01")
	var memory_ms := _build_ms("hero_room_01")
	print("SHADOW_CACHE_TIMING cold_ms=%.1f disk_hit_ms=%.1f memory_hit_ms=%.1f hits=%d misses=%d" % [
		cold_ms, disk_ms, memory_ms, ShadowPainter.cache_hits, ShadowPainter.cache_misses])
	_check(memory_ms < cold_ms * 0.5, "a memory-cached build is at least twice as fast")
	_check(disk_ms < cold_ms, "a disk-cached build is faster than a cold one")
	ShadowPainter.clear_cache(true)
	if _failures == 0:
		print("SHADOW_CACHE_OK")
	quit(0 if _failures == 0 else 1)
