extends Node2D

func _ready() -> void:
    var factory := RoomFactory.new()
    factory.build_room("res://map_factory/rooms/hero_room.json", self)
