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
    f = proj.get("fill")
    if f:
        # Warm shadowless fill from the front right so faces turned away from the sun stay golden.
        fdata = bpy.data.lights.new("fill", "SUN")
        fdata.energy, fdata.color = f["strength"], f["color"]
        fdata.angle = math.radians(f.get("angle_deg", 20.0))
        fdata.use_shadow = False
        fill = bpy.data.objects.new("fill", fdata)
        bpy.context.scene.collection.objects.link(fill)
        faz, fel = math.radians(f["azimuth_deg"]), math.radians(f["elevation_deg"])
        ftoward = -Vector((math.cos(faz) * math.cos(fel), math.sin(faz) * math.cos(fel), math.sin(fel)))
        fill.rotation_euler = ftoward.to_track_quat("-Z", "Y").to_euler()
    return sun


def projected(point, proj):
    """Image-plane coordinates in tile units: u to the right, v up (floor stays square)."""
    cot = 1.0 / math.tan(math.radians(proj["camera_elevation_deg"]))
    return point.x, point.y + point.z * cot


def frame_camera(objects, proj, extra_tiles=(0.0, 0.0, 0.0, 0.0), fixed=None):
    """Place an orthographic camera that frames the objects; returns frame metadata in pixels.

    extra_tiles = (left, right, bottom, top) margin in tiles (used to fit cast shadows).
    fixed = (umin, umax, vmin, vmax) image-plane window in tiles (map tiles: exactly the cell, no padding)."""
    scene = bpy.context.scene
    ss = int(proj.get("supersample", 1))
    px = proj["tile_px"] * ss
    if fixed is not None:
        umin, umax, vmin, vmax = fixed
    else:
        deps = bpy.context.evaluated_depsgraph_get()
        us, vs = [], []
        for obj in objects:
            ev = obj.evaluated_get(deps)
            for corner in ev.bound_box:
                u, v = projected(ev.matrix_world @ Vector(corner), proj)
                us.append(u)
                vs.append(v)
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


def shadow_catcher(size=12.0, center=(0.0, 0.0)):
    bpy.ops.mesh.primitive_plane_add(size=size, location=(center[0], center[1], 0))
    plane = bpy.context.active_object
    plane.name = "shadow_catcher"
    plane.is_shadow_catcher = True
    return plane


def render(path):
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)


def polygon_catcher(points):
    """Shadow catcher limited to a ground polygon (tiles), e.g. the floor beside a side wall,
    so shadows that would fall outside the room (on the sea) are not rendered at all."""
    import bmesh
    mesh = bpy.data.meshes.new("shadow_catcher")
    bm = bmesh.new()
    bm.faces.new([bm.verts.new((x, y, 0.0)) for x, y in points])
    bm.to_mesh(mesh)
    bm.free()
    plane = bpy.data.objects.new("shadow_catcher", mesh)
    bpy.context.scene.collection.objects.link(plane)
    plane.is_shadow_catcher = True
    return plane


def render_color_and_shadow(objects, color_path, shadow_path, region=None):
    """Color pass (no shadow on the ground) and a separate shadow-only pass on the same canvas.

    region: optional ground polygon (tiles) that receives the shadow; default = everything around the piece."""
    # Centre the catcher under the pieces: long side walls sit far from the world origin.
    pts = [obj.matrix_world @ Vector(c) for obj in objects for c in obj.bound_box]
    center = ((min(p.x for p in pts) + max(p.x for p in pts)) / 2, (min(p.y for p in pts) + max(p.y for p in pts)) / 2)
    span = max(max(p.x for p in pts) - min(p.x for p in pts), max(p.y for p in pts) - min(p.y for p in pts))
    catcher = polygon_catcher(region) if region else shadow_catcher(size=max(12.0, span + 8.0), center=center)
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


def _soft_specular(bsdf, level=0.2):
    # Blender 4+ name; a weak dielectric highlight keeps matte stone and wood from washing out grey.
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = level


