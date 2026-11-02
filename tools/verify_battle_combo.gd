extends SceneTree
## Behavioural verification without scenes, art, damage or gameplay dependencies.

const ComboSequence = preload("res://scenes/battle/combo_sequence.gd")

var _failures: int = 0


func _initialize() -> void:
	_order_and_timing()
	_unavailable()
	_cancellation()
	_validation()
	_reentrancy()
	if _failures == 0:
		print("BATTLE_COMBO_OK")
	quit(0 if _failures == 0 else 1)


func _check(condition: bool, message: String) -> void:
	if not condition:
		_failures += 1
		printerr("FAIL: " + message)


func _release_combos(combos: Array) -> void:
	# Lambdas capturing their RefCounted emitter form cycles; disconnect after checks.
	for combo in combos:
		for signal_info in combo.get_signal_list():
			for connection in combo.get_signal_connection_list(signal_info.name):
				combo.disconnect(signal_info.name, connection.callable)


func _catalogue() -> Dictionary:
	return {
		"normal": {"available": true, "duration": 0.5},
		"followup": {"available": true, "duration": 0.25},
		"finisher": {"available": true, "duration": 0.5},
		"skybreaker_combo": {"available": false},
	}


func _definition() -> Array:
	return [
		{"attack_id": "normal"},
		{"attack_id": "followup", "min_gap": 0.25, "max_gap": 0.5},
		{"attack_id": "finisher", "min_gap": 0.125, "max_gap": 0.25, "gap": 0.25},
	]


func _order_and_timing() -> void:
	var combo = ComboSequence.new()
	var played: Array = []
	var reasons: Array = []
	combo.attack_requested.connect(func(id): played.append([id, combo.elapsed]))
	combo.completed.connect(func(reason): reasons.append(reason))
	_check(combo.start(_definition(), _catalogue(), 0.5), "start valid chain")
	_check(not combo.start(_definition(), _catalogue()), "reject busy start")
	combo.advance(0.5)
	_check(combo.state == "Gap", "first attack ends at 0.5")
	combo.advance(0.125)
	_check(played.size() == 1, "do not play before gap opens")
	combo.advance(0.125)
	_check(combo.current_attack == "followup", "followup starts at gap boundary")
	combo.advance(1.0)
	_check(combo.state == "Recovery", "last attack enters recovery")
	_check(combo.is_running(), "recovery remains busy")
	combo.advance(0.25)
	_check(combo.state == "Recovery" and combo.elapsed == 2.0,
		"recovery remains active before its 2.25-second boundary")
	combo.advance(0.25)
	_check(combo.state == "Idle" and not combo.is_running(), "recovery restores Idle")
	_check(played == [["normal", 0.0], ["followup", 0.75], ["finisher", 1.25]],
		"chain order and exact start times")
	_check(reasons == ["finished"], "completion emitted once")
	combo.advance(100.0)
	_check(reasons.size() == 1, "idle advance does not complete again")

	var coarse = ComboSequence.new()
	var coarse_played: Array = []
	coarse.attack_requested.connect(func(id): coarse_played.append([id, coarse.elapsed]))
	coarse.start(_definition(), _catalogue(), 0.5)
	coarse.advance(100.0)
	_check(coarse_played == played, "large delta preserves all attack boundaries")
	_check(coarse.state == "Idle" and coarse.elapsed == 2.25,
		"large delta consumes only sequence duration")

	var zero = ComboSequence.new()
	var zero_played: Array = []
	zero.attack_requested.connect(func(id): zero_played.append(id))
	zero.start([{"attack_id": "instant"}, {"attack_id": "instant"}],
		{"instant": {"available": true, "duration": 0.0}})
	zero.advance(0.0)
	_check(zero_played == ["instant", "instant"] and zero.state == "Idle",
		"zero-duration steps terminate")
	_release_combos([combo, coarse, zero])


func _unavailable() -> void:
	var combo = ComboSequence.new()
	var played: Array = []
	var reports: Array = []
	combo.attack_requested.connect(func(id): played.append(id))
	combo.attack_reported.connect(func(id, status): reports.append([id, status]))
	var definition: Array = [
		{"attack_id": "normal"},
		{"attack_id": "skybreaker_combo", "min_gap": 10.0},
		{"attack_id": "missing"},
		{"attack_id": "followup"},
	]
	combo.start(definition, _catalogue())
	combo.advance(0.75)
	_check(played == ["normal", "followup"], "unavailable attacks are never requested")
	_check(reports == [["skybreaker_combo", "UNAVAILABLE"], ["missing", "UNAVAILABLE"]],
		"explicitly unavailable and unknown attacks reported")
	_check(combo.state == "Idle" and combo.elapsed == 0.75, "skip unavailable gaps")
	reports.clear()
	_check(not combo.start(definition, _catalogue(), 0.0, false),
		"strict mode rejects unavailable attack")
	_check(combo.state == "Idle" and reports == [["skybreaker_combo", "UNAVAILABLE"]],
		"strict rejection reports without playback")

	var empty = ComboSequence.new()
	_check(empty.start([{"attack_id": "missing"}], {}), "all unavailable accepted for skip")
	_check(empty.state == "Idle" and not empty.is_running(), "all skipped restores Idle")

	var snapshot = ComboSequence.new()
	var catalogue: Dictionary = _catalogue()
	snapshot.start(_definition(), catalogue)
	catalogue.followup.available = false
	snapshot.advance(0.75)
	_check(snapshot.current_attack == "followup", "catalogue is snapshotted at start")
	_release_combos([combo, empty, snapshot])


