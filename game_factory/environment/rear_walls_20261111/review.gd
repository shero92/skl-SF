extends SceneTree
const BASE := "res://game_factory/environment/"
func _initialize() -> void:
	call_deferred("_capture")
func label(board: Node2D, text: String, position: Vector2) -> void:
	var node := Label.new()
	node.text = text
	node.position = position
	board.add_child(node)
func image_sprite(board: Node2D, path: String, position: Vector2, zoom: int) -> bool:
	var im := Image.load_from_file("res://"+path)
	if im == null or im.is_empty():
		return false
	var node := Sprite2D.new()
	node.texture = ImageTexture.create_from_image(im)
	node.centered = false
	node.position = position
	node.scale = Vector2.ONE*zoom
	board.add_child(node)
	return true
func _capture() -> void:
	root.size = Vector2i(1536,1024)
	root.content_scale_size = Vector2i(1536,1024)
	for art: String in ["ART-0042","ART-0043"]:
		var board := Node2D.new()
		board.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		root.add_child(board)
		var bg := ColorRect.new()
		bg.size = Vector2(1536,1024)
		bg.color = Color("244c68")
		board.add_child(bg)
		var manifest: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(BASE+art+"/v001/manifest.json"))
		var item: Dictionary = manifest.items[0]
		label(board,art+" | INDEPENDENT REAR WALL | OWNER AUTO-APPROVED",Vector2(20,12))
		label(board,"Reference crop only (decor omitted in source)",Vector2(20,66))
		label(board,"New source at proposed native1x | alpha over blue",Vector2(600,66))
		if not image_sprite(board,str(item.reference_crop_path),Vector2(20,100),1) or not image_sprite(board,str(item.native_review_path),Vector2(600,100),1):
			quit(1)
			return
		label(board,"2x nearest inspection of whole canvas",Vector2(20,410))
		if not image_sprite(board,str(item.native_review_path),Vector2(20,450),2):
			quit(1)
			return
		label(board,"No room placement / join / collision calibration.",Vector2(980,460))
		label(board,"Reference is never a production sprite.",Vector2(980,492))
		label(board,"Canvas: "+str(item.native_canvas)+" | bottom-centre origin",Vector2(20,980))
		await process_frame
		await RenderingServer.frame_post_draw
		await RenderingServer.frame_post_draw
		var output := BASE+art+"/v001/godot_native_review.png"
		var capture := root.get_texture().get_image()
		if capture.is_empty() or capture.save_png(ProjectSettings.globalize_path(output)) != OK:
			quit(1)
			return
		var receipt := FileAccess.open(BASE+art+"/v001/godot_review_receipt.json",FileAccess.WRITE)
		receipt.store_string(JSON.stringify({"actual_viewport":true,"engine":Engine.get_version_info().string,
			"canvas_size":[1536,1024],"review_zoom":[1,2],"owner_approved":true,"approval_basis":"owner_automatic_20261111",
			"production_active":false,"room_integration_verified":false,"manifest_sha256":FileAccess.get_sha256(BASE+art+"/v001/manifest.json"),
			"review_script_sha256":FileAccess.get_sha256("res://game_factory/environment/rear_walls_20261111/review.gd"),
			"render_sha256":FileAccess.get_sha256(output)},"\t"))
		receipt.close()
		board.queue_free()
		await process_frame
	print("ART0042_ART0043_REAR_WALLS_GODOT_REVIEW_OK")
	quit(0)
