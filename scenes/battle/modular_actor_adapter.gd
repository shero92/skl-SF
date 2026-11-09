extends RefCounted
## Battle controller actor over an existing ModularBattleCharacter (left unmodified).
## Agent: claude (Claude Code); model: Sonnet 5.5.
##
## Implements the controller actor interface: set_view(view), set_frame(name, index), reset().
## set_frame maps pose "name" to the character animation "battle_<name>". A missing animation
## or frame is reported through last_error and never substituted or invented.

const NO_CHARACTER = "NO_CHARACTER"
const MISSING_ANIMATION = "MISSING_ANIMATION"
const MISSING_FRAME = "MISSING_FRAME"

var character: Node2D
var view: String = ""
var last_error: String = ""
var idle_animation: String = "idle_ready"


func _init(target: Node2D = null) -> void:
	character = target


func bind(target: Node2D) -> bool:
	if target == null or not is_instance_valid(target) or not target.has_method("equip"):
		return false
	character = target
	return true


func set_view(value) -> void:
	view = str(value)


func set_frame(pose_name, index: int) -> void:
	last_error = ""
	if not _usable():
		last_error = NO_CHARACTER
		return
	var frames: SpriteFrames = character.body.sprite_frames
	var key := "battle_" + str(pose_name)
	if frames == null or not frames.has_animation(key):
		last_error = MISSING_ANIMATION
		return
	if index < 0 or index >= frames.get_frame_count(key):
		last_error = MISSING_FRAME
		return
	character.body.animation = key
	character.body.frame = index
	character.update_attachment()


func reset() -> void:
	last_error = ""
	if not _usable():
		return
	var frames: SpriteFrames = character.body.sprite_frames
	var key := "battle_" + idle_animation
	if frames != null and frames.has_animation(key):
		character.body.animation = key
		character.body.frame = 0
	character.update_attachment()


func equip(weapon_id: String) -> bool:
	return _usable() and character.equip(weapon_id)


func equipped_weapon_id() -> String:
	if not _usable():
		return ""
	return String(character.equipped.get("asset_id", ""))


func _usable() -> bool:
	return character != null and is_instance_valid(character) and character.has_method("update_attachment")
