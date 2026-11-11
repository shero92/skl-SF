extends Node2D
## Playable skirmish on a grid: click a blue cell to move, a red-marked enemy to attack, Space to wait.
## Agent: claude (Claude Code); model: Fable 5.2.
## Units and terrain are drawn as plain shapes on purpose: battle-map art is requested, not generated here.

const Session = preload("res://scenes/battle/tactical_battle.gd")
const WeaponSystem = preload("res://scenes/battle/weapon_system.gd")
const Director = preload("res://scenes/battle/battle_director.gd")

const CELL := 64
const ORIGIN := Vector2(448, 224)
const ENEMY_DELAY := 0.55
const ROOM_SCENE := "res://scenes/main.tscn"
const TEAM_COLOR := {"player": Color(0.2, 0.45, 0.9), "enemy": Color(0.85, 0.25, 0.2)}

var session
var seed_value: int = 1
var save_path: String = HeroSave.DEFAULT_PATH
var director
var _enemy_timer: float = 0.0
var _font: Font
var _actors: Dictionary = {}      # id -> PoseActor, driven by the animation controller
var _shown_hp: Dictionary = {}    # id -> hp drawn on screen; follows the real hp when the blow lands
var _playing: Dictionary = {}     # the director entry being played
var _popups: Array[Dictionary] = []  # floating damage text: {id, text, time}


## Shape stand-in for a battle sprite: the controller sets its pose, _draw turns the pose into a lunge or a flash.
class PoseActor extends RefCounted:
	var pose: String = "idle"

	func set_view(_view) -> void:
		pass

	func set_frame(frame_name, _index: int) -> void:
		pose = String(frame_name)

	func reset() -> void:
		pose = "idle"


func _ready() -> void:
	_font = ThemeDB.fallback_font
	restart()


func restart() -> void:
	var weapons = WeaponSystem.load_default()
	var hero: Dictionary = weapons.make_unit("CHAR001", ["WPN_IRON_SWORD"], "WPN_HERO_BASIC_SWORD")
	HeroSave.load_into(weapons, hero, save_path)
	session = Session.new(seed_value, hero)
	session.changed.connect(queue_redraw)
	director = Director.new(session.manager)
	_actors.clear()
	_shown_hp.clear()
	_popups.clear()
	_playing = {}
	for c: Dictionary in session.manager.combatants:
		var id := String(c.id)
		_actors[id] = PoseActor.new()
		director.register_actor(id, _actors[id])
		_shown_hp[id] = session.hp(id)
	session.manager.attacked.connect(_on_attacked)
	director.playback_started.connect(func(entry: Dictionary): _playing = entry)
	director.hit_landed.connect(_on_hit_landed)
	director.playback_finished.connect(func(_entry: Dictionary): _playing = {})
	_enemy_timer = ENEMY_DELAY
	queue_redraw()


func cell_at(point: Vector2) -> Vector2i:
	var local := (point - ORIGIN) / float(CELL)
	return Vector2i(floori(local.x), floori(local.y))


func cell_rect(cell: Vector2i) -> Rect2:
	return Rect2(ORIGIN + Vector2(cell) * CELL, Vector2(CELL, CELL))


## True while an attack animation plays; input and enemy turns wait for it.
func is_animating() -> bool:
	return director.is_busy()


## The rules resolved the attack already; queue its playback (and the counter's) on the director.
func _on_attacked(attacker_id: String, defender_id: String, result: Dictionary, counter: Dictionary) -> void:
	director.queue.append({"attack_id": director.attack_id_for(attacker_id), "attacker_id": attacker_id,
		"defender_id": defender_id, "result": result, "counter": false})
	if not counter.is_empty():
		director.queue.append({"attack_id": director.attack_id_for(defender_id), "attacker_id": defender_id,
			"defender_id": attacker_id, "result": counter, "counter": true})


func _on_hit_landed(entry: Dictionary) -> void:
	var id := String(entry.defender_id)
	var result: Dictionary = entry.result
	var landed: bool = result.get("hit", false)
	if landed:
		_shown_hp[id] = maxi(0, int(_shown_hp.get(id, 0)) - int(result.get("damage", 0)))
	_popups.append({"id": id, "text": str(int(result.get("damage", 0))) if landed else "miss", "time": 0.6})


## One click: attack the enemy on that cell if it is in range, otherwise move there if allowed.
func click_cell(cell: Vector2i) -> bool:
	if is_animating():
		return false
	var other = session.manager.occupant(cell)
	if other != null and session.target_ids().has(String(other.id)):
		return session.attack(String(other.id))
	return session.move(cell)


