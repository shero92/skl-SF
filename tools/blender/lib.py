"""Shared Blender toolkit for Map Factory pieces (runs inside Blender's Python).

Conventions:
- 1 Blender unit = 1 map tile (tile_px pixels). +X = east (screen right), +Y = north (into the screen), +Z = up.
- An orthographic camera looks north from above at camera_elevation_deg; pixel aspect correction
  keeps the floor grid square, so a 1x1 floor tile renders as tile_px x tile_px.
- Builders model each piece with its front facing south (toward the camera); facings rotate the
  model about Z, so every facing is a real render (never a mirrored or rotated bitmap).
"""
import math
import random

import bpy
from mathutils import Vector

FRONT_ROTATION = {"south": 0.0, "west": -90.0, "north": 180.0, "east": 90.0}


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    return bpy.context.scene


def configure_render(scene, proj):
    r = scene.render
    r.engine = "CYCLES" if proj.get("engine", "CYCLES") == "CYCLES" else "BLENDER_EEVEE"
    r.film_transparent = True
    r.image_settings.file_format = "PNG"
    r.image_settings.color_mode = "RGBA"
    r.image_settings.color_depth = "8"
    r.resolution_percentage = 100
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    if r.engine == "CYCLES":
        cyc = scene.cycles
        cyc.samples = int(proj.get("samples", 96))
        cyc.use_denoising = True
        cyc.film_transparent_glass = False
        if proj.get("device", "GPU") == "GPU":
            prefs = bpy.context.preferences.addons["cycles"].preferences
            for kind in ("OPTIX", "CUDA", "HIP", "METAL", "ONEAPI"):
                try:
                    prefs.compute_device_type = kind
                    prefs.get_devices()
                    gpus = [d for d in prefs.devices if d.type == kind]
                except (TypeError, ValueError):
                    continue
                if gpus:
                    for d in prefs.devices:
                        d.use = d.type == kind
                    cyc.device = "GPU"
                    break


def add_world(scene, proj):
    world = bpy.data.worlds.new("world")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (*proj["world"]["color"], 1.0)
    bg.inputs["Strength"].default_value = proj["world"]["strength"]


def add_sun(proj):
    s = proj["sun"]
    data = bpy.data.lights.new("sun", "SUN")
    data.energy = s["strength"]
    data.color = s["color"]
    data.angle = math.radians(s.get("angle_deg", 3.0))
    sun = bpy.data.objects.new("sun", data)
    bpy.context.scene.collection.objects.link(sun)
    az, el = math.radians(s["azimuth_deg"]), math.radians(s["elevation_deg"])
    # Direction the light travels: from azimuth (measured from +X counter-clockwise) and elevation, toward the scene.
    toward = -Vector((math.cos(az) * math.cos(el), math.sin(az) * math.cos(el), math.sin(el)))
    sun.rotation_euler = toward.to_track_quat("-Z", "Y").to_euler()
    return sun


def projected(point, proj):
    """Image-plane coordinates in tile units: u to the right, v up (floor stays square)."""
    cot = 1.0 / math.tan(math.radians(proj["camera_elevation_deg"]))
    return point.x, point.y + point.z * cot


def frame_camera(objects, proj, extra_tiles=(0.0, 0.0, 0.0, 0.0)):
    """Place an orthographic camera that frames the objects; returns frame metadata in pixels.

    extra_tiles = (left, right, bottom, top) margin in tiles (used to fit cast shadows)."""
    scene = bpy.context.scene
    deps = bpy.context.evaluated_depsgraph_get()
    us, vs = [], []
    for obj in objects:
        ev = obj.evaluated_get(deps)
        for corner in ev.bound_box:
            u, v = projected(ev.matrix_world @ Vector(corner), proj)
            us.append(u)
            vs.append(v)
    ss = int(proj.get("supersample", 1))
    px = proj["tile_px"] * ss
    pad = proj.get("padding_px", 4) * ss
    # Snap the frame to the pixel grid so tile edges (integer world units) land on whole pixels.
    umin = (math.floor((min(us) - extra_tiles[0]) * px) - pad) / px
    umax = (math.ceil((max(us) + extra_tiles[1]) * px) + pad) / px
    vmin = (math.floor((min(vs) - extra_tiles[2]) * px) - pad) / px
    vmax = (math.ceil((max(vs) + extra_tiles[3]) * px) + pad) / px
    width = max(1, round((umax - umin) * px))
    height = max(1, round((vmax - vmin) * px))
    el = math.radians(proj["camera_elevation_deg"])
    cam_data = bpy.data.cameras.new("cam")
    cam_data.type = "ORTHO"
    cam_data.sensor_fit = "HORIZONTAL"
    cam_data.ortho_scale = width / px
    cam_data.clip_start, cam_data.clip_end = 0.01, 1000.0
    cam = bpy.data.objects.new("cam", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam
    # Look along +Y tilted down by the elevation; the target point is on the ground (z = 0).
    target = Vector(((umin + umax) / 2, (vmin + vmax) / 2, 0.0))
    forward = Vector((0.0, math.cos(el), -math.sin(el)))
    cam.location = target - forward * 50.0
    cam.rotation_euler = (math.pi / 2 - el, 0.0, 0.0)
    r = scene.render
    r.resolution_x, r.resolution_y = width, height
    # Each pixel covers 1/px horizontally and sin(el)/px of the camera's vertical axis -> square floor.
    r.pixel_aspect_x, r.pixel_aspect_y = 1.0 / math.sin(el), 1.0
    return {"umin": umin, "vmax": vmax, "px": px, "size": [width, height], "supersample": ss}


def to_pixels(frame, point, proj):
    u, v = projected(point, proj)
    return [round((u - frame["umin"]) * frame["px"] / frame["supersample"], 2),
            round((frame["vmax"] - v) * frame["px"] / frame["supersample"], 2)]


def shadow_catcher(size=12.0):
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, 0))
    plane = bpy.context.active_object
    plane.name = "shadow_catcher"
    plane.is_shadow_catcher = True
    return plane


