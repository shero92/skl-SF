extends Node2D
## Native-size painted square-block terrain with the room's existing actor, view and travel marker.
const Travel := preload("res://scenes/world/world_travel.gd")
const WORLD := "res://map_factory/painted_worlds/hidden_island/v001/world.json"
var definition: Dictionary
var current_zone: String
var player: HeroPlayer
var camera: Camera2D
var background: Sprite2D
var travel_enabled: bool = true
var transitioning: bool = false
var room_transition_pending: bool = false

func _ready() -> void:
	definition = JSON.parse_string(FileAccess.get_file_as_string(WORLD))
	background = Sprite2D.new()
	background.name = "PaintedGround"
	background.centered = false
	background.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	add_child(background)
	player = HeroPlayer.new()
	player.name = "Hero"
	player.use_factory_art = true
	add_child(player)
	if player.factory_art != null:
		player.factory_art.scale = Vector2.ONE*float(definition.hero_scale)
		player.factory_art.position = -Vector2(float(HeroPlayer._factory_anchor[0]),float(HeroPlayer._factory_anchor[1]))*float(definition.hero_scale)
		player.factory_art.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	# Respect the owner's optional high-resolution renderer when that separate actor work is present.
	var source_property := false
	for property: Dictionary in player.get_property_list():
		if str(property.name)=="source_art":source_property = true
	if source_property and ResourceLoader.exists("res://scenes/hero_source_art.gd"):
		var source: Node2D = load("res://scenes/hero_source_art.gd").new()
		source.set("figure_height",float(definition.hero_height_if_supported))
		player.set("source_art",source)
		player.add_child(source)
	camera = Camera2D.new()
	camera.name = "RoomMatchedCamera"
	camera.zoom = Vector2.ONE*float(definition.camera_zoom)
	add_child(camera)
	camera.make_current()
	RenderingServer.set_default_clear_color(Color("087ccc"))
	enter_zone(str(definition.default_zone))

func enter_zone(zone_id: String, arrival: Array = []) -> void:
	assert(definition.zones.has(zone_id))
	current_zone = zone_id
	var zone: Dictionary = definition.zones[zone_id]
	background.texture = load(str(zone.background)) as Texture2D
	assert(background.texture != null)
	player.navigation = NavigationGrid.from_navigation(zone.navigation)
	player.position = Travel.point(zone.spawn if arrival.is_empty() else arrival)
	player.velocity = Vector2.ZERO
	assert(player.navigation.footprint_open(player.position))
	camera.position = Travel.point(zone.canvas_size)*0.5
	camera.reset_smoothing()
	transitioning = false

func available_portal() -> Dictionary:
	if player==null or not player.movement_enabled or transitioning:return {}
	for portal: Dictionary in definition.zones[current_zone].portals:
		if Travel.rect(portal.rect).has_point(player.position):return portal
	return {}

func _physics_process(_delta: float) -> void:
	if not travel_enabled:return
	var portal := available_portal()
	if portal.is_empty():return
	transitioning = true
	if str(portal.target)=="room":
		room_transition_pending = true
		Travel.returning_to_room = true
		get_tree().call_deferred("change_scene_to_file",str(definition.room_scene))
	else:
		call_deferred("enter_zone",str(portal.target),portal.arrival)
