extends Node2D
## Candidate-only review scene. Reuses the battle controller, camera and modular actor.

const Controller = preload("res://scenes/battle/battle_animation_controller.gd")
const Unit = preload("res://scenes/modular_battle_character.gd")
const Camera = preload("res://scenes/battle/dynamic_battle_camera.gd")
const Effects = preload("res://scenes/battle/battle_vfx_layer.gd")
const DATA := "res://game_factory/golden_cyclone/v001/metadata/"
const PREVIEWS := "res://game_factory/golden_cyclone/v001/previews/"
const HOME := Vector2(700, 540)
const TARGET := Vector2(280, 310)

var controller = Controller.new()
var hero: ModularBattleCharacter
var defender: ModularBattleCharacter
var camera: Camera
var effects: Effects
var ready_for_review: bool = false
var initialization_error: String = ""
var hit_times: Array[float] = []
var camera_enabled: bool = true
var effects_enabled: bool = true
var capture_mode: bool = false
var _data: Dictionary
var _dependencies: Dictionary
var _hero_actor: ReviewActor
var _defender_actor: ReviewActor
var _status: Label
var _slider: HSlider
var _slow_toggle: CheckButton
var _effect_sprites: Dictionary = {}
var _background: Dictionary = {}
var _weapon_id: String = "WPN_HERO_BASIC_SWORD"
var _review_speed: float = 1.0
var _recovery_focus: bool = false


class ReviewActor extends RefCounted:
	var unit: ModularBattleCharacter
	var home: Vector2

	func _init(value: ModularBattleCharacter, location: Vector2) -> void:
		unit = value
		home = location

	func set_view(_view: String) -> void:
		pass # Independently illustrated orientations are already in the frame sequence.

	func set_frame(_name: String, index: int) -> void:
		unit.body.frame = index
		unit.update_attachment()

	func reset() -> void:
		unit.position = home
		unit.modulate = Color.WHITE
		unit.body.frame = 0
		unit.update_attachment()


func _ready() -> void:
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	get_window().size = Vector2i(1024, 576)
	get_window().content_scale_size = Vector2i(1024, 576)
	_data = _read(DATA + "review_assets.json")
	_dependencies = _read(DATA + "preview_dependencies.json")
	_build_ui()
	if _data.get("frames", []).size() != 22 or _dependencies.is_empty():
		initialization_error = "Missing validated candidate exports. Run golden_cyclone_assets.py build."
		_status.text = initialization_error
		return
	for entry in _data.frames:
		if not FileAccess.file_exists("res://" + entry.path) or FileAccess.get_sha256("res://" + entry.path) != entry.sha256:
			initialization_error = "Missing or altered candidate PNG: " + str(entry.path)
			_status.text = initialization_error
			return
	for dependency in _dependencies.get("sources", []):
		if FileAccess.get_sha256("res://" + str(dependency.copy)) != str(dependency.sha256):
			initialization_error = "Dependency hash mismatch: " + str(dependency.copy)
			_status.text = initialization_error
			return
	for key: String in _dependencies.background:
		_background[key] = Unit.load_texture(_dependencies.background[key])
	var frames := SpriteFrames.new()
	frames.remove_animation(&"default")
	frames.add_animation(&"battle_golden_cyclone")
	frames.set_animation_loop(&"battle_golden_cyclone", false)
	var attack_frames: Array[Dictionary] = []
	for index: int in range(22):
		var entry: Dictionary = _data.frames[index]
		frames.add_frame(&"battle_golden_cyclone", Unit.load_texture("res://" + entry.path))
		attack_frames.append({"duration_ms": entry.duration_ms, "hit": entry.hit,
			"phase": entry.phase, "attacker": {"view": "hero_rear_3q", "name": "golden_cyclone", "index": index}})
	hero = Unit.new()
	hero.position = HOME
	hero.scale = Vector2.ONE * 1.2 # Fixed foreground projection, identical for all frames.
	hero.z_index = 20
	add_child(hero)
	hero.configure(frames, _data.weapon_attachment_data, _dependencies.weapons, "sword", _vec(_data.ground_anchor))
	hero.body.animation = &"battle_golden_cyclone"
	hero.equip(_weapon_id)
	var guard := SpriteFrames.new()
	guard.remove_animation(&"default")
	guard.add_animation(&"battle_idle_ready")
	guard.add_frame(&"battle_idle_ready", Unit.load_texture(_dependencies.target_body))
	defender = Unit.new()
	defender.position = TARGET
	defender.z_index = 10
	defender.scale = Vector2.ONE * 0.8
	add_child(defender)
	defender.configure(guard, _dependencies.target_attachments, _dependencies.weapons)
	defender.body.animation = &"battle_idle_ready"
	defender.equip("WPN_HERO_BASIC_SWORD")
	_hero_actor = ReviewActor.new(hero, HOME)
	_defender_actor = ReviewActor.new(defender, TARGET)
	controller.attacks = {&"golden_cyclone": {"frames": attack_frames, "assets": []}}
	controller.hit.connect(_on_hit)
	controller.finished.connect(_on_end)
	controller.cancelled.connect(_on_end)
	camera = Camera.new()
	camera.position = Vector2(512, 288)
	camera.reference_size = Vector2(1024, 576)
	add_child(camera)
	camera.set_process(false)
	effects = Effects.new()
	add_child(effects)
	effects.set_process(false)
	_load_effects()
	ready_for_review = true
	_update_world()
	print("GOLDEN_CYCLONE_REVIEW_READY: 22 independent candidate frames")
	var capture_request := DATA + "capture_once.flag"
	if "capture" in OS.get_cmdline_user_args() or FileAccess.file_exists(capture_request):
		if FileAccess.file_exists(capture_request):
			DirAccess.remove_absolute(ProjectSettings.globalize_path(capture_request))
		call_deferred("capture_sequence")
	queue_redraw()


