#!/usr/bin/env python3
"""Technical validation of production PNG graphics and their metadata (TASK-0129).

Usage: python tools/graphics_validation.py [--all | --changed] [--base origin/main] [--root DIR]

Covers assets/characters/, assets_generated/, assets_hd/runtime/ and map_factory/parts/. It only reads files;
it never edits a PNG, never changes a QA or visual approval state, and a pass is a technical result only,
not artistic approval (ADR-005, ADR-009). With --changed only PNGs that differ from --base (plus untracked
ones) and the metadata they belong to are checked, so a small commit stays cheap.

Checks: PNG integrity and format, non-empty visible pixels, alpha where the art is a sprite (opaque tiles,
backgrounds and UI listed as such in their metadata are allowed), catalog dimensions/paths/duplicate IDs,
HD runtime textures vs hd_map.json (scale x native size), character animation frames (files exist, frame
counts, one canvas per animation and per manifest canvas size, "complete" only with real frames).

Execution provenance: Agent: claude (Claude Code); model: Sonnet 5.5.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

from PIL import Image, UnidentifiedImageError

ROOT = Path(__file__).resolve().parents[1]
PRODUCTION_ROOTS = ("assets/characters/", "assets_generated/", "assets_hd/runtime/", "map_factory/parts/")
OPAQUE_CATEGORIES = {"floors", "floor", "environment", "ui", "background"}
# Reference images, QA captures, rejected attempts and per-generation caches are archives, not production art.
ARCHIVE_DIRS = {"references", "godot_qa", "rejected", "rejected_sources", "previews", "preview_dependencies"}


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.checked_pngs = 0

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def res_path(root: Path, value: str) -> Path:
    return root / value.removeprefix("res://")


def is_archive(relative: str) -> bool:
    parts = Path(relative).parts[:-1]
    return any(part in ARCHIVE_DIRS or (len(part) == 32 and all(c in "0123456789abcdef" for c in part)) for part in parts)


def production_pngs(root: Path) -> list[str]:
    found: list[str] = []
    for prefix in PRODUCTION_ROOTS:
        base = root / prefix
        if base.is_dir():
            found += [p.relative_to(root).as_posix() for p in base.rglob("*.png")]
    return sorted(p for p in found if not is_archive(p))


def changed_paths(root: Path, base: str) -> set[str] | None:
    """Paths that differ from the merge base (committed, staged, unstaged) plus untracked files; None if git fails."""
    def run(*args: str) -> subprocess.CompletedProcess:
        return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    merge_base = run("merge-base", base, "HEAD")
    if merge_base.returncode != 0:
        return None
    diff = run("diff", "--name-only", merge_base.stdout.strip())
    untracked = run("ls-files", "--others", "--exclude-standard")
    if diff.returncode != 0 or untracked.returncode != 0:
        return None
    return set(diff.stdout.split("\n")) | set(untracked.stdout.split("\n")) - {""}


def opaque_allowed(root: Path, relative: str) -> bool:
    """A PNG may lack alpha when its metadata marks it as a tile/background/UI image."""
    index = root / "map_factory/metadata/asset_index.json"
    if relative.startswith("map_factory/parts/") and index.is_file():
        for record in load_json(index).get("assets", []):
            if record.get("texture_path", "").removeprefix("res://") == relative:
                return record.get("category") in OPAQUE_CATEGORIES
    manifest = root / "assets_generated/manifest.json"
    if relative.startswith("assets_generated/") and manifest.is_file():
        name = Path(relative).name
        for record in load_json(manifest).get("assets", []):
            if name.startswith(str(record.get("asset_id", "\0")) + "__"):
                return not record.get("transparent_background", True)
    if relative.startswith("assets_hd/runtime/") and manifest.is_file():
        return opaque_allowed(root, "assets_generated/" + Path(relative).name)
    return False


def check_png(root: Path, relative: str, report: Report) -> tuple[int, int] | None:
    path = root / relative
    report.checked_pngs += 1
    try:
        with Image.open(path) as image:
            image.load()
            if image.format != "PNG":
                report.error(f"{relative}: not a PNG (format {image.format})")
                return None
            size = image.size
            rgba = image.convert("RGBA")
            has_alpha = "A" in image.getbands() or "transparency" in image.info
    except (OSError, ValueError, UnidentifiedImageError) as exc:
        report.error(f"{relative}: unreadable PNG ({exc})")
        return None
    if rgba.getchannel("A").getbbox() is None:
        report.error(f"{relative}: fully transparent image")
    if not has_alpha and not opaque_allowed(root, relative):
        report.error(f"{relative}: no alpha channel but the metadata does not mark it as an opaque tile/background/UI image")
    return size


def check_hd_runtime(root: Path, report: Report, selected: set[str] | None) -> None:
    hd_map = root / "assets_hd/hd_map.json"
    if not hd_map.is_file():
        return
    config = load_json(hd_map)
    scale = int(config.get("scale", 2))
    for name, entry in config.get("map", {}).items():
        file_name = Path(name).name
        relative = f"assets_hd/runtime/{file_name}"
        if selected is not None and relative not in selected and f"assets_generated/{name}" not in selected:
            continue
        native = entry.get("native_size")
        if native is None:
            continue
        twin = root / relative
        if not twin.is_file():
            report.error(f"{relative}: HD runtime texture missing for hd_map entry {name}")
            continue
        try:
            with Image.open(twin) as image:
                size = list(image.size)
        except (OSError, ValueError, UnidentifiedImageError):
            continue  # reported by the PNG check
        expected = [int(value) * scale for value in native]
        if size != expected:
            report.error(f"{relative}: size {size} != {scale} x native {list(native)} recorded in hd_map.json")


def check_generated_manifest(root: Path, report: Report, selected: set[str] | None) -> None:
    manifest = root / "assets_generated/manifest.json"
    if not manifest.is_file():
        return
    records = load_json(manifest).get("assets", [])
    seen: set[tuple[str, str]] = set()
    for record in records:
        key = (str(record.get("asset_id", "")), str(record.get("orientation", "default")))
        if key in seen:
            report.error(f"assets_generated/manifest.json: duplicate asset_id/orientation {key[0]}/{key[1]}")
        seen.add(key)
    by_key = {(str(r.get("asset_id", "")), str(r.get("orientation", "default"))): r for r in records}
    # File names are <id>__<category>__<name>__<orientation>__<footprint>__<WxH>.png
    for path in (root / "assets_generated").rglob("*.png"):
        relative = path.relative_to(root).as_posix()
        if is_archive(relative) or (selected is not None and relative not in selected):
            continue
        fields = path.stem.split("__")
        if len(fields) < 6:
            continue
        record = by_key.get((fields[0], fields[3]))
        if record is None:
            report.error(f"{relative}: no entry {fields[0]}/{fields[3]} in assets_generated/manifest.json")
            continue
        try:
            with Image.open(path) as image:
                size = image.size
        except (OSError, ValueError, UnidentifiedImageError):
            continue
        native = (int(record.get("native_width", 0)), int(record.get("native_height", 0)))
        if native != (0, 0) and size != native:
            report.error(f"{relative}: size {list(size)} != native {list(native)} in assets_generated/manifest.json")


def check_part_catalog(root: Path, report: Report, selected: set[str] | None) -> None:
    index = root / "map_factory/metadata/asset_index.json"
    if not index.is_file():
        return
    seen: set[str] = set()
    for record in load_json(index).get("assets", []):
        ident = str(record.get("id", ""))
        if ident in seen:
            report.error(f"asset_index.json: duplicate id {ident}")
        seen.add(ident)
        relative = record.get("texture_path", "").removeprefix("res://")
        if not relative.startswith("map_factory/parts/"):
            continue
        if selected is not None and relative not in selected:
            continue
        path = root / relative
        if not path.is_file():
            report.error(f"{relative}: part {ident} is registered in asset_index.json but the PNG is missing")
            continue
        try:
            with Image.open(path) as image:
                size = list(image.size)
        except (OSError, ValueError, UnidentifiedImageError):
            continue
        if size != record.get("pixel_size"):
            report.error(f"{relative}: size {size} != pixel_size {record.get('pixel_size')} of {ident}")


def check_characters(root: Path, report: Report, selected: set[str] | None) -> None:
    manifest = root / "game_factory/character_manifest.json"
    if not manifest.is_file():
        return
    for character in load_json(manifest).get("characters", []):
        name = character.get("slug", character.get("character_id", "?"))
        canvases = {"map_": character.get("map_sprite_canvas_size"), "battle_": character.get("battle_sprite_canvas_size")}
        for animation, record in character.get("animations", {}).items():
            frames = record.get("frames", [])
            if record.get("complete") and not frames:
                report.error(f"{name}/{animation}: marked complete but has no frames")
            paths = [res_path(root, frame).relative_to(root).as_posix() for frame in frames]
            if selected is not None and not any(p in selected for p in paths):
                continue
            sizes = set()
            for relative in paths:
                path = root / relative
                if not path.is_file():
                    report.error(f"{name}/{animation}: frame file missing: {relative}")
                    continue
                try:
                    with Image.open(path) as image:
                        sizes.add(image.size)
                except (OSError, ValueError, UnidentifiedImageError):
                    continue
            if len(sizes) > 1:
                report.error(f"{name}/{animation}: frames use different canvases {sorted(sizes)}")
            expected = next((canvases[p] for p in canvases if animation.startswith(p)), None)
            if sizes and expected and not report_ok_canvas(sizes, expected):
                report.warn(f"{name}/{animation}: canvas {sorted(sizes)} differs from the manifest canvas {expected}")
        for direction_map in ("map_idle_frames", "map_walk_frames"):
            for direction, frames in character.get(direction_map, {}).items():
                kind = "idle" if "idle" in direction_map else "walk"
                key = f"map_{direction}_{kind}"
                animation = character.get("animations", {}).get(key)
                if animation is not None and animation.get("frames") != frames:
                    report.error(f"{name}/{key}: animations frame list differs from {direction_map}[{direction}]")


def report_ok_canvas(sizes: set, expected) -> bool:
    return all(list(size) == list(expected) for size in sizes)


def validate(root: Path, changed: set[str] | None) -> Report:
    report = Report()
    pngs = production_pngs(root)
    selected = None
    if changed is not None:
        selected = {p for p in pngs if p in changed}
        for metadata in ("assets_hd/hd_map.json", "assets_generated/manifest.json", "map_factory/metadata/asset_index.json",
                         "game_factory/character_manifest.json"):
            if metadata in changed:
                selected = None  # a metadata edit can affect any entry: validate that family fully
                break
    targets = pngs if selected is None else sorted(selected)
    for relative in targets:
        check_png(root, relative, report)
    check_part_catalog(root, report, selected)
    check_generated_manifest(root, report, selected)
    check_hd_runtime(root, report, selected)
    check_characters(root, report, selected)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--all", action="store_true", help="validate every production PNG (default)")
    mode.add_argument("--changed", action="store_true", help="only PNGs and metadata changed vs --base")
    parser.add_argument("--base", default="origin/main")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    changed = None
    if args.changed:
        changed = changed_paths(args.root, args.base)
        if changed is None:
            print(f"cannot compute changes against {args.base}; validating everything", file=sys.stderr)
        elif not any(p.startswith(PRODUCTION_ROOTS) or p.endswith(("hd_map.json", "manifest.json", "asset_index.json")) for p in changed):
            print("no production graphics changed; nothing to validate")
            return 0
    report = validate(args.root, changed)
    print(json.dumps({"png_checked": report.checked_pngs, "errors": report.errors, "warnings": report.warnings[:40]}, indent=2))
    return 1 if report.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
