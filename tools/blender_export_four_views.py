#!/usr/bin/env python3
"""Render four independent 3/4-view PNG candidates from a Blender collection.

Run inside Blender with an authored orthographic camera and lit .blend scene.
Outputs are candidates only: no catalog IDs or artistic QA are asserted.
"""
import argparse
import json
import math
from pathlib import Path
import re
import sys

import bpy
from mathutils import Matrix, Vector

FACING_ANGLES = (("north", 0), ("east", 90), ("south", 180), ("west", 270))
GEOMETRY_TYPES = {"MESH", "CURVE", "FONT", "SURFACE", "META"}
ROTATABLE_TYPES = GEOMETRY_TYPES | {"EMPTY"}


def get_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collection", required=True, help="Collection holding one asset, excluding lights/cameras")
    parser.add_argument("--output", required=True, help="Staging folder; do not point at map_factory/parts")
    parser.add_argument("--prefix", required=True, help="Safe output basename, e.g. hero_bed")
    parser.add_argument("--width", type=int, default=512)
    parser.add_argument("--height", type=int, default=512)
    args = parser.parse_args(argv)
    if not re.fullmatch(r"[A-Za-z0-9_-]+", args.prefix):
        parser.error("--prefix must contain only letters, digits, underscore and hyphen")
    if not (64 <= args.width <= 4096 and 64 <= args.height <= 4096):
        parser.error("dimensions must be between 64 and 4096")
    return args


def main():
    args = get_args()
    scene = bpy.context.scene
    if scene.camera is None or scene.camera.data.type != "ORTHO":
        raise RuntimeError("Set an orthographic camera in the .blend scene before exporting")
    collection = bpy.data.collections.get(args.collection)
    if collection is None:
        raise RuntimeError("Unknown Blender collection: " + args.collection)
    candidates = [obj for obj in collection.all_objects if obj.type in ROTATABLE_TYPES]
    geometry = [obj for obj in candidates if obj.type in GEOMETRY_TYPES]
    if not geometry:
        raise RuntimeError("Collection must contain at least one renderable geometry object")
    names = {obj.name for obj in candidates}
    roots = [obj for obj in candidates if obj.parent is None or obj.parent.name not in names]
    original = {obj.name: obj.matrix_world.copy() for obj in roots}
    corners = [obj.matrix_world @ Vector(corner) for obj in geometry for corner in obj.bound_box]
    center = Vector(((min(p.x for p in corners) + max(p.x for p in corners)) / 2,
                     (min(p.y for p in corners) + max(p.y for p in corners)) / 2, 0.0))
    output = Path(args.output).expanduser().resolve()
    if "map_factory/parts" in output.as_posix():
        raise RuntimeError("Export to a candidate folder, never directly to map_factory/parts")
    output.mkdir(parents=True, exist_ok=True)

    render = scene.render
    old = (render.filepath, render.resolution_x, render.resolution_y,
           render.resolution_percentage, render.film_transparent,
           render.image_settings.file_format, render.image_settings.color_mode)
    files = {}
    try:
        render.resolution_x, render.resolution_y = args.width, args.height
        render.resolution_percentage = 100
        render.film_transparent = True
        render.image_settings.file_format = "PNG"
        render.image_settings.color_mode = "RGBA"
        for facing, degrees in FACING_ANGLES:
            change = (Matrix.Translation(center)
                      @ Matrix.Rotation(math.radians(degrees), 4, "Z")
                      @ Matrix.Translation(-center))
            for obj in roots:
                obj.matrix_world = change @ original[obj.name]
            bpy.context.view_layer.update()
            filename = f"{args.prefix}_{facing}.png"
            render.filepath = str(output / filename)
            bpy.ops.render.render(write_still=True)
            files[facing] = filename
    finally:
        for obj in roots:
            obj.matrix_world = original[obj.name]
        (render.filepath, render.resolution_x, render.resolution_y,
         render.resolution_percentage, render.film_transparent,
         render.image_settings.file_format, render.image_settings.color_mode) = old
        bpy.context.view_layer.update()

    manifest = {
        "schema_version": 1,
        "status": "needs_review",
        "source_blend": bpy.data.filepath,
        "source_collection": args.collection,
        "output_kind": "four_perspective_sprite_candidates",
        "orientation_mode": "variants",
        "direction_files": files,
        "angles_degrees": dict(FACING_ANGLES),
        "pixel_size": [args.width, args.height],
        "suggested_origin": [args.width // 2, args.height - 1],
        "requires_review": ["pixel-art style", "ortho view", "pivot", "collision", "scale", "alpha", "shadows", "clipping", "lighting"],
        "note": "Assign four DISTINCT environment catalog IDs after visual approval; never auto-publish to maps."
    }
    (output / f"{args.prefix}_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Rendered four review-only sprites to {output}")


if __name__ == "__main__":
    main()
