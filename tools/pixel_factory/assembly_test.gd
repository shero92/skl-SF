extends SceneTree
## Review-only integration through existing RoomFactory; no map history writes.
func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	var args := OS.get_cmdline_user_args()
	var spec: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
	var sprite_image := Image.load_from_file(spec.sprite)
	if sprite_image == null or sprite_image.get_width() != int(spec.width) or sprite_image.get_height() != int(spec.height):
		quit(1)
		return
	var viewport := SubViewport.new()
	viewport.size = Vector2i(1536, 1024)
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(viewport)
	var host := Node2D.new()
	viewport.add_child(host)
	var room := RoomFactory.new().build_room(spec.base_path, host)
	var texture := ImageTexture.create_from_image(sprite_image)
	var replaced := 0
	if bool(spec.get("is_floor", false)):
		for node in room.find_children("Floor_*", "Sprite2D", true, false):
			var old_size: Vector2 = node.texture.get_size()
			node.scale *= old_size / texture.get_size()
			node.texture = texture
			node.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
			replaced += 1
	if replaced == 0:
		var sprite := Sprite2D.new()
		sprite.texture = texture
		sprite.centered = false
		sprite.position = Vector2(640 - spec.anchor[0], 640 - spec.anchor[1])
		sprite.z_index = 100
		sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		room.add_child(sprite)
	# A completed category also gets independently placed candidates in this QA room.
	var candidate_index := 0
	for candidate in spec.get("candidates", []):
		if bool(spec.get("is_floor", false)):
			break
		var candidate_image := Image.load_from_file(candidate.path)
		if candidate_image == null:
			quit(1)
			return
		var candidate_sprite := Sprite2D.new()
		candidate_sprite.texture = ImageTexture.create_from_image(candidate_image)
		candidate_sprite.centered = false
		candidate_sprite.position = Vector2(320 + (candidate_index % 4) * 256 - candidate.anchor[0],
			384 + (candidate_index / 4) * 192 - candidate.anchor[1])
		candidate_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		candidate_sprite.z_index = 101 + candidate_index
		room.add_child(candidate_sprite)
		candidate_index += 1
	var result := {"passed": room.get_child_count() > 0 and texture.get_width() == int(spec.width),
		"room_factory": true, "replaced_floor_cells": replaced, "visual_approval": false}
	if args.has("capture"):
		for frame in range(8):
			await process_frame
		await RenderingServer.frame_post_draw
		var picture := viewport.get_texture().get_image()
		result["passed"] = result.passed and picture != null and picture.save_png(spec.output + "/room.png") == OK
	var receipt := FileAccess.open(spec.output + "/receipt.json", FileAccess.WRITE)
	receipt.store_string(JSON.stringify(result))
	quit(0 if result.passed else 1)
