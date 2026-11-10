extends SceneTree
## Rejected candidate evidence only: never activates a tile or changes its alpha.
var attempt := 2
const BASE := "res://game_factory/environment/ART-0037/v001/"
func _initialize() -> void:
	for arg: String in OS.get_cmdline_user_args():
		if arg.begins_with("--attempt="):
			attempt = int(arg.trim_prefix("--attempt="))
	if attempt not in [1,2]:
		quit(1)
		return
	call_deferred("_capture")
func _capture() -> void:
	root.size = Vector2i(1280,1280)
	root.content_scale_size = Vector2i(1280,1280)
	var board := Node2D.new()
	board.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	root.add_child(board)
	var background := ColorRect.new()
	background.size = Vector2(1280,1280)
	background.color = Color("303c50")
	board.add_child(background)
	var title := Label.new()
	title.text = "ART-0037 REJECTED attempt " + str(attempt) + " | 2x2 native 512 tiles over project ocean QA"
	title.position = Vector2(20,15)
	board.add_child(title)
	var note := Label.new()
	note.text = "Source 1254x1254 < 2048x2048; alpha above 70%. Not delivered. Seams unapproved."
	note.position = Vector2(20,48)
	board.add_child(note)
	var ocean := Sprite2D.new()
	ocean.texture = ImageTexture.create_from_image(Image.load_from_file("res://game_factory/environment/batch_B3_20261110/qa/ocean_review_backdrop.png"))
	ocean.centered = false
	ocean.position = Vector2(128,100)
	board.add_child(ocean)
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(BASE+"manifest.json"))
	var entry: Dictionary = data.rejected_attempts[attempt-1]
	var tile := Image.load_from_file("res://" + str(entry.native_review_path))
	if tile == null or tile.is_empty():
		quit(1)
		return
	var texture := ImageTexture.create_from_image(tile)
	for y: int in range(2):
		for x: int in range(2):
			var sprite := Sprite2D.new()
			sprite.texture = texture
			sprite.centered = false
			sprite.position = Vector2(128+x*512,100+y*512)
			board.add_child(sprite)
	await process_frame
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	var output := BASE + "godot_tiled_review_attempt_%02d.png" % attempt
	var capture := root.get_texture().get_image()
	if capture.is_empty() or capture.save_png(ProjectSettings.globalize_path(output)) != OK:
		quit(1)
		return
	var receipt := FileAccess.open(BASE+"godot_tiled_receipt_attempt_%02d.json" % attempt,FileAccess.WRITE)
	receipt.store_string(JSON.stringify({"actual_viewport":true,"engine":Engine.get_version_info().string,
		"attempt":attempt,"tile_size":[512,512],"grid":[2,2],"owner_approved":false,"production_active":false,
		"manifest_sha256":FileAccess.get_sha256(BASE+"manifest.json"),
		"review_script_sha256":FileAccess.get_sha256("res://game_factory/environment/batch_B3_20261110/review_sea.gd"),
		"render_sha256":FileAccess.get_sha256(output)},"\t"))
	receipt.close()
	print("ART0037_REJECTED_TILE_CAPTURE_OK " + str(attempt))
	quit(0)
