extends CanvasLayer
class_name DialogueUI

## Decorative room label stays visible; conversation panel is toggled separately.
## Native pixel-art corners are protected by NinePatchRect margins.
var is_open: bool = false
var speaker: String = ""
var lines: Array = []
var line_number: int = 0
var container: Control
var speaker_label: Label
var body_label: Label
var portrait: TextureRect

func _ready() -> void:
    layer = 10
    _make_room_title()
    container = Control.new()
    container.name = "DialogueContainer"
    container.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    container.mouse_filter = Control.MOUSE_FILTER_IGNORE
    add_child(container)

    var backing := NinePatchRect.new()
    backing.name = "BlueGoldPanel"
    backing.patch_margin_left = 35
    backing.patch_margin_right = 35
    backing.patch_margin_top = 34
    backing.patch_margin_bottom = 32
    var path := "res://map_factory/parts/ui/UI001_Dialogue_Panel_Background.png"
    if ResourceLoader.exists(path):
        backing.texture = load(path) as Texture2D
    backing.anchor_left = 0.08
    backing.anchor_right = 0.92
    backing.anchor_top = 1.0
    backing.anchor_bottom = 1.0
    backing.offset_top = -190.0
    backing.offset_bottom = -18.0
    backing.mouse_filter = Control.MOUSE_FILTER_IGNORE
    container.add_child(backing)

    portrait = TextureRect.new()
    portrait.name = "DialoguePortrait"
    portrait.anchor_left = 0.09
    portrait.anchor_right = 0.09
    portrait.anchor_top = 1.0
    portrait.anchor_bottom = 1.0
    portrait.offset_left = 12
    portrait.offset_right = 148
    portrait.offset_top = -177
    portrait.offset_bottom = -30
    portrait.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
    portrait.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
    portrait.mouse_filter = Control.MOUSE_FILTER_IGNORE
    container.add_child(portrait)

    var frame := TextureRect.new()
    frame.name = "GoldPortraitFrame"
    var frame_path := "res://map_factory/parts/ui/UI004_Dialogue_Portrait_Frame.png"
    if ResourceLoader.exists(frame_path):
        frame.texture = load(frame_path) as Texture2D
    frame.anchor_left = 0.09
    frame.anchor_right = 0.09
    frame.anchor_top = 1.0
    frame.anchor_bottom = 1.0
    frame.offset_left = 8
    frame.offset_right = 152
    frame.offset_top = -182
    frame.offset_bottom = -25
    frame.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
    frame.stretch_mode = TextureRect.STRETCH_SCALE
    frame.mouse_filter = Control.MOUSE_FILTER_IGNORE
    container.add_child(frame)

    speaker_label = Label.new()
    speaker_label.anchor_left = 0.21
    speaker_label.anchor_right = 0.88
    speaker_label.anchor_top = 1.0
    speaker_label.anchor_bottom = 1.0
    speaker_label.offset_top = -169.0
    speaker_label.offset_bottom = -126.0
    speaker_label.add_theme_font_size_override("font_size", 27)
    speaker_label.add_theme_color_override("font_color", Color("#f9c766"))
    container.add_child(speaker_label)

    body_label = Label.new()
    body_label.anchor_left = 0.21
    body_label.anchor_right = 0.88
    body_label.anchor_top = 1.0
    body_label.anchor_bottom = 1.0
    body_label.offset_top = -123.0
    body_label.offset_bottom = -35.0
    body_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    body_label.add_theme_font_size_override("font_size", 24)
    body_label.add_theme_color_override("font_color", Color.WHITE)
    container.add_child(body_label)

    var next_arrow := TextureRect.new()
    next_arrow.name = "NextArrow"
    var next_path := "res://map_factory/parts/ui/UI005_Dialogue_Next_Arrow.png"
    if ResourceLoader.exists(next_path):
        next_arrow.texture = load(next_path) as Texture2D
    next_arrow.anchor_left = 0.86
    next_arrow.anchor_right = 0.86
    next_arrow.anchor_top = 1.0
    next_arrow.anchor_bottom = 1.0
    next_arrow.offset_left = 0
    next_arrow.offset_right = 52
    next_arrow.offset_top = -70
    next_arrow.offset_bottom = -18
    next_arrow.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
    next_arrow.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
    next_arrow.mouse_filter = Control.MOUSE_FILTER_IGNORE
    container.add_child(next_arrow)
    container.visible = false

func _make_room_title() -> void:
    var header := Control.new()
    header.name = "RoomTitle"
    header.position = Vector2(18, 16)
    header.size = Vector2(360, 72)
    header.mouse_filter = Control.MOUSE_FILTER_IGNORE
    add_child(header)
    var title_frame := NinePatchRect.new()
    title_frame.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    title_frame.patch_margin_left = 36
    title_frame.patch_margin_right = 36
    title_frame.patch_margin_top = 20
    title_frame.patch_margin_bottom = 20
    var path := "res://map_factory/parts/ui/UI011_Room_Title_Panel.png"
    if ResourceLoader.exists(path):
        title_frame.texture = load(path) as Texture2D
    title_frame.mouse_filter = Control.MOUSE_FILTER_IGNORE
    header.add_child(title_frame)
    var caption := Label.new()
    caption.text = "Hero's Room"
    caption.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    caption.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    caption.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
    caption.add_theme_font_size_override("font_size", 34)
    caption.add_theme_color_override("font_color", Color("#fff8e8"))
    caption.add_theme_color_override("font_shadow_color", Color("#07142e"))
    caption.add_theme_constant_override("shadow_offset_x", 2)
    caption.add_theme_constant_override("shadow_offset_y", 2)
    caption.mouse_filter = Control.MOUSE_FILTER_IGNORE
    header.add_child(caption)

func open_dialogue(character_name: String, script_lines: Array) -> void:
    if script_lines.is_empty():
        return
    speaker = character_name
    lines = script_lines
    line_number = 0
    is_open = true
    container.visible = true
    var is_fairy := "guardian" in speaker.to_lower() or "fairy" in speaker.to_lower()
    var portrait_path := "res://map_factory/parts/ui/UI008_Fairy_Portrait.png" if is_fairy else "res://map_factory/parts/ui/UI007_Hero_Portrait.png"
    portrait.texture = load(portrait_path) as Texture2D if ResourceLoader.exists(portrait_path) else null
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
