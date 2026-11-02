"""Shared headless verification runner. Missing Godot is a failure, never a skip.

Execution provenance: Agent: codex; model: GPT-6.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / ".agents/planner/config.json"


def _text(value: str | bytes | None) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value or ""


def run_godot(
    script: str,
    *,
    timeout: float = 60,
    root: Path = ROOT,
) -> tuple[int, str]:
    """Run a tools/verify_*.gd script and return its exit code and combined output."""
    if not re.fullmatch(r"res://tools/verify_[A-Za-z0-9_]+\.gd", script):
        return 1, "Expected a res://tools/verify_*.gd script"
    root = Path(root).resolve()
    try:
        config = json.loads(
            (root / ".agents/planner/config.json").read_text(encoding="utf-8")
        )
        executable = config.get("godot_executable")
        if not isinstance(executable, str) or not executable.strip():
            return 1, "Missing godot_executable in .agents/planner/config.json"
        command = [
            executable, "--headless", "--path", ".", "--script", script,
        ]
        proc = subprocess.run(
            command,
            cwd=str(root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        return 124, (
            f"Godot timed out after {timeout}s\n"
            + _text(exc.stdout) + _text(exc.stderr)
        )
    except (OSError, ValueError, AttributeError) as exc:
        return 1, f"Godot verification could not run: {exc}"
    return proc.returncode, proc.stdout + proc.stderr
