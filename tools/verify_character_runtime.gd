extends SceneTree
## Headless verification of the shared asset catalog and the opt-in Game Factory hero art in HeroPlayer.
## Agent: claude (Claude Code); model: Sonnet 5.5.

var _failures: int = 0
var _legacy: HeroPlayer
var _factory: HeroPlayer


func _check(condition: bool, message: String) -> void:
	if not condition:
		_failures += 1
		printerr("FAIL: " + message)


func _initialize() -> void:
	var first := AssetCatalog.shared()
	_check(first == AssetCatalog.shared(), "shared catalog is one instance")
	_check(not first.get_asset("CH001").is_empty(), "shared catalog has the hero sprite records")
	_legacy = HeroPlayer.new()
	_factory = HeroPlayer.new()
	_factory.use_factory_art = true
	root.add_child(_legacy)
	root.add_child(_factory)
	process_frame.connect(_finish, CONNECT_ONE_SHOT)


func _finish() -> void:
	var parses_before := AssetCatalog.load_count
	# Every state change used to re-parse asset_index.json; now it must not parse at all.
	for step in 40:
		_legacy._play("CH005" if step % 2 == 0 else "CH001")
		_legacy._anim_id = ""
	_check(AssetCatalog.load_count == parses_before, "animation changes do not re-parse the index (%d parses)" % (AssetCatalog.load_count - parses_before))
	_check(_legacy.art.texture != null, "legacy hero art still loads from the shared catalog")
	_check(_legacy.factory_art == null, "factory art is off by default")

	_check(_factory.factory_art != null, "opt-in factory art builds from the manifest")
	if _factory.factory_art != null:
		var frames := _factory.factory_art.sprite_frames
		for direction in ["down", "left", "right", "up"]:
			for state in ["idle", "walk"]:
				var key := "map_%s_%s" % [direction, state]
				_check(frames.has_animation(key) and frames.get_frame_count(key) > 0, key + " is a complete animation")
				_check(_factory._play_factory(state, direction), "plays " + key)
				_check(_factory.factory_art.animation == key and _factory.factory_art.visible, "selects " + key)
		_check(frames.get_frame_count("map_down_walk") == 6 and frames.get_frame_count("map_down_idle") == 4,
			"frame counts match the approved manifest (idle 4, walk 6)")
		_check(not _factory._play_factory("walk", "sideways"), "unknown direction falls back (returns false)")
		_check(not frames.has_animation("battle_hurt"), "incomplete animations are never playable")
	if _failures == 0:
		print("CHARACTER_RUNTIME_OK")
	quit(0 if _failures == 0 else 1)
