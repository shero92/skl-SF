extends Node2D

var player: HeroPlayer
var dialogue: DialogueUI
var interactions: Array = []
# Equipment: the hero's weapon data lives in WeaponSystem units; the menu opens with the I key.
const WeaponSystemScript = preload("res://scenes/battle/weapon_system.gd")
var weapons
var hero_unit: Dictionary = {}
var save_path: String = HeroSave.DEFAULT_PATH
var equipment_layer: CanvasLayer
var equipment_menu: EquipmentMenu

## Which Map Factory map this scene plays. Set it before the scene starts to play another map; the default is the hero room.
static var next_map_id: String = "hero_room_01"
var map_id: String = ""
const BATTLE_SCENE := "res://scenes/battle/tactical_battle.tscn"
const EDITOR_SCENE := "res://scenes/map_factory_editor.tscn"
# Photo room (owner decision 2026-11-12): the room is the target painting shown unchanged as one backdrop,
# with its own walk squares measured on the painting. F3 switches to the Map Factory pieces and back.
## Any map can be a photo room: put map_factory/photo_rooms/<map_id>.json beside it (see map_factory/PHOTO_ROOMS.md).
const PHOTO_ROOM_DIR := "res://map_factory/photo_rooms/"
static var keep_photo_mode: bool = true  # the choice survives a visit to the editor or a battle
var photo_mode: bool = false
var photo_room: Dictionary = {}
var _map_navigation: NavigationGrid
var _life: PhotoRoomLife
var _mist: Polygon2D
var _companion: Node2D
var _moved: Dictionary = {}  # instance id -> Node2D that a photo-room move relocates
var _room: Node2D
var _photo: Sprite2D
# Gameplay data (spawn, NPCs, interaction spots): map_factory/rooms/<map_id>.json, or the legacy hero_room.json.
const GAMEPLAY_DIR := "res://map_factory/rooms/"

func gameplay_path(id: String) -> String:
    for candidate in [GAMEPLAY_DIR + id + ".json", GAMEPLAY_DIR + "hero_room.json" if id == "hero_room_01" else ""]:
        if candidate != "" and FileAccess.file_exists(candidate):
            return candidate
    return ""

func _ready() -> void:
    # Always render the newest Map Factory version through the registry.
    var factory := RoomFactory.new()
    map_id = next_map_id
    var room := factory.build_latest(map_id, self)
    _room = room
    var entities := RoomFactory.entities_parent(room)
    # A map without a gameplay file is just walkable: no NPCs, no talk spots, the photo room's own spawn.
    var data: Dictionary = {}
    var gameplay := gameplay_path(map_id)
    if gameplay != "":
        var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(gameplay))
        if typeof(parsed) != TYPE_DICTIONARY:
            push_error("Cannot load room interactions: " + gameplay)
            return
        data = parsed
    var photo_file := PHOTO_ROOM_DIR + map_id + ".json"
    var photo_data: Variant = JSON.parse_string(FileAccess.get_file_as_string(photo_file)) if FileAccess.file_exists(photo_file) else null
    if photo_data is Dictionary:
        photo_room = photo_data
    var spawn: Array = data.get("player_spawn", photo_room.get("spawn", [770, 720]))
    player = HeroPlayer.new()
    player.name = "Hero"
    player.use_factory_art = true  # owner 2026-11-13: the hero comes from the character factory frames
    player.position = Vector2(float(spawn[0]), float(spawn[1]))
    entities.add_child(player)
    if room.has_meta("navigation"):
        player.navigation = NavigationGrid.from_navigation(room.get_meta("navigation"), room.global_position)
        if player.navigation != null and not player.navigation.footprint_open(player.position):
            push_warning("Player spawn is outside the walkable navigation area")

    var companion := RoomCompanion.new()
    companion.name = "CrystalCompanion"
    companion.position = player.position + Vector2(55, 30)
    companion.follow_target = player
    entities.add_child(companion)
    _companion = companion

    var camera := Camera2D.new()
    camera.position = Vector2(768, 512)
    if room.has_meta("camera"):
        # Per-map view from the Map Factory snapshot: centre in canvas pixels plus zoom.
        var view: Dictionary = room.get_meta("camera")
        camera.position = Vector2(float(view.get("x", 768)), float(view.get("y", 512)))
        camera.zoom = Vector2.ONE * float(view.get("zoom", 1.0))
    if room.has_meta("background_color"):
        # A zoomed-out camera shows a margin beside the canvas; fill it with the map's own backdrop colour.
        RenderingServer.set_default_clear_color(room.get_meta("background_color"))
    camera.enabled = true
    add_child(camera)

    dialogue = DialogueUI.new()
    add_child(dialogue)
    weapons = WeaponSystemScript.load_default()
    hero_unit = weapons.make_unit("CHAR001", ["WPN_IRON_SWORD"], "WPN_HERO_BASIC_SWORD")
    HeroSave.load_into(weapons, hero_unit, save_path)
    interactions = data.get("interactions", []).duplicate(true)
    for info in data.get("npcs", []):
        var npc := RoomNpc.new()
        npc.display_name = String(info.get("name", "NPC"))
        npc.flip_sprite = bool(info.get("flip_h", false))
        npc.character = String(info.get("character", ""))
        npc.facing = String(info.get("facing", "down"))
        npc.sprite_scale = float(info.get("scale", 0.8))
        npc.position = Vector2(float(info.get("x", 0)), float(info.get("y", 0)))
        entities.add_child(npc)
        _moved[String(info.get("instance_id", ""))] = npc
        interactions.append({
            "id": info.get("instance_id", ""), "npc": true,
            "x": info.get("x", 0), "y": info.get("y", 0),
            "radius": info.get("radius", 100),
            "speaker": info.get("name", "NPC"), "lines": info.get("lines", [])
        })
    _map_navigation = player.navigation
    if photo_mode or keep_photo_mode:
        set_photo_mode(true)

