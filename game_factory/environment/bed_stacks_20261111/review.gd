extends SceneTree
const BASE := "res://game_factory/environment/"
func _initialize() -> void:
	call_deferred("capture")
func label(board: Node2D, text: String, position: Vector2) -> void:
	var node := Label.new()
	node.text = text
	node.position = position
	board.add_child(node)
func sprite(board: Node2D, path: String, position: Vector2, zoom: int) -> void:
	var im := Image.load_from_file("res://"+path)
	assert(im != null and not im.is_empty())
	var node := Sprite2D.new()
	node.texture = ImageTexture.create_from_image(im)
	node.centered = false
	node.position = position
	node.scale = Vector2.ONE*zoom
	board.add_child(node)
func capture() -> void:
	root.size = Vector2i(1536,1200)
	root.content_scale_size = Vector2i(1536,1200)
	for art: String in ["ART-0048","ART-0049"]:
		var board := Node2D.new()
		board.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		root.add_child(board)
		var bg := ColorRect.new()
		bg.size = Vector2(1536,1200)
		bg.color = Color("27567a")
		board.add_child(bg)
		var manifest: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(BASE+art+"/v001/manifest.json"))
		label(board,art+" | SOURCE REVIEW | OWNER AUTO-APPROVED | NO ROOM INTEGRATION",Vector2(20,12))
		var selected: Dictionary = manifest.items[0]
		label(board,"Reference crop (not production)",Vector2(20,52))
		sprite(board,str(selected.reference_crop_path),Vector2(20,82),1)
		label(board,"Native1x | original alpha over blue",Vector2(360,52))
		sprite(board,str(selected.native_review_path),Vector2(360,82),1)
		label(board,"Native2x | nearest",Vector2(720,52))
		sprite(board,str(selected.native_review_path),Vector2(720,82),2)
		if art == "ART-0048":
			label(board,"South foot at bottom; north head/pillows at top.",Vector2(20,720))
			label(board,"Native255x290; source1178x1335 passes1020x1160 minimum.",Vector2(20,760))
			label(board,"No floor, neighbours or cast shadow. Placement/collision pending.",Vector2(20,800))
		else:
			var failed: Dictionary = manifest.rejected_attempts[0]
			label(board,"Cluster reference | foreground wall omitted in new source",Vector2(20,450))
			sprite(board,str(failed.reference_crop_path),Vector2(20,486),1)
			label(board,"Candidate1x: BLOCKED, SOURCE HEIGHT743 BELOW760",Vector2(620,450))
			sprite(board,str(failed.native_review_path),Vector2(620,486),1)
			label(board,"Candidate2x inspection ONLY | do not activate rejected source",Vector2(20,710))
			sprite(board,str(failed.native_review_path),Vector2(20,745),2)
			label(board,"Arch accepted source; cluster remains requested. No room placement tested.",Vector2(20,1170))
		await process_frame
		await RenderingServer.frame_post_draw
		await RenderingServer.frame_post_draw
		var output := BASE+art+"/v001/godot_native_review.png"
		var capture_image := root.get_texture().get_image()
		if capture_image.is_empty() or capture_image.save_png(ProjectSettings.globalize_path(output)) != OK:
			quit(1)
			return
		var receipt := FileAccess.open(BASE+art+"/v001/godot_review_receipt.json",FileAccess.WRITE)
		receipt.store_string(JSON.stringify({"actual_viewport":true,"engine":Engine.get_version_info().string,
			"canvas_size":[1536,1200],"owner_approved":true,"production_active":false,"room_integration_verified":false,
			"manifest_sha256":FileAccess.get_sha256(BASE+art+"/v001/manifest.json"),
			"review_script_sha256":FileAccess.get_sha256("res://game_factory/environment/bed_stacks_20261111/review.gd"),
			"render_sha256":FileAccess.get_sha256(output)},"\t"))
		receipt.close()
		board.queue_free()
		await process_frame
	print("ART0048_ART0049_SOURCE_REVIEW_OK_CLUSTER_BLOCKED")
	quit(0)