func _read(path: String) -> Dictionary:
	if not FileAccess.file_exists(path):
		return {}
	var value: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	return value if value is Dictionary else {}


func _vec(value: Array) -> Vector2:
	return Vector2(float(value[0]), float(value[1]))


func _build_ui() -> void:
	var layer := CanvasLayer.new()
	add_child(layer)
	var row := HBoxContainer.new()
	row.position = Vector2(14, 12)
	layer.add_child(row)
	var actions := {"Play / Restart": restart, "Pause / Resume": toggle_pause,
		"Previous": previous_frame, "Next": next_frame, "Swap sword": swap_sword,
		"Camera": toggle_camera, "VFX": toggle_effects, "Cancel": cancel_attack}
	for text: String in actions:
		var button := Button.new()
		button.text = text
		button.add_theme_font_size_override("font_size", 12)
		button.pressed.connect(actions[text])
		row.add_child(button)
	var slow := CheckButton.new()
	_slow_toggle = slow
	slow.text = "0.25x"
	slow.toggled.connect(func(value: bool):
		_review_speed = 0.25 if value else 1.0
		controller.set_speed(_review_speed))
	row.add_child(slow)
	_status = Label.new()
	_status.position = Vector2(16, 52)
	layer.add_child(_status)
	_slider = HSlider.new()
	_slider.position = Vector2(16, 548)
	_slider.size = Vector2(990, 18)
	_slider.min_value = 0
	_slider.max_value = 1499
	_slider.step = 1
	_slider.value_changed.connect(scrub)
	layer.add_child(_slider)


func _draw() -> void:
	draw_rect(Rect2(0, 0, 1024, 576), Color("243345"))
	if not ready_for_review:
		return
	draw_texture_rect(_background.sky, Rect2(0, 0, 1024, 320), false)
	draw_texture_rect(_background.cliff, Rect2(60, 130, 460, 220), false)
	draw_texture_rect(_background.cloud, Rect2(720, 105, 155, 95), false)
	for y: int in range(300, 576, 64):
		for x: int in range(0, 1024, 64):
			draw_texture_rect(_background.floor, Rect2(x, y, 64, 64), false)
	# Independent contact shadows, never painted into body PNGs.
	draw_set_transform(hero.position, 0, Vector2(1, 0.28))
	draw_circle(Vector2.ZERO, 54, Color(0, 0, 0, .24))
	draw_set_transform(defender.position, 0, Vector2(1, 0.28))
	draw_circle(Vector2.ZERO, 33, Color(0, 0, 0, .2))
	draw_set_transform(Vector2.ZERO)


func play_attack(attack_id: StringName, attacker: Variant = null, target: Variant = null) -> Dictionary:
	if not ready_for_review:
		return {"ok": false, "reason": "MISSING_REVIEW_ASSETS"}
	var source_actor: Variant = _hero_actor if attacker == null or attacker == hero else attacker
	var target_actor: Variant = _defender_actor if target == null or target == defender else target
	var result: Dictionary = controller.play_attack(attack_id, source_actor, target_actor)
	if result.ok:
		hit_times.clear()
		_recovery_focus = false
		controller.set_speed(_review_speed)
		if camera_enabled:
			camera.focus_on(Vector2(490, 300), Vector2.ONE * 1.04, 0.24)
	return result


