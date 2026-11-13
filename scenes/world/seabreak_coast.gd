extends Node2D
## Large environment scene assembled from reusable Map Factory blocks and the existing hero.
const Travel := preload("res://scenes/world/world_travel.gd")
var definition: Dictionary
var room: Node2D
var player: HeroPlayer
var camera: Camera2D
var transitioning: bool = false
var travel_enabled: bool = true

func _ready() -> void:
	definition = Travel.definition()
	room = RoomFactory.new().build_latest(str(definition.map_id),self)
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	# AssetFactory's HD default is linear; the exterior keeps every sprite crisp at1x.
	for node: Node in room.find_children("*","Sprite2D",true,false):
		node.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	player = HeroPlayer.new()
	player.name = "Hero"
	player.position = Travel.point(definition.player_spawn)
	player.navigation = NavigationGrid.from_navigation(room.get_meta("navigation"),room.global_position)
	RoomFactory.entities_parent(room).add_child(player)
	assert(player.navigation != null and player.navigation.footprint_open(player.position))
	camera = Camera2D.new()
	camera.name = "WorldCamera"
	camera.position_smoothing_enabled = true
	camera.position_smoothing_speed = 5.0
	camera.limit_left = int(definition.camera_limits[0])
	camera.limit_top = int(definition.camera_limits[1])
	camera.limit_right = int(definition.camera_limits[2])
	camera.limit_bottom = int(definition.camera_limits[3])
	player.add_child(camera)
	camera.make_current()
	RenderingServer.set_default_clear_color(Color("238ac6"))

func return_available() -> bool:
	return player != null and not transitioning and player.movement_enabled and Travel.rect(definition.world_return_rect).has_point(player.position)

func _physics_process(_delta: float) -> void:
	if travel_enabled and return_available():
		transitioning = true
		Travel.returning_to_room = true
		get_tree().call_deferred("change_scene_to_file",str(definition.room_scene))
