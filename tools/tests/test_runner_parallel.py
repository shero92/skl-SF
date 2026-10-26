"""Parallel claude/codex runs: per-task state, and usage limits release tasks instead of blocking.

2026-10-26: TASK-0033 (codex) was blocked twice by "You've hit your usage limit", and the
shared runner-state.json was overwritten by the concurrent TASK-0034 run.
"""
import contextlib
from datetime import datetime, timedelta, timezone
import io
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(TOOLS / "tests"))
import agent_runner as ar  # noqa: E402
from test_runner_main_clean import TASK, MainStaysClean, sh  # noqa: E402

CODEX_LIMIT = ('{"type":"turn.started"}\n{"type":"error","message":"You’ve hit your usage limit. '
               'Upgrade to Pro or try again at 3:53 PM."}\n')
CLAUDE_LIMIT = '{"type":"result","is_error":true,"result":"Claude AI usage limit reached|1761500000"}'


def proc(code, stdout="", stderr=""):
    return SimpleNamespace(returncode=code, stdout=stdout, stderr=stderr)


class ParallelRunner(unittest.TestCase):
    setUp = MainStaysClean.setUp
    write = MainStaysClean.write
    fake_index = MainStaysClean.fake_index

    def test_checkpoint_keeps_one_state_file_per_task(self):
        ar.checkpoint("TASK-0033", "codex", "claimed", "work/task-0033-a")
        ar.checkpoint("TASK-0034", "claude", "done", "5e4070a")
        self.assertEqual(ar.read_state("TASK-0033")["phase"], "claimed")
        self.assertEqual(ar.read_state("TASK-0034")["phase"], "done")
        latest = json.loads((ar.LOCAL / "runner-state.json").read_text())
        self.assertEqual(latest["task"], "TASK-0034")
        self.assertEqual(ar.read_state("TASK-0099"), {})

    def test_quota_message_detects_cli_usage_limits_only(self):
        self.assertIn("usage limit", ar.quota_message(proc(1, CODEX_LIMIT)) or "")
        self.assertIn("usage limit", ar.quota_message(proc(1, CLAUDE_LIMIT)) or "")
        self.assertIn("rate limit", ar.quota_message(proc(1, "", "Error: rate limit exceeded")) or "")
        self.assertIsNone(ar.quota_message(proc(1, "", "SyntaxError: invalid syntax")))
        self.assertIsNone(ar.quota_message(proc(0, CODEX_LIMIT)), "successful sessions are never quota failures")

    def test_release_returns_claimed_task_to_todo_and_keeps_main_clean(self):
        self.write(".agents/tasks/TASK-0001_task.md", TASK.format(status="in_progress").replace(
            "branch: none", "branch: work/task-0001-abc").replace("---\n# Task", "started_at: 2026-10-26T13:16:00\n---\n# Task"))
        sh(self.root, "commit", "-qam", "claim")
        ar.release_for_quota("TASK-0001", "codex", "You've hit your usage limit")
        text = (self.root / ".agents/tasks/TASK-0001_task.md").read_text()
        for line in ("status: todo", "owner: unassigned", "branch: none", "started_at: unknown"):
            self.assertIn(line, text)
        self.assertIn("Released to todo: codex CLI usage limit", text)
        self.assertNotIn("status: blocked", text)
        self.assertEqual(ar.dirty_paths(), [])
        self.assertIn("release TASK-0001 after codex usage limit", sh(self.root, "log", "-1", "--format=%s"))
        self.assertEqual(sh(self.root, "ls-remote", "origin", "refs/heads/main").split()[0],
                         sh(self.root, "rev-parse", "HEAD").strip())

    def test_cooldown_window(self):
        self.assertIsNone(ar.cooling_until("codex"))
        until = ar.start_cooldown("codex", "usage limit", minutes=60)
        self.assertEqual(ar.cooling_until("codex"), until)
        self.assertIsNone(ar.cooling_until("claude"), "cooldown is per agent")
        past = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
        ar.cooldown_path("codex").write_text(json.dumps({"retry_after": past}))
        self.assertIsNone(ar.cooling_until("codex"))
        ar.cooldown_path("codex").write_text("{\"retry_after\": \"not-a-date\"}")
        self.assertIsNone(ar.cooling_until("codex"))

    def test_run_next_skips_cooling_agent_without_claiming(self):
        saved = {name: getattr(ar, name) for name in ("execution_gate", "pick_next", "run")}
        self.addCleanup(lambda: [setattr(ar, k, v) for k, v in saved.items()])
        ar.execution_gate = lambda config: None
        ar.pick_next = lambda agent: self.fail("pick_next must not run during cooldown")
        ar.run = lambda tid, supervised=False: self.fail("no task may be claimed during cooldown")
        ar.start_cooldown("codex", "usage limit")
        argv, sys.argv = sys.argv, ["agent_runner.py", "--run-next", "codex"]
        self.addCleanup(setattr, sys, "argv", argv)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            ar.main()
        self.assertIn("codex usage cooldown until", out.getvalue())

    def test_quota_path_is_handled_before_generic_failure(self):
        text = (TOOLS / "agent_runner.py").read_text(encoding="utf-8")
        body = text[text.index("def _run("):text.index("def pick_next(")]
        self.assertLess(body.index("except QuotaExceeded"), body.index("except Exception as exc"))
        self.assertIn("raise QuotaExceeded(message)", body)
        self.assertIn('info=read_state(tid)', body)
        self.assertNotIn('LOCAL/"runner-state.json"', body)


if __name__ == "__main__":
    unittest.main()
