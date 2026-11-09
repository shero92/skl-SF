extends RefCounted
class_name PosterCharacter
## Map sprites cut from the approved character design posters (tools/extract_poster_sprites.py).
## Each direction is a 3-frame horizontal sheet of 144x144 frames, feet 6 px above the bottom edge.
## Agent: claude (Claude Code); model: Sonnet 5.5.

const FRAME_SIZE := 144
const FRAMES := 3
const FOOT_OFFSET := Vector2(-72, -138)
const DIRECTIONS := ["down", "left", "right", "up"]


static func sheet_path(slug: String, direction: String) -> String:
	return "res://assets/characters/%s/map/%s_map_%s.png" % [slug, slug, direction]


static func available(slug: String) -> bool:
	return slug != "" and ResourceLoader.exists(sheet_path(slug, "down"))


static func direction_for(vector: Vector2, fallback: String = "down") -> String:
	if vector.length() < 0.001:
		return fallback
	if absf(vector.x) > absf(vector.y):
		return "right" if vector.x > 0.0 else "left"
	return "down" if vector.y > 0.0 else "up"


## Applies a direction sheet to a Sprite2D (feet anchored at the node origin).
static func apply(sprite: Sprite2D, slug: String, direction: String, sprite_scale: float) -> bool:
	var path := sheet_path(slug, direction)
	if not ResourceLoader.exists(path):
		return false
	sprite.texture = load(path) as Texture2D
	sprite.hframes = FRAMES
	sprite.centered = false
	sprite.scale = Vector2.ONE * sprite_scale
	sprite.position = FOOT_OFFSET * sprite_scale
	return true
