import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import aider_worker as w

TASK = """---
id: TASK-{n}
status: {status}
agent: {agent}
depends_on: {dep}
touches: {touches}
test: none
---
# Example task {n}
Body.
"""


def mk(n, status="todo", agent="aider", dep="none", touches="tools/example_{n}.py"):
    touches = touches.format(n=n)
    text = TASK.format(n=n, status=status, agent=agent, dep=dep, touches=touches)
    return {"id": "TASK-" + n, "status": status, "agent": agent, "depends_on": dep,
            "touches": touches, "test": "none", "text": text}


def dead_pid():
    p = subprocess.Popen([sys.executable, "-c", "pass"])
    p.wait()
    return p.pid


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.state = Path(self.tmp.name) / "state"
        patcher = mock.patch.object(w, "STATE_DIR", self.state)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(self.tmp.cleanup)


class Eligibility(Base):
    def test_only_aider_todo_with_done_dependencies(self):
        items = [mk("0001", agent="codex"), mk("0002"), mk("0003", dep="TASK-0004"), mk("0004"),
                 mk("0005", status="blocked"), mk("0006", agent="claude"),
                 mk("0007", dep="TASK-0008"), mk("0008", status="done")]
        t = {x["id"]: x for x in items}
        ok = [i for i in t if w.eligible(t[i], t)]
        self.assertEqual(ok, ["TASK-0002", "TASK-0004", "TASK-0007"])

    def test_touch_conflict_with_in_progress_task(self):
        a = mk("0001", touches="tools/shared.py")
        b = mk("0002", status="in_progress", agent="codex", touches="tools/shared.py")
        c = mk("0003", touches="tools/other.py")
        tasks = {x["id"]: x for x in (a, b, c)}
        self.assertEqual(w.touch_conflict(a, tasks), "TASK-0002")
        self.assertIsNone(w.touch_conflict(c, tasks))

    def test_select_skips_conflicts_done_deferred_and_blocked(self):
        a = mk("0001", touches="tools/shared.py")
        b = mk("0002", status="in_progress", agent="codex", touches="tools/shared.py")
        tasks = {x["id"]: x for x in (a, b, mk("0003"), mk("0004"), mk("0005"))}
        w.save_state("TASK-0003", phase="done")
        w.save_state("TASK-0004", phase="deferred", retry_after=10 ** 12)
        self.assertEqual(w.select_next(tasks)["id"], "TASK-0005")
        w.save_state("TASK-0005", phase="blocked")
        self.assertIsNone(w.select_next(tasks))

    def test_malformed_touches_block_instead_of_running(self):
        bad = mk("0009", touches="assets/x.png")
        with self.assertRaises(RuntimeError):
            w.task_touches(bad)
        self.assertIsNone(w.select_next({bad["id"]: bad}))
        self.assertEqual(w.read_state("TASK-0009")["phase"], "blocked")


class Diff(unittest.TestCase):
    def test_reject_unauthorized_and_art(self):
        cases = ((["tools/unrelated.py"], ["tools/a.py"]), (["assets/c.png"], ["assets"]),
                 (["tools/a.py", "tools/b.png"], ["tools"]), (["AGENTS.md"], ["AGENTS.md"]))
        for changed, auth in cases:
            with self.assertRaises(RuntimeError):
                w.validate_changed(changed, auth)
        self.assertTrue(w.validate_changed(["tools/a.py"], ["tools/a.py"]))


class Locks(Base):
    def test_double_claim_is_refused(self):
        self.assertTrue(w.acquire_lock("task-TASK-0001"))
        self.assertFalse(w.acquire_lock("task-TASK-0001", pid=os.getpid() + 10 ** 6))
        w.release_lock("task-TASK-0001")
        self.assertTrue(w.acquire_lock("task-TASK-0001"))

    def test_stale_lock_from_dead_process_is_taken_over_once(self):
        lock = self.state / "locks" / "task-TASK-0001.lock"
        lock.parent.mkdir(parents=True)
        lock.write_text(json.dumps({"pid": dead_pid()}))
        self.assertTrue(w.acquire_lock("task-TASK-0001"))
        self.assertFalse(w.acquire_lock("task-TASK-0001", pid=os.getpid() + 10 ** 6))


