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

const MAP_ID := "hero_room_01"
const BATTLE_SCENE := "res://scenes/battle/tactical_battle.tscn"
# Gameplay data (spawn, NPCs, interaction spots) stays in the legacy room JSON.
const GAMEPLAY_PATH := "res://map_factory/rooms/hero_room.json"

func _ready() -> void:
    # Always render the newest Map Factory version through the registry.
    var factory := RoomFactory.new()
    var room := factory.build_latest(MAP_ID, self)
    var entities := RoomFactory.entities_parent(room)
    var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(GAMEPLAY_PATH))
    if typeof(data) != TYPE_DICTIONARY:
        push_error("Cannot load room interactions")
        return
    var spawn: Array = data.get("player_spawn", [770, 720])
    player = HeroPlayer.new()
    player.name = "Hero"
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

    var camera := Camera2D.new()
    camera.position = Vector2(768, 512)
    if room.has_meta("camera"):
        # Per-map view from the Map Factory snapshot: centre in canvas pixels plus zoom.
        var view: Dictionary = room.get_meta("camera")
        camera.position = Vector2(float(view.get("x", 768)), float(view.get("y", 512)))
        camera.zoom = Vector2.ONE * float(view.get("zoom", 1.0))
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
        interactions.append({
            "x": info.get("x", 0), "y": info.get("y", 0),
            "radius": info.get("radius", 100),
            "speaker": info.get("name", "NPC"), "lines": info.get("lines", [])
        })

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
    if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_B:
        get_viewport().set_input_as_handled()
        get_tree().change_scene_to_file(BATTLE_SCENE)  # practice skirmish; Esc there returns to the room
        return
    if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_E:
        var closest: Dictionary = {}
        var best := INF
        for candidate in interactions:
            var pos := Vector2(float(candidate.get("x",0)),float(candidate.get("y",0)))
            var distance := player.position.distance_to(pos)
            if distance <= float(candidate.get("radius", 96)) and distance < best:
                best = distance
                closest = candidate
        if not closest.is_empty():
            dialogue.open_dialogue(String(closest.get("speaker","Hero")),closest.get("lines",[]))
            get_viewport().set_input_as_handled()