## Shows the room as the painting with its own walk squares (true) or as the Map Factory pieces (false).
func set_photo_mode(on: bool) -> bool:
    if _room == null or photo_room.is_empty():
        return false
    if on and _photo == null:
        var texture := load(String(photo_room.get("image", ""))) as Texture2D
        if texture == null:
            push_warning("Photo room picture not found: " + String(photo_room.get("image", "")))
            return false
        _photo = Sprite2D.new()
        _photo.name = "PhotoBackdrop"
        _photo.texture = texture
        _photo.centered = false
        _photo.z_index = 25  # above the hidden map levels, below characters
        _room.add_child(_photo)
        _life = PhotoRoomLife.new()
        _life.name = "PhotoLife"
        _life.z_index = 26  # over the painting, under characters
        _room.add_child(_life)
        _life.build(texture, photo_room)
        _life.hero = player
        _mist = _life.build_mist(photo_room, texture.get_size())
        if _mist != null:
            _mist.z_index = 200  # over the characters too
            _room.add_child(_mist)
    photo_mode = on
    keep_photo_mode = on
    var entities := RoomFactory.entities_parent(_room)
    for child in _room.get_children():
        if child == _photo or child == _life or child == _mist:
            child.visible = on
        elif child.is_ancestor_of(entities):
            for inner in child.get_children():
                if inner != entities and inner is CanvasItem:
                    inner.visible = not on
        elif child != entities and child is CanvasItem:
            child.visible = not on
    # Furniture of the tile room must not block the painting: its collision shapes rest while the photo shows.
    for shape in _room.find_children("*", "CollisionShape2D", true, false):
        if not entities.is_ancestor_of(shape):
            shape.set_deferred("disabled", on)
    if player != null:
        # Shining Force movement in the painted room: one square per press. The map room keeps free walking.
        player.grid_step = float(photo_room.get("hero_step", 0)) if on else 0.0
        var shift: Array = photo_room.get("hero_step_offset", [0, 0])
        player.grid_offset = Vector2(float(shift[0]), float(shift[1]))
        # The painting is detailed, so the hero is drawn from the high-resolution source frames at a Shining Force
        # size (about two floor tiles tall). Without those local files the 96 px factory frames stay.
        if on and player.source_art == null and float(photo_room.get("hero_height", 0)) > 0.0:
            player.source_art = HeroSourceArt.new()
            player.source_art.name = "SourceArt"
            player.source_art.figure_height = float(photo_room["hero_height"])
            player.source_art.view_squash = float(photo_room.get("hero_view_squash", 1.0))
            player.add_child(player.source_art)
        elif not on and player.source_art != null:
            player.source_art.queue_free()
            player.source_art = null
    if player != null:
        player.navigation = NavigationGrid.from_navigation(photo_room.get("navigation", {}), _room.global_position) if on else _map_navigation
        if on and player.grid_step > 0.0:
            player.snap_to_grid()  # after the painted room's walk squares are in place
    # A hero-only photo room shows no NPCs and no companion; their talk spots rest too.
    var alone := on and bool(photo_room.get("hero_only", false))
    if _companion != null:
        _companion.visible = not alone
    for id: String in _moved:
        _moved[id].visible = not alone
    # NPCs and interaction spots that sit on painted furniture or plants move to a free square.
    var moves: Dictionary = photo_room.get("moves", {})
    for spot: Dictionary in interactions:
        var id := String(spot.get("id", ""))
        if not moves.has(id):
            continue
        if not spot.has("map_x"):
            spot["map_x"] = spot.get("x", 0)
            spot["map_y"] = spot.get("y", 0)
        if not spot.has("map_radius"):
            spot["map_radius"] = spot.get("radius", 96)
        spot["x"] = moves[id][0] if on else spot["map_x"]
        spot["y"] = moves[id][1] if on else spot["map_y"]
        spot["radius"] = moves[id][2] if on and moves[id].size() > 2 else spot["map_radius"]  # a third number widens the reach
        if _moved.has(id):
            _moved[id].position = Vector2(float(spot["x"]), float(spot["y"]))
    return true


