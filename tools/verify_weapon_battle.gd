extends SceneTree
## Headless verification of BattleResolver and its use from the animation controller's hit signal.
## Agent: claude (Claude Code); model: Sonnet 5.5.

const Resolver = preload("res://scenes/battle/battle_resolver.gd")
const Controller = preload("res://scenes/battle/battle_animation_controller.gd")

var _failures: int = 0


class Actor extends RefCounted:
	func set_view(_v) -> void: pass
	func set_frame(_n, _i) -> void: pass
	func reset() -> void: pass


func _check(condition: bool, message: String) -> void:
	if not condition:
		_failures += 1
		printerr("FAIL: " + message)


func _initialize() -> void:
	_test_resolve()
	_test_controller_hit()
	if _failures == 0:
		print("WEAPON_BATTLE_OK")
	quit(0 if _failures == 0 else 1)


func _test_resolve() -> void:
	var r = Resolver.new(null, 7)
	var ws = r.weapons
	var archer = ws.make_unit("CHAR006", ["WPN_SHORT_BOW"], "WPN_SHORT_BOW")
	var foe = ws.make_unit("CHAR004")
	_check(r.resolve(archer, foe, Vector2i(0, 0), Vector2i(1, 0)).reason == "out_of_range", "bow adjacent rejected")
	_check(r.resolve(archer, foe, Vector2i(0, 0), Vector2i(5, 0)).reason == "out_of_range", "bow too far rejected")
	var start_hp: int = r.current_hp(foe)
	var hits := 0
	var total := 0
	for i in 200:
		var target = ws.make_unit("CHAR004")
		var res: Dictionary = r.resolve(archer, target, Vector2i(0, 0), Vector2i(2, 1))
		_check(res.ok, "ranged attack resolves")
		if res.hit:
			hits += 1
			total += int(res.damage)
			_check(target.hp == start_hp - int(res.damage) or target.hp == 0, "damage applied")
		else:
			_check(target.hp == start_hp, "miss keeps hp")
	_check(hits > 150 and hits < 200, "hit rate near accuracy, got %d/200" % hits)
	_check(total > 0, "damage dealt")
	var weak = ws.make_unit("CHAR004")
	weak.hp = 1
	var kill: Dictionary = {}
	for i in 50:
		kill = r.resolve(ws.make_unit("CHAR001", ["WPN_IRON_SWORD"], "WPN_IRON_SWORD"), weak, Vector2i(0, 0), Vector2i(0, 1))
		if kill.hit:
			break
	_check(kill.defeated and weak.hp == 0, "defeat at 0 hp")
	var again: Dictionary = r.resolve(archer, weak, Vector2i(0, 0), Vector2i(2, 0))
	_check(again.reason == "defender_defeated", "cannot hit defeated")
	var assassin = ws.make_unit("CHAR001", ["WPN_ASSASSIN_DAGGER"], "WPN_ASSASSIN_DAGGER")
	var poisoned := false
	for i in 200:
		var t = ws.make_unit("CHAR004")
		t.hp = 999
		r.resolve(assassin, t, Vector2i(0, 0), Vector2i(0, 1))
		if t.get("statuses", []).has("poison"):
			poisoned = true
			break
	_check(poisoned, "poison applied sometimes")
	_check(r.art_asset_id(ws.make_unit("CHAR001", ["WPN_IRON_SWORD"], "WPN_IRON_SWORD")) == "WPN_IRON_SWORD", "art asset id")
	_check(r.art_asset_id(ws.make_unit("CHAR001")) == "", "no art for fists")
	var a = Resolver.new(null, 99)
	var b = Resolver.new(null, 99)
	var u1 = a.weapons.make_unit("CHAR001", ["WPN_IRON_SWORD"], "WPN_IRON_SWORD")
	var d1 = a.weapons.make_unit("CHAR004")
	var d2 = b.weapons.make_unit("CHAR004")
	_check(a.resolve(u1, d1, Vector2i.ZERO, Vector2i(0, 1)) == b.resolve(u1.duplicate(true), d2, Vector2i.ZERO, Vector2i(0, 1)), "same seed same result")


func _test_controller_hit() -> void:
	var r = Resolver.new(null, 3)
	var hero = r.weapons.make_unit("CHAR001", ["WPN_STEEL_SWORD"], "WPN_STEEL_SWORD")
	var foe = r.weapons.make_unit("CHAR004")
	var log: Array = []
	var controller = Controller.new()
	controller.attacks[&"slash"] = {"frames": [
		{"duration_ms": 100, "phase": "Attack", "hit": true},
		{"duration_ms": 100, "phase": "Recovery"},
	]}
	controller.hit.connect(func(_id, _a, _d): log.append(r.resolve(hero, foe, Vector2i(0, 0), Vector2i(0, 1))))
	var started: Dictionary = controller.play_attack(&"slash", Actor.new(), Actor.new())
	_check(started.ok, "attack started")
	controller.advance(1.0)
	_check(log.size() == 1, "hit fired once, got %d" % log.size())
	_check(log.size() == 1 and (not log[0].hit or foe.hp < 24), "damage landed on hit frame")
