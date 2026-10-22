extends CharacterBody2D
class_name HeroPlayer

## Temporary gameplay proxy. Replace with CH001-CH008 high-quality sprites
## once character animation frames have been imported and approved.
@export var move_speed: float = 210.0
var movement_enabled: bool = true
var facing: Vector2 = Vector2.DOWN

func _ready() -> void:
    var collision := CollisionShape2D.new()
    var capsule := CapsuleShape2D.new()
    capsule.radius = 12.0
    capsule.height = 30.0
    collision.position = Vector2(0, -15)
    collision.shape = capsule
    add_child(collision)
    queue_redraw()

func _physics_process(_delta: float) -> void:
    var direction := Vector2.ZERO
    if movement_enabled:
        if Input.is_key_pressed(KEY_A) or Input.is_action_pressed("ui_left"):
            direction.x -= 1.0
        if Input.is_key_pressed(KEY_D) or Input.is_action_pressed("ui_right"):
            direction.x += 1.0
        if Input.is_key_pressed(KEY_W) or Input.is_action_pressed("ui_up"):
            direction.y -= 1.0
        if Input.is_key_pressed(KEY_S) or Input.is_action_pressed("ui_down"):
            direction.y += 1.0
    if direction.length_squared() > 0:
        facing = direction.normalized()
    velocity = direction.normalized() * move_speed
    move_and_slide()

func _draw() -> void:
    # Visibly temporary blue/gold prototype marker; NOT approved character art.
    draw_circle(Vector2(0, -11), 17.0, Color("#122d71"))
    draw_circle(Vector2(0, -21), 10.0, Color("#f4bf79"))
    draw_polygon(PackedVector2Array([Vector2(-19,-33),Vector2(0,-49),Vector2(19,-33),Vector2(8,-29),Vector2(-8,-29)]),
        PackedColorArray([Color("#76451f"),Color("#9b572a"),Color("#76451f"),Color("#9b572a"),Color("#76451f")]))
    draw_line(Vector2(-13, -2), Vector2(13, -2), Color("#f5bd49"), 4.0)