func _physics_process(_delta: float) -> void:
    if player != null and dialogue != null:
        player.movement_enabled = not dialogue.is_open and not is_equipment_open()


func is_equipment_open() -> bool:
    return equipment_layer != null and equipment_layer.visible


func toggle_equipment() -> void:
    if equipment_layer == null:
        equipment_layer = CanvasLayer.new()
        equipment_layer.name = "EquipmentLayer"
        equipment_layer.layer = 11
        add_child(equipment_layer)
        equipment_menu = EquipmentMenu.new()
        equipment_menu.position = Vector2(24, 96)
        equipment_menu.closed.connect(func(): equipment_layer.visible = false)
        equipment_menu.changed.connect(func(unit): HeroSave.save(unit, save_path))
        equipment_layer.add_child(equipment_menu)
        equipment_layer.visible = false
    if equipment_layer.visible:
        equipment_layer.visible = false
        return
    equipment_menu.setup(weapons, hero_unit)
    equipment_layer.visible = true

func _unhandled_input(event: InputEvent) -> void:
    if player == null or dialogue == null or dialogue.is_open:
        return
    if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_I:
        toggle_equipment()
        get_viewport().set_input_as_handled()
        return
    if is_equipment_open():
        return # no interactions while the menu is open
    if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_F2:
        get_viewport().set_input_as_handled()
        get_tree().change_scene_to_file(EDITOR_SCENE)  # hands-on room editor; Esc there returns to the room
        return
    if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_F3:
        get_viewport().set_input_as_handled()
        set_photo_mode(not photo_mode)
        return
    if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_B:
        get_viewport().set_input_as_handled()
        get_tree().change_scene_to_file(BATTLE_SCENE)  # practice skirmish; Esc there returns to the room
        return
    if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_E:
        var closest: Dictionary = {}
        var best := INF
        for candidate in interactions:
            if photo_mode and bool(photo_room.get("hero_only", false)) and bool(candidate.get("npc", false)):
                continue
            var pos := Vector2(float(candidate.get("x",0)),float(candidate.get("y",0)))
            var distance := player.position.distance_to(pos)
            if distance <= float(candidate.get("radius", 96)) and distance < best:
                best = distance
                closest = candidate
        if not closest.is_empty():
            dialogue.open_dialogue(String(closest.get("speaker","Hero")),closest.get("lines",[]))
            get_viewport().set_input_as_handled()
