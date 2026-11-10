extends SceneTree
## Headless verification of BattleDirector (TurnManager + animation controller glue).
## Agent: claude (Claude Code); model: Sonnet 5.5.

const Manager = preload("res://scenes/battle/turn_manager.gd")
const Resolver = preload("res://scenes/battle/battle_resolver.gd")
const Director = preload("res://scenes/battle/battle_director.gd")

var _failures: int = 0


class Actor extends RefCounted:
	var poses: Array = []

	func set_view(_v) -> void: pass
	func set_frame(pose, _i) -> void: poses.append(pose)
	func reset() -> void: pass


func _check(condition: bool, message: String) -> void:
	if not condition:
		_failures += 1
		printerr("FAIL: " + message)


func _initialize() -> void:
	_test_flow()
	_test_missing_actor()
	_test_profiles()
	if _failures == 0:
		print("BATTLE_DIRECTOR_OK")
	quit(0 if _failures == 0 else 1)


func _setup(seed_value: int):
	var m = Manager.new(Resolver.new(null, seed_value))
	var ws = m.resolver.weapons
	m.add("hero", "player", ws.make_unit("CHAR001", ["WPN_IRON_SWORD"], "WPN_IRON_SWORD"), Vector2i(2, 2))
	m.add("brute", "enemy", ws.make_unit("CHAR004", ["WPN_BATTLE_AXE"], "WPN_BATTLE_AXE"), Vector2i(3, 2))
	m.add("archer", "player", ws.make_unit("CHAR006", ["WPN_SHORT_BOW"], "WPN_SHORT_BOW"), Vector2i(0, 2))
	m.start_round()
	return m


func _drain(director, limit: int = 400) -> int:
	var steps := 0
	while director.is_busy() and steps < limit:
		director.advance(0.05)
		steps += 1
	return steps


func _hero_turn(m) -> void:
	var guard := 0
	while m.current().id != "hero" and guard < 10:
		m.end_turn()
		guard += 1


func _test_flow() -> void:
	var m = _setup(4)
	var d = Director.new(m)
	var actors := {}
	for id in ["hero", "brute", "archer"]:
		actors[id] = Actor.new()
		d.register_actor(id, actors[id])
	_hero_turn(m)
	var log: Array = []
	d.playback_started.connect(func(e): log.append("start:%s>%s" % [e.attacker_id, e.defender_id]))
	d.hit_landed.connect(func(e): log.append("hit:%s" % e.attacker_id))
	d.playback_finished.connect(func(e): log.append("end:%s" % e.attacker_id))
	var emptied: Array = []
	d.queue_empty.connect(func(): emptied.append(true))
	var result: Dictionary = d.attack("hero", "brute")
	_check(result.ok, "attack resolves immediately")
	var hp_after_resolve: int = m.resolver.current_hp(m.find("brute").unit)
	_check(d.is_busy() and d.queue.size() >= 1, "animation is queued after the data result")
	_drain(d)
	_check(m.resolver.current_hp(m.find("brute").unit) == hp_after_resolve, "playback does not change hp again")
	_check(not d.is_busy() and emptied.size() == 1, "queue drains once")
	_check(log.size() >= 3 and log[0] == "start:hero>brute" and log[1] == "hit:hero" and log[2] == "end:hero",
		"attack order start, hit, end: %s" % str(log))
	_check(actors["hero"].poses.has("windup") and actors["hero"].poses.has("strike"), "attacker plays windup and strike")
	_check(actors["brute"].poses.has("hurt"), "defender plays hurt on the hit frame")
	if m.resolver.current_hp(m.find("brute").unit) > 0:
		_check(log.has("start:brute>hero"), "the counter-attack of a surviving defender is animated")
		_check(log.find("start:brute>hero") > log.find("end:hero"), "counter starts after the attack ends")
	_check(not d.attack("hero", "brute").ok, "a second attack in the same turn is refused")
	_check(d.queue.is_empty(), "a refused attack queues nothing")


func _test_missing_actor() -> void:
	var m = _setup(4)
	var d = Director.new(m)
	d.register_actor("hero", Actor.new())
	_hero_turn(m)
	var hits: Array = []
	d.hit_landed.connect(func(e): hits.append(e))
	_check(d.attack("hero", "brute").ok, "attack resolves without a defender actor")
	_drain(d)
	_check(d.skipped.size() >= 1 and hits.size() >= 1, "animation skipped but the hit event still fires for the UI")
	_check(not d.is_busy(), "no stuck queue when an actor is missing")


func _test_profiles() -> void:
	var m = _setup(1)
	var d = Director.new(m)
	_check(d.attack_id_for("hero") == &"slash" and d.attack_id_for("brute") == &"slash", "sword and axe slash")
	_check(d.attack_id_for("archer") == &"shoot", "bow shoots")
	var spear = m.resolver.weapons.make_unit("CHAR002", ["WPN_STEEL_SPEAR"], "WPN_STEEL_SPEAR")
	m.add("lancer", "player", spear, Vector2i(5, 5))
	var staff = m.resolver.weapons.make_unit("CHAR005", ["WPN_WOOD_STAFF"], "WPN_WOOD_STAFF")
	m.add("mage", "player", staff, Vector2i(6, 5))
	_check(d.attack_id_for("lancer") == &"thrust" and d.attack_id_for("mage") == &"cast", "spear thrusts, staff casts")
	for attack_id: StringName in Director.ATTACKS:
		_check(d.controller.attacks.has(attack_id), "controller knows " + String(attack_id))
