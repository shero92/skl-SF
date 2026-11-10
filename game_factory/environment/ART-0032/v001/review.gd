extends SceneTree
## Candidate-only ART-0032 board. PNGs are loaded explicitly; no catalog activation.
const BASE := "res://game_factory/environment/ART-0032/v001/"
func _initialize() -> void:
	call_deferred("_capture")
func _capture() -> void:
	root.size = Vector2i(1024, 1024)
	root.content_scale_size = Vector2i(1024, 1024)
	var board := Node2D.new()
	board.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	root.add_child(board)
	var background := ColorRect.new()
	background.color = Color("#303c50")
	background.size = Vector2(1024, 1024)
	board.add_child(background)
	var title := Label.new()
	title.text = "ART-0032 | OWNER APPROVED / map calibration pending | native review prototypes"
	title.position = Vector2(16, 12)
	board.add_child(title)
	var manifest: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(BASE + "manifest.json"))
	for i: int in range(manifest.items.size()):
		var entry: Dictionary = manifest.items[i]
		var cell := Vector2(16 + (i % 3) * 336, 62 + (i / 3) * 310)
		var label := Label.new()
		label.text = entry.id
		label.add_theme_font_size_override("font_size", 14)
		label.position = cell
		board.add_child(label)
		var image := Image.load_from_file("res://" + str(entry.native_review_path))
		if image == null or image.is_empty():
			printerr("Missing candidate: " + str(entry.id))
			quit(1)
			return
		var sprite := Sprite2D.new()
		sprite.texture = ImageTexture.create_from_image(image)
		sprite.centered = false
		sprite.position = cell + Vector2((320 - image.get_width()) / 2.0, 286 - image.get_height())
		board.add_child(sprite)
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
		"canvas_size": [1024,1024], "candidate_count": manifest.items.size(), "owner_approved": manifest.get("owner_approved", false),
		"native_review_only": true, "map_integration_verified": false,
		"manifest_sha256": FileAccess.get_sha256(BASE + "manifest.json"),
		"render_sha256": FileAccess.get_sha256(output)}, "\t"))
	receipt.close()
	print("ART0032_GODOT_REVIEW_OK")
	quit(0)
