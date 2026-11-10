extends SceneTree
## Headless verification of NavigationGrid and its wiring (HeroPlayer, RoomFactory meta, game factory actor).
## Agent: claude (Claude Code); model: Sonnet 5.5.

var _failures: int = 0
var _player: HeroPlayer


func _check(condition: bool, message: String) -> void:
	if not condition:
		_failures += 1
		printerr("FAIL: " + message)


func _initialize() -> void:
	_test_synthetic()
	_test_real_room()
	# Nodes added during _initialize get _ready on the first frame; wire the player after it.
	_player = HeroPlayer.new()
	root.add_child(_player)
	process_frame.connect(_finish, CONNECT_ONE_SHOT)


func _finish() -> void:
	_test_player_wiring()
	if _failures == 0:
		print("NAVIGATION_GRID_OK")
	quit(0 if _failures == 0 else 1)


func _nav() -> Dictionary:
	return {"schema_version": 1, "origin": [100, 100], "cell_size": 64, "grid_size": [6, 4],
		"default": {"walk": false, "fly": false, "swim": false},
		"regions": [
			{"id": "floor", "rect": [1, 1, 3, 2], "allow": ["walk", "fly"]},
			{"id": "pool", "rect": [4, 1, 1, 2], "allow": ["swim"]}],
		"obstacles": [], "links": [{"id": "door", "from": [0, 1], "to": [1, 1], "modes": ["walk"]}]}


func _test_synthetic() -> void:
	_check(NavigationGrid.from_navigation({}) == null, "empty block gives no grid")
	_check(NavigationGrid.from_navigation({"schema_version": 2}) == null, "unknown schema gives no grid")
	var grid := NavigationGrid.from_navigation(_nav())
	_check(grid.world_to_cell(Vector2(100, 100)) == Vector2i(0, 0), "origin cell")
	_check(grid.world_to_cell(Vector2(99, 100)) == Vector2i(-1, 0), "left of origin")
	_check(grid.is_cell_open(Vector2i(1, 1)) and grid.is_cell_open(Vector2i(3, 2)), "region cells open")
	_check(not grid.is_cell_open(Vector2i(4, 1)), "swim region is not walkable")
	_check(grid.is_cell_open(Vector2i(4, 1), "swim") and not grid.is_cell_open(Vector2i(2, 1), "swim"), "modes stay separate")
	_check(grid.is_cell_open(Vector2i(0, 1)), "link endpoint opens its cell for its modes")
	_check(not grid.is_cell_open(Vector2i(0, 2)), "unknown cell is closed by default")
	_check(not grid.is_cell_open(Vector2i(-3, 0)) and not grid.is_cell_open(Vector2i(50, 50)), "outside the map is closed")
	var inside := grid.cell_center(Vector2i(2, 1))
	_check(grid.footprint_open(inside), "centre of an open cell")
	# Straight into a wall: stops. Diagonal into a wall: slides along it instead of passing through.
	var edge := Vector2(grid.cell_center(Vector2i(3, 2)).x + 20.0, grid.cell_center(Vector2i(3, 2)).y)
	var blocked := grid.allowed_motion(edge, Vector2(30, 0))
	_check(blocked == Vector2.ZERO, "straight into closed cell is blocked, got %s" % str(blocked))
	var bottom := Vector2(grid.cell_center(Vector2i(2, 2)).x, grid.origin.y + 3.0 * 64.0 - 6.0)
	var slide := grid.allowed_motion(bottom, Vector2(6, 6))
	_check(slide.y == 0.0 and slide.x == 6.0, "diagonal slides along the edge, got %s" % str(slide))
	var position := inside
	for step in 400:
		position += grid.allowed_motion(position, Vector2(3, 3).normalized() * 4.0)
		_check(grid.footprint_open(position), "feet never leave open cells")
	_check(position.x > inside.x, "kept moving along the open edge")
	var open_all := NavigationGrid.from_navigation(_nav())
	_check(open_all.allowed_motion(inside, Vector2(1, 0)) == Vector2(1, 0), "free motion is untouched")


func _test_real_room() -> void:
	var holder := Node2D.new()
	root.add_child(holder)
	var room := RoomFactory.new().build_latest("hero_room_01", holder)
	_check(room.has_meta("navigation"), "latest hero room exposes navigation")
	if not room.has_meta("navigation"):
		return
	var grid := NavigationGrid.from_navigation(room.get_meta("navigation"), room.global_position)
	_check(grid != null, "hero room navigation parses")
	var gameplay: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://map_factory/rooms/hero_room.json"))
	var spawn: Array = gameplay.get("player_spawn", [770, 720])
	_check(grid.footprint_open(Vector2(float(spawn[0]), float(spawn[1]))), "player spawn is on walkable ground")
	_check(not grid.point_open(Vector2(60, 700)), "open water west of the terrace is closed")
	_check(not grid.point_open(Vector2(770, 150)), "the sea behind the arch is closed")
	var stairs := grid.cell_center(Vector2i(8, 9))
	_check(grid.point_open(stairs), "stairs cell is walkable")
	# Walking south from the spawn must end on the stairs or terrace, never in the sea.
	var position := Vector2(float(spawn[0]), float(spawn[1]))
	for step in 600:
		position += grid.allowed_motion(position, Vector2(0, 5))
	_check(grid.footprint_open(position) and position.y < grid.origin.y + 10.0 * 64.0, "south walk stops inside the area")
	holder.free()
	var courtyard := Node2D.new()
	root.add_child(courtyard)
	var old_room := RoomFactory.new().build_room("res://map_factory/maps/courtyard_demo_01/latest.json", courtyard)
	_check(old_room != null, "older map still builds")
	if old_room != null and not old_room.has_meta("navigation"):
		_check(NavigationGrid.from_navigation(null) == null, "map without navigation stays unrestricted")
	courtyard.free()


func _test_player_wiring() -> void:
	var player := _player
	_check(player.art != null, "player is ready after the first frame")
	player.navigation = NavigationGrid.from_navigation(_nav())
	player.position = player.navigation.cell_center(Vector2i(3, 2))
	player.movement_enabled = false
	player._physics_process(0.016)
	_check(player.velocity == Vector2.ZERO, "no movement while a dialogue disables it")
	_check(player.navigation.footprint_open(player.position), "player stays on open ground")
	player.free()
	var actor_script: Script = load("res://scenes/game_factory_actor.gd")
	_check(actor_script != null and "navigation" in actor_script.new(), "game factory actor uses the shared validator")