class Classification(unittest.TestCase):
    def test_kinds(self):
        self.assertEqual(w.classify("litellm.AuthenticationError: invalid api key"), "auth")
        self.assertEqual(w.classify("Error: insufficient_quota You exceeded your current quota"), "balance")
        self.assertEqual(w.classify("429 rate limit, Retry-After: 90"), "transient")
        self.assertEqual(w.classify("applied edit to tools/a.py"), "ok")
        self.assertEqual(w.retry_after_seconds("Retry-After: 90"), 90)

    def test_scrub_and_usage(self):
        env = {"OPENAI_API_KEY": "sk-abcdefghijklmnop1234"}
        self.assertNotIn("abcdefgh", w.scrub("key=sk-abcdefghijklmnop1234 end", env))
        self.assertNotIn("zzzzzzzz", w.scrub("sk-zzzzzzzzzzzzzzzzzzzz", {}))
        u = w.parse_usage("Tokens: 1.2k sent, 300 received. Cost: $0.01 message, $0.05 session.")
        self.assertEqual((u["tokens_sent"], u["tokens_received"], u["cost_session_usd"]), (1200, 300, 0.05))
        self.assertIsNone(w.parse_usage("nothing")["cost_session_usd"])

    def test_retry_delays_30_60_120_and_retry_after_wins(self):
        outs = iter([(1, "503 overloaded"), (1, "429 Retry-After: 200"), (1, "timeout"),
                     (0, "ok Tokens: 1k sent, 1k received.")])
        calls, sleeps = [], []

        def runner(*a, **k):
            calls.append(1)
            return next(outs)
        code, _ = w.aider_with_retry(["aider"], Path("."), dict(w.DEFAULTS), {}, mock.Mock(), sleeps.append, runner)
        self.assertEqual((code, sleeps, len(calls)), (0, [30, 200, 120], 4))

    def test_auth_and_balance_stop_without_retry(self):
        for text, kind in (("AuthenticationError 401", "auth"), ("insufficient_quota", "balance")):
            calls = []

            def runner(*a, **k):
                calls.append(1)
                return 1, text
            with self.assertRaises(w.Pause) as cm:
                w.aider_with_retry(["aider"], Path("."), dict(w.DEFAULTS), {}, mock.Mock(), lambda s: None, runner)
            self.assertEqual((cm.exception.kind, len(calls)), (kind, 1))


class Gate(Base):
    def test_no_limit_means_no_paid_runs(self):
        cfg = dict(w.DEFAULTS)
        w.start_window(cfg)
        self.assertEqual(w.run_gate(cfg)[0], "budget")

    def test_window_expiry_and_restart_keeps_window(self):
        cfg = dict(w.DEFAULTS, max_spend_usd=1.0)
        s = w.start_window(cfg, at=1000.0)
        self.assertEqual(s["ends_at"], 1000.0 + 24 * 3600)
        self.assertEqual(w.start_window(cfg, at=5000.0)["started_at"], 1000.0)  # restart resumes
        self.assertIsNone(w.run_gate(cfg, at=2000.0))
        self.assertEqual(w.run_gate(cfg, at=1000.0 + 24 * 3600 + 1)[0], "window")
        self.assertEqual(w.start_window(cfg, at=10 ** 9)["started_at"], 1000.0)  # expired stays expired
        self.assertGreater(w.new_window(cfg)["started_at"], 1000.0)

    def test_spend_and_run_limits(self):
        cfg = dict(w.DEFAULTS, max_spend_usd=1.0, max_aider_runs=2)
        w.start_window(cfg)
        costs = self.state / "costs.jsonl"
        row = {"at": w.now(), "cost_session_usd": 0.4}
        line = json.dumps(row) + "\n"
        costs.write_text(line, newline="\n")
        self.assertIsNone(w.run_gate(cfg))
        costs.write_text(line * 2, newline="\n")
        self.assertIn("max_aider_runs", w.run_gate(cfg)[1])
        costs.write_text(json.dumps(dict(row, cost_session_usd=1.5)) + "\n", newline="\n")
        self.assertIn("max_spend_usd", w.run_gate(cfg)[1])


