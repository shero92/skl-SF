extends SceneTree
## Genuine Godot rendering of delivered PNG, no live actor replacement.
func _initialize() -> void:
	call_deferred("capture")

func capture() -> void:
	var viewport := SubViewport.new()
	viewport.size = Vector2i(1536, 1024)
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(viewport)
	var canvas := Node2D.new()
	viewport.add_child(canvas)
	var room := Sprite2D.new()
	room.texture = ImageTexture.create_from_image(Image.load_from_file("res://map_factory/references/hero_room_01_target_20261103.png"))
	room.centered = false
	canvas.add_child(room)
	var hero := Sprite2D.new()
	hero.texture = ImageTexture.create_from_image(Image.load_from_file("res://.agents/graphics/deliveries/ART-0054/hero_map_sf_down_idle_01.png"))
	hero.centered = false
	hero.position = Vector2(920-48, 660-90)
	hero.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	canvas.add_child(hero)
	var label := Label.new()
	label.text = "ART-0054: unarmed down idle / native 96x96, figure 80px\nQA placement only; original painted reference hero remains visible."
	label.position = Vector2(20, 940)
	label.add_theme_color_override("font_color", Color.WHITE)
	label.add_theme_color_override("font_shadow_color", Color.BLACK)
	label.add_theme_constant_override("shadow_offset_x", 2)
	label.add_theme_constant_override("shadow_offset_y", 2)
	canvas.add_child(label)
	for i in 8:
		await process_frame
	await RenderingServer.frame_post_draw
	var result := viewport.get_texture().get_image().save_png("res://game_factory/environment/ART-0054/v001/godot_room_review.png")
	print("ART0054_GODOT_CAPTURE ", result)
	quit(0 if result == OK else 1)
