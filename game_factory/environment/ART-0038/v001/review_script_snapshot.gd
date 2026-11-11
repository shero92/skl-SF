extends SceneTree
## Review-only viewport: no map, catalog, runtime textures or production scene is changed.
var art := "ART-0005"
func _initialize() -> void:
	for argument: String in OS.get_cmdline_user_args():
		if argument.begins_with("--art="):
			art = argument.trim_prefix("--art=")
	if art not in ["ART-0005", "ART-0038"]:
		quit(1)
		return
	call_deferred("_capture")

func _capture() -> void:
	root.size = Vector2i(1536, 1024)
	root.content_scale_size = Vector2i(1536, 1024)
	var base := "res://game_factory/environment/" + art + "/v001/"
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(base + "manifest.json"))
	var board := Node2D.new()
	board.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	root.add_child(board)
	var background := ColorRect.new()
	background.color = Color("303c50")
	background.size = Vector2(1536, 1024)
	board.add_child(background)
	var heading := Label.new()
	heading.text = art + " | B3 | NEEDS REVIEW | Native canvas 1x and 2x QA zoom"
	heading.position = Vector2(20, 12)
	board.add_child(heading)
	var note := Label.new()
	note.text = "Full source retained. Uniform nearest fit. Literal master size gaps in manifest. No scene calibration or owner approval."
	note.position = Vector2(20, 42)
	note.add_theme_font_size_override("font_size", 15)
	board.add_child(note)
	for i: int in range(data.items.size()):
		var item: Dictionary = data.items[i]
		var cell := Vector2(20 + (i % 2) * 758, 78 + (i / 2) * 466)
		var label := Label.new()
		label.text = item.id
		label.position = cell
		board.add_child(label)
		var image := Image.load_from_file("res://" + str(item.native_review_path))
		if image == null or image.is_empty():
			printerr("MISSING_NATIVE_REVIEW " + str(item.id))
			quit(1)
			return
		var texture := ImageTexture.create_from_image(image)
		for zoom: int in [1, 2]:
			var sprite := Sprite2D.new()
			sprite.texture = texture
			sprite.centered = false
			sprite.scale = Vector2.ONE * zoom
			sprite.position = cell + Vector2(18 if zoom == 1 else 290, 390 - image.get_height() * zoom)
			if art == "ART-0038":
				sprite.position = Vector2(30 if zoom == 1 else 510, 650 - image.get_height() * zoom)
			board.add_child(sprite)
			var caption := Label.new()
			caption.text = str(zoom) + "x | " + str(image.get_width()) + "x" + str(image.get_height())
			caption.position = sprite.position + Vector2(0, image.get_height() * zoom + 12)
			board.add_child(caption)
	if art == "ART-0038":
		var join_label := Label.new()
		join_label.text = "QA JOIN: existing / candidate / existing | baseline only; courses and cap joins NOT calibrated"
		join_label.position = Vector2(230, 716)
		board.add_child(join_label)
		var ocean := Image.load_from_file("res://game_factory/environment/batch_B3_20261110/qa/ocean_review_backdrop.png")
		var ocean_sprite := Sprite2D.new()
		ocean_sprite.texture = ImageTexture.create_from_image(ocean.get_region(Rect2i(0,0,960,190)))
		ocean_sprite.centered = false
		ocean_sprite.position = Vector2(240,760)
		board.add_child(ocean_sprite)
		for j: int in range(3):
			var path := "res://game_factory/environment/batch_B3_20261110/qa/neighbor_wall_native.png"
			if j == 1:
				path = "res://" + str(data.items[0].native_review_path)
			var join_sprite := Sprite2D.new()
			join_sprite.texture = ImageTexture.create_from_image(Image.load_from_file(path))
			join_sprite.centered = false
			join_sprite.position = Vector2(240+j*320,760)
			board.add_child(join_sprite)
	await process_frame
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	var capture := root.get_texture().get_image()
	var output := base + "godot_native_review.png"
	if capture.is_empty() or capture.save_png(ProjectSettings.globalize_path(output)) != OK:
		quit(1)
		return
	var receipt := FileAccess.open(base + "godot_review_receipt.json", FileAccess.WRITE)
	receipt.store_string(JSON.stringify({"actual_viewport": true, "engine": Engine.get_version_info().string,
		"canvas_size": [1536,1024], "candidate_count": data.items.size(), "owner_approved": false,
		"review_zoom": [1,2], "scene_calibration_verified": false,
		"manifest_sha256": FileAccess.get_sha256(base + "manifest.json"),
		"review_script_sha256": FileAccess.get_sha256("res://game_factory/environment/batch_B3_20261110/review.gd"),
		"render_sha256": FileAccess.get_sha256(output)}, "\t"))
	receipt.close()
	print(art + "_GODOT_REVIEW_OK")
	quit(0)
