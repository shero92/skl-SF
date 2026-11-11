extends SceneTree
## ART-0023 candidate fixtures at native prototype size and 2x QA zoom.
const BASE := "res://game_factory/environment/ART-0023/v001/"
func _initialize() -> void:
	call_deferred("_capture")
func _capture() -> void:
	root.size = Vector2i(1024, 1024)
	root.content_scale_size = Vector2i(1024, 1024)
	var board := Node2D.new()
	board.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	root.add_child(board)
	var background := ColorRect.new()
	background.size = Vector2(1024, 1024)
	background.color = Color("#303c50")
	board.add_child(background)
	var heading := Label.new()
	heading.text = "ART-0023 | CANDIDATES | 1x native prototype / 2x QA zoom"
	heading.position = Vector2(16, 12)
	board.add_child(heading)
	var note := Label.new()
	note.text = "Yellow diamond = manually reviewed mount. Scene calibration pending."
	note.position = Vector2(16, 38)
	note.add_theme_font_size_override("font_size", 14)
	board.add_child(note)
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(BASE + "manifest.json"))
	for i: int in range(data.items.size()):
		var entry: Dictionary = data.items[i]
		var cell := Vector2(12 + (i % 2) * 506, 68 + (i / 2) * 460)
		var label := Label.new()
		label.text = entry.id
		label.position = cell
		label.add_theme_font_size_override("font_size", 14)
		board.add_child(label)
		var image := Image.load_from_file("res://" + str(entry.native_review_path))
		if image == null or image.is_empty():
			printerr("Missing fixture: " + str(entry.id))
			quit(1)
			return
		var texture := ImageTexture.create_from_image(image)
		for zoom: int in [1, 2]:
			var sprite := Sprite2D.new()
			sprite.texture = texture
			sprite.centered = false
			sprite.scale = Vector2.ONE * zoom
			sprite.position = cell + Vector2(42 if zoom == 1 else 220, 390 - image.get_height() * zoom)
			board.add_child(sprite)
			var pin := Polygon2D.new()
			pin.polygon = PackedVector2Array([Vector2(-3, 0), Vector2(0, -3), Vector2(3, 0), Vector2(0, 3)])
			pin.color = Color.YELLOW
			var anchor: Array = entry.native_review_mount_anchor
			pin.position = sprite.position + Vector2(float(anchor[0]), float(anchor[1])) * zoom
			board.add_child(pin)
			var scale_label := Label.new()
			scale_label.text = str(zoom) + "x"
			scale_label.position = cell + Vector2(42 if zoom == 1 else 220, 404)
			board.add_child(scale_label)
	await process_frame
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	var capture := root.get_texture().get_image()
	var output := BASE + "godot_native_review.png"
	if capture.is_empty() or capture.save_png(ProjectSettings.globalize_path(output)) != OK:
		quit(1)
		return
	var receipt := FileAccess.open(BASE + "godot_review_receipt.json", FileAccess.WRITE)
	receipt.store_string(JSON.stringify({"actual_viewport": true, "engine": Engine.get_version_info().string,
		"canvas_size": [1024,1024], "candidate_count": data.items.size(), "owner_approved": false,
		"review_zoom": [1,2], "scene_calibration_verified": false,
		"manifest_sha256": FileAccess.get_sha256(BASE + "manifest.json"),
		"review_script_sha256": FileAccess.get_sha256(BASE + "review.gd"),
		"render_sha256": FileAccess.get_sha256(output)}, "\t"))
	receipt.close()
	print("ART0023_GODOT_REVIEW_OK")
	quit(0)
