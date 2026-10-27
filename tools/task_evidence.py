"""Read-only, fail-closed evidence gates for optional task prerequisites.

An evidence_manifest is a repository-relative JSON object with a nonempty
requirements array. Every requirement has kind, status='approved', approved_at,
approved_by (or reviewer), and provenance={source, kind}. Reference requirements
add path, sha256 and pixel_size=[width,height]. Measurement requirements add
scope and target. Visual approvals add scope, target, owner_approved=true,
producer, producer_session, reviewer_session and target_sha256 or target_commit.
These checks validate recorded evidence; they never manufacture approval.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import struct


def _text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _contained(root: Path, value: object) -> Path:
    if not _text(value) or "\\" in value or ":" in value:
        raise ValueError("expected a normalized repository-relative path")
    relative = PurePosixPath(value)
    if relative.is_absolute() or any(part in (".", "..") for part in value.split("/")):
        raise ValueError("path traversal is forbidden")
    if str(relative) != value:
        raise ValueError("path must be normalized")
    resolved = (root / value).resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError("path escapes repository (including symlinks)")
    return resolved


def _approval_errors(item: dict) -> list[str]:
    errors = []
    if item.get("status") != "approved":
        errors.append("status must be approved")
    if not _text(item.get("reviewer") or item.get("approved_by")):
        errors.append("reviewer or approved_by is required")
    if not _text(item.get("approved_at")):
        errors.append("approved_at is required")
    provenance = item.get("provenance")
    if not isinstance(provenance, dict) or not all(_text(provenance.get(k)) for k in ("source", "kind")):
        errors.append("provenance source and kind are required")
    return errors


def _reference_errors(item: dict, root: Path) -> list[str]:
    value = item.get("path")
    try:
        path = _contained(root, value)
    except (ValueError, OSError, RuntimeError) as exc:
        return [str(exc)]
    allowed = r"(?:map_factory/references/|\.agents/planner/goals/GOAL-\d{4}/references/).+\.png"
    if not re.fullmatch(allowed, value) or not re.fullmatch(allowed, path.relative_to(root.resolve()).as_posix()):
        return ["reference path must be a PNG in an approved reference directory"]
    expected_hash = item.get("sha256")
    size = item.get("pixel_size")
    if not isinstance(expected_hash, str) or not re.fullmatch(r"[a-fA-F0-9]{64}", expected_hash):
        return ["sha256 must contain 64 hexadecimal characters"]
    if not isinstance(size, list) or len(size) != 2 or not all(type(n) is int and n > 0 for n in size):
        return ["pixel_size must contain two positive integers"]
    try:
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            header = stream.read(24)
            digest.update(header)
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[8:16] != b"\x00\x00\x00\rIHDR":
            return ["reference has an invalid PNG header"]
        errors = []
        if list(struct.unpack(">II", header[16:24])) != size:
            errors.append("reference pixel dimensions do not match approved manifest")
        if digest.hexdigest() != expected_hash.lower():
            errors.append("reference SHA-256 does not match approved manifest")
        return errors
    except OSError as exc:
        return [f"reference unavailable: {exc}"]


def check_task(task: dict, root: Path) -> list[str]:
    """Return prerequisite blockers without modifying files or decoding images."""
    if "evidence_manifest" not in task:
        return []
    try:
        manifest = _contained(root, task["evidence_manifest"])
        if manifest.suffix.lower() != ".json":
            return ["evidence_manifest must be a JSON file"]
        content = json.loads(manifest.read_text(encoding="utf-8"))
    except (ValueError, OSError, RuntimeError) as exc:
        return [f"evidence_manifest unavailable or malformed: {exc}"]
    requirements = content.get("requirements") if isinstance(content, dict) else None
    if not isinstance(requirements, list) or not requirements:
        return ["evidence_manifest requires a nonempty requirements array"]
    blockers = []
    for index, item in enumerate(requirements, 1):
        prefix = f"evidence requirement {index}"
        if not isinstance(item, dict):
            blockers.append(f"{prefix}: expected an object")
            continue
        errors = _approval_errors(item)
        kind = item.get("kind")
        # Approval/provenance must be complete before opening reference bytes.
        if not errors:
            if kind == "reference":
                errors.extend(_reference_errors(item, root))
            elif kind in ("measurement", "visual_approval"):
                for field in ("scope", "target"):
                    if not _text(item.get(field)):
                        errors.append(f"{field} is required")
                if kind == "visual_approval":
                    if item.get("owner_approved") is not True:
                        errors.append("explicit owner_approved=true is required")
                    reviewer = item.get("reviewer") or item.get("approved_by")
                    producer = item.get("producer")
                    if not _text(producer) or producer.strip().casefold() == reviewer.strip().casefold():
                        errors.append("producer and reviewer must be distinct identities")
                    for field in ("producer_session", "reviewer_session"):
                        if not _text(item.get(field)):
                            errors.append(f"{field} is required")
                    if item.get("producer_session") == item.get("reviewer_session"):
                        errors.append("visual review must use an independent session")
                    digest = item.get("target_sha256", "")
                    commit = item.get("target_commit", "")
                    if not (isinstance(digest, str) and re.fullmatch(r"[a-fA-F0-9]{64}", digest)) and not (isinstance(commit, str) and re.fullmatch(r"[a-fA-F0-9]{40,64}", commit)):
                        errors.append("visual approval must bind target_sha256 or full target_commit")
            else:
                errors.append("unknown evidence kind")
        blockers.extend(f"{prefix}: {message}" for message in errors)
    return blockers
