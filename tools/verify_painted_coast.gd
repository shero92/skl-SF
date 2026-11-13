extends SceneTree
const Travel := preload("res://scenes/world/world_travel.gd")
var failures: int = 0
var steps: int = 0
var boundaries: int = 0
func check(value: bool, message: String) -> void:
	if not value:
		failures += 1
		printerr("FAIL: "+message)
func _initialize() -> void:
	call_deferred("run")
func walk_to(hero: HeroPlayer, destination: Vector2) -> void:
	var nav: NavigationGrid = hero.navigation
	var astar := AStarGrid2D.new()
	astar.region = Rect2i(Vector2i.ZERO,nav.grid_size)
	astar.diagonal_mode = AStarGrid2D.DIAGONAL_MODE_NEVER
	astar.update()
	for y in nav.grid_size.y:
		for x in nav.grid_size.x:astar.set_point_solid(Vector2i(x,y),not nav.is_cell_open(Vector2i(x,y)))
	var route: Array[Vector2i] = astar.get_id_path(nav.world_to_cell(hero.position),nav.world_to_cell(destination))
	check(not route.is_empty(),"Route exists to "+str(destination))
	for cell: Vector2i in route:
		var goal := nav.cell_center(cell)
		var attempts: int = 0
		while hero.position.distance_to(goal)>3 and attempts<100:
			# Run the real controller inside physics with the matching tick, including after a zone switch.
			await physics_frame
			var delta := goal-hero.position
			var action: String = "ui_right" if delta.x>0 else "ui_left"
			if absf(delta.y)>absf(delta.x):action = "ui_down" if delta.y>0 else "ui_up"
			Input.action_press(action)
			hero._physics_process(1.0/60.0)
			Input.action_release(action)
			attempts += 1
			steps += 1
			check(nav.footprint_open(hero.position),"Hero feet remain on safe ground")
		check(attempts<100,"Hero reached a path cell")
	check(hero.position.distance_to(destination)<32,"Hero reached destination cell")
func run() -> void:
	var world: Node2D = load("res://scenes/world/painted_coast.tscn").instantiate()
	world.travel_enabled = false
	root.add_child(world)
	current_scene = world
	await physics_frame
	world.player.set_physics_process(false)
	var hero_id: int = world.player.get_instance_id()
	check(world.definition.zones.size()==6,"Six painted regions exist")
	check(world.camera.zoom.is_equal_approx(Vector2.ONE*0.84375),"Camera uses same room zoom")
	for id: String in world.definition.zones:
		world.enter_zone(id)
		check(not world.player.navigation.is_cell_open(Vector2i.ZERO),"Unknown corner is blocked in "+id)
		await walk_to(world.player,Travel.point(world.definition.zones[id].landmark))
		for portal: Dictionary in world.definition.zones[id].portals:
			world.enter_zone(id)
			await walk_to(world.player,Travel.rect(portal.rect).get_center())
			var actual: Dictionary = world.available_portal()
			check(str(actual.get("id",""))==str(portal.id),"Walked to portal "+id+"/"+str(portal.id))
			if str(portal.target)=="room":continue
			world.travel_enabled = true
			world._physics_process(1.0/60.0)
			world.travel_enabled = false
			await process_frame
			await process_frame
			boundaries += 1
			check(world.current_zone==str(portal.target),"Actual zone transition reached "+str(portal.target))
			check(world.player.get_instance_id()==hero_id,"Same actor survives zone change")
			check(world.player.navigation.footprint_open(world.player.position),"Zone arrival is safe")
			check(world.available_portal().is_empty(),"Zone arrival does not trigger an immediate return")
	check(boundaries>=12 and steps>1500,"Substantial real movement and every boundary tested")
	world.queue_free()
	await process_frame
	var room: Node2D = load("res://scenes/main.tscn").instantiate()
	room.save_path = "res://.qa-tmp/painted_coast_missing_save.json"
	root.add_child(room)
	current_scene = room
	await process_frame
	var gate: Node = room.get_node("OutdoorExit")
	gate.travel_enabled = false
	room.player.position = Travel.rect(gate.settings().rect).get_center()
	check(gate.exit_available(),"Current room stair trigger is reachable")
	gate.travel_enabled = true
	gate._physics_process(1.0/60.0)
	await process_frame
	await process_frame
	check(current_scene.scene_file_path=="res://scenes/world/painted_coast.tscn","Actual default room exit opens painted exterior")
	if current_scene.scene_file_path=="res://scenes/world/painted_coast.tscn":
		world = current_scene
		world.travel_enabled = false
		world.player.set_physics_process(false)
		check(world.current_zone=="home_descent","Room exit arrives below same stair")
		await walk_to(world.player,Vector2(768,64))
		world.travel_enabled = true
		world._physics_process(1.0/60.0)
		await process_frame
		await process_frame
		await process_frame
		check(current_scene.scene_file_path=="res://scenes/main.tscn","Climbing stairs returns to real room")
		if current_scene.scene_file_path=="res://scenes/main.tscn":
			room = current_scene
			check(room.player.position.distance_to(Vector2(768,832))<1,"Room return uses measured safe position")
			check(room.player.navigation.footprint_open(room.player.position),"Room return ground is safe")
			check(not room.get_node("OutdoorExit").exit_available(),"No room return loop")
	check(not Travel.returning_to_room,"Room return marker consumed once")
	if failures==0:print("PAINTED_COAST_WALK_AND_RETURN_OK steps=",steps," boundaries=",boundaries)
	quit(0 if failures==0 else 1)
