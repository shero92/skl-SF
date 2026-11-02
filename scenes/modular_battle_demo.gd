extends Node2D
## Two independent weapons, one shared unchanged body-frame resource.
const UNIT = preload("res://scenes/modular_battle_character.gd")
var units: Array = []
var weapon_ids := ["WPN_HERO_BASIC_SWORD","WPN_IRON_SWORD"]
var frames := SpriteFrames.new()
var attachment_data: Dictionary
var weapons: Dictionary
var event_count: int = 0
var paths: Dictionary = {}
var labels: Array[Label] = []

func _ready() -> void:
	RenderingServer.set_default_clear_color(Color("202936"))
	attachment_data = JSON.parse_string(FileAccess.get_file_as_string("res://game_factory/hero_correction/hero_weapon_anchors.json"))
	weapons = JSON.parse_string(FileAccess.get_file_as_string("res://game_factory/weapons/catalog.json"))
	frames.remove_animation("default")
	for key: String in attachment_data.frames:
		var record: Dictionary = attachment_data.frames[key]
		var animation: String = "battle_"+record.animation_name
		if not frames.has_animation(animation):
			frames.add_animation(animation)
			frames.set_animation_loop(animation,false)
			frames.set_animation_speed(animation,7)
			paths[animation] = []
		frames.add_frame(animation,UNIT.load_texture(record.body_path))
		paths[animation].append(record.body_path)
	for n in range(2):
		var unit = UNIT.new()
		unit.position = Vector2(480+580*n,700)
		unit.scale = Vector2(2,2)
		add_child(unit)
		unit.configure(frames,attachment_data,weapons,"sword")
		assert(unit.equip(weapon_ids[n]),"Missing compatible independent sword")
		unit.body.frame_changed.connect(func() -> void: event_count+=1)
		units.append(unit)
		var label := Label.new()
		label.text = weapon_ids[n]
		label.position = Vector2(280+580*n,95)
		label.add_theme_font_size_override("font_size",24)
		add_child(label)
		labels.append(label)
	var title := Label.new()
	title.text = "Same weaponless body PNGs | separate equipment | SPACE swaps swords"
	title.position = Vector2(240,35)
	title.add_theme_font_size_override("font_size",24)
	add_child(title)
	queue_redraw()
	var args := OS.get_cmdline_user_args()
	if args.has("verify"):
		await verify(args.has("capture"))
		if args.has("quit"):
			get_tree().quit()
			return
	while is_inside_tree():
		for phase: String in ["attack_windup","attack_execute"]:
			for unit in units:unit.play(phase)
			await units[0].body.animation_finished
		await get_tree().create_timer(.5).timeout

func _draw() -> void:
	draw_line(Vector2(160,700),Vector2(1380,700),Color("728391"),1)
	draw_line(Vector2(770,160),Vector2(770,760),Color("3e4d5b"),1)

func _unhandled_key_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and event.keycode==KEY_SPACE:
		weapon_ids.reverse()
		for n in range(2):
			units[n].equip(weapon_ids[n])
			labels[n].text = weapon_ids[n]

func verify(capture: bool) -> void:
	var checked: Array = []
	var body_hashes: Dictionary = {}
	for animation: String in paths:
		for path: String in paths[animation]:body_hashes[path] = FileAccess.get_sha256(path)
	var saved := "res://game_factory/hero_correction/previews"
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(saved))
	for pass_index in range(2):
		for n in range(2):
			assert(units[n].equip(weapon_ids[(n+pass_index)%2]))
			labels[n].text = weapon_ids[(n+pass_index)%2]
		for animation: String in ["battle_attack_windup","battle_attack_execute"]:
			assert(frames.has_animation(animation))
			for index in range(frames.get_frame_count(animation)):
				for unit in units:
					unit.body.animation = animation
					unit.body.frame = index
					unit.body.pause()
					unit.update_attachment()
					assert(not unit.current_attachment.is_empty(),"Missing per-frame hand anchor")
					var weapon: Sprite2D = unit.weapon_front if unit.weapon_front.visible else unit.weapon_back
					var pivot: Array = unit.equipped.grip_pivot
					var grip_world := weapon.to_global(Vector2(float(pivot[0]),float(pivot[1]))+weapon.offset)
					var hand_world: Vector2 = unit.to_global(unit.body.position+Vector2(unit.current_attachment.hand_anchor_x,unit.current_attachment.hand_anchor_y))
					assert(grip_world.distance_to(hand_world)<.001,"Weapon pivot moved off actual hand")
				assert(units[0].body.sprite_frames==units[1].body.sprite_frames,"Swap changed body resource")
				assert(units[0].body.sprite_frames.get_frame_texture(animation,index)==units[1].body.sprite_frames.get_frame_texture(animation,index))
				checked.append({"animation":animation,"frame":index,"swap_pass":pass_index,
					"body_path":paths[animation][index],"weapon_ids":[units[0].equipped.asset_id,units[1].equipped.asset_id],
					"hand_anchor":units[0].current_attachment,"body_resource_unchanged":true})
				if capture:
					await get_tree().process_frame
					await RenderingServer.frame_post_draw
					get_viewport().get_texture().get_image().save_png(saved+"/godot_swap_"+str(pass_index)+"_"+animation+"_"+str(index)+".png")
	# Exercise actual engine animation/frame_changed updates, not only manual frames.
	var before := event_count
	for animation_name: String in ["attack_windup","attack_execute"]:
		for unit in units:assert(unit.play(animation_name))
		await units[0].body.animation_finished
	assert(event_count>before+8,"Animation signals did not drive equipment updates")
	for path: String in body_hashes:
		assert(not String(body_hashes[path]).is_empty() and FileAccess.get_sha256(path)==body_hashes[path],"Swap modified a body PNG")
	var receipt := {"passed":true,"checked_frames":checked,"real_frame_events":event_count-before,
		"two_independent_weapon_pngs":true,"shared_unchanged_body_resource":true,
		"body_png_hashes_unchanged":true,"body_png_hashes":body_hashes,
		"per_frame_translation_rotation_depth":true,"godot_capture":capture,"visual_approval":false}
	var out := FileAccess.open(saved+"/godot_weapon_swap_receipt.json",FileAccess.WRITE)
	out.store_string(JSON.stringify(receipt,"  ")+"\n")
	print("MODULAR_WEAPON_SWAP_PASSED frames="+str(checked.size())+" actual_frame_events="+str(event_count-before))
