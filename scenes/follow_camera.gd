extends Camera2D
class_name FollowCamera
## A camera that moves with the characters: it eases toward the hero, leads a little in the direction he walks,
## zooms in while he talks, and never shows anything outside the map. With `follow` off it is the plain fixed
## camera of the map (what F5 showed before). `toggle_overview()` switches to the whole map and back.
## Used by scenes/main.gd; settings come from the map's photo room file ("camera"), see map_factory/PHOTO_ROOMS.md.
## Agent: claude (Claude Code); model: Sonnet 5.5.

var target: Node2D
var follow: bool = false
## Where the camera looks relative to the hero's feet (up toward his chest).
var focus_offset: Vector2 = Vector2(0, -56)
var base_zoom: float = 1.15
var talk_zoom: float = 1.5
var lead: float = 48.0          # pixels ahead of him while he moves
var smoothing: float = 5.0      # higher catches up faster
var zoom_smoothing: float = 4.0
var bounds: Rect2 = Rect2(0, 0, 1536, 1024)
var overview: bool = false
var talking: bool = false
var fixed_position: Vector2 = Vector2(768, 512)
var fixed_zoom: float = 1.0

var _lead_now: Vector2 = Vector2.ZERO


## Settings from the photo room file, e.g. {"follow": true, "zoom": 1.15, "talk_zoom": 1.5, "lead": 48, "smoothing": 5}.
func configure(settings: Dictionary, map_bounds: Rect2) -> void:
	bounds = map_bounds
	follow = bool(settings.get("follow", false))
	base_zoom = float(settings.get("zoom", base_zoom))
	talk_zoom = float(settings.get("talk_zoom", talk_zoom))
	lead = float(settings.get("lead", lead))
	smoothing = float(settings.get("smoothing", smoothing))
	var offset: Array = settings.get("focus_offset", [focus_offset.x, focus_offset.y])
	focus_offset = Vector2(float(offset[0]), float(offset[1]))
	snap()


func toggle_overview() -> void:
	overview = not overview


## Whole-map zoom: the largest zoom at which the map still fills the view height (what the fixed camera showed).
func overview_zoom() -> float:
	var view := get_viewport_rect().size
	return minf(view.x / bounds.size.x, view.y / bounds.size.y)


func desired_zoom() -> float:
	if not follow:
		return fixed_zoom
	if overview:
		return overview_zoom()
	return talk_zoom if talking else base_zoom


## The camera centre the camera is steering toward, kept inside the map for the given zoom.
func desired_position(zoom_level: float) -> Vector2:
	if not follow:
		return fixed_position
	if overview or target == null:
		return bounds.get_center()
	var centre := target.global_position + focus_offset + _lead_now
	return clamp_to_bounds(centre, zoom_level)


func clamp_to_bounds(centre: Vector2, zoom_level: float) -> Vector2:
	var half := get_viewport_rect().size / (2.0 * zoom_level)
	var low := bounds.position + half
	var high := bounds.end - half
	# A view larger than the map in one direction simply centres on the map in that direction.
	return Vector2(
		bounds.get_center().x if low.x > high.x else clampf(centre.x, low.x, high.x),
		bounds.get_center().y if low.y > high.y else clampf(centre.y, low.y, high.y))


## Puts the camera exactly where it wants to be (scene start, map change).
func snap() -> void:
	_lead_now = Vector2.ZERO
	var level := desired_zoom()
	zoom = Vector2.ONE * level
	global_position = desired_position(level)
	reset_smoothing()


func _process(delta: float) -> void:
	if not follow:
		return
	var moving := false
	if target != null and target.has_method("is_moving"):
		moving = target.is_moving()
	var ahead := Vector2.ZERO
	if moving and target != null:
		ahead = (target.get("facing") as Vector2) * lead
	_lead_now = _lead_now.lerp(ahead, 1.0 - exp(-3.0 * delta))
	var level := lerpf(zoom.x, desired_zoom(), 1.0 - exp(-zoom_smoothing * delta))
	zoom = Vector2.ONE * level
	global_position = global_position.lerp(desired_position(level), 1.0 - exp(-smoothing * delta))
