"""Audit which PNG files the game actually uses (local helper, read only).

Usage: python tools/audit_art_usage.py [--json out.json]

A PNG counts as USED when its path or file name appears in game code (scenes/**/*.gd,
*.tscn, map_factory/scripts/*.gd, tools/*.gd), in the latest compiled map (texture paths of
map_factory/maps/*/latest.json and layers/latest.json) or in a catalog the game loads
(map_factory/metadata/asset_index.json, game_factory/environment/catalog.json,
game_factory/character_manifest.json). SUPERSEDED means a same-named HD runtime texture exists in
assets_hd/runtime. Indexes (FILES.md, INDEX.md) and docs are ignored on purpose, because they list
every file. The result is a hint for a human, never an automatic delete list.

Execution provenance: Agent: claude (Claude Code); model: Sonnet 5.5.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
IMAGE_DIRS = ("assets", "assets_generated", "map_factory/parts", "map_factory/candidates",
              "map_factory/references", "room_previews", "docs/previews", "game_factory", "assets_hd/runtime")
CODE_GLOBS = ("scenes/**/*.gd", "scenes/**/*.tscn", "map_factory/scripts/*.gd", "tools/*.gd", "project.godot")
DATA_FILES = ("map_factory/metadata/asset_index.json", "game_factory/environment/catalog.json",
              "game_factory/character_manifest.json", "game_factory/environment/room.json")


def load_text() -> str:
    parts = []
    for pattern in CODE_GLOBS:
        for path in ROOT.glob(pattern):
            if path.is_file():
                parts.append(path.read_text(encoding="utf-8", errors="ignore"))
    for name in DATA_FILES:
        path = ROOT / name
        if path.is_file():
            parts.append(path.read_text(encoding="utf-8", errors="ignore"))
    for path in ROOT.glob("map_factory/maps/*/latest.json"):
        parts.append(path.read_text(encoding="utf-8", errors="ignore"))
    for path in ROOT.glob("map_factory/maps/*/layers/latest.json"):
        parts.append(path.read_text(encoding="utf-8", errors="ignore"))
    return "\n".join(parts)


def audit() -> dict:
    text = load_text()
    names_in_text = set(re.findall(r"[\w\-. ]+?\.png", text))
    runtime = {p.name for p in (ROOT / "assets_hd" / "runtime").glob("*.png")}
    report: dict = {}
    for directory in IMAGE_DIRS:
        base = ROOT / directory
        rows = {"total": 0, "used": 0, "superseded_unused": 0, "unused": 0, "size_mb": 0.0, "unused_files": []}
        for path in sorted(base.rglob("*.png")) if base.is_dir() else []:
            rows["total"] += 1
            rows["size_mb"] += path.stat().st_size / 1_048_576
            relative = path.relative_to(ROOT).as_posix()
            used = relative in text or path.name in names_in_text
            if used:
                rows["used"] += 1
            elif path.name in runtime and directory != "assets_hd/runtime":
                rows["superseded_unused"] += 1
                rows["unused_files"].append(relative)
            else:
                rows["unused"] += 1
                rows["unused_files"].append(relative)
        rows["size_mb"] = round(rows["size_mb"], 1)
        report[directory] = rows
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json")
    args = parser.parse_args()
    report = audit()
    for directory, rows in report.items():
        print(f"{directory:28s} total {rows['total']:4d}  used {rows['used']:4d}  superseded+unused {rows['superseded_unused']:4d}  unused {rows['unused']:4d}  {rows['size_mb']} MB")
    if args.json:
        Path(args.json).write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