def render(path):
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)


def render_color_and_shadow(objects, color_path, shadow_path):
    """Color pass (no shadow on the ground) and a separate shadow-only pass on the same canvas."""
    catcher = shadow_catcher()
    catcher.hide_render = True
    render(color_path)
    catcher.hide_render = False
    for obj in objects:
        obj.visible_camera = False
    render(shadow_path)
    for obj in objects:
        obj.visible_camera = True
    bpy.data.objects.remove(catcher, do_unlink=True)


# ---------------------------------------------------------------- materials

def _node(nt, kind, loc, **inputs):
    n = nt.nodes.new(kind)
    n.location = loc
    for k, v in inputs.items():
        n.inputs[k].default_value = v
    return n


def limestone(name="limestone", base=(0.80, 0.62, 0.38), dark=(0.52, 0.36, 0.18), seed=1.0):
    """Warm golden limestone: per-object tint, mottled colour, pitted bump."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.82
    coord = _node(nt, "ShaderNodeTexCoord", (-900, 0))
    info = _node(nt, "ShaderNodeObjectInfo", (-900, -250))
    noise = _node(nt, "ShaderNodeTexNoise", (-650, 100), Scale=7.0, Detail=9.0, Roughness=0.62)
    noise.noise_dimensions = "4D"  # the W input only exists in 4D mode
    noise.inputs["W"].default_value = seed
    nt.links.new(coord.outputs["Object"], noise.inputs["Vector"])
    mix_in = _node(nt, "ShaderNodeMath", (-650, -200))
    mix_in.operation = "MULTIPLY_ADD"
    nt.links.new(info.outputs["Random"], mix_in.inputs[0])
    mix_in.inputs[1].default_value = 0.35
    nt.links.new(noise.outputs["Fac"], mix_in.inputs[2])
    ramp = _node(nt, "ShaderNodeValToRGB", (-400, 100))
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = (*dark, 1.0)
    ramp.color_ramp.elements[1].position = 0.95
    ramp.color_ramp.elements[1].color = (*base, 1.0)
    nt.links.new(mix_in.outputs[0], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    vor = _node(nt, "ShaderNodeTexVoronoi", (-650, -450), Scale=22.0)
    nt.links.new(coord.outputs["Object"], vor.inputs["Vector"])
    fine = _node(nt, "ShaderNodeTexNoise", (-650, -650), Scale=60.0, Detail=4.0)
    nt.links.new(coord.outputs["Object"], fine.inputs["Vector"])
    add = _node(nt, "ShaderNodeMath", (-400, -500))
    add.operation = "ADD"
    nt.links.new(vor.outputs["Distance"], add.inputs[0])
    nt.links.new(fine.outputs["Fac"], add.inputs[1])
    bump = _node(nt, "ShaderNodeBump", (-200, -400), Strength=0.35, Distance=0.02)
    nt.links.new(add.outputs[0], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def flat(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


# ---------------------------------------------------------------- geometry helpers

def block(name, size, location, material, bevel=0.025, rotation_z=0.0, collection=None):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    obj.rotation_euler.z = rotation_z
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    mod = obj.modifiers.new("bevel", "BEVEL")
    mod.width = bevel
    mod.segments = 3
    mod.limit_method = "ANGLE"
    obj.data.materials.append(material)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    if collection is not None:
        for c in obj.users_collection:
            c.objects.unlink(obj)
        collection.objects.link(obj)
    return obj


def rotate_group(objects, facing, pivot=(0.0, 0.0)):
    """Rotate a piece built facing south so its front faces `facing`, about a ground pivot."""
    angle = math.radians(FRONT_ROTATION[facing])
    pivot = Vector((pivot[0], pivot[1], 0.0))
    from mathutils import Matrix
    rot = Matrix.Translation(pivot) @ Matrix.Rotation(angle, 4, "Z") @ Matrix.Translation(-pivot)
    for obj in objects:
        obj.matrix_world = rot @ obj.matrix_world


def rng(seed):
    return random.Random(seed)
