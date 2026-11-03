"""Capture a registered environment snapshot with Godot and verify its evidence.

Usage: python tools/hero_room_capture_evidence.py --version 14 --target TARGET
       --godot GODOT --capture-id REVIEW_ID

The target must be the original owner PNG. Outputs use a new capture-id directory;
existing directories are rejected. The tool runs Godot with a real display and
the gl_compatibility renderer. On Linux CI provide a virtual X11 display.
Use --prepare-only to write the request and print the exact Godot invocation,
then use the same arguments with --verify-only after running that invocation.
No image is synthesised and no visual approval is inferred.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
TARGET_HASH = "47a7855cf242302108e1a6b9eaf4bfd3422f9f8c812585fa4da5bcaea948668b"
CANVAS = [1536, 1024]
ZONES = {
    "sea": [0, 0, 1536, 360],
    "rear_arch": [555, 0, 990, 390],
    "left_architecture": [100, 130, 640, 700],
    "right_architecture": [965, 100, 1510, 710],
    "floor": [190, 315, 1390, 800],
    "bed": [220, 335, 580, 665],
    "study": [1000, 430, 1350, 675],
    "compass": [635, 545, 890, 730],
    "vegetation_and_perimeter": [90, 640, 1460, 950],
    "stairs": [655, 755, 875, 1024],
    "lighting_and_shadows": [0, 0, 1536, 1024],
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def png_size(path: Path) -> list[int]:
    with path.open("rb") as stream:
        header = stream.read(24)
    if (len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n"
            or header[12:16] != b"IHDR"):
        raise ValueError("Missing or invalid PNG header")
    return list(struct.unpack(">II", header[16:24]))


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_new(path: Path, data: dict) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(data, stream, indent=2, ensure_ascii=True)
        stream.write("\n")


def texture_paths(value) -> set[str]:
    """Collect literal registered PNG paths without assuming registry field names."""
    found = set()
    if isinstance(value, dict):
        for key, child in value.items():
            found.update(texture_paths(key))
            found.update(texture_paths(child))
    elif isinstance(value, list):
        for child in value:
            found.update(texture_paths(child))
    elif isinstance(value, str) and value.lower().endswith(".png"):
        found.add(value.removeprefix("res://").replace("\\", "/"))
    return found


def resource(root: Path, name: str) -> Path:
    path = (root / name.removeprefix("res://")).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Resource escapes repository")
    return path


def forbidden_texture(name: str) -> bool:
    parts = re.split(r"[/_. -]+", name.lower())
    return any(part in {"hero", "neru", "character", "characters",
                        "portrait", "portraits", "reference", "references"}
               for part in parts)


def prepare(root: Path, version: int, target: Path, capture_id: str) -> tuple[Path, dict]:
    if isinstance(version, bool) or not isinstance(version, int) or version <= 13:
        raise ValueError("Specify a new room version greater than 13")
    if not re.fullmatch(r"[a-z][a-z0-9_]{2,63}", capture_id):
        raise ValueError("Unsafe capture identity")
    if png_size(target) != CANVAS or digest(target) != TARGET_HASH:
        raise ValueError("Original target dimensions or SHA256 do not match")
    maps = root / "map_factory" / "maps"
    registry = read_json(maps / ("index" + ".json"))
    map_id = "hero_room_01"
    entry = registry["maps"][map_id]
    if version > int(entry["version"]):
        raise ValueError("Requested version is not published")
    snapshot = maps / map_id / "versions" / ("v%04d" % version + ".json")
    snapshot_hash = digest(snapshot)
    data = read_json(snapshot)
    if data.get("canvas_size", CANVAS) != CANVAS:
        raise ValueError("Snapshot must use the reference canvas")
    assets = read_json(root / "map_factory" / "metadata" /
                       ("environment_assets_v2" + ".json"))
    allowed = sorted(texture_paths(assets))
    if not allowed:
        raise ValueError("Environment registry contains no texture paths")
    for name in allowed:
        resource(root, name)
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, check=True,
        capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(
        ["git", "status", "--porcelain"], cwd=root, check=True,
        capture_output=True, text=True).stdout.strip()
    output = root / "docs" / "previews" / "map_factory_renders" / capture_id
    request = {
        "capture_id": capture_id,
        "commit": commit,
        "working_tree_dirty": bool(dirty),
        "target_sha256": digest(target),
        "registry_sha256": digest(maps / ("index" + ".json")),
        "asset_registry_sha256": digest(root / "map_factory" / "metadata" /
                                        ("environment_assets_v2" + ".json")),
        "output_dir": "res://" + output.relative_to(root).as_posix() + "/",
        "allowed_textures": allowed,
        "cases": [{
            "id": map_id, "version": version,
            "file": "%s_v%04d.png" % (map_id, version),
            "snapshot_sha256": snapshot_hash,
            "canvas_size": CANVAS,
        }],
    }
    return output, request


def verify(root: Path, output: Path, expected: dict) -> dict:
    case = expected["cases"][0]
    receipt = read_json(output / (Path(case["file"]).stem + ".json"))
    render = output / case["file"]
    required = {
        "capture_id": expected["capture_id"],
        "commit": expected["commit"],
        "target_sha256": expected["target_sha256"],
        "snapshot_sha256": case["snapshot_sha256"],
        "map_id": case["id"], "version": case["version"],
        "canvas_size": CANVAS, "environment_only": True,
    }
    for key, value in required.items():
        if receipt.get(key) != value:
            raise ValueError("Invalid provenance: " + key)
    if png_size(render) != CANVAS or receipt.get("render_sha256") != digest(render):
        raise ValueError("Render dimensions or hash mismatch")
    placements = receipt.get("resolved_assets")
    if not isinstance(placements, list) or not placements:
        raise ValueError("Missing resolved placement provenance")
    allowed = set(expected["allowed_textures"])
    missing, unregistered = [], []
    for placement in placements:
        name = placement["texture_path"].removeprefix("res://")
        if forbidden_texture(name):
            raise ValueError("Non-environment texture rejected")
        if name not in allowed:
            unregistered.append(name)
        path = resource(root, name)
        if not path.is_file():
            missing.append(name)
        elif placement.get("texture_sha256") != digest(path):
            raise ValueError("Source texture hash mismatch")
        bounds = placement.get("bounds")
        if (not isinstance(bounds, list) or len(bounds) != 4
                or any(type(v) not in (int, float) for v in bounds)
                or not all(float("-inf") < v < float("inf") for v in bounds)
                or bounds[2] <= 0 or bounds[3] <= 0):
            raise ValueError("Invalid rendered placement bounds")
    if missing or unregistered:
        raise ValueError("Missing or unregistered source textures: " +
                         repr(sorted(set(missing + unregistered))))
    findings = {}
    for zone, (left, top, right, bottom) in ZONES.items():
        hits = []
        for index, placement in enumerate(placements):
            x, y, width, height = placement["bounds"]
            if x < right and x + width > left and y < bottom and y + height > top:
                hits.append(index)
        findings[zone] = {
            "region": [left, top, right, bottom],
            "intersecting_placements": hits,
            "texture_paths": sorted({placements[i]["texture_path"] for i in hits}),
            "structural_finding": (
                "Rendered sprite bounds intersect region; semantic composition unverified"
                if hits else "No registered sprite bounds intersect region; inspect procedural background"),
            "discrepancy": "Not measured; compare reference with render in this region",
            "human_review_required": True,
        }
    paths = sorted({p["texture_path"] for p in placements})
    return {
        **required, "render_sha256": digest(render),
        "working_tree_dirty": expected["working_tree_dirty"],
        "registry_sha256": expected["registry_sha256"],
        "asset_registry_sha256": expected["asset_registry_sha256"],
        "resolved_assets": placements, "texture_paths": paths,
        "distinct_texture_count": len(paths), "placement_count": len(placements),
        "missing_paths": missing, "unregistered_paths": unregistered,
        "structural_zones": findings,
        "visual_approval": False,
        "similarity": {"score": None, "authoritative": False,
                       "reason": "Human reference comparison is required"},
        "optional_character_overlay": "Absent; request a separate gameplay capture from Claude",
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", type=int, required=True)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--capture-id", required=True)
    parser.add_argument("--godot", default="godot")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--prepare-only", action="store_true")
    mode.add_argument("--verify-only", action="store_true")
    args = parser.parse_args(argv)
    try:
        output, request = prepare(ROOT, args.version, args.target, args.capture_id)
        manifest = output / ("request" + ".json")
        if args.verify_only:
            if read_json(manifest) != request:
                raise ValueError("Capture inputs changed since preparation")
        else:
            output.mkdir(parents=True, exist_ok=False)
            write_new(manifest, request)
        command = [
            args.godot, "--path", str(ROOT), "--rendering-method",
            "gl_compatibility", "--script", "res://tools/capture_map_previews.gd",
            "--", "--capture-manifest", str(manifest),
        ]
        if args.prepare_only:
            print(subprocess.list2cmdline(command))
            return 0
        if not args.verify_only:
            subprocess.run(command, cwd=ROOT, check=True, timeout=300)
        report = verify(ROOT, output, request)
        write_new(output / ("evidence" + ".json"), report)
        print("Capture evidence verified; visual_approval: false")
        return 0
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        print("Capture failed: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