func _cancellation() -> void:
	# Stop during an attack, a gap and recovery, using both public stop methods.
	for stop_time in [0.125, 0.625, 1.875]:
		for method in ["cancel", "interrupt"]:
			var combo = ComboSequence.new()
			var played: Array = []
			var reasons: Array = []
			combo.attack_requested.connect(func(id): played.append(id))
			combo.completed.connect(func(reason): reasons.append(reason))
			combo.start(_definition(), _catalogue(), 0.5)
			combo.advance(stop_time)
			_check(combo.call(method), method + " succeeds while active")
			_check(combo.state == "Idle" and combo.current_attack.is_empty(),
				method + " immediately restores Idle")
			var count: int = played.size()
			combo.advance(100.0)
			_check(played.size() == count, "stop prevents later attacks")
			var expected: String = "cancelled" if method == "cancel" else "interrupted"
			_check(reasons == [expected], "stop reason emitted once")
			_check(not combo.call(method), "idle stop is a no-op")
			_check(combo.start(_definition(), _catalogue()), "restart after stop")
			combo.cancel()
			_release_combos([combo])


func _validation() -> void:
	var combo = ComboSequence.new()
	for definition in [
		[],
		[{}],
		[{"attack_id": " "}],
		[{"attack_id": "normal", "min_gap": -1.0}],
		[{"attack_id": "normal", "min_gap": 0.5, "max_gap": 0.25}],
		[{"attack_id": "normal", "max_gap": 0.5, "gap": 0.75}],
		[{"attack_id": "normal", "min_gap": 0.25, "max_gap": 0.5, "gap": 0.0}],
		[{"attack_id": "normal", "gap": INF}],
		[{"attack_id": "normal", "gap": NAN}],
		[{"attack_id": "normal", "gap": true}],
	]:
		_check(not combo.start(definition, _catalogue()), "reject invalid definition")
		_check(combo.state == "Idle", "validation preserves Idle")
	_check(not combo.start(_definition(), _catalogue(), -1.0), "reject negative recovery")
	_check(not combo.start(_definition(), _catalogue(), INF), "reject infinite recovery")
	for asset in [
		{"available": true},
		{"available": true, "duration": -1.0},
		{"available": true, "duration": NAN},
		{"available": "yes", "duration": 1.0},
	]:
		_check(not combo.start([{"attack_id": "normal"}], {"normal": asset}),
			"reject malformed catalogue")
	combo.start(_definition(), _catalogue())
	for delta in [-1.0, INF, NAN]:
		_check(not combo.advance(delta), "reject invalid delta")
	_check(combo.elapsed == 0.0 and combo.current_attack == "normal",
		"invalid delta leaves active sequence unchanged")
	combo.cancel()


func _reentrancy() -> void:
	var combo = ComboSequence.new()
	var played: Array = []
	combo.attack_requested.connect(func(id):
		played.append(id)
		combo.cancel()
	)
	combo.start(_definition(), _catalogue())
	combo.advance(100.0)
	_check(played == ["normal"] and combo.state == "Idle", "cancel inside attack request")

	var on_state = ComboSequence.new()
	var state_played: Array = []
	on_state.state_changed.connect(func(value):
		if value == "Attack":
			on_state.cancel()
	)
	on_state.attack_requested.connect(func(id): state_played.append(id))
	on_state.start(_definition(), _catalogue())
	_check(state_played.is_empty() and on_state.state == "Idle",
		"state listener cancellation suppresses stale attack request")

	var replacement = ComboSequence.new()
	var replacement_played: Array = []
	replacement.attack_requested.connect(func(id): replacement_played.append(id))
	replacement.attack_reported.connect(func(_id, _status):
		replacement.cancel()
		replacement.start([{"attack_id": "normal"}], _catalogue())
	)
	replacement.start([{"attack_id": "missing"}, {"attack_id": "finisher"}], _catalogue())
	_check(replacement_played == ["normal"], "report callback can replace sequence")
	_check(replacement.current_attack == "normal", "old sequence does not resume")
	replacement.advance(0.5)
	_check(replacement.state == "Idle", "replacement completes normally")
	_release_combos([combo, on_state, replacement])