func restart() -> void:
	if ready_for_review:
		controller.cancel()
		play_attack(&"golden_cyclone")


func cancel_attack() -> void:
	controller.cancel()
	_update_world()


func toggle_pause() -> void:
	if controller.is_playing():
		controller.pause()
	else:
		controller.resume()


func scrub(time_ms: float) -> void:
	if not ready_for_review:
		return
	if controller.state == Controller.State.IDLE:
		restart()
	controller.pause()
	controller.seek(time_ms)
	_update_world()


func next_frame() -> void:
	if ready_for_review:
		if controller.state == Controller.State.IDLE:
			restart()
		controller.step_frame()
		_update_world()


func previous_frame() -> void:
	if not ready_for_review:
		return
	var index: int = maxi(0, controller.get_frame_index() - 1)
	var time_ms := 0.0
	for i: int in range(index):
		time_ms += float(_data.frames[i].duration_ms)
	scrub(time_ms)


func swap_sword() -> void:
	if ready_for_review:
		_weapon_id = "WPN_IRON_SWORD" if _weapon_id == "WPN_HERO_BASIC_SWORD" else "WPN_HERO_BASIC_SWORD"
		hero.equip(_weapon_id)
		_update_world()


func toggle_camera() -> void:
	camera_enabled = not camera_enabled
	if is_instance_valid(camera):
		camera.restore()


func toggle_effects() -> void:
	effects_enabled = not effects_enabled
	if is_instance_valid(effects):
		effects.set_vfx_enabled(effects_enabled)


func _process(delta: float) -> void:
	if not ready_for_review or capture_mode:
		return
	controller.advance(delta)
	_update_world()
	if camera_enabled:
		camera.advance(delta)


func _impact_origin() -> Vector2:
	var record: Dictionary = _data.weapon_attachment_data.frames["golden_cyclone:16"]
	var weapon: Dictionary = hero.equipped
	var tip: Vector2 = (_vec(weapon.review_blade_tip) - _vec(weapon.grip_pivot))
	tip *= float(weapon.display_scale) * float(record.weapon_scale)
	tip = tip.rotated(deg_to_rad(float(record.hand_rotation_degrees)))
	var hand := Vector2(float(record.hand_anchor_x), float(record.hand_anchor_y)) - _vec(_data.ground_anchor)
	return TARGET + Vector2(0, -92) - (hand + tip) * hero.scale


func weapon_tip_world() -> Vector2:
	var sprite: Sprite2D = hero.weapon_front if hero.weapon_front.visible else hero.weapon_back
	return sprite.to_global(_vec(hero.equipped.review_blade_tip) + sprite.offset)


func _update_world() -> void:
	if not ready_for_review:
		return
	var time_ms: float = controller.get_position_ms()
	var impact := _impact_origin()
	if controller.state == Controller.State.IDLE:
		hero.position = HOME
	elif time_ms < 800:
		hero.position = HOME
	elif time_ms < 930:
		hero.position = HOME.lerp(impact, smoothstep(800, 930, time_ms))
	elif time_ms < 1080:
		hero.position = impact
	else:
		hero.position = impact.lerp(HOME, smoothstep(1080, 1500, time_ms))
		if camera_enabled and not _recovery_focus:
			camera.focus_on(Vector2(512, 288), Vector2.ONE, .42 / _review_speed)
			_recovery_focus = true
	defender.position = TARGET
	defender.modulate = Color.WHITE
	if not hit_times.is_empty() and time_ms >= 930:
		var reaction: float = clampf((time_ms - 1000) / 300, 0, 1)
		defender.position += Vector2(-16, -4) * sin(reaction * PI)
		defender.modulate = Color(1.2, .85, .7) if time_ms < 1010 else Color.WHITE
	camera.hitstop_active = time_ms >= 930 and time_ms < 1000 and controller.state != Controller.State.IDLE
	_update_effects(time_ms)
	_slider.set_value_no_signal(time_ms)
	_status.text = "Golden Cyclone | CANDIDATE / needs_review | %02d / 22 | hits: %d | %s | target: existing Hero" % [
		controller.get_frame_index() + 1, hit_times.size(), _weapon_id]
	queue_redraw()


