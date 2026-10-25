import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "goal_task_factory.py"

class GoalFactoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.base = self.root / ".agents/planner"
        self.base.mkdir(parents=True)
        (self.root / ".agents/tasks").mkdir(parents=True)
        (self.root / "code.py").write_text("a = 1\nb = 2\n", encoding="utf8")
        self.env = {**os.environ, "SKL_PLANNER_ROOT": str(self.root)}

    def run_script(self, *args, success=True):
        p = subprocess.run([sys.executable, str(SCRIPT), *args], env=self.env,
                           capture_output=True, text=True)
        if success:
            self.assertEqual(p.returncode, 0, p.stderr)
        else:
            self.assertNotEqual(p.returncode, 0)
        return p

    def goals(self, status="active", steps=None):
        data = {"goals": [{"id": "GOAL-0099", "title": "Safe objective",
                "status": status, "task_ids": [], "final_verified": False,
                "steps": steps or []}]}
        (self.base / "goals.json").write_text(json.dumps(data), encoding="utf8")
        return data

    def step(self, key, kind="bug"):
        return {"key": key, "title": "Fix something " + key,
                "problem": "Observed regression " + key,
                "file": "code.py", "line": 2,
                "done_when": "Test passes", "test": "python -m unittest",
                "priority": "high", "kind": kind}

    def test_daily_pulse_deduplicated_and_small(self):
        self.goals(steps=[self.step(str(i)) for i in range(5)])
        a = json.loads(self.run_script("pulse", "--date", "2026-10-25").stdout)
        self.assertEqual(len(a["created"]), 3)
        self.assertEqual(len(list((self.root / ".agents/tasks").glob("TASK-*.md"))), 3)
        b = json.loads(self.run_script("pulse", "--date", "2026-10-25").stdout)
        self.assertEqual(b["created"], [])
        c = json.loads(self.run_script("pulse", "--date", "2026-10-26").stdout)
        self.assertEqual(len(c["created"]), 2)

    def test_manual_request_and_prompt_and_claim(self):
        self.goals(status="draft")
        self.run_script("request", "--title", "Fix wall",
                        "--problem", "Wrong turn", "--file", "code.py",
                        "--done-when", "Orientation passes", "--line", "2",
                        "--test", "python -m unittest")
        self.assertEqual(len(list((self.base / "requests").glob("REQ-*.json"))), 1)
        self.run_script("pulse", "--date", "2026-10-25")
        file = next((self.root / ".agents/tasks").glob("TASK-*.md"))
        text = file.read_text()
        self.assertIn("**Line:** 2", text)
        self.assertIn("**Suggested agent:** codex", text)
        out = self.run_script("prompt", "TASK-0001").stdout
        self.assertIn("Map Factory", out)
        self.run_script("claim", "TASK-0001", "--agent", "codex",
                        "--branch", "feat/task-0001")
        self.assertIn("status: in_progress", file.read_text())
        self.run_script("claim", "TASK-0001", "--agent", "claude",
                        "--branch", "feat/task-0001", success=False)

    def test_wrong_lines_are_unverified(self):
        self.goals(steps=[{**self.step("1"), "line": 999}])
        self.run_script("pulse", "--date", "2026-10-25")
        content = next((self.root / ".agents/tasks").glob("TASK-*.md")).read_text()
        self.assertIn("unverified (inspect source)", content)

    def test_architecture_routes_to_claude_and_art_blocked(self):
        self.goals(steps=[self.step("arch", "architecture"), self.step("art", "art")])
        self.run_script("pulse", "--date", "2026-10-25")
        contents = [p.read_text() for p in (self.root / ".agents/tasks").glob("TASK-*.md")]
        self.assertTrue(any("**Suggested agent:** claude" in c for c in contents))
        self.assertTrue(any("**Suggested agent:** specialist" in c and
                            "status: blocked" in c for c in contents))

    def test_goal_notification_requires_final_verification_and_pr(self):
        self.goals()
        t = self.root / ".agents/tasks/TASK-0001_demo.md"
        t.write_text("---\nid: TASK-0001\nstatus: done\nowner: codex\n"
                     "branch: feat/demo\ndepends_on: none\nissue: none\n"
                     "art_request: none\n---\n# Demo\n- PR: https://github.com/example/pr/1\n")
        goals = json.loads((self.base / "goals.json").read_text())
        goals["goals"][0]["task_ids"] = ["TASK-0001"]
        (self.base / "goals.json").write_text(json.dumps(goals))
        self.assertEqual(json.loads(self.run_script("completed").stdout), [])
        goals["goals"][0]["final_verified"] = True
        (self.base / "goals.json").write_text(json.dumps(goals))
        self.assertEqual(json.loads(self.run_script("completed").stdout)[0]["id"], "GOAL-0099")

    def test_goal_waits_for_uncreated_milestones(self):
        self.goals(steps=[self.step("not-created")])
        file = self.root / ".agents/tasks/TASK-0001_existing.md"
        file.write_text("---\nid: TASK-0001\nstatus: done\nowner: codex\n"
                        "branch: feat/example\ndepends_on: none\nissue: none\n"
                        "art_request: none\n---\n# Done\n- PR: https://github.com/example/repo/pull/1\n")
        config = json.loads((self.base / "goals.json").read_text())
        config["goals"][0]["task_ids"] = ["TASK-0001"]
        config["goals"][0]["final_verified"] = True
        (self.base / "goals.json").write_text(json.dumps(config))
        self.assertEqual(json.loads(self.run_script("completed").stdout), [])

    def test_unsafe_file_refused(self):
        self.goals(steps=[{**self.step("bad"), "file": "../secret"}])
        self.run_script("pulse", "--date", "2026-10-25", success=False)

if __name__ == "__main__":
    unittest.main()
