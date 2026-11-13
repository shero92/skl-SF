extends RefCounted
## Transient return marker only. No player-save writes or global project/autoload changes.
static var returning_to_room: bool = false
const DEFINITION := "res://map_factory/worlds/seabreak_coast_01.json"
static func definition() -> Dictionary:
	return JSON.parse_string(FileAccess.get_file_as_string(DEFINITION))
static func rect(values: Array) -> Rect2:
	return Rect2(float(values[0]),float(values[1]),float(values[2]),float(values[3]))
static func point(values: Array) -> Vector2:
	return Vector2(float(values[0]),float(values[1]))