func _process(delta: float) -> void:
	for popup: Dictionary in _popups:
		popup.time -= delta
	if not _popups.is_empty():
		_popups = _popups.filter(func(p: Dictionary) -> bool: return p.time > 0.0)
		queue_redraw()
	if is_animating():
		director.advance(delta)
		_enemy_timer = ENEMY_DELAY
		queue_redraw()
		return
	if session.is_over() or session.is_player_turn():
		_enemy_timer = ENEMY_DELAY
		return
	_enemy_timer -= delta
	if _enemy_timer <= 0.0:
		_enemy_timer = ENEMY_DELAY
		session.step_enemy()


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		click_cell(cell_at(get_global_mouse_position()))
	elif event is InputEventKey and event.pressed and not event.echo:
		match event.keycode:
			KEY_SPACE, KEY_ENTER:
				if not is_animating():
					session.wait()
			KEY_R:
				if session.is_over():
					seed_value += 1
					restart()
			KEY_ESCAPE:
				get_tree().change_scene_to_file(ROOM_SCENE)


func _draw() -> void:
	var size: Vector2i = Session.SIZE
	draw_rect(Rect2(Vector2.ZERO, Vector2(1536, 1024)), Color(0.08, 0.1, 0.14))
	for y in size.y:
		for x in size.x:
			var cell := Vector2i(x, y)
			var shade := Color(0.36, 0.52, 0.3) if (x + y) % 2 == 0 else Color(0.33, 0.48, 0.28)
			if session.manager.blocked.has(cell):
				shade = Color(0.4, 0.4, 0.42)
			draw_rect(cell_rect(cell).grow(-1), shade)
	for cell: Vector2i in session.move_cells():
		draw_rect(cell_rect(cell).grow(-3), Color(0.3, 0.6, 1.0, 0.35))
	var targets: Array[String] = session.target_ids()
	var acting = session.current()
	for c: Dictionary in session.manager.combatants:
		var unit_id := String(c.id)
		if int(_shown_hp.get(unit_id, 0)) <= 0:
			continue  # stays on screen until the blow that defeats it has landed
		var rect := cell_rect(c.cell)
		var centre := rect.get_center() + _pose_offset(unit_id)
		if targets.has(String(c.id)):
			draw_rect(rect.grow(-3), Color(1.0, 0.2, 0.2, 0.45))
		draw_circle(centre, 22, Color(1, 1, 1) if _actors[unit_id].pose == "hurt" else TEAM_COLOR[c.team])
		if acting != null and acting.id == c.id:
			draw_arc(centre, 26, 0, TAU, 32, Color(1, 0.9, 0.3), 3)
		var label: String = session.display_name(String(c.id))
		draw_string(_font, centre + Vector2(-20, 5), label.left(4), HORIZONTAL_ALIGNMENT_LEFT, 44, 14, Color.WHITE)
		var ratio := float(_shown_hp[unit_id]) / float(session.max_hp(unit_id))
		draw_rect(Rect2(rect.position + Vector2(8, 54), Vector2(48, 5)), Color(0.15, 0.15, 0.15))
		draw_rect(Rect2(rect.position + Vector2(8, 54), Vector2(48 * ratio, 5)), Color(0.3, 0.9, 0.3))
	for popup: Dictionary in _popups:
		var owner = session.manager.find(String(popup.id))
		if owner != null:
			var at: Vector2 = cell_rect(owner.cell).get_center() + Vector2(-12, -30 - (0.6 - float(popup.time)) * 30.0)
			draw_string(_font, at, String(popup.text), HORIZONTAL_ALIGNMENT_LEFT, 60, 18, Color(1, 0.95, 0.4))
	var status := "Victory - R: new battle, Esc: room" if session.winner() == "player" else "Defeat - R: retry, Esc: room"
	if is_animating():
		status = "..."
	elif not session.is_over():
		status = ("Your turn: %s - click blue to move, red to attack, Space to wait" % session.display_name(String(acting.id))) \
			if session.is_player_turn() else "Enemy turn..."
	draw_string(_font, Vector2(448, 190), status, HORIZONTAL_ALIGNMENT_LEFT, 900, 20, Color.WHITE)
	var lines: Array = session.log_lines.slice(maxi(0, session.log_lines.size() - 6))
	for i in lines.size():
		draw_string(_font, Vector2(448, 710 + i * 22), String(lines[i]), HORIZONTAL_ALIGNMENT_LEFT, 900, 16, Color(0.85, 0.85, 0.85))


## Lunge toward the target on the strike frame, lean back on the wind-up, shake when hurt.
func _pose_offset(id: String) -> Vector2:
	if _playing.is_empty():
		return Vector2.ZERO
	var pose: String = _actors[id].pose
	if id == String(_playing.attacker_id):
		var from = session.manager.find(id)
		var to = session.manager.find(String(_playing.defender_id))
		var toward := Vector2(to.cell - from.cell).normalized()
		if pose in ["strike", "release", "cast_release"]:
			return toward * 14.0
		if pose in ["windup", "draw", "cast"]:
			return toward * -6.0
	elif pose == "hurt":
		return Vector2(3, 0)
	return Vector2.ZERO
