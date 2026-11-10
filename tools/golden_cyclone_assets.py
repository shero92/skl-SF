"""Validate independent masters and export review assets without activating them.

Agent: codex. No image generation or painting is performed by this tool.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = Path("game_factory/golden_cyclone/v001/manifest.json")
ANNOTATIONS = Path("game_factory/golden_cyclone/v001/metadata/source_annotations.json")
OUTPUT = Path("assets/characters/hero/battle/golden_cyclone/v001/game_frames")
REVIEW = Path("game_factory/golden_cyclone/v001/previews")
DEPENDENCIES = Path("assets/characters/hero/battle/golden_cyclone/v001/preview_dependencies")


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local(root: Path, value: str) -> Path:
    path = (root / value.removeprefix("res://")).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Path escapes project: " + value)
    return path


def inspect_png(path: Path, minimum: int = 1024) -> dict:
    with Image.open(path) as image:
        image.verify()
    with Image.open(path) as image:
        if image.format != "PNG" or image.mode != "RGBA":
            raise ValueError("Expected RGBA PNG: " + str(path))
        if min(image.size) < minimum:
            raise ValueError("Insufficient source resolution: " + str(path))
        alpha = image.getchannel("A")
        bounds = alpha.point(lambda x: 255 if x >= 128 else 0).getbbox()
        if bounds is None or alpha.getextrema() != (0, 255):
            raise ValueError("Missing genuine transparency/visible body: " + str(path))
        if bounds[0] <= 0 or bounds[1] <= 0 or bounds[2] >= image.width or bounds[3] >= image.height:
            raise ValueError("Silhouette touches canvas edge: " + str(path))
        return {"body_canvas_size": list(image.size), "mode": image.mode,
                "alpha_extrema": list(alpha.getextrema()), "bounds_alpha_128": list(bounds),
                "sha256": sha(path)}


def validate(root: Path, *, complete: bool = True, minimum: int = 1024) -> dict:
    manifest = read(root / MANIFEST)
    frames = manifest["frames"]
    if len(frames) != 22 or manifest.get("production_source_mode") != "INDIVIDUAL_FRAME":
        raise ValueError("Expected 22 individually generated source records")
    seen: set[str] = set()
    existing = 0
    for index, frame in enumerate(frames, 1):
        ident = f"hero_golden_cyclone_{index:03}"
        if frame.get("frame_id") != ident:
            raise ValueError("Invalid source frame order")
        if not frame.get("source_image_path"):
            if complete:
                raise ValueError("Missing source: " + ident)
            continue
        if frame.get("source_generation_mode") != "individual_request":
            raise ValueError("Source is not an independent generation: " + ident)
        if frame.get("quality_status") == "needs_regeneration":
            raise ValueError("Rejected source: " + ident)
        request = local(root, frame["generation_request_path"])
        if not request.is_file():
            raise ValueError("Missing generation provenance: " + ident)
        path = local(root, frame["source_image_path"])
        if path.name != ident + ".png":
            raise ValueError("Unexpected frame filename: " + ident)
        actual = inspect_png(path, minimum)
        if actual["sha256"] != frame.get("sha256"):
            raise ValueError("Master hash mismatch: " + ident)
        if actual["sha256"] in seen:
            raise ValueError("Duplicate source: " + ident)
        seen.add(actual["sha256"])
        duration = frame.get("frame_duration")
        if not isinstance(duration, (float, int)) or isinstance(duration, bool) or not math.isfinite(duration) or duration <= 0:
            raise ValueError("Invalid duration: " + ident)
        existing += 1
    if manifest["generated_frame_count"] != existing:
        raise ValueError("Generated count does not match actual source files")
    return {"verified_source_count": existing, "unique_hashes": len(seen),
            "art_approval": "not_granted_by_technical_validation"}


def record_source(root: Path, index: int, source: Path, request: str) -> dict:
    """Record an actual built-in image_gen result after caller's visual single-pose review."""
    if not 1 <= index <= 22 or "generated_images" not in source.parts:
        raise ValueError("Expected frame 1..22 and a real built-in generated_images source path")
    if not local(root, request).is_file():
        raise ValueError("Missing actual generation request")
    info = inspect_png(source)
    manifest = read(root / MANIFEST)
    frame = manifest["frames"][index - 1]
    relative = Path("assets/characters/hero/battle/golden_cyclone/v001/source_frames") / (frame["frame_id"] + ".png")
    target = root / relative
    if target.exists() and sha(target) != info["sha256"]:
        raise ValueError("Source preservation conflict; archive rejected version explicitly first")
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        shutil.copy2(source, target)
    frame.update(info, source_image_path=relative.as_posix(), quality_status="needs_review",
                 png_validation="passed", source_generation_mode="individual_request",
                 source_generation_tool="builtin_image_gen", generation_request_path=request,
                 generation_cache_required=False,
                 visual_review={"one_complete_character": True, "no_visible_weapon": True,
                                "reviewer": "codex", "owner_approved": False})
    for existing in manifest["frames"]:
        if existing.get("source_image_path"):
            actual = local(root, existing["source_image_path"])
            if not actual.is_file() or sha(actual) != existing.get("sha256"):
                raise ValueError("Missing or changed registered master: " + existing["frame_id"])
    manifest["generated_frame_count"] = sum(bool(f.get("source_image_path")) for f in manifest["frames"])
    manifest["quality_status"] = "needs_review"
    write(root / MANIFEST, manifest)
    return {"recorded": frame["frame_id"], "sha256": info["sha256"],
            "source_count": manifest["generated_frame_count"]}


