extends SceneTree
## Headless behavioural verification; uses an existing script as a resource fixture.

const Reactions = preload("res://scenes/battle/battle_reactions.gd")
const FIXTURE := "res://scenes/battle/battle_reactions.gd"


class HitSource:
	extends RefCounted
	signal hit(payload: Dictionary)
	signal cancelled
	signal reset


var _failures: Array[String] = []
var _started: Array[Dictionary] = []
var _missing: Array[Dictionary] = []
var _cleared: int = 0


func _initialize() -> void:
	call_deferred("_run")


func _check(condition: bool, message: String) -> void:
	if not condition:
		_failures.append(message)
		push_error(message)


func _run() -> void:
	var reactions := Reactions.new()
	root.add_child(reactions)
	reactions.set_process(false)
	reactions.reaction_started.connect(func(value: Dictionary): _started.append(value))
	reactions.missing_reaction_art.connect(func(value: Dictionary): _missing.append(value))
	reactions.reaction_cleared.connect(func(): _cleared += 1)
	reactions.configure({
		"front": {"hit": FIXTURE, "block": FIXTURE},
		"rear": {"hit": "res://missing_reaction_art_fixture.tres"},
	})
	var source := HitSource.new()
	_check(reactions.bind_source(source), "Source binding must succeed")
	var hero := {
		"outcome": "hit",
		"defender_id": "hero",
		"defender_is_hero": true,
		"defender_view_id": "rear",
	}
	source.hit.emit(hero)
	_check(_started.size() == 1, "Hit signal must start a reaction")
	_check(reactions.active_reaction().get("view_id") == "front", "Hero uses front view")
	_check(reactions.active_reaction().get("reaction") == "hit", "Hit selects hit state")
	var snapshot := reactions.active_reaction()
	snapshot["view_id"] = "tampered"
	_check(reactions.active_reaction().get("view_id") == "front", "State is a snapshot")

	source.cancelled.emit()
	_check(reactions.active_reaction().is_empty(), "Cancel clears immediately")
	reactions._process(10.0)
	_check(reactions.active_reaction().is_empty(), "Cancelled reaction cannot resume")

	hero["outcome"] = "block"
	source.hit.emit(hero)
	_check(reactions.active_reaction().get("reaction") == "block", "Block selects block state")
	source.reset.emit()
	_check(reactions.active_reaction().is_empty(), "Reset clears immediately")
	reactions._process(10.0)
	_check(reactions.active_reaction().is_empty(), "Reset reaction cannot resume")

	source.hit.emit(hero)
	reactions._process(reactions.reaction_duration / 2.0)
	_check(not reactions.active_reaction().is_empty(), "Reaction survives half duration")
	reactions._process(reactions.reaction_duration)
	_check(reactions.active_reaction().is_empty(), "Reaction expires")

	source.hit.emit({"outcome": "hit", "defender_view_id": "rear"})
	_check(_missing.size() == 1, "Missing resource must be reported")
	_check(_missing[0].get("code") == "MISSING_REACTION_ART", "Missing art diagnostic code")
	_check(reactions.active_reaction().is_empty(), "Missing art has no substitute")
	source.hit.emit({"outcome": "block", "defender_view_id": "unknown"})
	_check(_missing.size() == 2, "Missing view must be reported")
	_check(reactions.active_reaction().is_empty(), "Missing view has no fallback")

	source.hit.emit({"outcome": "miss"})
	_check(reactions.active_reaction().is_empty(), "Miss has no defender reaction")
	_check(_missing.size() == 2, "Miss does not request art")
	source.hit.emit({"outcome": "hit", "defender_id": "monster"})
	_check(reactions.active_reaction().get("defender_id") == "monster", "Monster receives hit")

	var clear_reset := Callable(reactions, "reset")
	reactions.reaction_cleared.connect(clear_reset, CONNECT_ONE_SHOT)
	source.hit.emit(hero)
	_check(reactions.active_reaction().is_empty(), "Reentrant reset prevents replacement")

	var start_reset := func(_value: Dictionary): reactions.reset()
	reactions.reaction_started.connect(start_reset, CONNECT_ONE_SHOT)
	source.hit.emit(hero)
	_check(reactions.active_reaction().is_empty(), "Reentrant reset clears new reaction")

	reactions.unbind_source()
	var count := _started.size()
	source.hit.emit(hero)
	_check(_started.size() == count, "Unbound source cannot trigger reactions")
	_check(not reactions.bind_source(RefCounted.new()), "Invalid source is rejected")
	var replacement := HitSource.new()
	_check(reactions.bind_source(source), "Original source can rebind")
	_check(reactions.bind_source(replacement), "Replacement source can bind")
	source.hit.emit(hero)
	_check(_started.size() == count, "Rebinding disconnects original source")
	replacement.hit.emit(hero)
	_check(_started.size() == count + 1, "Replacement source triggers reaction")
	replacement.cancelled.emit()
	_check(_cleared > 0, "Presentation receives clear notifications")
	reactions.free()
	_check(not replacement.hit.is_connected(Callable(reactions, "on_hit")), "Freed adapter disconnects")

	if _failures.is_empty():
		print("BATTLE_REACTIONS_OK")
		quit(0)
	else:
		quit(1)
