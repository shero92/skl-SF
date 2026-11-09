extends SceneTree
## Headless verification of the draft/fallback detection used by evidence captures.
## Agent: claude (Claude Code); model: Sonnet 5.5.

const Checks = preload("res://tools/capture_checks.gd")

var _failures: int = 0


func _initialize() -> void:
	var catalog := AssetCatalog.new()
	catalog.load_index()
	var factory := AssetFactory.new(catalog)
	var unknown: Node2D = factory.create_asset("ZZ_NOT_REGISTERED")
	_check(Checks.find_drafts(unknown).size() == 2, "unknown asset draws a polygon and a draft label")
	var real: Node2D = factory.create_asset("F01")
	_check(Checks.find_drafts(real).is_empty(), "a registered asset has no draft placeholder")
	var label := Label.new()
	label.text = "Chest (draft)"
	_check(Checks.is_draft_placeholder(label), "draft label is detected")
	var plain := Label.new()
	plain.text = "Hero's Room"
	_check(not Checks.is_draft_placeholder(plain), "ordinary label is accepted")
	var polygon := Polygon2D.new()
	polygon.color = Color.RED
	_check(not Checks.is_draft_placeholder(polygon), "ordinary polygon is accepted")
	var room := Node2D.new()
	room.add_child(unknown)
	_check(Checks.find_drafts(room).size() == 2, "drafts are found inside a room tree")
	if _failures == 0:
		print("CAPTURE_CHECKS_OK")
	quit(0 if _failures == 0 else 1)


func _check(condition: bool, message: String) -> void:
	if not condition:
		_failures += 1
		printerr("FAIL: " + message)
