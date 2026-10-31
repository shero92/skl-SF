extends Node2D
## Actual RoomFactory reconstruction + isolated character/viewer/battle demonstrations.
const ACTOR = preload("res://scenes/game_factory_actor.gd")
const MODULAR = preload("res://scenes/modular_battle_character.gd")
signal animation_event(event_name: String, action_context: Dictionary)
var room: Node2D
var characters: Array = []
var selected: int = 0
var actor: CharacterBody2D
var battle: AnimatedSprite2D
var battle_root: Node2D
var battle_equipment: Node2D
var equipped_weapon_id: String = "WPN_HERO_BASIC_SWORD"
var context: Dictionary = {}
@export_enum("room","interactive","viewer","battle") var mode: String = "room"
var debug_label: Label
var debug_visible: bool = false
var direction: String = "down"
var state: String = "idle"
var viewer: AnimatedSprite2D
var event_log: Array = []
var room_data: Dictionary = {}

func _ready() -> void:
	var args := OS.get_cmdline_user_args()
	for value: String in args:
		if value.begins_with("mode="):
			mode = value.trim_prefix("mode=")
	var factory := RoomFactory.new()
	factory.catalog.load_index("res://game_factory/environment/catalog.json")
	factory.assets = AssetFactory.new(factory.catalog)
	room_data = JSON.parse_string(FileAccess.get_file_as_string("res://game_factory/environment/room.json"))
	room = factory.build_room("res://game_factory/environment/room.json",self)
	var camera := Camera2D.new()
	camera.position = Vector2(768,512)
	camera.zoom = Vector2(.8,.8)
	add_child(camera)
	var manifest: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://game_factory/character_manifest.json"))
	characters = manifest.get("characters",[])
	debug_label = Label.new()
	debug_label.position = Vector2(12,12)
	debug_label.z_index = 200
	debug_label.visible = false
	add_child(debug_label)
	if mode == "interactive":
		_spawn_actor()
	elif mode == "viewer":
		room.visible = false
		_create_viewer()
	elif mode == "battle":
		room.visible = false
	if mode == "battle":
		present_battle("attack_execute")
	var stage: String = "lighting"
	for arg: String in args:
		if arg.begins_with("stage="):
			stage = arg.trim_prefix("stage=")
	var stage_nodes := {"ground":["Level2_Walls","Level3_Decorations","Level4_Shadows"],
		"structures":["Level3_Decorations","Level4_Shadows"],"decorations":["Level4_Shadows"]}
	for node_name: String in stage_nodes.get(stage,[]):
		var stage_node := room.find_child(node_name,true,false) as CanvasItem
		if stage_node != null:
			stage_node.visible = false
	if args.has("capture"):
		for n in range(10):
			await get_tree().process_frame
		await RenderingServer.frame_post_draw
		var image := get_viewport().get_texture().get_image()
		var path := "res://game_factory/previews/"+mode+("_"+stage if args.has("stage="+stage) else "")+".png"
		DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://game_factory/previews"))
		image.save_png(path)
		print("GAME_FACTORY_CAPTURE "+path)
		if args.has("quit"):
			get_tree().quit()

func _spawn_actor() -> void:
	actor = ACTOR.new()
	actor.definition = characters[selected]
	actor.position = Vector2(740,760)
	_configure_floor(actor)
	var world := room.get_node("WorldDepthSort")
	world.add_child(actor)
	actor.battle_requested.connect(func(_unit: CharacterBody2D) -> void: await present_battle("attack_execute"))
	if not _has_complete_map(characters[selected]):
		push_warning("Interactive demo incomplete: selected character map frames are missing")
	for record: Dictionary in characters:
		if String(record.get("slug",""))=="neru" and _has_complete_map(record):
			var companion: CharacterBody2D = ACTOR.new()
			companion.definition = record
			companion.position = actor.position+Vector2(80,0)
			companion.follow_target = actor
			_configure_floor(companion)
			world.add_child(companion)

