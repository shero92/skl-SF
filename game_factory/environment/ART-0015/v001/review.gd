extends SceneTree
const BASE := "res://game_factory/environment/ART-0015/v001/"
func _initialize() -> void:
	call_deferred("_capture")
func _capture() -> void:
	root.size = Vector2i(1536,1280)
	root.content_scale_size = Vector2i(1536,1280)
	var board := Node2D.new()
	board.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	root.add_child(board)
	var background := ColorRect.new()
	background.size = Vector2(1536,1280)
	background.color = Color("303c50")
	board.add_child(background)
	var heading := Label.new()
	heading.text = "ART-0015 | TWO INDEPENDENT OBLIQUE RUGS | NEEDS REVIEW"
	heading.position = Vector2(20,12)
	board.add_child(heading)
	var note := Label.new()
	note.text = "Native proposal 1x / 2x QA. Uniform fit only; exact floor projection and placement not calibrated."
	note.position = Vector2(20,42)
	note.add_theme_font_size_override("font_size",16)
	board.add_child(note)
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(BASE+"manifest.json"))
	for i: int in range(data.items.size()):
		var item: Dictionary = data.items[i]
		var cell := Vector2(20,90+i*580)
		var label := Label.new()
		label.text = str(item.id)
		label.position = cell
		board.add_child(label)
		var img := Image.load_from_file("res://"+str(item.native_review_path))
		if img == null or img.is_empty():
			quit(1)
			return
		var texture := ImageTexture.create_from_image(img)
		for zoom: int in [1,2]:
			var sprite := Sprite2D.new()
			sprite.texture = texture
			sprite.centered = false
			sprite.scale = Vector2.ONE*zoom
			sprite.position = cell+Vector2(20 if zoom==1 else 600,490-img.get_height()*zoom)
			board.add_child(sprite)
			var caption := Label.new()
			caption.text = str(zoom)+"x | "+str(img.get_width())+"x"+str(img.get_height())
			caption.position = cell+Vector2(20 if zoom==1 else 600,506)
			board.add_child(caption)
	await process_frame
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	var output := BASE+"godot_native_review.png"
	var capture := root.get_texture().get_image()
	if capture.is_empty() or capture.save_png(ProjectSettings.globalize_path(output)) != OK:
		quit(1)
		return
	var receipt := FileAccess.open(BASE+"godot_review_receipt.json",FileAccess.WRITE)
	receipt.store_string(JSON.stringify({"actual_viewport":true,"engine":Engine.get_version_info().string,
		"canvas_size":[1536,1280],"candidate_count":2,"owner_approved":false,"production_active":false,
		"scene_calibration_verified":false,"review_zoom":[1,2],
		"manifest_sha256":FileAccess.get_sha256(BASE+"manifest.json"),
		"review_script_sha256":FileAccess.get_sha256(BASE+"review.gd"),
		"render_sha256":FileAccess.get_sha256(output)},"\t"))
	receipt.close()
	print("ART0015_RUGS_GODOT_REVIEW_OK")
	quit(0)