func _on_hit(_id: StringName, _attacker: Variant, _defender: Variant) -> void:
	hit_times.append(controller.get_position_ms())
	if camera_enabled:
		camera.shake(3, .16)


func _on_end(_id: StringName, _attacker: Variant, _defender: Variant) -> void:
	camera.restore()


func _load_effects() -> void:
	var manifest := _read(DATA + "vfx.json")
	for entry in manifest.get("effects", []):
		var sprite := Sprite2D.new()
		sprite.texture = Unit.load_texture("res://" + str(entry.path))
		sprite.centered = false
		sprite.offset = -_vec(entry.anchor_normalized) * sprite.texture.get_size()
		sprite.scale = Vector2.ONE * float(entry.review_scale)
		sprite.z_index = 5 if entry.space == "world_ground" else 30
		effects.get_effect_slot(StringName(entry.id)).add_child(sprite)
		_effect_sprites[entry.id] = sprite


func _update_effects(time_ms: float) -> void:
	for key: String in _effect_sprites:
		var sprite: Sprite2D = _effect_sprites[key]
		var ground_effect: bool = key in ["golden_energy_ring_001", "cyclone_ground_dust_001"]
		sprite.position = hero.position if ground_effect else weapon_tip_world()
		if key in ["golden_impact_sparks_001", "golden_final_flash_001"]:
			sprite.position = TARGET + Vector2(0, -92)
			sprite.visible = effects_enabled and time_ms >= 930 and time_ms < 1030
		else:
			sprite.visible = effects_enabled and time_ms >= 340 and time_ms < 1080
		if key in ["golden_spinning_arc_001", "golden_motion_trail_001"]:
			sprite.rotation = deg_to_rad(float(hero.current_attachment.get("hand_rotation_degrees", 0)))
		sprite.modulate.a = minf(clampf((time_ms - 300) / 80, 0, 1), clampf((1100 - time_ms) / 100, 0, 1))


func capture_sequence() -> void:
	if not ready_for_review:
		get_tree().quit(1)
		return
	capture_mode = true
	get_viewport().gui_disable_input = true
	var modes: Dictionary = {}
	for mode: String in ["normal", "slow_no_effects"]:
		var folder := "godot_frames_" + mode
		var directory := ProjectSettings.globalize_path(PREVIEWS + folder)
		DirAccess.make_dir_recursive_absolute(directory)
		var captures: Array[Dictionary] = []
		camera_enabled = mode == "normal"
		effects_enabled = mode == "normal"
		_slow_toggle.set_pressed_no_signal(mode != "normal")
		effects.set_vfx_enabled(effects_enabled)
		camera.restore()
		restart()
		for index: int in range(85):
			_update_world()
			camera.advance(.02)
			await RenderingServer.frame_post_draw
			var image := get_viewport().get_texture().get_image()
			if image.is_empty() or image.get_size() != Vector2i(1024, 576):
				printerr("Capture failed: real 1024x576 viewport image required")
				get_tree().quit(1)
				return
			var name := "godot_%03d.png" % index
			if image.save_png(directory.path_join(name)) != OK:
				get_tree().quit(1)
				return
			captures.append({"path": folder + "/" + name, "duration_ms": 20 if mode == "normal" else 80,
				"source_frame": controller.get_frame_index() + 1,
				"sha256": FileAccess.get_sha256(directory.path_join(name))})
			if index == 47 and mode == "normal":
				image.save_png(ProjectSettings.globalize_path(PREVIEWS + "hero_golden_cyclone_godot_preview.png"))
			controller.advance(.02)
		modes[mode] = {"frames": captures, "hit_times_ms": hit_times.duplicate(),
			"camera_enabled": camera_enabled, "effects_enabled": effects_enabled,
			"logical_sample_interval_ms": 20, "playback_speed": 1.0 if mode == "normal" else .25}
	var file := FileAccess.open(PREVIEWS + "godot_capture_receipt.json", FileAccess.WRITE)
	file.store_string(JSON.stringify({"engine": Engine.get_version_info().string, "modes": modes,
		"actual_viewport": true, "candidate_only": true,
		"review_assets_sha256": FileAccess.get_sha256(DATA + "review_assets.json"),
		"vfx_sha256": FileAccess.get_sha256(DATA + "vfx.json"),
		"scene_sha256": FileAccess.get_sha256("res://scenes/battle/golden_cyclone_preview.gd")}, "\t"))
	file.close()
	print("GOLDEN_CYCLONE_CAPTURE_OK")
	get_tree().quit(0)
