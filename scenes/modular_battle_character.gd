class_name ModularBattleCharacter
extends Node2D
## Body PNGs never change when equipment changes. Coordinates are native pixels.
signal equipment_changed(weapon_id: String)
var body := AnimatedSprite2D.new()
var weapon_back := Sprite2D.new()
var weapon_front := Sprite2D.new()
var hand_front := Sprite2D.new()
var effects := Node2D.new()
var anchors: Dictionary = {}
var catalog: Dictionary = {}
var equipped: Dictionary = {}
var profile: String = "sword"
var body_anchor := Vector2(128,240)
var current_attachment: Dictionary = {}

func _init() -> void:
	name = "BattleCharacter"
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	weapon_back.name = "WeaponBack"
	body.name = "BodySprite"
	weapon_front.name = "WeaponFront"
	hand_front.name = "HandOcclusion"
	effects.name = "Effects"
	for sprite: Sprite2D in [weapon_back,weapon_front,hand_front]:
		sprite.centered = false
	add_child(weapon_back)
	add_child(body)
	add_child(weapon_front)
	add_child(hand_front)
	add_child(effects)
	body.centered = false
	body.frame_changed.connect(update_attachment)
	body.animation_changed.connect(update_attachment)

func configure(frames: SpriteFrames, attachment_data: Dictionary, weapons: Dictionary, equipment_profile: String = "sword", anchor: Vector2 = Vector2(128,240)) -> void:
	profile = equipment_profile
	body_anchor = anchor
	body.position = -body_anchor
	body.sprite_frames = frames
	anchors = attachment_data
	catalog = weapons
	update_attachment()

func equip(weapon_id: String) -> bool:
	var candidate: Dictionary = catalog.get("weapons",{}).get(weapon_id,{})
	if candidate.is_empty() or profile not in candidate.get("compatible_profiles",[]):
		return false
	var texture := load_texture(candidate.get("texture_path",""))
	if texture == null:
		return false
	equipped = candidate.duplicate(true)
	weapon_back.texture = texture
	weapon_front.texture = texture
	update_attachment()
	equipment_changed.emit(weapon_id)
	return true

static func load_texture(path: String) -> Texture2D:
	if path.is_empty():return null
	if ResourceLoader.exists(path):
		var resource := load(path) as Texture2D
		if resource != null:return resource
	var image := Image.load_from_file(ProjectSettings.globalize_path(path))
	return ImageTexture.create_from_image(image) if image != null else null

func update_attachment() -> void:
	weapon_back.visible = false
	weapon_front.visible = false
	hand_front.visible = false
	current_attachment = {}
	if body.sprite_frames == null or equipped.is_empty():return
	var animation_name := String(body.animation).trim_prefix("battle_")
	var record: Dictionary = anchors.get("frames",{}).get(animation_name+":"+str(body.frame),{})
	if record.is_empty():return # No fabricated fixed anchor fallback.
	current_attachment = record
	var weapon := weapon_back if record.get("weapon_render_order","front")=="behind" else weapon_front
	var pivot: Array = equipped.get("grip_pivot",[0,0])
	weapon.offset = -Vector2(float(pivot[0]),float(pivot[1]))
	weapon.position = body.position+Vector2(float(record.hand_anchor_x),float(record.hand_anchor_y))
	weapon.rotation_degrees = float(record.hand_rotation_degrees)
	weapon.scale = Vector2.ONE*float(record.get("weapon_scale",1.0))*float(equipped.get("display_scale",1.0))
	weapon.visible = true
	var rect: Array = record.get("hand_occlusion_rect",[])
	if rect.size()==4 and weapon==weapon_front:
		hand_front.texture = body.sprite_frames.get_frame_texture(body.animation,body.frame)
		hand_front.region_enabled = true
		hand_front.region_rect = Rect2(float(rect[0]),float(rect[1]),float(rect[2]),float(rect[3]))
		hand_front.position = body.position+Vector2(float(rect[0]),float(rect[1]))
		hand_front.visible = true

func play(animation_name: String) -> bool:
	var key := "battle_"+animation_name
	if body.sprite_frames == null or not body.sprite_frames.has_animation(key):return false
	body.play(key)
	update_attachment()
	return true
