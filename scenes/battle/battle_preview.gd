extends Control
## Standalone battle animation preview. Stub actors only: no art, damage or gameplay code.
## Agent: claude (Claude Code); model: Sonnet 5.5.
##
## Selectors: attack, view, weapon. Transport: play/pause/restart/step, speed (1x/0.5x/0.25x).
## Toggles: camera, vfx. Headless capture: pass `-- --capture=<path>`; nothing is written otherwise.

const Controller = preload("res://scenes/battle/battle_animation_controller.gd")
const Bridge = preload("res://scenes/battle/hit_timing_bridge.gd")
const Perspective = preload("res://scenes/battle/battle_perspective.gd")
const VfxLayer = preload("res://scenes/battle/battle_vfx_layer.gd")
const BattleCamera = preload("res://scenes/battle/dynamic_battle_camera.gd")

const REFERENCE_SIZE := Vector2i(320, 180)
const SPEEDS: Array[float] = [1.0, 0.5, 0.25]
## attack id -> frames of [duration_ms, phase, hit, attacker pose, defender pose]
const ATTACKS := {
	&"slash": [
		[120, "Attack", false, "windup", "idle"],
		[80, "Attack", true, "strike", "hurt"],
		[160, "Recovery", false, "recover", "idle"],
	],
	&"thrust": [
		[100, "Attack", false, "windup", "idle"],
		[60, "Attack", true, "strike", "hurt"],
		[60, "Attack", true, "strike_2", "hurt"],
		[140, "Recovery", false, "recover", "idle"],
	],
}
const WEAPONS := {&"sword": Color(0.85, 0.85, 0.95), &"spear": Color(0.95, 0.8, 0.45)}

var controller := Controller.new()
var bridge := Bridge.new()
var playing: bool = false
var speed: float = 1.0
var camera_enabled: bool = true
var hits: int = 0
var elapsed_ms: float = 0.0
var attack_id: StringName = &"slash"
var view_id: String = Perspective.HERO_REAR_3Q
var weapon_id: StringName = &"sword"
var attacker: StubActor
var defender: StubActor
var vfx: Node2D
var camera: Camera2D
var viewport: SubViewport

var _frame_starts: Array[float] = []
var _status: Label


class StubActor extends Node2D:
	var view: String = ""
	var frame_name: String = "idle"
	var frame_index: int = 0
	var body := ColorRect.new()
	var socket := Node2D.new()

	func _init(color: Color = Color.WHITE) -> void:
		body.size = Vector2(24, 40)
		body.position = Vector2(-12, -40)
		body.color = color
		add_child(body)
		socket.position = Vector2(14, -24)
		add_child(socket)

	func set_view(value) -> void:
		view = str(value)

	func set_frame(frame: Variant, index: int) -> void:
		frame_name = str(frame)
		frame_index = index
		socket.position = Vector2(14 + (8 if frame_name.begins_with("strike") else 0), -24)
		body.modulate = Color(1.0, 0.5, 0.5) if frame_name == "hurt" else Color.WHITE

	func reset() -> void:
		frame_name = "idle"
		frame_index = 0
		socket.position = Vector2(14, -24)
		body.modulate = Color.WHITE


func _ready() -> void:
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_build_scene()
	_build_controls()
	bridge.bind_controller(controller)
	bridge.hit_confirmed.connect(_on_hit_confirmed)
	controller.finished.connect(func(_a, _b, _c): _on_ended())
	controller.cancelled.connect(func(_a, _b, _c): _refresh())
	_refresh()
	var path := _capture_path()
	if path != "":
		restart()
		tick(0.2)
		await RenderingServer.frame_post_draw
		capture(path)
		get_tree().quit()


func _process(delta: float) -> void:
	if playing:
		tick(delta * speed)


func _build_scene() -> void:
	var container := SubViewportContainer.new()
	container.stretch = true
	container.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	container.size = Vector2(REFERENCE_SIZE) * 3.0
	container.position = Vector2(0, 40)
	add_child(container)
	viewport = SubViewport.new()
	viewport.size = REFERENCE_SIZE
	viewport.canvas_item_default_texture_filter = Viewport.DEFAULT_CANVAS_ITEM_TEXTURE_FILTER_NEAREST
	viewport.snap_2d_transforms_to_pixel = true
	container.add_child(viewport)
	var backdrop := ColorRect.new()
	backdrop.color = Color(0.18, 0.2, 0.26)
	backdrop.size = Vector2(REFERENCE_SIZE)
	viewport.add_child(backdrop)
	attacker = StubActor.new(WEAPONS[weapon_id])
	attacker.position = Vector2(100, 130)
	defender = StubActor.new(Color(0.8, 0.35, 0.3))
	defender.position = Vector2(220, 130)
	viewport.add_child(attacker)
	viewport.add_child(defender)
	vfx = VfxLayer.new()
	viewport.add_child(vfx)
	vfx.bind_socket(attacker.socket)
	camera = BattleCamera.new()
	camera.position = Vector2(REFERENCE_SIZE) * 0.5
	viewport.add_child(camera)


func _build_controls() -> void:
	var bar := HBoxContainer.new()
	bar.position = Vector2(4, 4)
	add_child(bar)
	_selector(bar, ATTACKS.keys(), func(i): set_attack(ATTACKS.keys()[i]))
	_selector(bar, Perspective.VIEWS.keys(), func(i): set_view(Perspective.VIEWS.keys()[i]))
	_selector(bar, WEAPONS.keys(), func(i): set_weapon(WEAPONS.keys()[i]))
	_button(bar, "Play", play)
	_button(bar, "Pause", pause)
	_button(bar, "Restart", restart)
	_button(bar, "Step", step_frame)
	_toggle(bar, "0.25x", false, func(on): set_speed(0.25 if on else 1.0))
	_toggle(bar, "Camera", true, set_camera_enabled)
	_toggle(bar, "VFX", true, set_vfx_enabled)
	_status = Label.new()
	_status.position = Vector2(4, 40 + REFERENCE_SIZE.y * 3 + 4)
	add_child(_status)