def quantize_durations(durations: list[float]) -> list[int]:
    """GIF uses centiseconds: round cumulative boundaries, avoiding accumulated drift."""
    result, elapsed, previous = [], 0.0, 0
    for duration in durations:
        if not math.isfinite(duration) or duration < 10:
            raise ValueError("GIF duration must be finite and at least 10ms")
        elapsed += duration
        boundary = int(math.floor(elapsed / 10 + 0.5)) * 10
        result.append(boundary - previous)
        previous = boundary
    return result


def point(value, size: tuple[int, int], label: str) -> tuple[float, float]:
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError("Missing measured point: " + label)
    x, y = value
    if not all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) for v in value):
        raise ValueError("Invalid point: " + label)
    if not (0 <= x < size[0] and 0 <= y < size[1]):
        raise ValueError("Point outside source: " + label)
    return float(x), float(y)


def save_gif(images: list[Image.Image], durations: list[float], target: Path) -> dict:
    if len(images) != len(durations) or not images:
        raise ValueError("GIF images/durations mismatch")
    # One palette for the complete sequence avoids per-frame palette shimmer.
    sample = Image.new("RGB", (images[0].width * len(images), images[0].height), (28, 35, 47))
    rgb = []
    for index, image in enumerate(images):
        canvas = Image.new("RGB", image.size, (28, 35, 47))
        canvas.paste(image.convert("RGBA"), mask=image.convert("RGBA").getchannel("A"))
        sample.paste(canvas, (index * image.width, 0))
        rgb.append(canvas)
    palette = sample.quantize(colors=256)
    converted = [im.quantize(palette=palette, dither=Image.Dither.NONE) for im in rgb]
    timing = quantize_durations(durations)
    target.parent.mkdir(parents=True, exist_ok=True)
    converted[0].save(target, save_all=True, append_images=converted[1:], duration=timing,
                      loop=0, disposal=2, optimize=False)
    with Image.open(target) as image:
        actual = []
        for index in range(image.n_frames):
            image.seek(index)
            actual.append(image.info.get("duration", 0))
    if sum(actual) != sum(timing):
        raise ValueError("GIF encoded duration mismatch")
    return {"path": target.as_posix(), "frames": len(actual), "duration_ms": sum(actual),
            "requested_duration_ms": sum(durations), "quantized_frame_durations_ms": timing}


