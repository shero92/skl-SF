extends Node2D
## Playable skirmish on a grid: click a blue cell to move, a red-marked enemy to attack, Space to wait.
## Agent: claude (Claude Code); model: Fable 5.2.
## Units and terrain are drawn as plain shapes on purpose: battle-map art is requested, not generated here.

const Session = preload("res://scenes/battle/tactical_battle.gd")
const WeaponSystem = preload("res://scenes/battle/weapon_system.gd")

const CELL := 64
const ORIGIN := Vector2(448, 224)
const ENEMY_DELAY := 0.55
const ROOM_SCENE := "res://scenes/main.tscn"
const TEAM_COLOR := {"player": Color(0.2, 0.45, 0.9), "enemy": Color(0.85, 0.25, 0.2)}

var session
var seed_value: int = 1
var save_path: String = HeroSave.DEFAULT_PATH
var _enemy_timer: float = 0.0
var _font: Font


func _ready() -> void:
	_font = ThemeDB.fallback_font
	restart()


func restart() -> void:
	var weapons = WeaponSystem.load_default()
	var hero: Dictionary = weapons.make_unit("CHAR001", ["WPN_IRON_SWORD"], "WPN_HERO_BASIC_SWORD")
	HeroSave.load_into(weapons, hero, save_path)
	session = Session.new(seed_value, hero)
	session.changed.connect(queue_redraw)
	_enemy_timer = ENEMY_DELAY
	queue_redraw()


func cell_at(point: Vector2) -> Vector2i:
	var local := (point - ORIGIN) / float(CELL)
	return Vector2i(floori(local.x), floori(local.y))


func cell_rect(cell: Vector2i) -> Rect2:
	return Rect2(ORIGIN + Vector2(cell) * CELL, Vector2(CELL, CELL))


## One click: attack the enemy on that cell if it is in range, otherwise move there if allowed.
func click_cell(cell: Vector2i) -> bool:
	var other = session.manager.occupant(cell)
	if other != null and session.target_ids().has(String(other.id)):
		return session.attack(String(other.id))
	return session.move(cell)


func _process(delta: float) -> void:
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
	for c: Dictionary in session.manager.alive():
		var rect := cell_rect(c.cell)
		var centre := rect.get_center()
		if targets.has(String(c.id)):
			draw_rect(rect.grow(-3), Color(1.0, 0.2, 0.2, 0.45))
		draw_circle(centre, 22, TEAM_COLOR[c.team])
		if acting != null and acting.id == c.id:
			draw_arc(centre, 26, 0, TAU, 32, Color(1, 0.9, 0.3), 3)
		var label: String = session.display_name(String(c.id))
		draw_string(_font, centre + Vector2(-20, 5), label.left(4), HORIZONTAL_ALIGNMENT_LEFT, 44, 14, Color.WHITE)
		var ratio := float(session.hp(String(c.id))) / float(session.max_hp(String(c.id)))
		draw_rect(Rect2(rect.position + Vector2(8, 54), Vector2(48, 5)), Color(0.15, 0.15, 0.15))
		draw_rect(Rect2(rect.position + Vector2(8, 54), Vector2(48 * ratio, 5)), Color(0.3, 0.9, 0.3))
	var status := "Victory - R: new battle, Esc: room" if session.winner() == "player" else "Defeat - R: retry, Esc: room"
	if not session.is_over():
		status = ("Your turn: %s - click blue to move, red to attack, Space to wait" % session.display_name(String(acting.id))) \
			if session.is_player_turn() else "Enemy turn..."
	draw_string(_font, Vector2(448, 190), status, HORIZONTAL_ALIGNMENT_LEFT, 900, 20, Color.WHITE)
	var lines: Array = session.log_lines.slice(maxi(0, session.log_lines.size() - 6))
	for i in lines.size():
		draw_string(_font, Vector2(448, 710 + i * 22), String(lines[i]), HORIZONTAL_ALIGNMENT_LEFT, 900, 16, Color(0.85, 0.85, 0.85))
