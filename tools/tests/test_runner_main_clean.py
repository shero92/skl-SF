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
        self.assertIn('*>> $log', text)
        self.assertIn('run_agents_manual.ps1', text)
        self.assertIn('-Agents @($Agent)', text)


class CoordinatedBudgetTests(unittest.TestCase):
    def test_deadline_caps_commands_and_resets_context(self):
        import time
        from unittest.mock import patch
        with patch.object(ar.time, "monotonic", return_value=100):
            with ar.execution_budget(105):
                self.assertEqual(ar.remaining_timeout(1800), 5)
            self.assertEqual(ar.remaining_timeout(1800), 1800)
            with ar.execution_budget(99):
                with self.assertRaises(subprocess.TimeoutExpired):
                    ar.execute([sys.executable, "-c", "pass"])

    def test_timeout_kills_process_tree(self):
        import time
        from unittest.mock import patch
        with ar.execution_budget(time.monotonic() + .3):
            with patch.object(ar, "terminate_tree", wraps=ar.terminate_tree) as kill:
                with self.assertRaises(subprocess.TimeoutExpired):
                    ar.execute([sys.executable, "-c", "import time; time.sleep(20)"])
                self.assertEqual(kill.call_count, 1)

    def test_cancellation_prevents_any_new_subprocess(self):
        import threading
        import time
        from unittest.mock import patch
        cancelled = threading.Event()
        ar.cancel_budget(cancelled)
        with ar.execution_budget(time.monotonic()+10, cancel_event=cancelled), \
             patch.object(ar.subprocess,"Popen") as launch:
            with self.assertRaisesRegex(RuntimeError,"cancelled"):
                ar.execute(["fake-cli"])
            launch.assert_not_called()

    def test_cancellation_kills_registered_child_and_unregisters(self):
        import threading
        import time
        from unittest.mock import Mock, patch
        cancelled = threading.Event()
        started = threading.Event()
        killed = threading.Event()
        child = Mock(returncode=-1)
        def communicate(**kwargs):
            started.set()
            if not killed.wait(3):
                raise AssertionError("child was not terminated")
            return "", ""
        child.communicate.side_effect = communicate
        errors=[]
        def worker():
            try:
                with ar.execution_budget(time.monotonic()+10, cancel_event=cancelled):
                    ar.execute(["fake-cli"])
            except Exception as exc:
                errors.append(str(exc))
        with patch.object(ar.subprocess,"Popen",return_value=child), \
             patch.object(ar,"terminate_tree",side_effect=lambda proc:killed.set()) as kill:
            thread=threading.Thread(target=worker)
            thread.start()
            self.assertTrue(started.wait(3))
            self.assertEqual(ar.cancel_budget(cancelled), [])
            thread.join(3)
            self.assertFalse(thread.is_alive())
            kill.assert_called_once_with(child)
        self.assertEqual(errors,["Coordinated execution cancelled"])
        self.assertNotIn(cancelled,ar._CHILDREN)

    def test_infrastructure_requires_review_even_in_mixed_task(self):
        self.assertTrue(ar.requires_pr(["tools/new.py"]))
        self.assertTrue(ar.requires_pr(["map_factory/scripts/x.gd", ".github/workflows/tests.yml"]))
        self.assertFalse(ar.requires_pr(["map_factory/scripts/room_factory.gd"]))

    def test_repair_rehides_images_and_revalidates_touches_once(self):
        import time
        from unittest.mock import patch, Mock
        calls=[]
        def tests(*args):
            calls.append("tests")
            if calls.count("tests") == 1:
                raise RuntimeError("tools/run_tests.py returned 1")
        def hide(*args):calls.append("hide")
        def session(*args, **kwargs):
            calls.append("repair")
            self.assertIn("returned 1",kwargs["repair_context"])
            return subprocess.CompletedProcess([],0,"",""), None
        with ar.execution_budget(time.monotonic()+10), \
             patch.object(ar,"tests",tests), patch.object(ar,"hide_images",hide), \
             patch.object(ar,"sanitized_session",session), patch.object(ar,"git"), \
             patch.object(ar,"changed_paths",return_value=["tools/x.py"]), \
             patch.object(ar,"allowed_changed") as allowed:
            ar.validate_with_repair(Path("."),{},["tools/x.py"],"codex","TASK-0001",100)
            self.assertEqual(calls,["tests","hide","repair","tests"])
            allowed.assert_called_once()

    def test_coordination_is_reentrant_and_serializes_workers(self):
        import threading
        import time
        from unittest.mock import patch
        from contextlib import contextmanager
        events=[]
        @contextmanager
        def lease(label):
            events.append("lease")
            yield
        def worker():
            with ar.coordination_lock():
                events.append("enter")
                with ar.coordination_lock():
                    time.sleep(.02)
                events.append("exit")
        with patch.object(ar,"_exclusive_file",lease):
            threads=[threading.Thread(target=worker) for _ in range(2)]
            for thread in threads:thread.start()
            for thread in threads:thread.join()
        self.assertEqual(events,["lease","enter","exit","lease","enter","exit"])

    def test_no_repair_outside_manual_budget(self):
        from unittest.mock import patch
        with patch.object(ar,"tests",side_effect=RuntimeError("test failed")), \
             patch.object(ar,"sanitized_session") as session:
            with self.assertRaisesRegex(RuntimeError,"test failed"):
                ar.validate_with_repair(Path("."),{},[],"codex","TASK-0001",100)
            session.assert_not_called()


if __name__ == "__main__":
    unittest.main()
