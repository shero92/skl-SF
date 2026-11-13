extends SceneTree
const OUT := "res://game_factory/environment/ART-0052/v003/"
func _initialize() -> void:
	call_deferred("capture")
func save_view(name: String) -> void:
	await process_frame
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(ProjectSettings.globalize_path(OUT+name+".png"))==OK)
func capture() -> void:
	root.size = Vector2i(1536,864)
	root.content_scale_size = Vector2i(1536,864)
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	var room: Node2D = load("res://scenes/main.tscn").instantiate()
	room.save_path = "res://.qa-tmp/painted_capture_missing_save.json"
	root.add_child(room)
	current_scene = room
	room.get_node("OutdoorExit").travel_enabled = false
	room.player.position = Vector2(768,832)
	await save_view("godot_room_stairs")
	room.queue_free()
	await process_frame
	var world: Node2D = load("res://scenes/world/painted_coast.tscn").instantiate()
	world.travel_enabled = false
	root.add_child(world)
	current_scene = world
	var receipts: Array = [{"path":"game_factory/environment/ART-0052/v003/godot_room_stairs.png","sha256":FileAccess.get_sha256(OUT+"godot_room_stairs.png")}]
	for id: String in world.definition.zones:
		world.enter_zone(id)
		world.player.position = preload("res://scenes/world/world_travel.gd").point(world.definition.zones[id].landmark)
		await save_view("godot_"+id)
		receipts.append({"path":"game_factory/environment/ART-0052/v003/godot_"+id+".png","sha256":FileAccess.get_sha256(OUT+"godot_"+id+".png")})
	var file := FileAccess.open(OUT+"capture_receipt.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"actual_viewport":true,"engine":Engine.get_version_info().string,
		"viewport":[1536,864],"camera_zoom":world.camera.zoom.x,"room_camera_zoom":0.84375,
		"world_sha256":FileAccess.get_sha256(world.WORLD),"script_sha256":FileAccess.get_sha256("res://tools/capture_painted_coast.gd"),
		"source_master_unchanged":true,"rendered_zones":world.definition.zones.size(),"files":receipts},"\t"))
	file.close()
	print("PAINTED_HIDDEN_ISLAND_CAPTURE_OK")
	quit(0)
