extends SceneTree
const BASE := "res://game_factory/environment/ART-0040/v001/"
func _initialize() -> void:
	call_deferred("_capture")
func caption(board: Node2D, text: String, at: Vector2) -> void:
	var label := Label.new()
	label.text = text
	label.position = at
	board.add_child(label)
func _capture() -> void:
	root.size = Vector2i(960,720)
	root.content_scale_size = Vector2i(960,720)
	var board := Node2D.new()
	board.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	root.add_child(board)
	var bg := ColorRect.new()
	bg.size = Vector2(960,720)
	bg.color = Color("303c50")
	board.add_child(bg)
	caption(board,"ART-0040 | INDEPENDENT EAST LANTERN | OWNER AUTO-APPROVED",Vector2(16,12))
	caption(board,"Left mount / right arm. Native29x53. L07 placed in v0028 by PR178; mount calibration provisional.",Vector2(16,42))
	var manifest: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(BASE+"manifest.json"))
	var item: Dictionary = manifest.items[0]
	var im := Image.load_from_file("res://"+str(item.native_review_path))
	if im == null or im.is_empty():
		quit(1)
		return
	var texture := ImageTexture.create_from_image(im)
	for zoom: int in [1,3,8]:
		var pos := Vector2(60 if zoom==1 else (230 if zoom==3 else 520),140)
		var background := ColorRect.new()
		background.position = pos-Vector2(12,12)
		background.size = Vector2(29,53)*zoom+Vector2(24,24)
		background.color = Color("e3dfd0") if zoom==3 else Color("28597e")
		board.add_child(background)
		var sprite := Sprite2D.new()
		sprite.texture = texture
		sprite.centered = false
		sprite.position = pos
		sprite.scale = Vector2.ONE*zoom
		board.add_child(sprite)
		caption(board,str(zoom)+"x nearest",pos+Vector2(-10,-42))
		var pin := Line2D.new()
		pin.width = 1
		pin.default_color = Color.MAGENTA
		var pivot := pos+Vector2(float(item.native_origin[0]),float(item.native_origin[1]))*zoom
		pin.add_point(pivot+Vector2(-4,0)); pin.add_point(pivot+Vector2(4,0))
		board.add_child(pin)
	caption(board,"Magenta tick = measured wall mount. Alpha composited on blue and ivory.",Vector2(16,608))
	caption(board,"Colored RGB beneath alpha0 is invisible; no painted halo in the actual sprite.",Vector2(16,638))
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
		"canvas_size":[960,720],"owner_approved":true,"approval_basis":"owner_automatic_20261111","production_active":true,
		"wall_calibration_verified":false,"review_zoom":[1,3,8],"manifest_sha256":FileAccess.get_sha256(BASE+"manifest.json"),
		"review_script_sha256":FileAccess.get_sha256(BASE+"review.gd"),"render_sha256":FileAccess.get_sha256(output)},"\t"))
	receipt.close()
	print("ART0040_EAST_LANTERN_GODOT_REVIEW_OK")
	quit(0)