func _configure_floor(unit: CharacterBody2D) -> void:
	var navigation: Dictionary = room_data.get("navigation",{})
	var origin: Array = navigation.get("origin",[0,0])
	unit.grid_origin = room.global_position+Vector2(float(origin[0]),float(origin[1]))
	unit.tile_size = float(navigation.get("cell_size",64))
	for region: Dictionary in navigation.get("regions",[]):
		var rect: Array = region.get("rect",[0,0,0,0])
		for y in range(int(rect[1]),int(rect[1])+int(rect[3])):
			for x in range(int(rect[0]),int(rect[0])+int(rect[2])):
				unit.walkable_cells[Vector2i(x,y)] = "walk" in region.get("allow",[])

func _has_complete_map(record: Dictionary) -> bool:
	var animations: Dictionary = record.get("animations",{})
	for d in ["down","left","right","up"]:
		for s in ["idle","walk"]:
			if not bool(animations.get("map_"+d+"_"+s,{}).get("complete",false)):
				return false
	return true

func _create_viewer() -> void:
	if viewer != null:
		viewer.queue_free()
	viewer = AnimatedSprite2D.new()
	viewer.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	viewer.sprite_frames = ACTOR.make_frames(characters[selected],"map_")
	viewer.position = Vector2(768,512)
	viewer.scale = Vector2(4,4)
	add_child(viewer)
	_play_viewer()

func _play_viewer() -> void:
	var key := "map_"+direction+"_"+state
	viewer.visible = viewer.sprite_frames.has_animation(key)
	if viewer.visible:
		viewer.play(key)
	else:
		print("INCOMPLETE_ANIMATION "+key)

func present_battle(action: String) -> void:
	if battle_root != null:
		return
	var character: Dictionary = characters[selected]
	var frames := ACTOR.make_frames(character,"battle_")
	var key := "battle_"+action
	if not frames.has_animation(key):
		push_warning("Battle demo incomplete: "+key)
		return
	context = {"position":actor.position if actor != null else Vector2.ZERO,
		"facing":actor.facing if actor != null else "down", "hp":actor.hp if actor != null else 100,
		"movement_enabled":actor.movement_enabled if actor != null else false,
		"character_id":character.character_id,"action":action}
	var previous_process: ProcessMode = room.process_mode
	var previous_visibility: bool = room.visible
	if actor != null:
		actor.movement_enabled = false
	room.process_mode = Node.PROCESS_MODE_DISABLED
	room.visible = false
	battle_root = Node2D.new()
	battle_root.z_index = 100
	add_child(battle_root)
	var shadow := ShadowFactory.create_shadow({"type":"character","opacity":0.3,"offset_y":-5},Vector2(85,30))
	shadow.position = Vector2(768,680)
	shadow.z_index = -1
	battle_root.add_child(shadow)
	var anchor: Array = character.get("battle_anchor",[128,240])
	var attachment_path: String = character.get("weapon_attachment_metadata","") if character.get("weapon_attachment_metadata") != null else ""
	if not attachment_path.is_empty() and FileAccess.file_exists(attachment_path):
		var attachments: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(attachment_path))
		var weapon_catalog: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://game_factory/weapons/catalog.json"))
		var unit = MODULAR.new()
		unit.position = Vector2(768,680)
		battle_root.add_child(unit)
		unit.configure(frames,attachments,weapon_catalog,character.get("equipment_profile","natural"),Vector2(float(anchor[0]),float(anchor[1])))
		unit.equip(equipped_weapon_id)
		battle_equipment = unit
		battle = unit.body
	else:
		battle = AnimatedSprite2D.new()
		battle.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		battle.sprite_frames = frames
		battle.centered = false
		battle.position = Vector2(768-float(anchor[0]),680-float(anchor[1]))
		battle_root.add_child(battle)
	if action == "attack_execute" and frames.has_animation("battle_attack_windup"):
		battle.play("battle_attack_windup")
		await battle.animation_finished
	var emitted: Dictionary = {}
	var notify_frame := func() -> void:
		if battle.animation != key:
			return
		var event_name: String = ""
		if action=="attack_execute" and battle.frame==3:
			event_name = "projectile_release" if character.get("character_role","")=="archer" else "attack_impact"
		elif action=="cast_magic" and battle.frame==3:
			event_name = "spell_release"
		elif action=="hurt" and battle.frame==0:
			event_name = "damage_reaction"
		if event_name!="" and not emitted.has(event_name):
			emitted[event_name] = true
			event_log.append({"event":event_name,"frame":battle.frame,"action":action})
			animation_event.emit(event_name,context.duplicate(true))
	battle.frame_changed.connect(notify_frame)
	battle.play(key)
	notify_frame.call()
	if frames.get_animation_loop(key):
		await battle.animation_looped
	else:
		await battle.animation_finished
	event_log.append({"event":"animation_complete","action":action})
	animation_event.emit("animation_complete",context.duplicate(true))
	battle_root.queue_free()
	battle_root = null
	battle_equipment = null
	room.visible = previous_visibility
	room.process_mode = previous_process
	if actor != null:
		actor.position = context.position
		actor.facing = context.facing
		# HP belongs to combat logic; presentation never overwrites damage updates.
		actor.movement_enabled = context.movement_enabled

