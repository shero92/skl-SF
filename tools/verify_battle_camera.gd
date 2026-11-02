extends SceneTree
## Deterministic headless behavioural checks; no rendered assets required.

const CameraController = preload("res://scenes/battle/dynamic_battle_camera.gd")
var _failures := 0


func _initialize() -> void:
	call_deferred("_verify")


func _check(condition: bool, message: String) -> void:
	if not condition:
		_failures += 1
		printerr("FAIL: " + message)


func _verify() -> void:
	var camera := CameraController.new()
	camera.position = Vector2(40.0, 20.0)
	camera.rotation = 0.2
	camera.offset = Vector2(4.0, -2.0)
	camera.zoom = Vector2(1.2, 1.2)
	root.add_child(camera)
	camera.set_process(false)
	var original_transform := camera.transform
	var original_offset := camera.offset
	var original_zoom := camera.zoom

	camera.focus_on(camera.to_global(Vector2(20.0, 0.0)), Vector2(1.5, 1.5), 1.0)
	var previous_x := camera.offset.x
	var previous_zoom := camera.zoom.x
	for step in range(100):
		camera.advance(0.01)
		_check(camera.offset.x >= previous_x - 0.00001, "focus must be monotonic")
		_check(camera.offset.x <= original_offset.x + 20.00001, "focus overshot")
		_check(camera.zoom.x >= previous_zoom - 0.00001, "zoom must be monotonic")
		_check(camera.zoom.x <= 1.50001, "zoom overshot")
		previous_x = camera.offset.x
		previous_zoom = camera.zoom.x
	_check(camera.offset.is_equal_approx(original_offset + Vector2(20.0, 0.0)), "focus endpoint")
	_check(camera.zoom.is_equal_approx(Vector2(1.5, 1.5)), "zoom endpoint")

	camera.restore()
	camera.focus_on(camera.to_global(Vector2(15.0, 5.0)), Vector2(1.4, 1.4), 1.0)
	camera.advance(0.2)
	camera.hitstop_active = true
	var frozen_offset := camera.offset
	var frozen_zoom := camera.zoom
	camera.shake(100.0, 0.5)
	var peak := 0.0
	for step in range(60):
		camera.advance(0.01)
		var pixels := (camera.shake_offset * camera.zoom).length()
		peak = maxf(peak, pixels)
		_check(pixels <= 3.00001, "shake exceeded pixel cap")
		_check((camera.offset - camera.shake_offset).is_equal_approx(frozen_offset), "hitstop moved focus")
		_check(camera.zoom == frozen_zoom, "hitstop moved zoom")
	_check(peak > 0.0, "shake did not run")
	_check(camera.shake_offset == Vector2.ZERO, "shake did not finish at zero")
	camera.hitstop_active = false
	camera.advance(1.0)
	_check(camera.zoom.is_equal_approx(Vector2(1.4, 1.4)), "focus did not resume")

	var target := Node2D.new()
	root.add_child(target)
	target.global_position = camera.to_global(Vector2(10000.0, -10000.0))
	camera.follow(target)
	camera.advance(10.0)
	var displacement := ((camera.offset - original_offset) * original_zoom).abs()
	_check(displacement.x <= 32.00001 and displacement.y <= 18.00001, "follow exceeded motion budget")
	var followed := camera.offset
	camera.hitstop_active = true
	target.position += Vector2(100.0, 100.0)
	camera.advance(1.0)
	_check(camera.offset == followed, "follow ignored hitstop")
	target.free()
	camera.hitstop_active = false
	camera.advance(0.1)

	for preset_name in ["hero_rear_3q", "hero_front", "monster_rear"]:
		_check(camera.set_preset(preset_name, 0.1), "missing preset")
		camera.advance(0.1)
	_check(not camera.set_preset("unknown"), "unknown preset accepted")

	camera.shake(2.0, 1.0)
	camera.advance(0.1)
	camera.restore()
	_check(camera.transform == original_transform, "restore changed transform")
	_check(camera.offset == original_offset, "restore changed offset")
	_check(camera.zoom == original_zoom, "restore changed zoom")
	camera.advance(10.0)
	_check(camera.transform == original_transform and camera.offset == original_offset and camera.zoom == original_zoom, "restored camera drifted")

	camera.focus_on(camera.to_global(Vector2(10.0, 0.0)), Vector2.ONE, 1.0)
	camera.advance(0.5)
	var half_offset := camera.offset
	camera.restore()
	camera.focus_on(camera.to_global(Vector2(10.0, 0.0)), Vector2.ONE, 1.0)
	for step in range(50):
		camera.advance(0.01)
	_check(camera.offset.is_equal_approx(half_offset), "transition depends on frame rate")
	camera.restore()
	camera.free()
	if _failures == 0:
		print("BATTLE_CAMERA_OK")
	quit(0 if _failures == 0 else 1)
