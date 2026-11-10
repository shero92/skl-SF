"""Regenerate every main-only generated output in one call (ADR-006).

Usage: python tools/regenerate_main_outputs.py [--check]

Task branches never carry generated files; after a merge `main` goes stale by design. This runs the four
writers whose strict `--check` forms gate `main` in CI, so a post-merge job (and an owner) can refresh them
in one step. With --check it only runs the strict checks and fails when anything is stale.

Execution provenance: Agent: claude (Claude Code); model: Sonnet 5.5.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
# (writer, strict check) pairs; the checks are exactly the ones the main-branch workflows run.
STEPS = [
    (["tools/agent_workflow.py", "--write"], ["tools/agent_workflow.py", "--check"]),
    (["tools/generate_project_indexes.py", "--write"], ["tools/generate_project_indexes.py", "--check"]),
    (["tools/agent_costs.py", "report"], ["tools/agent_costs.py", "report", "--check"]),
    (["tools/run_tests.py", "--write-index"], ["tools/run_tests.py", "--check-index"]),
]


def run(arguments: list[str]) -> int:
    print("+ python " + " ".join(arguments), flush=True)
    return subprocess.run([sys.executable, *arguments], cwd=ROOT).returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="only run the strict checks")
    args = parser.parse_args()
    if not args.check:
        for step in STEPS:
            code = run(step[0])
            if code:
                print(f"writer failed ({code}): {' '.join(step[0])}", file=sys.stderr)
                return code
    failed = [step[1] for step in STEPS if run(step[1])]
    if failed:
        print("still stale or invalid: " + "; ".join(" ".join(c) for c in failed), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
