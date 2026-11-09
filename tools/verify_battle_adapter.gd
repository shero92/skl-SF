extends SceneTree
## Headless verification of the ModularBattleCharacter adapter with the real controller.
## Agent: claude (Claude Code); model: Sonnet 5.5.
## Reads existing anchor/catalog data and weapon PNGs; body frames are in-memory placeholders.

const Adapter = preload("res://scenes/battle/modular_actor_adapter.gd")
const Unit = preload("res://scenes/modular_battle_character.gd")
const Controller = preload("res://scenes/battle/battle_animation_controller.gd")

var _failures: int = 0
var _anchors: Dictionary
var _weapons: Dictionary


func _initialize() -> void:
	_anchors = JSON.parse_string(FileAccess.get_file_as_string("res://game_factory/hero_correction/hero_weapon_anchors.json"))
	_weapons = JSON.parse_string(FileAccess.get_file_as_string("res://game_factory/weapons/catalog.json"))
	_test_interface()
	_test_sword_swap()
	_test_frames_and_errors()
	_test_controller()
	if _failures == 0:
		print("BATTLE_ADAPTER_OK")
	quit(0 if _failures == 0 else 1)


func _check(condition: bool, message: String) -> void:
	if not condition:
		_failures += 1
		printerr("FAIL: " + message)


func _frames() -> SpriteFrames:
	var frames := SpriteFrames.new()
	frames.remove_animation("default")
	var image := Image.create(8, 8, false, Image.FORMAT_RGBA8)
	image.fill(Color.WHITE)
	var texture := ImageTexture.create_from_image(image)
	var counts := {}
	for record in _anchors["frames"].values():
		counts[record["animation_name"]] = int(counts.get(record["animation_name"], 0)) + 1
	for animation in counts:
		frames.add_animation("battle_" + animation)
		for i in range(counts[animation]):
			frames.add_frame("battle_" + animation, texture)
	return frames


func _unit(weapon_id: String = ""):
	var unit = Unit.new()
	root.add_child(unit)
	unit.configure(_frames(), _anchors, _weapons, "sword")
	if weapon_id != "":
		unit.equip(weapon_id)
	return unit


func _test_interface() -> void:
	var adapter = Adapter.new(_unit())
	for method in ["set_view", "set_frame", "reset"]:
		_check(adapter.has_method(method), "actor interface: " + method)
	_check(not Adapter.new().bind(null), "bind rejects null")
	adapter.set_view("HERO_FRONT")
	_check(adapter.view == "HERO_FRONT", "set_view stores the view")
	var empty = Adapter.new()
	empty.set_frame("attack_windup", 0)
	_check(empty.last_error == Adapter.NO_CHARACTER, "no character reported")
	empty.reset()


func _test_sword_swap() -> void:
	var adapter = Adapter.new(_unit())
	_check(adapter.equip("WPN_HERO_BASIC_SWORD") and adapter.equipped_weapon_id() == "WPN_HERO_BASIC_SWORD", "equip basic sword")
	var basic_texture = adapter.character.weapon_front.texture
	_check(adapter.equip("WPN_IRON_SWORD") and adapter.equipped_weapon_id() == "WPN_IRON_SWORD", "swap to iron sword")
	_check(adapter.character.weapon_front.texture != basic_texture, "weapon texture changed")
	_check(not adapter.equip("WPN_MISSING") and adapter.equipped_weapon_id() == "WPN_IRON_SWORD", "unknown sword rejected, previous kept")
	var other = Adapter.new(_unit("WPN_HERO_BASIC_SWORD"))
	_check(other.equipped_weapon_id() == "WPN_HERO_BASIC_SWORD" and adapter.equipped_weapon_id() == "WPN_IRON_SWORD", "weapons are independent per unit")


func _test_frames_and_errors() -> void:
	var adapter = Adapter.new(_unit("WPN_HERO_BASIC_SWORD"))
	adapter.set_frame("attack_execute", 2)
	_check(adapter.last_error == "", "valid frame accepted")
	_check(adapter.character.body.animation == &"battle_attack_execute" and adapter.character.body.frame == 2, "body shows the requested frame")
	_check(adapter.character.weapon_front.visible or adapter.character.weapon_back.visible, "weapon follows the anchor record")
	adapter.set_frame("no_such_pose", 0)
	_check(adapter.last_error == Adapter.MISSING_ANIMATION, "missing animation reported")
	_check(adapter.character.body.animation == &"battle_attack_execute", "missing animation does not change the body")
	adapter.set_frame("attack_execute", 99)
	_check(adapter.last_error == Adapter.MISSING_FRAME, "missing frame reported")
	adapter.reset()
	_check(adapter.character.body.animation == &"battle_idle_ready" and adapter.character.body.frame == 0, "reset returns to idle")


func _test_controller() -> void:
	var attacker = Adapter.new(_unit("WPN_IRON_SWORD"))
	var defender = Adapter.new(_unit("WPN_HERO_BASIC_SWORD"))
	var controller = Controller.new()
	controller.attacks = {&"slash": {"frames": [
		{"duration_ms": 100, "attacker": {"view": "HERO_REAR_3Q", "name": "attack_windup", "index": 0}},
		{"duration_ms": 100, "hit": true, "attacker": {"view": "HERO_REAR_3Q", "name": "attack_execute", "index": 1}},
		{"duration_ms": 100, "phase": "Recovery", "attacker": {"view": "HERO_REAR_3Q", "name": "idle_ready", "index": 0}},
	]}}
	var hits := [0]
	controller.hit.connect(func(_id, _a, _d): hits[0] += 1)
	_check(controller.play_attack(&"slash", attacker, defender)["ok"], "controller accepts adapters")
	_check(attacker.character.body.animation == &"battle_attack_windup", "first frame applied through controller")
	controller.advance(0.12)
	_check(attacker.character.body.animation == &"battle_attack_execute" and hits[0] == 1, "hit frame through controller")
	controller.advance(1.0)
	_check(controller.state == Controller.State.IDLE, "attack finished")
	_check(attacker.character.body.animation == &"battle_idle_ready", "actors reset after the attack")
