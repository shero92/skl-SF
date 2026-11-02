#!/usr/bin/env python3
"""Validate battle weapon socket JSON without writing files.

Each document contains an attack_id and a non-empty frames array. Each frame
declares its weapon, socket, layer and annotation/measurement provenance.
Coordinates are sprite-local pixels; rotation is in [-180, 180] degrees.
Provenance is required metadata, not independent verification of its accuracy.

The JSON schema describes record structure; this standard-library validator also
rejects duplicate frame names, duplicate JSON keys and non-finite numbers.
Agent: codex. Model: GPT-6 (session identity).
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys

WEAPON_IDS = ("WPN_HERO_BASIC_SWORD", "WPN_IRON_SWORD")
LAYERS = ("behind_hand", "in_hand", "front")
SOURCE_METHODS = ("annotation", "measurement")


def _object(value: object, required: tuple[str, ...], path: str,
            errors: list[str]) -> bool:
    if not isinstance(value, dict):
        errors.append(f"{path}: expected object")
        return False
    for key in required:
        if key not in value:
            errors.append(f"{path}.{key}: missing required field")
    for key in value:
        if key not in required:
            errors.append(f"{path}.{key}: unknown field")
    return True


def _text(value: object, path: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{path}: expected non-empty string")


def _choice(value: object, choices: tuple[str, ...], path: str,
            errors: list[str]) -> None:
    if value not in choices:
        errors.append(f"{path}: expected one of {', '.join(choices)}")


def _number(value: object, path: str, errors: list[str]) -> bool:
    # bool is an int subclass, but JSON booleans are not numeric coordinates.
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        errors.append(f"{path}: expected finite number")
        return False
    if isinstance(value, float) and not math.isfinite(value):
        errors.append(f"{path}: expected finite number")
        return False
    return True


def validate(data: object) -> list[str]:
    """Return named validation errors; an empty list means the document is valid."""
    errors: list[str] = []
    if not _object(data, ("attack_id", "frames"), "$", errors):
        return errors
    if "attack_id" in data:
        _text(data["attack_id"], "$.attack_id", errors)
    if "frames" not in data:
        return errors
    frames = data["frames"]
    if not isinstance(frames, list) or not frames:
        errors.append("$.frames: expected non-empty array")
        return errors

    seen: set[str] = set()
    for index, frame in enumerate(frames):
        path = f"$.frames[{index}]"
        if not _object(frame, ("frame_name", "weapon_id", "socket", "layer",
                               "provenance"), path, errors):
            continue
        if "frame_name" in frame:
            name = frame["frame_name"]
            _text(name, f"{path}.frame_name", errors)
            if isinstance(name, str):
                if name in seen:
                    errors.append(f"{path}.frame_name: duplicate frame {name!r}")
                seen.add(name)
        if "weapon_id" in frame:
            _choice(frame["weapon_id"], WEAPON_IDS, f"{path}.weapon_id", errors)
        if "layer" in frame:
            _choice(frame["layer"], LAYERS, f"{path}.layer", errors)
        if "socket" in frame:
            socket = frame["socket"]
            socket_path = f"{path}.socket"
            if _object(socket, ("x", "y", "rotation_deg"), socket_path, errors):
                for key in ("x", "y", "rotation_deg"):
                    if key not in socket:
                        continue
                    value = socket[key]
                    if _number(value, f"{socket_path}.{key}", errors):
                        if key == "rotation_deg" and not -180 <= value <= 180:
                            errors.append(
                                f"{socket_path}.rotation_deg: out of range [-180, 180]"
                            )
        if "provenance" in frame:
            source = frame["provenance"]
            source_path = f"{path}.provenance"
            if _object(source, ("method", "reference"), source_path, errors):
                if "method" in source:
                    _choice(source["method"], SOURCE_METHODS,
                            f"{source_path}.method", errors)
                if "reference" in source:
                    _text(source["reference"], f"{source_path}.reference", errors)
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
    """Read one UTF-8 JSON file and report syntax, I/O and validation errors."""
    try:
        data = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
        )
    except (OSError, ValueError, RecursionError) as exc:
        return [f"cannot read valid socket JSON: {exc}"]
    return validate(data)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", type=Path, help="socket JSON files to validate")
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
