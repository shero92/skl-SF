"""The post-merge regeneration covers every strict main-branch generated-file check.

Execution provenance: Agent: claude (Claude Code); model: Sonnet 5.5.
"""
from __future__ import annotations

from pathlib import Path
import re
import sys
import unittest

TOOLS = Path(__file__).resolve().parents[1]
ROOT = TOOLS.parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import regenerate_main_outputs as regen

STRICT_CHECKS = {
    ".github/workflows/agent_workflow.yml": "tools/agent_workflow.py --check",
    ".github/workflows/project_indexes.yml": "tools/generate_project_indexes.py --check",
    ".github/workflows/agent_costs.yml": "tools/agent_costs.py report --check",
}


class RegenerateTests(unittest.TestCase):
    def test_every_strict_main_check_has_a_writer(self):
        checks = {" ".join(step[1]) for step in regen.STEPS}
        for workflow, command in STRICT_CHECKS.items():
            self.assertIn(command, (ROOT / workflow).read_text(encoding="utf-8"), workflow)
            self.assertIn(command, checks, "no writer registered for " + command)
        self.assertIn("tools/run_tests.py --check-index", checks)

    def test_workflow_runs_the_script_on_main_only_with_write_access(self):
        text = (ROOT / ".github/workflows/regenerate_main_outputs.yml").read_text(encoding="utf-8")
        self.assertIn("tools/regenerate_main_outputs.py", text)
        self.assertRegex(text, r"branches: \[main\]")
        self.assertIn("contents: write", text)
        self.assertNotIn("--force", text)
        self.assertNotIn("pull_request", re.sub(r"#.*", "", text))

    def test_writers_and_checks_exist(self):
        for step in regen.STEPS:
            for command in step:
                self.assertTrue((ROOT / command[0]).is_file(), command[0])


if __name__ == "__main__":
    unittest.main()
