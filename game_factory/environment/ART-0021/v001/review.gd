extends SceneTree
## Native placement + catalog + 2x catalog QA; never loads a production map.
const BASE := "res://game_factory/environment/ART-0021/v001/"
func _initialize() -> void:
	call_deferred("_capture")
func _capture() -> void:
	root.size = Vector2i(1536,1024)
	root.content_scale_size = Vector2i(1536,1024)
	var board := Node2D.new()
	board.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	root.add_child(board)
	var background := ColorRect.new()
	background.size = Vector2(1536,1024)
	background.color = Color("303c50")
	board.add_child(background)
	var title := Label.new()
	title.text = "ART-0021 | FOUR INDEPENDENT CHEST VIEWS | NEEDS REVIEW"
	title.position = Vector2(20,10)
	board.add_child(title)
	var note := Label.new()
	note.text = "Placement 58x73 / catalog 191x157 / catalog 2x. Uniform fit; size and floor footprint provisional."
	note.position = Vector2(20,40)
	note.add_theme_font_size_override("font_size",16)
	board.add_child(note)
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(BASE+"manifest.json"))
	for i: int in range(data.items.size()):
		var item: Dictionary = data.items[i]
		var cell := Vector2(20+(i%2)*758,78+(i/2)*466)
		var label := Label.new()
		label.text = str(item.id)
		label.position = cell
		board.add_child(label)
		for variant: int in range(3):
			var review: Dictionary = item.reviews[0 if variant==0 else 1]
			var img := Image.load_from_file("res://"+str(review.path))
			if img == null or img.is_empty():
				quit(1)
				return
			var zoom := 2 if variant==2 else 1
			var sprite := Sprite2D.new()
			sprite.texture = ImageTexture.create_from_image(img)
			sprite.centered = false
			sprite.scale = Vector2.ONE*zoom
			sprite.position = cell+Vector2([12,100,330][variant],370-img.get_height()*zoom)
			board.add_child(sprite)
			var caption := Label.new()
			caption.text = ["placement 1x","catalog 1x","catalog 2x"][variant]
			caption.position = cell+Vector2([12,100,330][variant],384)
			caption.add_theme_font_size_override("font_size",13)
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
		"canvas_size":[1536,1024],"candidate_count":4,"owner_approved":false,"production_active":false,
		"scene_calibration_verified":false,"native_canvases":[[58,73],[191,157]],
		"manifest_sha256":FileAccess.get_sha256(BASE+"manifest.json"),
		"review_script_sha256":FileAccess.get_sha256(BASE+"review.gd"),
		"render_sha256":FileAccess.get_sha256(output)},"\t"))
	receipt.close()
	print("ART0021_CHEST_GODOT_REVIEW_OK")
	quit(0)