func _unhandled_key_input(event: InputEvent) -> void:
	if not event is InputEventKey or not event.pressed or event.echo:
		return
	if event.keycode == KEY_B:
		equipped_weapon_id = "WPN_IRON_SWORD" if equipped_weapon_id=="WPN_HERO_BASIC_SWORD" else "WPN_HERO_BASIC_SWORD"
		if battle_equipment != null:battle_equipment.equip(equipped_weapon_id)
	if event.keycode == KEY_F1:
		debug_visible = not debug_visible
		debug_label.visible = debug_visible
		queue_redraw()
	if event.keycode in [KEY_0,KEY_1,KEY_2,KEY_3,KEY_4]:
		var names := ["Level0_Background","Level1_Ground","Level2_Walls","Level3_Decorations","Level4_Shadows"]
		var found := room.find_child(names[event.keycode-KEY_0],true,false) as CanvasItem
		if found != null:
			found.visible = not found.visible
	if mode in ["viewer","battle"]:
		if event.keycode == KEY_TAB and battle_root == null:
			selected = (selected+1)%characters.size()
			if mode=="viewer": _create_viewer()
	if mode=="viewer":
		if event.keycode == KEY_LEFT:
			direction = "left"
		elif event.keycode == KEY_RIGHT:
			direction = "right"
		elif event.keycode == KEY_UP:
			direction = "up"
		elif event.keycode == KEY_DOWN:
			direction = "down"
		elif event.keycode == KEY_I:
			state = "idle"
		elif event.keycode == KEY_W:
			state = "walk"
		elif event.keycode == KEY_P:
			if viewer.is_playing(): viewer.pause()
			else: viewer.play()
		if event.keycode != KEY_P:
			_play_viewer()
	var actions := {KEY_A:"attack_execute",KEY_D:"defend",KEY_M:"cast_magic",KEY_H:"hurt",KEY_V:"victory",
		KEY_R:"idle_ready",KEY_S:"step",KEY_W:"attack_windup",KEY_I:"use_item"}
	if mode == "battle" and actions.has(event.keycode):
		await present_battle(actions[event.keycode])

func _process(_delta: float) -> void:
	if debug_visible:
		debug_label.text = "%s | %s | %s %s | TAB character, arrows facing, I/W state, P pause\n0-4 layers | F1 grid | battle A/D/M/H/V | SPACE attack" % [mode,characters[selected].display_name,direction,state]

func _draw() -> void:
	if not debug_visible:
		return
	for x in range(256,1153,64): draw_line(Vector2(x,288),Vector2(x,928),Color(1,1,1,.35))
	for y in range(288,929,64): draw_line(Vector2(256,y),Vector2(1152,y),Color(1,1,1,.35))
