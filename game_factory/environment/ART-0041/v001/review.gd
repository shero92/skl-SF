extends SceneTree
const BASE := "res://game_factory/environment/ART-0041/v001/"
func _initialize() -> void:
	call_deferred("_capture")
func add_label(board: Node2D, text: String, at: Vector2) -> void:
	var label := Label.new()
	label.text = text
	label.position = at
	board.add_child(label)
func add_sprite(board: Node2D, texture: Texture2D, at: Vector2, zoom: int, opacity: float = 1.0) -> void:
	var sprite := Sprite2D.new()
	sprite.texture = texture
	sprite.centered = false
	sprite.position = at
	sprite.scale = Vector2.ONE*zoom
	sprite.modulate.a = opacity
	board.add_child(sprite)
func save_view(path: String) -> bool:
	await process_frame
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	var img := root.get_texture().get_image()
	return not img.is_empty() and img.save_png(ProjectSettings.globalize_path(path))==OK
func _capture() -> void:
	root.size = Vector2i(1536,1024)
	root.content_scale_size = Vector2i(1536,1024)
	var manifest: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(BASE+"manifest.json"))
	var textures: Dictionary = {}
	for item: Dictionary in manifest.items:
		var im := Image.load_from_file("res://"+str(item.native_review_path))
		if im==null or im.is_empty():
			quit(1)
			return
		textures[str(item.id)] = ImageTexture.create_from_image(im)
	var board := Node2D.new()
	board.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	root.add_child(board)
	var bg := ColorRect.new()
	bg.size = Vector2(1536,1024);bg.color=Color("283849");board.add_child(bg)
	add_label(board,"ART-0041 | SIX INDEPENDENT ASSETS | Native checker / marker readability",Vector2(24,12))
	add_label(board,"4x4 checker,2x inspection: A/B seams, no grid lines",Vector2(24,58))
	for y: int in range(4):
		for x: int in range(4):
			add_sprite(board,textures["field_grass_a" if (x+y)%2==0 else "field_grass_b"],Vector2(24+x*128,90+y*128),2)
	add_label(board,"Rock64x96 / 3x inspection; no baked ground shadow",Vector2(600,58))
	add_sprite(board,textures.field_rock_block,Vector2(600,90),3)
	for col: int in range(3):
		var key: String = ["marker_move","marker_target","marker_active"][col]
		add_label(board,key+" | 3x / opacity0.75",Vector2(600+col*300,420))
		for row: int in range(2):
			var at := Vector2(600+col*300,460+row*250)
			add_sprite(board,textures["field_grass_a" if row==0 else "field_grass_b"],at,3)
			add_sprite(board,textures[key],at,3,0.75)
	add_label(board,"Two floor RGB originals preserved; RGBA export changes no RGB value.",Vector2(24,660))
	add_label(board,"Gold native phase aligns the empty source margin; masters remain untouched.",Vector2(24,700))
	if not await save_view(BASE+"godot_asset_review.png"):
		quit(1)
		return
	board.queue_free()
	await process_frame
	# Instantiate the real scene, then substitute only a QA rendering subclass in memory.
	var game = load("res://scenes/battle/tactical_battle.tscn").instantiate()
	game.set_script(load(BASE+"qa_battle.gd"))
	game.save_path = "res://.qa-tmp/art0041_absent_save.json"
	root.add_child(game)
	game.set_process(false);game.set_process_unhandled_input(false)
	if not await save_view(BASE+"godot_skirmish_review.png"):
		quit(1)
		return
	var receipt := FileAccess.open(BASE+"godot_review_receipt.json",FileAccess.WRITE)
	receipt.store_string(JSON.stringify({"actual_viewport":true,"engine":Engine.get_version_info().string,
		"canvas_size":[1536,1024],"source_count":6,"owner_approved":true,"production_active":false,
		"existing_scene":"scenes/battle/tactical_battle.tscn","existing_scene_sha256":FileAccess.get_sha256("res://scenes/battle/tactical_battle.tscn"),
		"scene_usage":"rendering-only QA subclass in memory; no production script edits; frozen session; target marker visual demo only",
		"gameplay_integration_verified":false,"marker_opacity":0.75,
		"manifest_sha256":FileAccess.get_sha256(BASE+"manifest.json"),"review_script_sha256":FileAccess.get_sha256(BASE+"review.gd"),
		"qa_override_sha256":FileAccess.get_sha256(BASE+"qa_battle.gd"),"asset_render_sha256":FileAccess.get_sha256(BASE+"godot_asset_review.png"),
		"skirmish_render_sha256":FileAccess.get_sha256(BASE+"godot_skirmish_review.png")},"\t"))
	receipt.close()
	print("ART0041_ASSETS_AND_EXISTING_SKIRMISH_QA_CAPTURE_OK")
	quit(0)
