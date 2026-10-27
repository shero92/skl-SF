import json
import os
from pathlib import Path
import re
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
        state = self.base / "goals/GOAL-0099/state.json"
        state.parent.mkdir(parents=True, exist_ok=True)
        state.write_text(json.dumps({"status": status, "milestones_approved": True}))
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

    def task_status(self, task_id):
        file = next((self.root / ".agents/tasks").glob(task_id + "_*.md"))
        return file, re.search(r"(?m)^status: (.+)$", file.read_text()).group(1)

    def set_done(self, task_id):
        file, status = self.task_status(task_id)
        file.write_text(file.read_text().replace("status: " + status, "status: done", 1))

    def test_after_blocks_until_previous_step_done(self):
        self.goals(steps=[self.step("a"), {**self.step("b"), "after": ["a"]}])
        out = json.loads(self.run_script("pulse", "--date", "2026-10-25").stdout)
        self.assertEqual(out["created"], ["TASK-0001"])
        out = json.loads(self.run_script("pulse", "--date", "2026-10-26").stdout)
        self.assertEqual(out["created"], [])

    def test_after_creates_with_depends_on_when_done(self):
        self.goals(steps=[self.step("a"), self.step("b"),
                          {**self.step("c"), "after": ["a", "b"]}])
        self.run_script("pulse", "--date", "2026-10-25")
        self.set_done("TASK-0001")
        out = json.loads(self.run_script("pulse", "--date", "2026-10-26").stdout)
        self.assertEqual(out["created"], [])
        self.set_done("TASK-0002")
        out = json.loads(self.run_script("pulse", "--date", "2026-10-27").stdout)
        self.assertEqual(out["created"], ["TASK-0003"])
        file, status = self.task_status("TASK-0003")
        self.assertEqual(status, "todo")
        self.assertIn("depends_on: TASK-0001,TASK-0002", file.read_text())

    def test_unsafe_file_refused(self):
        self.goals(steps=[{**self.step("bad"), "file": "../secret"}])
        out = json.loads(self.run_script("pulse", "--date", "2026-10-25").stdout)
        self.assertEqual(out["created"], [])
        self.assertEqual([r["source"] for r in out["refused"]], ["goal:GOAL-0099:bad"])
        self.assertIn("Unsafe path", out["refused"][0]["error"])
        self.assertEqual(list((self.root / ".agents/tasks").glob("TASK-*.md")), [])

    def done_task(self, task_id, status="done"):
        (self.root / ".agents/tasks" / (task_id + "_fixture.md")).write_text(
            "---\nid: " + task_id + "\nstatus: " + status + "\nowner: codex\nbranch: none\n"
            "depends_on: none\nissue: none\nart_request: none\n---\n# Fixture\n")

    def by_source(self):
        out = {}
        for p in (self.root / ".agents/tasks").glob("TASK-*.md"):
            m = re.search(r"(?m)^\*\*Source:\*\* (.+)$", p.read_text())
            if m:
                out[m.group(1)] = p.read_text()
        return out

    def calibration_step(self, **extra):
        return {**self.step("recovery-calibration", "investigation"), "agent": "specialist",
                "file": "docs/HERO_ROOM_CALIBRATION.md",
                "touches": ["docs/HERO_ROOM_CALIBRATION.md", ".agents/graphics/requests/"],
                "new_graphics_required": True,
                "source_gate_note": "TASK-0001 proves source identity.", **extra}

    def test_calibration_doc_specialist_step_is_blocked_with_requirements(self):
        # Regression: pulse exited 1 with "Outside Map Factory coding scope: docs/HERO_ROOM_CALIBRATION.md".
        self.done_task("TASK-0001")
        self.done_task("TASK-0002", status="review")
        self.goals(steps=[self.calibration_step(depends_on=["TASK-0001", "TASK-0002"]), self.step("independent")])
        out = json.loads(self.run_script("pulse", "--date", "2026-10-27").stdout)
        self.assertEqual(out["refused"], [])
        self.assertEqual(len(out["created"]), 2)
        texts = self.by_source()
        calib = texts["goal:GOAL-0099:recovery-calibration"]
        self.assertIn("status: blocked", calib)
        self.assertIn("agent: graphics", calib)
        self.assertIn("touches: docs/HERO_ROOM_CALIBRATION.md,.agents/graphics/requests/", calib)
        blocker = re.search(r"(?m)^\*\*Blocked by:\*\* specialist step .+$", calib).group(0)
        self.assertIn("TASK-0002 is review", blocker)
        self.assertNotIn("TASK-0001 is", blocker)
        self.assertIn("art request", blocker)
        self.assertIn("TASK-0001 proves source identity.", blocker)
        self.assertIn("status: todo", texts["goal:GOAL-0099:independent"])
        # Even once its dependencies are done, the pulse never promotes a specialist step to todo.
        self.set_done("TASK-0002")
        self.run_script("pulse", "--date", "2026-10-28")
        self.assertIn("status: blocked", self.by_source()["goal:GOAL-0099:recovery-calibration"])

    def test_only_the_exact_calibration_doc_leaves_the_coding_scope(self):
        sys.path.insert(0, str(SCRIPT.parent))
        import runner_safety
        self.assertEqual(runner_safety.touches("docs/HERO_ROOM_CALIBRATION.md"), ["docs/HERO_ROOM_CALIBRATION.md"])
        for path in ("docs/", "docs/OTHER.md", "docs/HERO_ROOM_CALIBRATION.png", "docs/hero_room_calibration.md"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                runner_safety.touches(path)
        self.goals(steps=[self.calibration_step(touches=["docs/OTHER.md"]), self.step("independent")])
        out = json.loads(self.run_script("pulse", "--date", "2026-10-27").stdout)
        self.assertEqual(len(out["created"]), 1)
        self.assertIn("Outside Map Factory coding scope: docs/OTHER.md", out["refused"][0]["error"])
        daily = (self.base / "daily/2026-10-27.md").read_text(encoding="utf-8")
        self.assertIn("goal:GOAL-0099:recovery-calibration: Outside Map Factory coding scope", daily)

    def test_pulse_approval_run_cap_and_step_receipt(self):
        self.goals(steps=[{**self.step(str(i)), "agent": "claude",
                          "touches": ["tools/example.py"],
                          "test": "py -3 -m unittest tools.tests.test_map_layers"} for i in range(4)])
        state = self.base / "goals/GOAL-0099/state.json"
        state.write_text(json.dumps({"status": "active", "milestones_approved": False}))
        self.assertEqual(json.loads(self.run_script("pulse").stdout)["created"], [])
        state.write_text(json.dumps({"status": "active", "milestones_approved": True}))
        (self.base / "config.json").write_text(json.dumps({"max_tasks_per_run": 1}))
        out = json.loads(self.run_script("pulse").stdout)
        self.assertEqual(out["created"], ["TASK-0001"])
        stored = json.loads((self.base / "goals.json").read_text())["goals"][0]["steps"]
        self.assertEqual(stored[0]["task_id"], "TASK-0001")
        text = self.task_status("TASK-0001")[0].read_text()
        self.assertIn("agent: claude", text)
        self.assertIn("touches: tools/example.py", text)
        self.assertIn("test: py -3 -m unittest discover -s tools/tests -p test_map_layers.py", text)

    def test_legacy_ai_step_annotation_deduplicates_and_unlocks_after(self):
        self.goals(steps=[self.step("a"), {**self.step("b"), "after": ["a"]}])
        p = self.root / ".agents/tasks/TASK-0001_old.md"
        p.write_text("---\nid: TASK-0001\nstatus: done\n---\n**Source:** ai:old\n"
                     "**Goal:** GOAL-0099\n**Problem:** observed (goal step a).\n")
        out = json.loads(self.run_script("pulse").stdout)
        self.assertEqual(out["created"], ["TASK-0002"])
        self.assertIn("depends_on: TASK-0001", self.task_status("TASK-0002")[0].read_text())
        stored = json.loads((self.base / "goals.json").read_text())["goals"][0]["steps"]
        self.assertEqual([s["task_id"] for s in stored], ["TASK-0001", "TASK-0002"])

if __name__ == "__main__":
    unittest.main()
