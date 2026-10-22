extends CanvasLayer
class_name DialogueUI

var is_open: bool = false
var speaker: String = ""
var lines: Array = []
var line_number: int = 0
var container: Control
var speaker_label: Label
var body_label: Label

func _ready() -> void:
    layer = 10
    container = Control.new()
    container.name = "DialogueContainer"
    container.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    container.mouse_filter = Control.MOUSE_FILTER_IGNORE
    add_child(container)

    var backing := TextureRect.new()
    backing.name = "BlueGoldPanel"
    var path := "res://map_factory/parts/ui/UI001_Dialogue_Panel_Background.png"
    if ResourceLoader.exists(path):
        backing.texture = load(path) as Texture2D
    backing.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
    backing.stretch_mode = TextureRect.STRETCH_SCALE
    backing.anchor_left = 0.08
    backing.anchor_right = 0.92
    backing.anchor_top = 1.0
    backing.anchor_bottom = 1.0
    backing.offset_top = -190.0
    backing.offset_bottom = -18.0
    backing.mouse_filter = Control.MOUSE_FILTER_IGNORE
    container.add_child(backing)

    speaker_label = Label.new()
    speaker_label.anchor_left = 0.12
    speaker_label.anchor_right = 0.88
    speaker_label.anchor_top = 1.0
    speaker_label.anchor_bottom = 1.0
    speaker_label.offset_top = -170.0
    speaker_label.offset_bottom = -128.0
    speaker_label.add_theme_font_size_override("font_size", 29)
    speaker_label.add_theme_color_override("font_color", Color("#f9c766"))
    container.add_child(speaker_label)

    body_label = Label.new()
    body_label.anchor_left = 0.12
    body_label.anchor_right = 0.88
    body_label.anchor_top = 1.0
    body_label.anchor_bottom = 1.0
    body_label.offset_top = -124.0
    body_label.offset_bottom = -35.0
    body_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    body_label.add_theme_font_size_override("font_size", 25)
    body_label.add_theme_color_override("font_color", Color("#ffffff"))
    container.add_child(body_label)
    container.visible = false

func open_dialogue(character_name: String, script_lines: Array) -> void:
    if script_lines.is_empty():
        return
    speaker = character_name
    lines = script_lines
    line_number = 0
    is_open = true
    container.visible = true
    _render()

func _render() -> void:
    speaker_label.text = speaker
    body_label.text = String(lines[line_number])

func _input(event: InputEvent) -> void:
    if not is_open:
        return
    if event is InputEventKey and event.pressed and not event.echo:
        if event.keycode in [KEY_E, KEY_ENTER, KEY_SPACE, KEY_ESCAPE]:
            _advance()
            get_viewport().set_input_as_handled()

func _advance() -> void:
    line_number += 1
    if line_number >= lines.size():
        is_open = false
        container.visible = false
    else:
        _render()
