#!/usr/bin/env python3
"""Validate battle socket JSON without modifying source files or images.

Agent: codex. Model: GPT-6.
Uses the standard library; mirrors weapon_sockets.schema.json and additionally
checks finite numbers and unique frame names. Provenance must cite annotation
or measurement evidence; this tool cannot establish the truth of that evidence.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys

WEAPON_IDS = ("WPN_HERO_BASIC_SWORD", "WPN_IRON_SWORD")
LAYERS = ("behind_hand", "in_hand", "front")
METHODS = ("annotation", "measurement")


def validate(data: object) -> list[str]:
    """Return named validation errors, or an empty list for a valid attack."""
    errors: list[str] = []

    def error(path: str, reason: str) -> None:
        errors.append(f"{path}: {reason}")

    def fields(value: object, path: str, required: tuple[str, ...]) -> bool:
        if not isinstance(value, dict):
            error(path, "expected object")
            return False
        for key in required:
            if key not in value:
                error(f"{path}.{key}", "missing required field")
        for key in value:
            if key not in required:
                error(f"{path}.{key}", "unknown field")
        return True

    def nonblank(value: object, path: str) -> None:
        if not isinstance(value, str) or not value.strip():
            error(path, "expected nonblank string")

    if not fields(data, "$", ("attack_id", "frames")):
        return errors
    nonblank(data.get("attack_id"), "$.attack_id")
    frames = data.get("frames")
    if not isinstance(frames, list) or not frames:
        error("$.frames", "expected nonempty array")
        return errors

    seen: set[str] = set()
    for index, frame in enumerate(frames):
        path = f"$.frames[{index}]"
        if not fields(frame, path, ("frame_name", "socket", "layer",
                                    "weapon_ids", "provenance")):
            continue
        name = frame.get("frame_name")
        nonblank(name, f"{path}.frame_name")
        if isinstance(name, str):
            if name in seen:
                error(f"{path}.frame_name", f"duplicate frame {name!r}")
            seen.add(name)

        socket = frame.get("socket")
        if fields(socket, f"{path}.socket", ("x", "y", "rotation_deg")):
            for key in ("x", "y", "rotation_deg"):
                value = socket.get(key)
                # Integers are finite without conversion to a bounded float.
                finite = (type(value) is int or
                          (type(value) is float and math.isfinite(value)))
                if not finite:
                    error(f"{path}.socket.{key}", "expected finite number")
                elif key == "rotation_deg" and not -180 <= value <= 180:
                    error(f"{path}.socket.{key}", "rotation out of range [-180, 180]")

        if frame.get("layer") not in LAYERS:
            error(f"{path}.layer", "invalid layer")
        weapons = frame.get("weapon_ids")
        if not isinstance(weapons, list) or not weapons:
            error(f"{path}.weapon_ids", "expected nonempty array")
        else:
            for weapon_index, weapon in enumerate(weapons):
                weapon_path = f"{path}.weapon_ids[{weapon_index}]"
                if weapon not in WEAPON_IDS:
                    error(weapon_path, "unsupported weapon id")
                if weapon in weapons[:weapon_index]:
                    error(weapon_path, "duplicate weapon id")

        provenance = frame.get("provenance")
        if fields(provenance, f"{path}.provenance", ("method", "reference")):
            if provenance.get("method") not in METHODS:
                error(f"{path}.provenance.method",
                      "source must be annotation or measurement")
            nonblank(provenance.get("reference"), f"{path}.provenance.reference")
    return errors


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON number {value}")


def validate_file(path: Path) -> list[str]:
    """Read one JSON file and report parse, I/O or socket validation errors."""
    try:
        data = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
        )
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        return [f"cannot read valid JSON: {exc}"]
    return validate(data)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", type=Path, nargs="+", help="socket JSON files")
    args = parser.parse_args(argv)
    failed = 0
    for path in args.files:
        errors = validate_file(path)
        if errors:
            failed += 1
            print(f"FAIL {path}")
            for error in errors:
                print(f"  {error}")
        else:
            print(f"PASS {path}")
    print(f"{len(args.files) - failed}/{len(args.files)} files passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
