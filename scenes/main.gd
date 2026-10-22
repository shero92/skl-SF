extends Node2D

var player: HeroPlayer
var dialogue: DialogueUI
var interactions: Array = []

func _ready() -> void:
    var map_path := "res://map_factory/rooms/hero_room.json"
    var factory := RoomFactory.new()
    var room := factory.build_room(map_path, self)
    var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(map_path))
    if typeof(data) != TYPE_DICTIONARY:
        push_error("Cannot load room interactions")
        return
    var spawn: Array = data.get("player_spawn", [770, 720])
    player = HeroPlayer.new()
    player.name = "HeroGameplayProxy"
    player.position = Vector2(float(spawn[0]), float(spawn[1]))
    room.get_node("Entities").add_child(player)

    var camera := Camera2D.new()
    camera.position = Vector2(768, 512)
    camera.enabled = true
    add_child(camera)

    dialogue = DialogueUI.new()
    add_child(dialogue)
    interactions = data.get("interactions", []).duplicate(true)
    for info in data.get("npcs", []):
        var npc := RoomNpc.new()
        npc.display_name = String(info.get("name", "NPC"))
        npc.position = Vector2(float(info.get("x", 0)), float(info.get("y", 0)))
        room.get_node("Entities").add_child(npc)
        interactions.append({
            "x": info.get("x", 0), "y": info.get("y", 0),
            "radius": info.get("radius", 100),
            "speaker": info.get("name", "NPC"), "lines": info.get("lines", [])
        })

func _physics_process(_delta: float) -> void:
    if player != null and dialogue != null:
        player.movement_enabled = not dialogue.is_open

func _unhandled_input(event: InputEvent) -> void:
    if player == null or dialogue == null or dialogue.is_open:
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