func _selector(parent: Node, items: Array, on_select: Callable) -> void:
	var option := OptionButton.new()
	for item in items:
		option.add_item(str(item))
	option.item_selected.connect(on_select)
	parent.add_child(option)


func _button(parent: Node, text: String, action: Callable) -> void:
	var button := Button.new()
	button.text = text
	button.pressed.connect(action)
	parent.add_child(button)


func _toggle(parent: Node, text: String, initial: bool, action: Callable) -> void:
	var toggle := CheckButton.new()
	toggle.text = text
	toggle.button_pressed = initial
	toggle.toggled.connect(action)
	parent.add_child(toggle)


# --- Selectors -------------------------------------------------------------

func set_attack(value: StringName) -> bool:
	if not ATTACKS.has(value):
		return false
	attack_id = value
	restart()
	return true


func set_view(value: String) -> bool:
	if not Perspective.VIEWS.has(value):
		return false
	view_id = value
	restart()
	return true


func set_weapon(value: StringName) -> bool:
	if not WEAPONS.has(value):
		return false
	weapon_id = value
	attacker.body.color = WEAPONS[value]
	_refresh()
	return true


# --- Transport -------------------------------------------------------------

func play() -> void:
	if controller.state == Controller.State.IDLE:
		restart()
	else:
		playing = true
	_refresh()


func pause() -> void:
	playing = false
	_refresh()


func restart() -> Dictionary:
	controller.cancel()
	controller.attacks = {attack_id: {"frames": _frames()}}
	elapsed_ms = 0.0
	hits = 0
	vfx.clear()
	vfx.bind_socket(attacker.socket)
	vfx.start_trail()
	if camera_enabled:
		camera.restore()
	var result: Dictionary = controller.play_attack(attack_id, attacker, defender)
	playing = bool(result.get("ok", false))
	_refresh()
	return result


func step_frame() -> void:
	## Pause and advance to the next frame boundary (or to the end of the attack).
	if controller.state == Controller.State.IDLE:
		restart()
	playing = false
	for start in _frame_starts:
		if start > elapsed_ms + 0.001:
			tick((start - elapsed_ms + 0.01) / 1000.0)
			_refresh()
			return
	tick(10.0)  # beyond the final frame: completes the attack
	_refresh()


func set_speed(value: float) -> bool:
	if not SPEEDS.has(value):
		return false
	speed = value
	_refresh()
	return true


func tick(delta_seconds: float) -> void:
	## Advance by already speed-scaled seconds (_process applies `speed`).
	if controller.state == Controller.State.IDLE:
		return
	elapsed_ms += delta_seconds * 1000.0
	# Camera first: a shake started by this tick's hit is felt from the next tick.
	if camera_enabled:
		camera.advance(delta_seconds)
	controller.advance(delta_seconds)
	vfx.sample_socket()


# --- Toggles ---------------------------------------------------------------

func set_camera_enabled(value: bool) -> void:
	camera_enabled = value
	if not value:
		camera.restore()
	_refresh()


func set_vfx_enabled(value: bool) -> void:
	vfx.set_vfx_enabled(value)
	_refresh()


# --- State and capture -----------------------------------------------------

func get_state() -> Dictionary:
	return {
		"attack": attack_id, "view": view_id, "weapon": weapon_id,
		"playing": playing, "speed": speed, "camera": camera_enabled,
		"vfx": vfx.is_vfx_enabled(), "elapsed_ms": elapsed_ms, "hits": hits,
		"controller_state": controller.state,
		"attacker_frame": attacker.frame_name, "defender_frame": defender.frame_name,
	}


func capture(path: String) -> bool:
	## Writes the viewport to `path` only when a path is given and a real image exists.
	if path.strip_edges() == "" or DisplayServer.get_name() == "headless":
		return false  # headless has a dummy renderer: no real image exists
	var image := viewport.get_texture().get_image()
	if image == null or image.is_empty():
		return false
	return image.save_png(path) == OK


func _capture_path() -> String:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--capture="):
			return arg.substr("--capture=".length())
	return ""


func _frames() -> Array[Dictionary]:
	var frames: Array[Dictionary] = []
	_frame_starts.clear()
	var start := 0.0
	for row in ATTACKS[attack_id]:
		_frame_starts.append(start)
		start += float(row[0])
		frames.append({
			"duration_ms": row[0], "phase": row[1], "hit": row[2],
			"attacker": {"view": view_id, "name": row[3], "index": frames.size()},
			"defender": {"view": view_id, "name": row[4], "index": frames.size()},
		})
	return frames


func _on_hit_confirmed(_attacker, _defender, _attack_id, _hit_index) -> void:
	hits += 1
	if camera_enabled:
		camera.shake(2.0, 0.12)
	vfx.sample_socket()
	_refresh()


func _on_ended() -> void:
	playing = false
	_refresh()


func _refresh() -> void:
	if _status == null:
		return
	var s := get_state()
	_status.text = "%s | %s | %s | %s %sx | hits %d | %s / %s" % [
		s["attack"], s["view"], s["weapon"], "playing" if s["playing"] else "paused",
		s["speed"], s["hits"], s["attacker_frame"], s["defender_frame"],
	]
