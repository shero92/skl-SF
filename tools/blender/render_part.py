"""Render one piece spec inside Blender:
    blender -b --factory-startup --python tools/blender/render_part.py -- <spec.json> <out_dir>

Writes <name>.png (color, supersampled master), <name>_shadow.png and <name>.json (frame, anchors).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import builders  # noqa: E402
import lib  # noqa: E402


def main():
    argv = sys.argv[sys.argv.index("--") + 1:]
    spec_path, out_dir = argv[0], argv[1]
    spec = json.load(open(spec_path, encoding="utf-8"))
    here = os.path.dirname(os.path.abspath(__file__))
    proj = json.load(open(os.path.join(here, "projection.json"), encoding="utf-8"))
    proj.update(spec.get("projection", {}))
    os.makedirs(out_dir, exist_ok=True)
    results = []
    for out in spec["outputs"]:
        scene = lib.reset_scene()
        lib.configure_render(scene, proj)
        lib.add_world(scene, proj)
        lib.add_sun(proj)
        build = builders.BUILDERS[out.get("builder", spec["builder"])]
        piece = {**spec, "params": {**spec.get("params", {}), **out.get("params", {})}}
        objects, anchors = build(piece, out.get("facing", "south"))
        st = proj.get("shadow_padding_tiles", 1.0) if out.get("shadow", True) else 0.0
        frame = lib.frame_camera(objects, proj, extra_tiles=(0.1, st, st, 0.1))
        color = os.path.join(out_dir, out["name"] + ".png")
        shadow = os.path.join(out_dir, out["name"] + "_shadow.png")
        if out.get("shadow", True):
            # A builder may limit the shadow-receiving ground (piece["shadow_region"], tiles), e.g. to the floor.
            lib.render_color_and_shadow(objects, color, shadow, piece.get("shadow_region"))
        else:
            lib.render(color)
            shadow = None
        meta = {"name": out["name"], "facing": out.get("facing", "south"), "builder": out.get("builder", spec["builder"]),
                "params": piece["params"], "frame_px": frame["size"], "supersample": frame["supersample"],
                "anchors_px": {k: lib.to_pixels(frame, v, proj) for k, v in anchors.items()},
                "color": os.path.basename(color), "shadow": os.path.basename(shadow) if shadow else None,
                "projection": {k: proj[k] for k in ("tile_px", "camera_elevation_deg", "sun", "engine", "samples")}}
        json.dump(meta, open(os.path.join(out_dir, out["name"] + ".json"), "w", encoding="utf-8", newline="\n"), indent=2)
        results.append(meta)
        print("RENDERED", out["name"], frame["size"])
    print("DONE", len(results))


if __name__ == "__main__":
    main()
