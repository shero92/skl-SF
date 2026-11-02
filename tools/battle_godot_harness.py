"""Shared headless runner for battle verifiers; missing Godot is a failure.

Read the repository's configured executable and return (exit_code, combined_output).
No editor import is required by verifiers that explicitly preload their scripts.
"""
from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def _text(value: str | bytes | None) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value or ""


def run_godot(
    script: str,
    *,
    timeout: float = 60.0,
    root: Path = ROOT,
) -> tuple[int, str]:
    """Run a res://tools/verify_*.gd script, never skipping missing dependencies."""
    relative = script.removeprefix("res://")
    path = PurePosixPath(relative)
    if (
        path.parent != PurePosixPath("tools")
        or not path.name.startswith("verify_")
        or path.suffix != ".gd"
        or "\\" in relative
    ):
        return 1, "Invalid verifier: expected res://tools/verify_*.gd"
    if timeout <= 0:
        return 1, "Godot timeout must be positive"

    root = Path(root).resolve()
    try:
        config = json.loads(
            (root / ".agents/planner/config.json").read_text(encoding="utf-8")
        )
        executable = config.get("godot_executable")
        if not isinstance(executable, str) or not executable.strip():
            return 1, "Missing godot_executable in .agents/planner/config.json"
        candidate = Path(executable)
        if not candidate.is_absolute():
            candidate = root / candidate
        resolved = str(candidate) if candidate.is_file() else shutil.which(executable)
        if not resolved:
            return 1, "Configured Godot executable not found: " + executable
        if not (root / relative).is_file():
            return 1, "Godot verifier not found: " + relative
        proc = subprocess.run(
            [
                resolved,
                "--headless",
                "--path",
                ".",
                "--script",
                "res://" + relative,
            ],
            cwd=str(root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return 124, (
            f"Godot timed out after {timeout}s\n"
            + _text(exc.stdout)
            + _text(exc.stderr)
        )
    except (OSError, ValueError, AttributeError) as exc:
        return 1, f"Cannot run Godot verifier: {exc}"
    return proc.returncode, proc.stdout + proc.stderr
