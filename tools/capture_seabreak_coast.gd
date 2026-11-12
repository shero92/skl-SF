extends SceneTree
const OUTPUT := "res://docs/previews/seabreak_coast/"
var world: Node2D
func _initialize() -> void:
	call_deferred("capture")
func save_view(name: String, position: Vector2, zoom: float) -> void:
	world.camera.position = position
	world.camera.zoom = Vector2.ONE*zoom
	world.camera.reset_smoothing()
	await process_frame
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	var im := root.get_texture().get_image()
	assert(im.save_png(ProjectSettings.globalize_path(OUTPUT+name+".png")) == OK)
func capture() -> void:
	root.size = Vector2i(1536,1024)
	root.content_scale_size = Vector2i(1536,1024)
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUTPUT))
	world = load("res://scenes/world/seabreak_coast.tscn").instantiate()
	world.travel_enabled = false
	root.add_child(world)
	current_scene = world
	world.player.movement_enabled = false
	world.camera.position_smoothing_enabled = false
	world.camera.reparent(world,false)
	await save_view("arrival",world.player.position,1.0)
	await save_view("overview",Vector2(3072,2048),0.25)
	for landmark: Dictionary in world.definition.landmarks:
		world.player.position = Vector2(float(landmark.cell[0])*64+32,float(landmark.cell[1])*64+32)
		await save_view(str(landmark.id),world.player.position,1.0)
	var receipts: Array = []
	for name: String in ["arrival","overview","sanctuary_gate","compass_court","palm_gardens","beacon_terrace","sunken_archive","quiet_overlook"]:
		receipts.append({"path":"docs/previews/seabreak_coast/"+name+".png","sha256":FileAccess.get_sha256(OUTPUT+name+".png")})
	var file := FileAccess.open(OUTPUT+"capture_receipt.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"actual_Godot_viewport":true,"engine":Engine.get_version_info().string,
		"canvas_size":[1536,1024],"map_id":"seabreak_coast_01","map_version":world.room.get_meta("map_version"),
		"map_sha256":FileAccess.get_sha256("res://map_factory/maps/seabreak_coast_01/latest.json"),
		"world_connection_sha256":FileAccess.get_sha256("res://map_factory/worlds/seabreak_coast_01.json"),
		"capture_script_sha256":FileAccess.get_sha256("res://tools/capture_seabreak_coast.gd"),"files":receipts},"\t"))
	file.close()
	print("SEABREAK_COAST_CAPTURE_OK")
	quit(0)
