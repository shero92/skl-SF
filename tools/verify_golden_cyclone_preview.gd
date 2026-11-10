extends SceneTree
## Real candidate assets and reusable controller contracts; no production activation.

const Review = preload("res://scenes/battle/golden_cyclone_preview.tscn")
var failures: int = 0


func _initialize() -> void:
	call_deferred("run")


func check(value: bool, message: String) -> void:
	if not value:
		failures += 1
		printerr("FAIL: " + message)


func run() -> void:
	var preview = Review.instantiate()
	root.add_child(preview)
	preview.set_process(false)
	await process_frame
	check(preview.ready_for_review, "candidate exports load: " + preview.initialization_error)
	if not preview.ready_for_review:
		quit(1)
		return
	check(preview.get("_effect_sprites").size() == 6, "six independent VFX assets load")
	preview.toggle_effects()
	check(not preview.effects.visible, "VFX toggle hides separate effect layer")
	preview.toggle_effects()
	for hz: int in [30, 60, 144]:
		preview.restart()
		for tick: int in range(hz * 3):
			preview.controller.advance(1.0 / hz)
			preview.call("_update_world")
			if preview.controller.state == 0:
				break
		check(preview.controller.state == 0, "attack finishes at every update rate")
		check(preview.hit_times.size() == 1 and is_equal_approx(preview.hit_times[0], 930), "one hit at 930ms")
		check(preview.hero.position.is_equal_approx(Vector2(700, 540)), "hero position restored")
		check(preview.defender.position.is_equal_approx(Vector2(280, 310)), "target position restored")
	preview.restart()
	preview.controller.advance(.5)
	preview.controller.pause()
	preview.controller.advance(.7)
	check(is_equal_approx(preview.controller.get_position_ms(), 500), "paused advance preserves position")
	check(preview.controller.state != 0, "paused attack is not completed")
	preview.controller.seek(940)
	check(preview.hit_times.is_empty(), "scrubbing is side-effect free")
	preview.controller.resume()
	preview.controller.advance(.2)
	check(preview.hit_times.is_empty(), "consumed scrubbed hit does not replay")
	preview.restart()
	preview.controller.advance(.94)
	preview.controller.seek(400)
	preview.controller.resume()
	preview.controller.advance(.6)
	check(preview.hit_times.size() == 1, "rewind does not duplicate hit")
	preview.cancel_attack()
	var facade: Dictionary = preview.play_attack(&"golden_cyclone", preview.hero, preview.defender)
	check(facade.ok, "review facade accepts its actual modular units")
	preview.cancel_attack()
	check(preview.camera.zoom.is_equal_approx(Vector2.ONE), "camera restored after cancel")
	preview.restart()
	preview.controller.hit.connect(func(_id, _a, _d): preview.controller.pause(), CONNECT_ONE_SHOT)
	preview.controller.advance(.95)
	check(preview.controller.state != 0 and is_equal_approx(preview.controller.get_position_ms(), 930),
		"pause from a hit listener does not finish the attack")
	preview.controller.resume()
	preview.controller.advance(.6)
	check(preview.hit_times.size() == 1 and preview.controller.state == 0, "listener pause resumes without duplicate hits")
	preview.restart()
	preview.controller.set_speed(.25)
	preview.controller.advance(1)
	check(is_equal_approx(preview.controller.get_position_ms(), 250), "slow motion uses shared clock")
	preview.cancel_attack()
	var weapon_receipt: Dictionary = {}
	for sword: String in ["WPN_HERO_BASIC_SWORD", "WPN_IRON_SWORD"]:
		preview.hero.equip(sword)
		preview.restart()
		preview.controller.pause()
		var elapsed := 0.0
		var maximum_grip_error := 0.0
		var contact_error := 0.0
		for index: int in range(22):
			preview.controller.seek(elapsed)
			preview.call("_update_world")
			var hero = preview.hero
			var sprite: Sprite2D = hero.weapon_front if hero.weapon_front.visible else hero.weapon_back
			check(sprite.visible, "weapon rendered for frame " + str(index))
			var grip: Array = hero.equipped.grip_pivot
			var grip_world := sprite.to_global(Vector2(grip[0], grip[1]) + sprite.offset)
			var record: Dictionary = hero.current_attachment
			var hand: Vector2 = hero.to_global(hero.body.position + Vector2(record.hand_anchor_x, record.hand_anchor_y))
			maximum_grip_error = maxf(maximum_grip_error, grip_world.distance_to(hand))
			check(is_zero_approx(hero.rotation), "body is not rotated to fake poses")
			preview.camera.zoom = Vector2.ONE * 1.04
			preview.camera.offset = Vector2(-22, 12)
			preview.camera.force_update_scroll()
			for visual in [hero.body, sprite]:
				var texture: Texture2D = hero.body.sprite_frames.get_frame_texture(hero.body.animation, hero.body.frame) if visual == hero.body else sprite.texture
				var used: Rect2i = texture.get_image().get_used_rect()
				var origin: Vector2 = Vector2(used.position) + visual.offset
				if visual.centered:
					origin -= texture.get_size() / 2
				var on_screen: Rect2 = visual.get_global_transform_with_canvas() * Rect2(origin, Vector2(used.size))
				check(Rect2(0, 0, 1024, 576).encloses(on_screen), "camera keeps body/weapon in frame " + str(index))
			if index == 16:
				contact_error = preview.weapon_tip_world().distance_to(Vector2(280, 218))
			elapsed += float(preview.get("_data").frames[index].duration_ms)
		check(maximum_grip_error < .01, "measured hand and weapon grip coincide")
		check(contact_error < .01, "actual sword tip reaches target on hit frame")
		weapon_receipt[sword] = {"frames_checked": 22, "maximum_grip_error_px": maximum_grip_error,
			"impact_tip_error_px": contact_error, "body_resource_shared": true}
	preview.cancel_attack()
	var directory := "res://game_factory/golden_cyclone/v001/previews"
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(directory))
	var file := FileAccess.open(directory + "/weapon_swap_verification.json", FileAccess.WRITE)
	file.store_string(JSON.stringify({"weapons": weapon_receipt, "owner_approved": false,
		"render_quality_review_required": true, "engine": Engine.get_version_info().string}, "\t"))
	file.close()
	preview.queue_free()
	await process_frame
	if failures == 0:
		print("GOLDEN_CYCLONE_PREVIEW_OK")
	quit(0 if failures == 0 else 1)