class EndToEnd(Base):
    """Real temp git repo + fake Aider process: claim, worktree, edit, tests, commit, no repeat."""

    def setUp(self):
        super().setUp()
        self.repo = Path(self.tmp.name) / "repo"
        self.repo.mkdir()

        def g(*a):
            subprocess.run(["git", *a], cwd=self.repo, check=True, capture_output=True)
        g("init", "-q", "-b", "main")
        g("config", "user.email", "t@t")
        g("config", "user.name", "t")
        (self.repo / ".agents/tasks").mkdir(parents=True)
        (self.repo / "tools").mkdir()
        (self.repo / "tools/keep.py").write_text("")
        (self.repo / "AGENTS.md").write_text("rules\n")
        (self.repo / ".agents/tasks/TASK-0042_x.md").write_text(TASK.format(
            n="0042", status="todo", agent="aider", dep="none", touches="tools/example_0042.py"))
        g("add", "-A")
        g("commit", "-q", "-m", "init")
        cfg = dict(w.DEFAULTS, enabled=True, max_spend_usd=5.0, worktree_root=str(Path(self.tmp.name) / "wt"))
        w.start_window(cfg)
        for target, val in (("ROOT", self.repo), ("settings", lambda: cfg), ("find_aider", lambda c: "aider"),
                            ("run_tests", lambda t, wt, to: (True, "ok"))):
            p = mock.patch.object(w, target, val)
            p.start()
            self.addCleanup(p.stop)
        p = mock.patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-secret-value-123456"})
        p.start()
        self.addCleanup(p.stop)
        self.aider_calls = []

    def fake(self, out="Tokens: 2k sent, 100 received. Cost: $0.01 message, $0.02 session.", code=0):
        def runner(argv, cwd=None, timeout=600, env=None):
            if argv[0] == "aider":
                self.aider_calls.append(argv)
                (Path(cwd) / "tools/example_0042.py").write_text("x = 1\n")
                return code, out
            return w.run(argv, cwd=cwd, timeout=timeout, env=env)
        return runner

    def test_full_cycle_commit_and_no_duplicate(self):
        self.assertEqual(w.cycle(runner=self.fake()), "done")
        self.assertEqual(w.read_state("TASK-0042")["phase"], "done")
        msg = subprocess.run(["git", "log", "-1", "--format=%B", "aider/task-0042"], cwd=self.repo,
                             capture_output=True, text=True).stdout
        self.assertIn("Agent: aider", msg)
        self.assertIn("Model: openai/gpt-6.1-sol", msg)
        cmd = self.aider_calls[0]
        for flag in ("--message-file", "--no-auto-commits", "--file", "--read", "--yes-always"):
            self.assertIn(flag, cmd)
        self.assertNotIn("sk-test-secret-value-123456", " ".join(cmd))
        self.assertEqual(w.cycle(runner=self.fake()), "idle")
        self.assertEqual(w.run_task(w.load_tasks()["TASK-0042"], runner=self.fake())["result"], "done")
        self.assertEqual(len(self.aider_calls), 1)
        self.assertFalse((self.repo / "tools/example_0042.py").exists())

    def test_auth_failure_pauses_and_stops_api_calls(self):
        bad = self.fake(out="AuthenticationError 401 invalid_api_key", code=1)
        self.assertEqual(w.cycle(runner=bad), "paused")
        self.assertEqual(w.pause_info()["kind"], "auth")
        self.assertEqual(w.cycle(runner=self.fake()), "paused")
        self.assertEqual(len(self.aider_calls), 1)
        w.clear_pause()
        self.assertEqual(w.cycle(runner=self.fake()), "done")

    def test_expired_window_pauses_before_any_call(self):
        sess = w.read_json(w.session_file(), {})
        sess["ends_at"] = 1.0
        w.write_json(w.session_file(), sess)
        self.assertEqual(w.cycle(runner=self.fake()), "paused")
        self.assertEqual(w.pause_info()["kind"], "window")
        self.assertEqual(self.aider_calls, [])

    def test_balance_failure_pauses(self):
        self.assertEqual(w.cycle(runner=self.fake(out="insufficient_quota", code=1)), "paused")
        self.assertEqual(w.pause_info()["kind"], "balance")

    def test_out_of_scope_edit_blocks(self):
        def runner(argv, cwd=None, timeout=600, env=None):
            if argv[0] == "aider":
                (Path(cwd) / "tools/other.py").write_text("y\n")
                return 0, "ok"
            return w.run(argv, cwd=cwd, timeout=timeout, env=env)
        self.assertEqual(w.cycle(runner=runner), "blocked")
        self.assertEqual(w.read_state("TASK-0042")["phase"], "blocked")

    def test_test_failure_repairs_twice_then_blocks(self):
        with mock.patch.object(w, "run_tests", lambda t, wt, to: (False, "FAILED x")):
            self.assertEqual(w.cycle(runner=self.fake()), "blocked")
        self.assertEqual(len(self.aider_calls), 3)

    def test_missing_credentials_and_disabled_gate(self):
        with mock.patch.dict(os.environ):
            os.environ.pop("OPENAI_API_KEY")
            self.assertEqual(w.cycle(runner=self.fake()), "paused")
        self.assertEqual(self.aider_calls, [])
        w.clear_pause()
        with mock.patch.object(w, "settings", lambda: dict(w.DEFAULTS, enabled=False)):
            with self.assertRaises(RuntimeError):
                w.run_task(w.load_tasks()["TASK-0042"])


if __name__ == "__main__":
    unittest.main()
