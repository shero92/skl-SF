extends SceneTree
## Headless verification of the poster character sprites in the game scene.
## Agent: claude (Claude Code); model: Sonnet 5.5.

const Poster = preload("res://scenes/poster_character.gd")
const Npc = preload("res://scenes/room_npc.gd")
const Companion = preload("res://scenes/room_companion.gd")

var _failures: int = 0


func _initialize() -> void:
	call_deferred("_run")


func _check(condition: bool, message: String) -> void:
	if not condition:
		_failures += 1
		printerr("FAIL: " + message)


func _run() -> void:
	for slug in ["cely", "neru", "old_father", "reef_friend", "temple_archer"]:
		_check(Poster.available(slug), "sheet exists: " + slug)
		for direction in Poster.DIRECTIONS:
			var texture := load(Poster.sheet_path(slug, direction)) as Texture2D
			_check(texture != null and texture.get_width() == Poster.FRAME_SIZE * Poster.FRAMES and texture.get_height() == Poster.FRAME_SIZE, "sheet size %s %s" % [slug, direction])
	_check(not Poster.available("nobody"), "unknown character is not available")
	_check(not Poster.available(""), "empty slug is not available")
	_check(Poster.direction_for(Vector2(5, 1)) == "right", "direction right")
	_check(Poster.direction_for(Vector2(-5, 1)) == "left", "direction left")
	_check(Poster.direction_for(Vector2(0, 5)) == "down", "direction down")
	_check(Poster.direction_for(Vector2(0, -5)) == "up", "direction up")
	_check(Poster.direction_for(Vector2.ZERO, "left") == "left", "no movement keeps the facing")

	var npc := Npc.new()
	npc.character = "cely"
	npc.facing = "left"
	root.add_child(npc)
	await process_frame
	var sprite := npc.sprite as Sprite2D
	_check(sprite != null and sprite.hframes == 3, "poster npc has a 3 frame sprite")
	_check(sprite != null and sprite.texture.resource_path == Poster.sheet_path("cely", "left"), "poster npc faces left")
	for _i in 30:
		await process_frame
	_check(sprite != null and sprite.frame >= 0 and sprite.frame < 3, "poster npc animates inside its frames")
	var fallback := Npc.new()
	root.add_child(fallback)
	await process_frame
	_check(fallback.character == "", "npc without a character keeps the legacy fairy")

	var companion := Companion.new()
	var leader := Node2D.new()
	leader.position = Vector2(400, 400)
	root.add_child(leader)
	companion.follow_target = leader
	companion.position = Vector2(100, 400)
	root.add_child(companion)
	await process_frame
	_check(companion.poster_mode, "companion uses the poster character")
	for _i in 10:
		await physics_frame
	_check(companion.facing == "right", "companion faces its walking direction (%s)" % companion.facing)
	if _failures == 0:
		print("POSTER_CHARACTERS_OK")
	quit(0 if _failures == 0 else 1)