GOLDEN_STONE = ((0.66, 0.40, 0.14), (0.33, 0.17, 0.05))   # v4 golden limestone (linear RGB): base, dark
GOLDEN_CAP = ((0.76, 0.49, 0.19), (0.40, 0.22, 0.07))


def limestone(name="limestone", base=(0.68, 0.48, 0.26), dark=(0.36, 0.23, 0.10), seed=1.0, specular=None):
    """Warm golden limestone: per-object tint, mottled colour, pitted bump (v2: warmer and darker).

    Colours are linear RGB; v4 pieces pass GOLDEN_STONE / GOLDEN_CAP and specular=0.2 (see README)."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.82
    if specular is not None:
        _soft_specular(bsdf, specular)
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


def wood(name="wood", light=(0.36, 0.19, 0.07), dark=(0.13, 0.06, 0.02), seed=1.0):
    """Weathered wood: grain stretched along the object's Z axis (posts stand upright), soft bump."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.7
    _soft_specular(bsdf, 0.25)
    coord = _node(nt, "ShaderNodeTexCoord", (-900, 0))
    stretch = _node(nt, "ShaderNodeMapping", (-700, 0))
    stretch.inputs["Scale"].default_value = (9.0, 9.0, 1.2)
    nt.links.new(coord.outputs["Object"], stretch.inputs["Vector"])
    grain = _node(nt, "ShaderNodeTexNoise", (-500, 0), Scale=6.0, Detail=12.0, Roughness=0.7)
    grain.noise_dimensions = "4D"
    grain.inputs["W"].default_value = seed
    nt.links.new(stretch.outputs["Vector"], grain.inputs["Vector"])
    ramp = _node(nt, "ShaderNodeValToRGB", (-300, 0))
    ramp.color_ramp.elements[0].position, ramp.color_ramp.elements[0].color = 0.3, (*dark, 1.0)
    ramp.color_ramp.elements[1].position, ramp.color_ramp.elements[1].color = 0.75, (*light, 1.0)
    nt.links.new(grain.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    bump = _node(nt, "ShaderNodeBump", (-200, -300), Strength=0.4, Distance=0.02)
    nt.links.new(grain.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def rope(name="rope", color=(0.55, 0.40, 0.20), dark=(0.24, 0.15, 0.06)):
    """Twisted hemp: diagonal wave bands along the strand read as twist at 64 px per tile."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.9
    _soft_specular(bsdf, 0.15)
    coord = _node(nt, "ShaderNodeTexCoord", (-700, 0))
    wave = _node(nt, "ShaderNodeTexWave", (-500, 0), Scale=40.0, Distortion=1.5)
    wave.bands_direction = "DIAGONAL"
    nt.links.new(coord.outputs["Object"], wave.inputs["Vector"])
    ramp = _node(nt, "ShaderNodeValToRGB", (-300, 0))
    ramp.color_ramp.elements[0].color, ramp.color_ramp.elements[1].color = (*dark, 1.0), (*color, 1.0)
    nt.links.new(wave.outputs["Color"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    return mat


def gold(name="gold"):
    # Mostly dielectric: a fully metallic flat face only mirrors the dim world in an ortho view and reads grey.
    return flat(name, (0.80, 0.50, 0.11), roughness=0.42, metallic=0.35)


def sapphire(name="sapphire", color=(0.02, 0.10, 0.42)):
    """Deep blue enamel inlay: glossy dielectric so it keeps its colour under the warm sun."""
    return flat(name, color, roughness=0.25)


def _math(nt, op, a, b=None, loc=(0, 0)):
    n = nt.nodes.new("ShaderNodeMath")
    n.operation, n.location = op, loc
    for i, x in enumerate((a, b)):
        if x is None:
            continue
        if isinstance(x, (int, float)):
            n.inputs[i].default_value = x
        else:
            nt.links.new(x, n.inputs[i])
    return n.outputs[0]


def periodic_material(name, stops, scale=4.0, detail=6.0, roughness=0.8, bump=0.3, specular=None, seed=0.0,
                      distortion=0.0, edge=None, plane="xy"):
    """Map-tile material whose pattern repeats exactly every world unit along `plane` (seamless tiles).

    plane is "xy" for ground tiles, "xz" for wall/cliff faces. Both axes are wrapped onto circles of circumference 1 and fed to a 4D noise
    (cos a, sin a, cos b; W = sin b), so neighbouring tiles continue each other.
    stops: colour-ramp [(position, linear RGB)], scale ~ features per tile.
    edge: optional (axis 'y'|'z', from, to, linear RGB): blends a noisy band toward `to`
    (e.g. shore foam toward the cliff); that axis is then not periodic."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = roughness
    if specular is not None:
        _soft_specular(bsdf, specular)
    geo = _node(nt, "ShaderNodeNewGeometry", (-1400, 0))
    sep = _node(nt, "ShaderNodeSeparateXYZ", (-1200, 0))
    nt.links.new(geo.outputs["Position"], sep.inputs[0])
    r = scale / (2 * math.pi)
    parts = []
    for axis in plane.upper():
        ang = _math(nt, "MULTIPLY", sep.outputs[axis], 2 * math.pi)
        parts.append(_math(nt, "MULTIPLY", _math(nt, "COSINE", ang), r))
        parts.append(_math(nt, "MULTIPLY", _math(nt, "SINE", ang), r))
    comb = _node(nt, "ShaderNodeCombineXYZ", (-700, 0))
    for i in range(3):
        nt.links.new(parts[i], comb.inputs[i])
    w = _math(nt, "ADD", parts[3], seed)
    noise = _node(nt, "ShaderNodeTexNoise", (-500, 0), Scale=1.0, Detail=detail, Roughness=0.6, Distortion=distortion)
    noise.noise_dimensions = "4D"
    nt.links.new(comb.outputs[0], noise.inputs["Vector"])
    nt.links.new(w, noise.inputs["W"])
    ramp = _node(nt, "ShaderNodeValToRGB", (-300, 0))
    elements = ramp.color_ramp.elements
    while len(elements) < len(stops):
        elements.new(0.5)
    for el, (pos, col) in zip(elements, stops):
        el.position, el.color = pos, (*col, 1.0)
    nt.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    color = ramp.outputs["Color"]
    if edge:
        axis, a, b, to = edge
        band = _node(nt, "ShaderNodeMapRange", (-500, -300))
        nt.links.new(sep.outputs[axis.upper()], band.inputs["Value"])
        band.inputs["From Min"].default_value, band.inputs["From Max"].default_value = a, b
        wobble = _math(nt, "ADD", band.outputs[0], _math(nt, "MULTIPLY", noise.outputs["Fac"], 0.7))
        cut = _node(nt, "ShaderNodeMapRange", (-300, -300))
        nt.links.new(wobble, cut.inputs["Value"])
        cut.inputs["From Min"].default_value, cut.inputs["From Max"].default_value = 0.75, 0.95
        mix = _node(nt, "ShaderNodeMix", (-100, -100))
        mix.data_type = "RGBA"
        nt.links.new(cut.outputs[0], mix.inputs["Factor"])
        nt.links.new(color, mix.inputs["A"])
        mix.inputs["B"].default_value = (*to, 1.0)
        color = mix.outputs["Result"]
    nt.links.new(color, bsdf.inputs["Base Color"])
    if bump:
        bn = _node(nt, "ShaderNodeBump", (-200, -400), Strength=bump, Distance=0.02)
        nt.links.new(noise.outputs["Fac"], bn.inputs["Height"])
        nt.links.new(bn.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def wrap_copies(obj, axes="xy"):
    """Linked copies one tile away in every direction of `axes` ('xy' ground, 'xz' wall faces), so
    geometry and shadows crossing a tile edge reappear on the opposite edge (seamless tiles)."""
    copies = []
    for i in (-1, 0, 1):
        for j in (-1, 0, 1):
            if i == 0 and j == 0:
                continue
            c = obj.copy()
            bpy.context.scene.collection.objects.link(c)
            off = Vector((i, j, 0.0)) if axes == "xy" else Vector((i, 0.0, j))
            c.location = obj.location + off
            copies.append(c)
    return copies


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


def lean_matrix(k):
    """Horizontal shear x += k * z: the foot (z = 0) stays on the floor grid while the top shifts,
    so a side wall's inner face, edge-on in the plain orthographic view, becomes visible."""
    from mathutils import Matrix
    m = Matrix.Identity(4)
    m[0][2] = k
    return m


def lean(objects, k):
    m = lean_matrix(k)
    for obj in objects:
        obj.matrix_world = m @ obj.matrix_world


def join(objects, name):
    """Apply modifiers and merge the objects into one mesh object (materials kept per face)."""
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.convert(target="MESH")
    bpy.ops.object.join()
    merged = bpy.context.view_layer.objects.active
    merged.name = name
    return merged


def ivy(name, x_range, face_y, z_top, rng_, density=1.0, hang=0.9, flowers=0.12, leaf_scale=1.0):
    """Ivy hanging from z_top down a wall face at y = face_y (front faces -y): leaves and small
    white flowers as two meshes; leaf_scale enlarges leaves so they read at 64 px per tile."""
    import bmesh
    leaf_mat = flat(name + "_leaf", (0.10, 0.27, 0.07), roughness=0.55)
    leaf_dark = flat(name + "_leaf_dark", (0.05, 0.16, 0.04), roughness=0.6)
    petal = flat(name + "_flower", (0.93, 0.92, 0.86), roughness=0.45)
    meshes = {"leaves": (bpy.data.meshes.new(name + "_leaves"), bmesh.new()),
              "flowers": (bpy.data.meshes.new(name + "_flowers"), bmesh.new())}
    x0, x1 = x_range
    strands = max(2, int((x1 - x0) * 7 * density))
    for s in range(strands):
        x = rng_.uniform(x0 + 0.03, x1 - 0.03)
        length = rng_.uniform(0.25, hang)
        z = z_top + rng_.uniform(-0.02, 0.06)
        steps = int(length / 0.045)
        for i in range(steps):
            z -= 0.045
            x += rng_.uniform(-0.025, 0.025)
            for _ in range(2):
                size = rng_.uniform(0.035, 0.06) * leaf_scale * (1.0 - 0.35 * i / max(1, steps))
                cx, cz = x + rng_.uniform(-0.03, 0.03), z + rng_.uniform(-0.02, 0.02)
                cy = face_y - rng_.uniform(0.012, 0.05)
                tilt = rng_.uniform(-0.6, 0.6)
                bm = meshes["leaves"][1]
                pts = [(0.0, 0.0, 0.5), (0.42, 0.0, 0.0), (0.0, 0.0, -0.6), (-0.42, 0.0, 0.0)]
                verts = []
                for px, py, pz in pts:
                    rx = px * math.cos(tilt) - pz * math.sin(tilt)
                    rz = px * math.sin(tilt) + pz * math.cos(tilt)
                    verts.append(bm.verts.new((cx + rx * size, cy - abs(rx) * size * 0.4, cz + rz * size)))
                face = bm.faces.new(verts)
                face.material_index = rng_.random() < 0.35
            if rng_.random() < flowers:
                bm = meshes["flowers"][1]
                bmesh.ops.create_icosphere(bm, subdivisions=1, radius=rng_.uniform(0.012, 0.02),
                                           matrix=Matrix_translation((x, face_y - 0.055, z)))
    created = []
    for key, (mesh, bm) in meshes.items():
        if not bm.faces:
            bm.free()
            continue
        bm.to_mesh(mesh)
        bm.free()
        obj = bpy.data.objects.new(mesh.name, mesh)
        bpy.context.scene.collection.objects.link(obj)
        if key == "leaves":
            obj.data.materials.append(leaf_mat)
            obj.data.materials.append(leaf_dark)
        else:
            obj.data.materials.append(petal)
        for poly in obj.data.polygons:
            poly.use_smooth = True
        created.append(obj)
    return created


def Matrix_translation(xyz):
    from mathutils import Matrix
    return Matrix.Translation(Vector(xyz))


def rng(seed):
    return random.Random(seed)
