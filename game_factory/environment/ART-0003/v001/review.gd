extends SceneTree
const BASE := "res://game_factory/environment/ART-0003/v001/"
func _initialize() -> void:
	call_deferred("_capture")
func caption(board: Node2D, text: String, at: Vector2) -> void:
	var label := Label.new()
	label.text = text
	label.position = at
	board.add_child(label)
func _capture() -> void:
	root.size = Vector2i(960,640)
	root.content_scale_size = Vector2i(960,640)
	var board := Node2D.new()
	board.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	root.add_child(board)
	var bg := ColorRect.new()
	bg.size = Vector2(960,640)
	bg.color = Color("183751")
	board.add_child(bg)
	caption(board,"ART-0003 | FOUR AUTHORED FOAM PHASES | OWNER AUTO-APPROVED",Vector2(16,10))
	caption(board,"Fixed canvas; no per-frame fit. Native96x48 / 2x. Map contact calibration pending.",Vector2(16,38))
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(BASE+"manifest.json"))
	var textures: Array[ImageTexture] = []
	for i: int in range(data.items.size()):
		var im := Image.load_from_file("res://"+str(data.items[i].native_review_path))
		if im == null or im.is_empty():
			quit(1)
			return
		var texture := ImageTexture.create_from_image(im)
		textures.append(texture)
		caption(board,str(data.items[i].id)+" 250ms",Vector2(18+i*235,80))
		for zoom: int in [1,2]:
			var sprite := Sprite2D.new()
			sprite.texture = texture
			sprite.centered = false
			sprite.scale = Vector2.ONE*zoom
			sprite.position = Vector2(25+i*235,110 if zoom==1 else 174)
			board.add_child(sprite)
	caption(board,"Actual Godot playback: 4fps, 1 second cycle | 6x inspection",Vector2(18,302))
	var panel := ColorRect.new()
	panel.position = Vector2(180,350)
	panel.size = Vector2(576,288)
	panel.color = Color("0f64a0")
	board.add_child(panel)
	var animated := Sprite2D.new()
	animated.centered = false
	animated.position = panel.position
	animated.scale = Vector2.ONE*6
	board.add_child(animated)
	var sequence: Array[Dictionary] = []
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(BASE+"godot_frames"))
	for tick: int in range(12):
		animated.texture = textures[tick%4]
		await process_frame
		await RenderingServer.frame_post_draw
		await RenderingServer.frame_post_draw
		var output := BASE+"godot_frames/capture_%02d.png"%tick
		var capture := root.get_texture().get_image()
		if capture.is_empty() or capture.save_png(ProjectSettings.globalize_path(output)) != OK:
			quit(1)
			return
		if tick == 0:
			capture.save_png(ProjectSettings.globalize_path(BASE+"godot_native_review.png"))
		sequence.append({"tick":tick,"frame_index":tick%4,"duration_ms":250,"path":output.trim_prefix("res://"),"sha256":FileAccess.get_sha256(output)})
		await create_timer(0.25).timeout
	var receipt := FileAccess.open(BASE+"godot_review_receipt.json",FileAccess.WRITE)
	receipt.store_string(JSON.stringify({"actual_viewport":true,"engine":Engine.get_version_info().string,
		"canvas_size":[960,640],"source_count":4,"fps":4,"cycles_captured":3,"sequence":sequence,
		"owner_approved":true,"approval_basis":"owner_automatic_20261111","production_active":false,
		"scene_calibration_verified":false,"review_zoom":[1,2,6],"manifest_sha256":FileAccess.get_sha256(BASE+"manifest.json"),
		"review_script_sha256":FileAccess.get_sha256(BASE+"review.gd"),"render_sha256":FileAccess.get_sha256(BASE+"godot_native_review.png")},"\t"))
	receipt.close()
	print("ART0003_FOAM_GODOT_PLAYBACK_OK")
	quit(0)
