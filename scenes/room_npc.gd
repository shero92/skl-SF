extends Node2D
class_name RoomNpc

@export var display_name: String = "NPC (placeholder)"
@export var tint: Color = Color("#469a6b")

func _ready() -> void:
    queue_redraw()

func _draw() -> void:
    # Only for gameplay testing: NPC art is still planned in the catalog.
    draw_circle(Vector2(0,-13),18.0,tint)
    draw_circle(Vector2(0,-31),11.0,Color("#eed2a0"))
    draw_circle(Vector2(-4,-32),1.5,Color("#19354f"))
    draw_circle(Vector2(4,-32),1.5,Color("#19354f"))
