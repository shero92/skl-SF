"""Continuous automation: owner-set daily cap, reserved plan IDs, in-flight steps, dependency promotion."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
FACTORY = ROOT / "tools/goal_task_factory.py"


def step(key, **extra):
    return {"key": key, "title": "Step " + key, "problem": "Owner plan step " + key,
            "file": "tools/x.py", "done_when": key + " works", "test": "py -3 -m unittest",
            "priority": "normal", "kind": "feature", "agent": "codex", "after": [], **extra}


class ContinuousPulse(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        (self.root / ".agents/tasks").mkdir(parents=True)
        (self.root / ".agents/planner/goals/GOAL-0001").mkdir(parents=True)
        (self.root / "tools").mkdir()
        (self.root / "tools/x.py").write_text("x = 1\n")
        (self.root / ".agents/planner/goals/GOAL-0001/state.json").write_text(
            json.dumps({"status": "active", "milestones_approved": True}))
        self.env = {**os.environ, "SKL_PLANNER_ROOT": str(self.root)}

    def setup(self, steps, cap: object = "unset"):
        cfg: dict = {"max_tasks_per_run": 10}
        if cap != "unset":
            cfg["max_new_tasks_per_day"] = cap
        (self.root / ".agents/planner/config.json").write_text(json.dumps(cfg))
        (self.root / ".agents/planner/goals.json").write_text(json.dumps(
            {"goals": [{"id": "GOAL-0001", "title": "g", "status": "active", "steps": steps}]}))

    def pulse(self):
        x = subprocess.run([sys.executable, str(FACTORY), "pulse", "--date", "2026-10-26"],
                           cwd=self.root, env=self.env, capture_output=True, text=True)
        self.assertEqual(x.returncode, 0, x.stderr)
        return json.loads(x.stdout)

    def task(self, tid):
        return next((self.root / ".agents/tasks").glob(tid + "_*.md")).read_text(encoding="utf-8")

    def test_default_cap_is_three_and_null_removes_it(self):
        self.setup([step("s%d" % i) for i in range(5)])
        self.assertEqual(len(self.pulse()["created"]), 3)
        for f in (self.root / ".agents/tasks").glob("*.md"):
            f.unlink()
        self.setup([step("s%d" % i) for i in range(5)], cap=None)
        self.assertEqual(len(self.pulse()["created"]), 5)

    def test_reserved_plan_ids_are_kept_and_never_reused(self):
        self.setup([step("a", proposed_task_id="TASK-0002"), step("b"),
                    step("c", proposed_task_id="TASK-0001", task_id="TASK-0001")], cap=None)
        created = self.pulse()["created"]
        self.assertIn("TASK-0002", created)
        self.assertNotIn("TASK-0001", created, "a step reserved by an unmerged branch is skipped")
        self.assertEqual(sorted(created), ["TASK-0002", "TASK-0003"])

    def test_dependency_blocked_task_is_promoted_when_dependency_is_done(self):
        self.setup([step("first", proposed_task_id="TASK-0001"),
                    step("later", proposed_task_id="TASK-0002", depends_on=["TASK-0001"])], cap=None)
        self.pulse()
        self.assertIn("status: blocked", self.task("TASK-0002"))
        self.assertIn("**Blocked by:** dependencies", self.task("TASK-0002"))
        path = next((self.root / ".agents/tasks").glob("TASK-0001_*.md"))
        path.write_text(path.read_text().replace("status: todo", "status: done"))
        result = self.pulse()
        self.assertEqual(result["promoted"], ["TASK-0002"])
        self.assertIn("status: todo", self.task("TASK-0002"))
        self.assertEqual(self.pulse()["promoted"], [], "promotion happens once")

    def test_owner_or_runner_blocks_are_never_promoted(self):
        self.setup([step("first", proposed_task_id="TASK-0001")], cap=None)
        self.pulse()
        path = next((self.root / ".agents/tasks").glob("TASK-0001_*.md"))
        path.write_text(path.read_text().replace("status: todo", "status: blocked")
                        + "\n## Runner evidence\n- Runner failed: tests\n")
        self.assertEqual(self.pulse()["promoted"], [])
        self.assertIn("status: blocked", self.task("TASK-0001"))


if __name__ == "__main__":
    unittest.main()
