"""Main must stay clean after every runner exit (TASK-0009 left receipts/FILES.md dirty)."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import agent_runner as ar  # noqa: E402

TASK = "---\nid: TASK-0001\nstatus: {status}\nowner: codex\nbranch: none\nagent: codex\n" \
       "touches: tools/x.py\ntest: py -3 -m unittest\n---\n# Task\n"


def sh(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout


class MainStaysClean(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        base = Path(tmp.name)
        sh(base, "init", "-q", "--bare", "-b", "main", "origin.git")
        self.root = base / "main"
        sh(base, "clone", "-q", str(base / "origin.git"), str(self.root))
        sh(self.root, "config", "user.email", "runner@example.invalid")
        sh(self.root, "config", "user.name", "runner")
        sh(self.root, "checkout", "-q", "-b", "main")
        self.write(".agents/tasks/TASK-0001_task.md", TASK.format(status="in_progress"))
        self.write(".agents/monitoring/receipts/FILES.md", "# Files\n")
        self.write(".agents/project/TASKS.md", "| TASK-0001 | in_progress |\n")
        self.write("tools/x.py", "x = 1\n")
        sh(self.root, "add", "-A")
        sh(self.root, "commit", "-q", "-m", "base")
        sh(self.root, "push", "-q", "-u", "origin", "main")
        saved = {name: getattr(ar, name) for name in ("ROOT", "LOCAL", "index_main")}
        self.addCleanup(lambda: [setattr(ar, k, v) for k, v in saved.items()])
        ar.ROOT, ar.LOCAL = self.root, self.root / ".agents/monitoring/.local"
        (self.root / ".gitignore").write_text(".agents/monitoring/.local/\n")
        sh(self.root, "add", ".gitignore")
        sh(self.root, "commit", "-q", "-m", "ignore local")
        sh(self.root, "push", "-q")
        ar.index_main = self.fake_index

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")

    def fake_index(self):
        # Like generate_project_indexes/agent_workflow: list every receipt, mirror task status.
        receipts = sorted(p.name for p in (self.root / ".agents/monitoring/receipts").glob("*.json"))
        self.write(".agents/monitoring/receipts/FILES.md", "# Files\n" + "".join("- " + r + "\n" for r in receipts))
        status = "done" if "status: done" in (self.root / ".agents/tasks/TASK-0001_task.md").read_text() else "todo"
        self.write(".agents/project/TASKS.md", "| TASK-0001 | " + status + " |\n")

    def remote_head(self):
        return sh(self.root, "ls-remote", "origin", "refs/heads/main").split()[0]

    def test_record_validated_commits_regenerated_receipt_index(self):
        # The merge brings a new receipt; the receipts FILES.md is only regenerated afterwards.
        self.write(".agents/monitoring/receipts/TASK-0001_codex_1.json", "{}\n")
        sh(self.root, "add", "-A")
        sh(self.root, "commit", "-q", "-m", "merge task")
        ar.amend_status("TASK-0001", "done", reason="Merged; post-merge validation passed")
        ar.main_commit("chore: record validated TASK-0001", "codex", "TASK-0001")
        self.assertEqual(ar.dirty_paths(), [])
        self.assertEqual(self.remote_head(), sh(self.root, "rev-parse", "HEAD").strip())
        files = sh(self.root, "show", "HEAD:.agents/monitoring/receipts/FILES.md")
        self.assertIn("TASK-0001_codex_1.json", files)
        self.assertIn("Agent: codex", sh(self.root, "log", "-1", "--format=%B"))

    def test_verified_generated_commit_stops_before_commit_when_tests_fail(self):
        from unittest.mock import patch
        original=ar.execute
        before=sh(self.root,"rev-parse","HEAD")
        def execute(argv,*args,**kwargs):
            if "tools/run_tests.py" in argv:
                self.assertEqual(argv[-1],"--changed")
                raise RuntimeError("generated-output tests failed")
            return original(argv,*args,**kwargs)
        self.write(".agents/project/TASKS.md","stale\n")
        with patch.object(ar,"execute",execute):
            with self.assertRaisesRegex(RuntimeError,"tests failed"):
                ar.main_commit("chore: refresh","codex","planning",verify=True)
        self.assertEqual(sh(self.root,"rev-parse","HEAD"),before)
        self.assertEqual(self.remote_head(),before.strip())

    def test_main_commit_refuses_non_generated_changes(self):
        self.write("tools/x.py", "x = 2\n")
        before = sh(self.root, "rev-parse", "HEAD")
        with self.assertRaisesRegex(RuntimeError, "non-generated changes.*tools/x.py"):
            ar.main_commit("chore: record validated TASK-0001", "codex", "TASK-0001")
        self.assertEqual(sh(self.root, "rev-parse", "HEAD"), before)

    def test_settle_commits_regenerated_drift_only(self):
        self.write(".agents/monitoring/receipts/FILES.md", "# Files\n- stale\n")
        self.assertIsNone(ar.settle_main("TASK-0001", "codex"))
        self.assertEqual(ar.dirty_paths(), [])
        self.write("tools/x.py", "x = 3\n")
        problem = ar.settle_main("TASK-0001", "codex")
        self.assertIn("non-generated changes: tools/x.py", problem or "")
        self.assertEqual(ar.dirty_paths(), ["tools/x.py"])

    def test_run_wrapper_cleans_after_success_and_reports_after_failure(self):
        saved = ar._run
        self.addCleanup(setattr, ar, "_run", saved)
        ar._run = lambda tid, supervised=False: self.write(".agents/monitoring/receipts/FILES.md", "# drift\n")
        ar.run("TASK-0001")
        self.assertEqual(ar.dirty_paths(), [])

        def fail(tid, supervised=False):
            ar.checkpoint(tid, "codex", "blocked_pending_review", "tests returned 1")
            self.write("tools/x.py", "broken = True\n")
            raise RuntimeError("tests returned 1")
        ar._run = fail
        with self.assertRaisesRegex(RuntimeError, "tests returned 1"):
            ar.run("TASK-0001")
        state = ar.read_json(ar.LOCAL / "runner-state.json", {})
        self.assertEqual(state["phase"], "blocked_dirty_main")
        self.assertIn("tests returned 1 | Main left dirty", state["details"])

        ar._run = lambda tid, supervised=False: None
        with self.assertRaisesRegex(RuntimeError, "Main left dirty"):
            ar.run("TASK-0001")

    def test_generated_set_matches_index_main_outputs(self):
        for path in ("FILES.md", "tools/FILES.md", ".agents/monitoring/receipts/FILES.md",
                     ".agents/project/TASKS.md", ".agents/graphics/QUEUE.md", "tools/tests/INDEX.md",
                     ".agents/monitoring/goal_summary.json"):
            self.assertTrue(ar.regenerated(path), path)
        for path in ("INDEX.md", "tools/x.py", ".agents/tasks/TASK-0001_task.md", "AGENTS.md"):
            self.assertFalse(ar.regenerated(path), path)
        text = (TOOLS / "agent_runner.py").read_text(encoding="utf-8")
        for script in ("agent_workflow.py", "generate_project_indexes.py", "agent_costs.py", "goal_costs.py",
                       "run_tests.py"):
            self.assertIn('"tools/' + script + '"', text)

    def test_scheduled_worker_logs_output(self):
        text = (TOOLS / "run_local_agent.ps1").read_text(encoding="utf-8")
        self.assertIn(r".agents\monitoring\.local\runner-$Agent.log", text)
        self.assertIn('2>&1', text)
        self.assertIn("--run-next $Agent", text)


if __name__ == "__main__":
    unittest.main()
