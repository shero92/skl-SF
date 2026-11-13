extends SceneTree
## Saves what the real game window shows (main scene, real camera and window size) to a PNG.
## Usage: godot --path . -s res://tools/capture_game_window.gd -- <output.png> [res://scene.tscn] [property=value ...]
## Agent: claude (Claude Code); model: Fable 5.2.

func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	if args.is_empty():
		push_error("Usage: -- <output.png>")
		quit(1)
		return
	var scene_path := args[1] if args.size() > 1 else String(ProjectSettings.get_setting("application/run/main_scene"))
	var scene: Node = load(scene_path).instantiate()
	for index in range(2, args.size()):  # e.g. battle_path=res://game_factory/battles/hero_room_01.json
		var pair := args[index].split("=", true, 1)
		if pair.size() == 2:
			var typed: Variant = str_to_var(pair[1])  # true, 3, 0.5 keep their type; paths stay text
			scene.set(pair[0], typed if typed != null else pair[1])
	root.add_child(scene)
	for i in 12:
		await process_frame
	await RenderingServer.frame_post_draw
	var image := root.get_texture().get_image()
	var error := image.save_png(args[0])
	print("GAME_WINDOW_CAPTURE %s %dx%d" % ["OK" if error == OK else "FAILED", image.get_width(), image.get_height()])
	quit(0 if error == OK else 1)