def build(root: Path) -> dict:
    validation = validate(root)
    manifest, annotations = read(root / MANIFEST), read(root / ANNOTATIONS)
    scale = float(annotations["uniform_source_scale"])
    if not math.isfinite(scale) or not 0 < scale <= 1:
        raise ValueError("Invalid uniform scale")
    canvas = tuple(annotations["game_canvas_size"])
    ground = tuple(annotations["game_ground_anchor"])
    pictures, exported, anchors = [], [], {}
    before = {}
    for index, frame in enumerate(manifest["frames"]):
        source = local(root, frame["source_image_path"])
        before[source] = sha(source)
        annotation = annotations["frames"][frame["frame_id"]]
        if annotation.get("method") != "manual_source_review":
            raise ValueError("Missing manual source annotation")
        with Image.open(source) as image:
            g = point(annotation.get("character_ground_anchor"), image.size, "ground")
            h = point(annotation.get("weapon_hand_anchor"), image.size, "hand")
            x, y = map(int, h)
            region = image.getchannel("A").crop((max(0, x - 12), max(0, y - 12), min(image.width, x + 13), min(image.height, y + 13)))
            if region.getextrema()[1] < 128:
                raise ValueError("Weapon socket misses visible hand: " + frame["frame_id"])
            cleaned = image.copy()
            cleaned.putalpha(cleaned.getchannel("A").point(lambda a: 0 if a < 8 else a))
            resized = cleaned.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.NEAREST)
            offset = (round(ground[0] - g[0] * scale), round(ground[1] - g[1] * scale))
            bounds = resized.getchannel("A").getbbox()
            if bounds is None or min(bounds[0] + offset[0], bounds[1] + offset[1]) < 0 or bounds[2] + offset[0] > canvas[0] or bounds[3] + offset[1] > canvas[1]:
                raise ValueError("Derivative clips; enlarge the shared canvas, never refit frame: " + frame["frame_id"])
            native = Image.new("RGBA", canvas)
            native.paste(resized, offset)
        path = root / OUTPUT / (frame["frame_id"] + ".png")
        path.parent.mkdir(parents=True, exist_ok=True)
        native.save(path)
        angle = annotation.get("hand_rotation")
        order = annotation.get("weapon_render_order")
        if not isinstance(angle, (float, int)) or not math.isfinite(angle) or order not in ("front", "behind"):
            raise ValueError("Missing measured weapon orientation/depth")
        socket = [round(h[0] * scale + offset[0], 3), round(h[1] * scale + offset[1], 3)]
        anchors[f"golden_cyclone:{index}"] = {
            "hand_anchor_x": socket[0], "hand_anchor_y": socket[1],
            "hand_rotation_degrees": angle, "weapon_scale": annotation["weapon_scale"],
            "weapon_render_order": order,
            "hand_occlusion_rect": [round(socket[0] - 4), round(socket[1] - 4), 8, 8],
        }
        for key in ("character_ground_anchor", "weapon_hand_anchor", "hand_rotation", "weapon_scale", "weapon_render_order"):
            frame[key] = annotation[key]
        frame["annotation_status"] = "manual_source_review; render_verification_required"
        pictures.append(native)
        exported.append({"frame_id": frame["frame_id"], "path": path.relative_to(root).as_posix(),
                         "sha256": sha(path),
                         "duration_ms": frame["frame_duration"], "ground_anchor": list(ground),
                         "hand_anchor": socket, "source_offset": list(offset), "source_scale": scale,
                         "hit": index == 16, "phase": "Recovery" if index >= 18 else "Attack"})
    sheet = Image.new("RGBA", (canvas[0] * 6, canvas[1] * 4))
    review = root / REVIEW
    review.mkdir(parents=True, exist_ok=True)
    for index, picture in enumerate(pictures):
        sheet.paste(picture, ((index % 6) * canvas[0], (index // 6) * canvas[1]))
    sheet.save(review / "hero_golden_cyclone_sprite_sheet.png")
    gif_durations = [f["duration_ms"] for f in exported]
    gif_durations[-1] += 350  # Visible recovery pause; attack clock remains 1500ms.
    gif = save_gif(pictures, gif_durations, review / "hero_golden_cyclone_body_review.gif")
    slow = save_gif(pictures, [d * 4 for d in gif_durations], review / "hero_golden_cyclone_body_slow.gif")
    if any(sha(path) != digest for path, digest in before.items()):
        raise ValueError("Original master changed during export")
    result = {"attack_id": "golden_cyclone", "quality_status": "needs_review", "owner_approved": False,
              "source_validation": validation, "uniform_source_scale": scale,
              "canvas_size": list(canvas), "ground_anchor": list(ground), "frames": exported,
              "weapon_attachment_data": {"frames": anchors}, "body_review_gif": gif,
              "body_slow_gif": slow, "duration_ms": sum(f["duration_ms"] for f in exported),
              "impact_ms": sum(f["duration_ms"] for f in exported[:16]),
              "hitstop_ms": 70, "hitstop_included": True, "production_activation": False}
    write(root / "game_factory/golden_cyclone/v001/metadata/review_assets.json", result)
    write(root / MANIFEST, manifest)
    return {"source_frames": 22, "exported_frames": len(exported), "duration_ms": result["duration_ms"],
            "impact_ms": result["impact_ms"], "original_hashes_unchanged": True}


def stage_dependencies(root: Path, source_root: Path) -> dict:
    """Copy byte-identical existing art into a portable, isolated review package."""
    source_root = source_root.resolve()
    catalog = read(source_root / "game_factory/weapons/catalog.json")
    result = {"weapons": {"weapons": {}}, "background": {}, "sources": [],
              "target_role": "Existing Hero body used as a review sparring target, not a new monster"}

    def copy_asset(source: Path, name: str, expected: str | None = None) -> str:
        digest = sha(source)
        if expected and digest != expected:
            raise ValueError("Approved dependency hash mismatch: " + str(source))
        relative = DEPENDENCIES / name
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists() and sha(destination) != digest:
            raise ValueError("Preserved dependency conflict: " + str(destination))
        if not destination.exists():
            shutil.copy2(source, destination)
        result["sources"].append({"source": source.relative_to(source_root).as_posix(),
                                  "copy": relative.as_posix(), "sha256": digest})
        return "res://" + relative.as_posix()

    for ident in ("WPN_HERO_BASIC_SWORD", "WPN_IRON_SWORD"):
        record = dict(catalog["weapons"][ident])
        source = local(source_root, record["texture_path"])
        record["texture_path"] = copy_asset(source, source.name, record["sha256"])
        with Image.open(source) as image:
            alpha = image.convert("RGBA").getchannel("A")
            bounds = alpha.point(lambda a: 255 if a >= 128 else 0).getbbox()
            top_y = bounds[1]
            xs = [x for x in range(image.width) if alpha.getpixel((x, top_y)) >= 128]
            record["review_blade_tip"] = [sum(xs) / len(xs), top_y]
        result["weapons"]["weapons"][ident] = record
    target = next(item for item in read(source_root / "game_factory/hero_correction/queue.json")["items"]
                  if item["id"] == "CHAR001_weaponless_idle_ready_01")
    result["target_body"] = copy_asset(local(source_root, target["output"]), "existing_hero_target.png", target["sha256"])
    result["target_attachments"] = read(source_root / "game_factory/hero_correction/hero_weapon_anchors.json")
    locations = {
        "sky": "assets_generated/background/B10__background__clear_sky_gradient_segment__default__4x4__256x256",
        "cliff": "assets_generated/background/B04__background__far_cliff_rock_segment__default__4x4__256x256",
        "cloud": "assets_generated/background/B08__background__bright_cloud_small__default__4x4__256x256",
        "floor": "assets_generated/floor/G01__floor__clean_sandstone_floor_tile__default__1x1__64x64",
    }
    for name, stem in locations.items():
        meta = read(source_root / (stem + ".json"))
        if meta.get("approval_status") != "approved":
            raise ValueError("Unapproved scenery dependency: " + stem)
        result["background"][name] = copy_asset(source_root / (stem + ".png"), name + ".png", meta["sha256"])
    write(root / "game_factory/golden_cyclone/v001/metadata/preview_dependencies.json", result)
    return {"copied_dependencies": len(result["sources"]), "approved_weapon_hashes_verified": True}


def pin_review(root: Path) -> dict:
    """Source-pixel crops for socket inspection only; never production frame sources."""
    manifest, annotations = read(root / MANIFEST), read(root / ANNOTATIONS)
    sheet = Image.new("RGB", (6 * 208, 4 * 224), (28, 35, 47))
    draw = ImageDraw.Draw(sheet)
    for index, frame in enumerate(manifest["frames"]):
        if not frame.get("source_image_path"):
            continue
        record = annotations["frames"][frame["frame_id"]]
        x, y = record["weapon_hand_anchor"]
        with Image.open(local(root, frame["source_image_path"])) as image:
            crop = image.crop((round(x - 96), round(y - 96), round(x + 96), round(y + 96)))
        left, top = (index % 6) * 208 + 8, (index // 6) * 224 + 24
        sheet.paste(crop, (left, top), crop.getchannel("A"))
        draw.text((left, top - 19), frame["frame_id"][-3:] + " " + record["weapon_render_order"], fill="white")
        draw.ellipse((left + 91, top + 91, left + 101, top + 101), outline="yellow", width=2)
    path = root / REVIEW / "weapon_socket_source_review.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(path)
    return {"inspection_only": True, "path": path.as_posix()}


def encode_godot(root: Path) -> dict:
    receipt = read(root / REVIEW / "godot_capture_receipt.json")
    if not receipt.get("actual_viewport") or not receipt.get("candidate_only"):
        raise ValueError("Expected actual candidate viewport capture receipt")
    for field, relative in {
        "review_assets_sha256": "game_factory/golden_cyclone/v001/metadata/review_assets.json",
        "vfx_sha256": "game_factory/golden_cyclone/v001/metadata/vfx.json",
        "scene_sha256": "scenes/battle/golden_cyclone_preview.gd",
    }.items():
        if receipt.get(field) != sha(root / relative):
            raise ValueError("Stale Godot capture; regenerate viewport frames: " + field)
    exports = {}
    for mode, entry in receipt["modes"].items():
        if entry["hit_times_ms"] != [930.0]:
            raise ValueError("Godot did not emit one correctly timed hit")
        if {f["source_frame"] for f in entry["frames"]} != set(range(1, 23)):
            raise ValueError("Godot capture does not show all 22 body frames")
        digests = []
        for frame in entry["frames"]:
            digest = sha(local(root, (REVIEW / frame["path"]).as_posix()))
            if digest != frame.get("sha256"):
                raise ValueError("Godot capture PNG changed after receipt")
            digests.append(digest)
        if len(set(digests)) < 22:
            raise ValueError("Blank/static viewport capture cannot prove the animation")
        images = [Image.open(local(root, (REVIEW / f["path"]).as_posix())).convert("RGBA") for f in entry["frames"]]
        if any(image.size != (1024, 576) for image in images):
            raise ValueError("Unexpected actual viewport dimensions")
        target = root / REVIEW / ("hero_golden_cyclone.gif" if mode == "normal" else "hero_golden_cyclone_slow_no_effects.gif")
        exports[mode] = save_gif(images, [f["duration_ms"] for f in entry["frames"]], target)
    write(root / REVIEW / "godot_gif_verification.json", exports)
    return exports


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate", "build", "stage-dependencies", "pin-review", "record-source", "encode-godot", "request-capture"))
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--partial", action="store_true")
    parser.add_argument("--asset-source", type=Path)
    parser.add_argument("--frame", type=int)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--request")
    parser.add_argument("--reviewed-single-character", action="store_true")
    args = parser.parse_args()
    if args.command == "request-capture":
        path = args.root / "game_factory/golden_cyclone/v001/metadata/capture_once.flag"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("One capture on the next launch of golden_cyclone_preview.tscn\n", encoding="utf-8", newline="\n")
        result = {"capture_requested": True, "scene": "res://scenes/battle/golden_cyclone_preview.tscn"}
    elif args.command == "encode-godot":
        result = encode_godot(args.root)
    elif args.command == "record-source":
        if not args.reviewed_single_character or args.frame is None or args.source is None or not args.request:
            parser.error("record-source requires --frame --source --request --reviewed-single-character")
        result = record_source(args.root, args.frame, args.source, args.request)
    elif args.command == "pin-review":
        result = pin_review(args.root)
    elif args.command == "stage-dependencies":
        if args.asset_source is None:
            parser.error("stage-dependencies requires --asset-source")
        result = stage_dependencies(args.root, args.asset_source)
    else:
        result = validate(args.root, complete=not args.partial) if args.command == "validate" else build(args.root)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
