extends SceneTree
const BASE := "res://game_factory/environment/"
func _initialize() -> void:
	call_deferred("_capture")
func label(board: Node2D, text: String, position: Vector2) -> void:
	var node := Label.new()
	node.text = text
	node.position = position
	board.add_child(node)
func sprite(board: Node2D, path: String, position: Vector2) -> bool:
	var im := Image.load_from_file("res://"+path)
	if im == null or im.is_empty():
		return false
	var node := Sprite2D.new()
	node.texture = ImageTexture.create_from_image(im)
	node.centered = false
	node.position = position
	board.add_child(node)
	return true
func _capture() -> void:
	root.size = Vector2i(1280,800)
	root.content_scale_size = Vector2i(1280,800)
	for art: String in ["ART-0044","ART-0045"]:
		var board := Node2D.new()
		board.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		root.add_child(board)
		var bg := ColorRect.new()
		bg.size = Vector2(1280,800)
		bg.color = Color("264c66")
		board.add_child(bg)
		var manifest: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(BASE+art+"/v001/manifest.json"))
		var candidates: Array = manifest.rejected_attempts
		label(board,art+" | CANDIDATES ONLY | REQUESTED 4X SOURCE GATE FAILED",Vector2(20,12))
		label(board,"Owner auto-approval recorded; technical qualification remains false. No production activation.",Vector2(20,42))
		label(board,"Reference crop only",Vector2(20,80))
		if not sprite(board,str(candidates[0].reference_crop_path),Vector2(20,110)):
			quit(1)
			return
		for i: int in range(candidates.size()):
			var item: Dictionary = candidates[i]
			var at := Vector2(310+i*290,110)
			label(board,"Attempt "+str(i+1)+" | requested native1x",at+Vector2(0,-30))
			if not sprite(board,str(item.native_review_path),at):
				quit(1)
				return
			label(board,"Source "+str(item.pixel_size),at+Vector2(0,560))
			label(board,"Required "+str(item.requested_minimum_master),at+Vector2(0,590))
		label(board,"No upscale / no mirror / no silent native-size reduction. No room placement or collision calibration.",Vector2(20,756))
		await process_frame
		await RenderingServer.frame_post_draw
		await RenderingServer.frame_post_draw
		var output := BASE+art+"/v001/godot_candidate_review.png"
		var capture := root.get_texture().get_image()
		if capture.is_empty() or capture.save_png(ProjectSettings.globalize_path(output)) != OK:
			quit(1)
			return
		var receipt := FileAccess.open(BASE+art+"/v001/godot_review_receipt.json",FileAccess.WRITE)
		receipt.store_string(JSON.stringify({"actual_viewport":true,"engine":Engine.get_version_info().string,
			"canvas_size":[1280,800],"candidate_count":candidates.size(),"qualified_production_count":0,
			"requested4x_gate_passed":false,"owner_approved":true,"production_active":false,
			"manifest_sha256":FileAccess.get_sha256(BASE+art+"/v001/manifest.json"),
			"review_script_sha256":FileAccess.get_sha256("res://game_factory/environment/curved_side_walls_20261111/review.gd"),
			"render_sha256":FileAccess.get_sha256(output)},"\t"))
		receipt.close()
		board.queue_free()
		await process_frame
	print("CURVED_WALLS_CANDIDATE_CAPTURE_OK_QUALIFIED_OUTPUTS_ZERO")
	quit(0)
