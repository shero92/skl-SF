extends Node
## A small room-side connection; the owner's main.gd and HeroPlayer remain untouched.
const Travel := preload("res://scenes/world/world_travel.gd")
var definition: Dictionary
var transitioning: bool = false
var travel_enabled: bool = true # headless tests can inspect the trigger without changing scenes

func _ready() -> void:
	definition = Travel.definition()
	call_deferred("restore_return")

func settings() -> Dictionary:
	return definition.room_exit_photo if bool(get_parent().get("photo_mode")) else definition.room_exit_factory

func restore_return() -> void:
	if not Travel.returning_to_room:
		return
	var hero := get_parent().get("player") as HeroPlayer
	if hero == null:
		return
	var destination := Travel.point(settings().return_position)
	if hero.navigation == null or not hero.navigation.footprint_open(destination):
		push_error("Room return position must be walkable")
		return
	hero.position = destination
	hero.velocity = Vector2.ZERO
	Travel.returning_to_room = false

func exit_available() -> bool:
	var host := get_parent()
	var hero := host.get("player") as HeroPlayer
	if hero == null or not hero.movement_enabled or transitioning:
		return false
	var dialogue: Node = host.get("dialogue")
	if dialogue != null and bool(dialogue.get("is_open")):
		return false
	if host.has_method("is_equipment_open") and host.is_equipment_open():
		return false
	return Travel.rect(settings().rect).has_point(hero.position)

func _physics_process(_delta: float) -> void:
	if travel_enabled and exit_available():
		transitioning = true
		get_tree().call_deferred("change_scene_to_file",str(definition.world_scene))
