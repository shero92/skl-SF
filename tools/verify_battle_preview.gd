extends SceneTree
## Headless verification of the battle preview scene (stub actors, real controller).
## Agent: claude (Claude Code); model: Sonnet 5.5.

var _failures: int = 0


func _initialize() -> void:
	var scene: PackedScene = load("res://scenes/battle/battle_preview.tscn")
	var preview = scene.instantiate()
	root.add_child(preview)
	await process_frame  # _ready runs once the tree is processing
	_test_selectors(preview)
	_test_transport(preview)
	_test_speed(preview)
	_test_toggles(preview)
	_test_capture(preview)
	if _failures == 0:
		print("BATTLE_PREVIEW_OK")
	quit(0 if _failures == 0 else 1)


func _check(condition: bool, message: String) -> void:
	if not condition:
		_failures += 1
		printerr("FAIL: " + message)


func _test_selectors(p) -> void:
	_check(p.set_attack(&"thrust") and p.get_state()["attack"] == &"thrust", "attack selector")
	_check(not p.set_attack(&"missing"), "unknown attack rejected")
	_check(p.set_view("HERO_FRONT") and p.get_state()["view"] == "HERO_FRONT", "view selector")
	_check(p.attacker.view == "HERO_FRONT", "view reaches the actor")
	_check(not p.set_view("NOPE"), "unknown view rejected")
	_check(p.set_weapon(&"spear") and p.get_state()["weapon"] == &"spear", "weapon selector")
	_check(not p.set_weapon(&"axe"), "unknown weapon rejected")
	p.set_attack(&"slash")
	p.set_view("HERO_REAR_3Q")


func _test_transport(p) -> void:
	var result: Dictionary = p.restart()
	_check(result["ok"] and p.get_state()["playing"], "restart plays")
	_check(p.attacker.frame_name == "windup", "first frame applied")
	p.tick(0.13)
	_check(p.attacker.frame_name == "strike" and p.get_state()["hits"] == 1, "tick reaches the hit")
	p.pause()
	var before: float = p.get_state()["elapsed_ms"]
	p._process(1.0)
	_check(p.get_state()["elapsed_ms"] == before, "pause stops time")
	p.play()
	_check(p.get_state()["playing"], "play resumes")
	p.restart()
	_check(p.get_state()["hits"] == 0 and p.get_state()["elapsed_ms"] == 0.0, "restart resets")
	p.pause()
	p.step_frame()
	_check(p.attacker.frame_name == "strike" and not p.get_state()["playing"], "step to next frame")
	p.step_frame()
	_check(p.attacker.frame_name == "recover", "step to recovery")
	p.step_frame()
	_check(p.attacker.frame_name == "idle" and p.get_state()["controller_state"] == 0, "step completes")
	p.step_frame()
	_check(p.get_state()["controller_state"] != 0 and not p.get_state()["playing"], "step restarts a finished attack")
	p.pause()


func _test_speed(p) -> void:
	_check(p.set_speed(0.25) and p.speed == 0.25, "0.25x speed")
	_check(not p.set_speed(3.0), "unsupported speed rejected")
	p.restart()
	p._process(0.4)  # 0.4 s * 0.25 = 100 ms: still in the 120 ms windup frame
	_check(p.attacker.frame_name == "windup", "slow speed scales time")
	p.set_speed(1.0)
	p.pause()


func _test_toggles(p) -> void:
	p.set_vfx_enabled(false)
	_check(not p.vfx.is_vfx_enabled() and not p.vfx.visible, "vfx off")
	p.set_vfx_enabled(true)
	_check(p.vfx.is_vfx_enabled(), "vfx on")
	p.set_camera_enabled(true)
	p.restart()
	p.tick(0.13)
	p.tick(0.01)
	_check(p.camera.offset != Vector2.ZERO or p.camera.shake_offset != Vector2.ZERO, "camera reacts to hit")
	p.set_camera_enabled(false)
	_check(p.camera.offset == Vector2.ZERO and p.camera.shake_offset == Vector2.ZERO, "camera off restores")
	p.restart()
	p.tick(0.13)
	p.tick(0.01)
	_check(p.camera.shake_offset == Vector2.ZERO, "camera off ignores hits")
	p.set_camera_enabled(true)
	p.pause()


func _test_capture(p) -> void:
	var path := "user://battle_preview_capture_test.png"
	if FileAccess.file_exists(path):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(path))
	_check(not p.capture(""), "empty path never captures")
	_check(not FileAccess.file_exists(path), "no file without a path")
	var wrote: bool = p.capture(path)
	# Headless uses a dummy renderer: no image there is a clean false, never a fake file.
	_check(wrote == FileAccess.file_exists(path), "capture result matches the file on disk")
	if wrote:
		var image := Image.load_from_file(ProjectSettings.globalize_path(path))
		_check(image != null and not image.is_empty(), "captured image is real")
		DirAccess.remove_absolute(ProjectSettings.globalize_path(path))
