# Art pipeline

1. Generate one clean, uncropped asset PNG per catalog ID, using reference for style only.
2. Remove backgrounds and embedded labels; verify true alpha transparency.
3. Inspect outline and pixel scale; repair seams for tileable floors.
4. Record true pixel_size, origin, collision footprint and shadow metadata.
5. Set status to `ready` only after import and scene test in Godot.
6. Reuse IDs in room JSON layouts across maps.

No generated production PNG sprites are committed in this initial architecture scaffold.
