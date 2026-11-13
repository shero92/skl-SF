extends SceneTree
const Travel := preload("res://scenes/world/world_travel.gd")
var failures: int = 0
var walked_steps: int = 0
func check(value: bool, message: String) -> void:
	if not value:
		failures += 1
		printerr("FAIL: "+message)
func _initialize() -> void:
	call_deferred("run")
func drive(hero: HeroPlayer, destination: Vector2) -> void:
	var attempts: int = 0
	while hero.position.distance_to(destination)>4.0 and attempts<100:
		var delta := destination-hero.position
		var action: String = "ui_right" if delta.x>0 else "ui_left"
		if absf(delta.y)>absf(delta.x):
			action = "ui_down" if delta.y>0 else "ui_up"
		Input.action_press(action)
		hero._physics_process(1.0/60.0)
		Input.action_release(action)
		attempts += 1
		walked_steps += 1
		if not hero.navigation.footprint_open(hero.position):
			check(false,"Hero feet left walkable cells during actual movement")
			return
	check(attempts<100,"Hero reached next route cell")
func run() -> void:
	var world: Node2D = load("res://scenes/world/seabreak_coast.tscn").instantiate()
	world.travel_enabled = false
	root.add_child(world)
	current_scene = world
	await physics_frame
	world.player.set_physics_process(false)
	var nav: NavigationGrid = world.player.navigation
	check(nav!=null and nav.footprint_open(world.player.position),"Outdoor arrival is safe")
	check(not nav.is_cell_open(Vector2i.ZERO),"Water is blocked")
	var pathfinder := AStarGrid2D.new()
	pathfinder.region = Rect2i(Vector2i.ZERO,nav.grid_size)
	pathfinder.diagonal_mode = AStarGrid2D.DIAGONAL_MODE_NEVER
	pathfinder.update()
	for y in nav.grid_size.y:
		for x in nav.grid_size.x:
			pathfinder.set_point_solid(Vector2i(x,y),not nav.is_cell_open(Vector2i(x,y)))
	for landmark: Dictionary in world.definition.landmarks:
		var target := Vector2i(int(landmark.cell[0]),int(landmark.cell[1]))
		var route: Array[Vector2i] = pathfinder.get_id_path(nav.world_to_cell(world.player.position),target)
		check(not route.is_empty(),"Route reaches "+str(landmark.name))
		for cell: Vector2i in route:
			drive(world.player,nav.cell_center(cell))
		check(world.player.position.distance_to(nav.cell_center(target))<5,"Actual HeroPlayer walked to "+str(landmark.name))
	check(walked_steps>3000,"Long-distance exploration uses actual hero movement")
	world.queue_free()
	await process_frame
	var room_scene: Node2D = load("res://scenes/main.tscn").instantiate()
	room_scene.save_path = "res://.qa-tmp/seabreak_test_missing_save.json"
	root.add_child(room_scene)
	current_scene = room_scene
	await process_frame
	var gate: Node = room_scene.get_node("OutdoorExit")
	gate.travel_enabled = false
	room_scene.set_photo_mode(false)
	check(room_scene.player.navigation.footprint_open(Vector2(768,784)),"Factory room return point is safe too")
	check(room_scene.player.navigation.footprint_open(Travel.rect(gate.settings().rect).get_center()),"Factory room stair trigger is walkable")
	Travel.returning_to_room = true
	gate.restore_return()
	check(room_scene.player.position.distance_to(Vector2(768,784))<1 and not Travel.returning_to_room,"Factory return marker restores and consumes correctly")
	room_scene.set_photo_mode(true)
	room_scene.player.position = Vector2(768,896)
	check(gate.exit_available(),"Room stair exit can be reached")
	room_scene.player.movement_enabled = false
	check(not gate.exit_available(),"Paused hero cannot trigger travel")
	room_scene.player.movement_enabled = true
	gate.travel_enabled = true
	gate._physics_process(1.0/60.0)
	await process_frame
	await process_frame
	check(current_scene.scene_file_path=="res://scenes/world/seabreak_coast.tscn","Actual room exit changes to world scene")
	if current_scene.scene_file_path=="res://scenes/world/seabreak_coast.tscn":
		world = current_scene
		world.player.position = Travel.rect(world.definition.world_return_rect).get_center()
		world._physics_process(1.0/60.0)
		await process_frame
		await process_frame
		await process_frame
		check(current_scene.scene_file_path=="res://scenes/main.tscn","World gate returns to room")
		if current_scene.scene_file_path=="res://scenes/main.tscn":
			room_scene = current_scene
			check(room_scene.player.position.distance_to(Vector2(768,832))<1,"Safe return spawn restored")
			check(room_scene.player.navigation.footprint_open(room_scene.player.position),"Return spawn is walkable")
			check(not room_scene.get_node("OutdoorExit").exit_available(),"Return does not immediately retrigger exit")
	check(not Travel.returning_to_room,"Return marker consumed once")
	if failures==0:
		print("SEABREAK_COAST_WALK_AND_ROUNDTRIP_OK steps=",walked_steps)
	quit(0 if failures==0 else 1)
