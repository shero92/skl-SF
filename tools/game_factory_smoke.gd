extends SceneTree

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	var scene := load("res://scenes/game_factory_demo.tscn") as PackedScene
	var demo := scene.instantiate() as Node2D
	root.add_child(demo)
	for frame in range(5):
		await process_frame
	var room := demo.get_node("Room")
	var names := ["Level0_Background","Level1_Ground","Level2_Walls","Level3_Decorations","Level4_Shadows"]
	for level: String in names:
		assert(room.find_child(level,true,false)!=null,"Missing pass "+level)
	var shadows := room.find_child("Level4_Shadows",true,false) as Node2D
	var world := room.get_node("WorldDepthSort") as Node2D
	assert(shadows.z_index<world.z_index,"Contact shadows must draw below structures")
	assert(not room.find_children("SolidFootprint","StaticBody2D",true,false).is_empty(),"Missing collisions")
	var mounted_count: int = 0
	for node: Node in room.find_children("*","Node2D",true,false):
		if node.has_meta("mount_on"):
			assert(String(node.get_parent().name)==String(node.get_meta("mount_on")),"Attachment not parented to host")
			mounted_count += 1
	assert(mounted_count>=4,"Missing mounted table/wall decorations")
	for label: Node in room.find_children("*","Label",true,false):
		assert(false,"Placeholder label in reconstructed room: "+str(label))
	var manifest: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://game_factory/character_manifest.json"))
	assert(manifest.characters.size()==6,"Exactly six characters")
	var present_frames: int = 0
	var complete_animations: int = 0
	for record: Dictionary in manifest.characters:
		for key: String in record.animations:
			var anim: Dictionary = record.animations[key]
			for path: String in anim.frames:
				assert(FileAccess.file_exists(path),"Registry contains nonexistent frame")
				present_frames += 1
			if anim.complete:
				complete_animations += 1
	var movement_checks: Dictionary = {"tested":false}
	if OS.get_cmdline_user_args().has("require_hero"):
		var hero: Dictionary = manifest.characters[0]
		assert(demo._has_complete_map(hero),"Hero needs all 40 actual map frames")
		var script := load("res://scenes/game_factory_actor.gd") as Script
		var unit: CharacterBody2D = script.new()
		unit.definition = hero
		unit.position = Vector2(740,760)
		demo._configure_floor(unit)
		world.add_child(unit)
		await physics_frame
		var directions := {KEY_D:"right",KEY_A:"left",KEY_W:"up",KEY_S:"down"}
		for key: int in directions:
			unit.position = Vector2(740,760)
			var start := unit.position
			var event := InputEventKey.new()
			event.keycode = key
			event.pressed = true
			Input.parse_input_event(event)
			for frame in range(12): await physics_frame
			assert(unit.position.distance_to(start)>10,"No keyboard movement")
			assert(unit.facing==directions[key],"Incorrect direction")
			assert(unit.art.animation=="map_"+directions[key]+"_walk","Walk animation not selected")
			event.pressed = false
			Input.parse_input_event(event)
			for frame in range(3): await physics_frame
			assert(unit.art.animation=="map_"+directions[key]+"_idle","Idle animation not selected")
		unit.position = Vector2(740,760)
		var right := InputEventKey.new()
		right.keycode = KEY_D
		right.pressed = true
		Input.parse_input_event(right)
		var seen_frames: Dictionary = {}
		for frame in range(140):
			await physics_frame
			seen_frames[unit.art.frame] = true
		right.pressed = false
		Input.parse_input_event(right)
		assert(unit.position.x>780 and unit.position.x<1106,"Solid structure collision failed")
		assert(seen_frames.size()>1,"Animation never advanced beyond one static frame")
		movement_checks={"tested":true,"directions":4,"idle_walk_selection":true,"solid_collision":true,"animation_frames_observed":seen_frames.size()}
	var receipt := {"passed":true,"room_factory":true,"logical_levels":4,"separate_background":true,
		"mounted_objects":mounted_count,"registered_existing_frames":present_frames,
		"frame_count_complete_sequences":complete_animations,"hero_movement":movement_checks,"visual_approval":false,
		"full_character_library_complete":false}
	var file := FileAccess.open("res://game_factory/smoke_receipt.json",FileAccess.WRITE)
	file.store_string(JSON.stringify(receipt,"  "))
	print("GAME_FACTORY_SMOKE "+JSON.stringify(receipt))
	quit()
