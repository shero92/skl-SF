"""Prepare a fresh checkout or worktree so Map Factory captures work (TASK-0105).

Usage: python tools/prepare_map_workspace.py [--source PATH] [--copy] [--no-import]

Many PNGs are git-ignored locally (assets_generated, assets_hd/runtime, map_factory/parts,
reference images), so a new worktree misses them and a capture fails with confusing
`RoomFactory not declared` errors. This tool lists the files that exist in a source checkout
(default: the main worktree) but not here, optionally copies them (`--copy`, never
overwrites) and runs the Godot import so class names are registered. It exits 1 while files
are missing and not copied.

Execution provenance: Agent: claude (Claude Code); model: Sonnet 5.5.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PNG_DIRS = ("assets_generated", "assets_hd/runtime", "map_factory/parts", "map_factory/references")


def main_worktree(root: Path = ROOT) -> Path | None:
    result = subprocess.run(["git", "worktree", "list", "--porcelain"], cwd=root, capture_output=True, text=True)
    if result.returncode != 0:
        return None
    for line in result.stdout.splitlines():
        if line.startswith("worktree "):
            return Path(line.split(" ", 1)[1])
    return None


def missing_files(source: Path, target: Path, directories: tuple[str, ...] = PNG_DIRS) -> list[str]:
    """Relative POSIX paths of PNGs present in source but absent in target."""
    missing = []
    for directory in directories:
        base = source / directory
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.png")):
            relative = path.relative_to(source)
            if not (target / relative).exists():
                missing.append(relative.as_posix())
    return missing


def copy_missing(source: Path, target: Path, relative_paths: list[str]) -> int:
    copied = 0
    for relative in relative_paths:
        destination = target / relative
        if destination.exists():
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / relative, destination)
        copied += 1
    return copied


def godot_path(root: Path = ROOT) -> str | None:
    config = root / ".agents" / "planner" / "config.json"
    try:
        value = json.loads(config.read_text(encoding="utf-8")).get("godot_executable")
    except (OSError, ValueError):
        return None
    return value if isinstance(value, str) and Path(value).is_file() else None


def run_import(root: Path = ROOT) -> tuple[bool, str]:
    godot = godot_path(root)
    if godot is None:
        return False, "configured godot_executable is not installed here"
    result = subprocess.run([godot, "--headless", "--path", str(root), "--import"], capture_output=True, text=True, timeout=600)
    return result.returncode == 0, (result.stdout + result.stderr)[-400:]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, help="checkout that holds the ignored PNGs (default: main worktree)")
    parser.add_argument("--copy", action="store_true", help="copy missing PNGs from the source")
    parser.add_argument("--no-import", action="store_true", help="skip the Godot import step")
    args = parser.parse_args(argv)
    source = args.source or main_worktree()
    missing: list[str] = []
    if source is None or source.resolve() == ROOT.resolve():
        print("source: this checkout (nothing to compare)")
    else:
        missing = missing_files(source, ROOT)
        print(f"missing PNGs compared with {source}: {len(missing)}")
        if missing and args.copy:
            print(f"copied: {copy_missing(source, ROOT, missing)}")
            missing = missing_files(source, ROOT)
        for name in missing[:10]:
            print(f"  missing: {name}")
    if not args.no_import:
        ok, tail = run_import(ROOT)
        print("godot import:", "ok" if ok else "FAILED - " + tail)
        if not ok:
            return 1
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
