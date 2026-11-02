#!/usr/bin/env python3
"""Unattended Aider CLI task worker (Windows-first, gated).

Uses the canonical `.agents/tasks/TASK-*.md` records (no parallel queue). Scans every
`poll_seconds`, claims one `todo` task whose `agent: aider`, runs Aider non-interactively
inside a dedicated Git worktree, runs tests, commits on the task branch and moves on.

Safety: never merges, never pushes, never touches the owner's checkout, never reads or
logs credentials (the API key is inherited from the environment of the worker process
and scrubbed from every log). Disabled until `aider_execution_enabled` is true in
`.agents/planner/config.json` (owner decision required).

  python tools/aider_worker.py run [--once] [--dry-run]
  python tools/aider_worker.py status | stop | resume
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import runner_safety  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / ".agents/planner/config.json"
STATE_DIR = ROOT / ".agents/monitoring/.local/aider"
DEFAULTS = {
    "main_model": "openai/gpt-6.1-sol",
    "weak_model": "openai/gpt-6-sol",
    "api_base": "https://apimaster.ai/v1",
    "api_key_env": "OPENAI_API_KEY",
    "poll_seconds": 10,
    "task_timeout_seconds": 1800,
    "max_repair_attempts": 2,
    "base_ref": "main",
    "worktree_root": None,
    "aider_executable": None,
    "transient_delays": [30, 60, 120],
    "defer_seconds": 600,
    "run_window_hours": 24,
    "max_spend_usd": None,
    "max_aider_runs": None,
}
TERMINAL = {"done", "blocked"}
TEST_PYTHON = {"python", "python3", "py"}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path, default):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def write_json(path: Path, data) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    os.replace(tmp, path)


def settings() -> dict:
    cfg = read_json(CONFIG, {})
    out = dict(DEFAULTS)
    out.update(cfg.get("aider") or {})
    out["enabled"] = bool(cfg.get("aider_execution_enabled", False))
    return out


# ---------------------------------------------------------------- tasks
def load_tasks(root: Path = None) -> dict:
    root = root or ROOT
    out = {}
    for p in sorted((root / ".agents/tasks").glob("TASK-*.md")):
        text = p.read_text(encoding="utf-8-sig")
        if not text.startswith("---"):
            continue
        info = {}
        for line in text.replace("\r\n", "\n").split("---", 2)[1].splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                info[k.strip()] = v.strip()
        if re.fullmatch(r"TASK-\d{4}", info.get("id", "")):
            info["file"] = p
            info["text"] = text
            out[info["id"]] = info
    return out


def dependencies(task: dict) -> list:
    return [d.strip() for d in task.get("depends_on", "none").split(",") if d.strip() and d.strip() != "none"]


def eligible(task: dict, tasks: dict) -> bool:
    """Pure check: todo + agent aider + dependencies done. Never raises."""
    if task.get("status") != "todo" or task.get("agent") != "aider":
        return False
    return all(tasks.get(d, {}).get("status") == "done" for d in dependencies(task))


def task_touches(task: dict) -> list:
    """Validated touches; raises RuntimeError for malformed/forbidden scope."""
    try:
        return runner_safety.touches(task.get("touches", ""))
    except ValueError as exc:
        raise RuntimeError("Unsupported touches: " + str(exc)) from exc


def touch_conflict(task: dict, tasks: dict, claimed: list = ()) -> str | None:
    mine = task_touches(task)
    others = [t for t in tasks.values() if t["id"] != task["id"] and t.get("status") == "in_progress"]
    others += [tasks[i] for i in claimed if i in tasks and i != task["id"]]
    for other in others:
        try:
            theirs = runner_safety.touches(other.get("touches", ""))
        except ValueError:
            continue
        if any(runner_safety.overlaps(a, b) for a in mine for b in theirs):
            return other["id"]
    return None


def validate_changed(changed: list, authorized: list) -> bool:
    """Whole-diff validation (tracked + untracked) against touches; RuntimeError on violation."""
    try:
        return runner_safety.allowed_changed(changed, authorized)
    except ValueError as exc:
        raise RuntimeError(str(exc)) from exc


# ---------------------------------------------------------------- state / locks
def state_file(tid: str, state_dir: Path = None) -> Path:
    return (state_dir or STATE_DIR) / "runs" / tid / "state.json"


def read_state(tid: str, state_dir: Path = None) -> dict:
    return read_json(state_file(tid, state_dir), {})


def save_state(tid: str, state_dir: Path = None, **fields) -> dict:
    data = read_state(tid, state_dir)
    data.update(fields, updated_at=now())
    write_json(state_file(tid, state_dir), data)
    return data


def pid_alive(pid: int) -> bool:
    if not pid or pid < 0:
        return False
    if os.name == "nt":
        import ctypes
        handle = ctypes.windll.kernel32.OpenProcess(0x1000, False, int(pid))  # QUERY_LIMITED_INFORMATION
        if not handle:
            return False
        code = ctypes.c_ulong()
        ok = ctypes.windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(code))
        ctypes.windll.kernel32.CloseHandle(handle)
        return bool(ok) and code.value == 259  # STILL_ACTIVE
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def acquire_lock(name: str, state_dir: Path = None, pid: int = None) -> bool:
    """Atomic exclusive lock (O_EXCL). A lock whose owner process is dead is taken over once."""
    path = (state_dir or STATE_DIR) / "locks" / (name + ".lock")
    path.parent.mkdir(parents=True, exist_ok=True)
    pid = pid or os.getpid()
    for _ in range(2):
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            owner = read_json(path, {}).get("pid", 0)
            if pid_alive(owner) and owner != pid:
                return False
            if owner == pid:
                return False
            try:  # stale: owner died. Removal race is settled by the next O_EXCL.
                path.unlink()
            except OSError:
                return False
            continue
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            json.dump({"pid": pid, "at": now()}, f)
        return True
    return False


def release_lock(name: str, state_dir: Path = None) -> None:
    try:
        ((state_dir or STATE_DIR) / "locks" / (name + ".lock")).unlink()
    except OSError:
        pass


def lock_live(name: str, state_dir: Path = None) -> bool:
    return pid_alive(read_json((state_dir or STATE_DIR) / "locks" / (name + ".lock"), {}).get("pid", 0))


def pause_info(state_dir: Path = None) -> dict:
    return read_json((state_dir or STATE_DIR) / "pause.json", {})


def set_pause(kind: str, reason: str, state_dir: Path = None) -> None:
    write_json((state_dir or STATE_DIR) / "pause.json", {"kind": kind, "reason": reason, "at": now()})


def clear_pause(state_dir: Path = None) -> None:
    try:
        ((state_dir or STATE_DIR) / "pause.json").unlink()
    except OSError:
        pass


def stop_requested(state_dir: Path = None) -> bool:
    return ((state_dir or STATE_DIR) / "stop.flag").exists()


def select_next(tasks: dict, state_dir: Path = None, at: float = None) -> dict | None:
    """First eligible task (by id) not claimed/finished/deferred and without scope conflict."""
    at = at if at is not None else time.time()
    live = [t for t in tasks if lock_live("task-" + t, state_dir)]
    for tid in sorted(tasks):
        task = tasks[tid]
        if not eligible(task, tasks):
            continue
        st = read_state(tid, state_dir)
        if st.get("phase") in TERMINAL or tid in live:
            continue
        if st.get("retry_after", 0) > at:
            continue
        try:
            if touch_conflict(task, tasks, live):
                continue
        except RuntimeError as exc:
            save_state(tid, state_dir, phase="blocked", reason=str(exc))
            continue
        return task
    return None


# ---------------------------------------------------------------- classification / secrets
AUTH = re.compile(r"authenticationerror|invalid[_ ]api[_ ]key|incorrect api key|\b401\b|unauthori[sz]ed|invalid_api_key", re.I)
BALANCE = re.compile(r"insufficient[_ ](quota|balance|funds)|exceeded your current quota|out of credits|billing|payment required|\b402\b|balance.{0,20}(exhaust|insufficient|low)", re.I)
TRANSIENT = re.compile(r"rate ?limit|\b429\b|\b50[0234]\b|overloaded|timed? ?out|timeout|temporarily unavailable|connection (reset|error)|serviceunavailable", re.I)


def classify(output: str) -> str:
    """'balance' | 'auth' | 'transient' | 'ok' (balance wins over auth, auth over transient)."""
    if BALANCE.search(output):
        return "balance"
    if AUTH.search(output):
        return "auth"
    if TRANSIENT.search(output):
        return "transient"
    return "ok"


def retry_after_seconds(output: str) -> int:
    m = re.search(r"retry[- ]after\D{0,5}(\d+)", output, re.I)
    return int(m.group(1)) if m else 0


def scrub(text: str, env=None) -> str:
    """Remove secret values (any env var that looks like a key/token) and key-shaped strings."""
    env = os.environ if env is None else env
    for k, v in env.items():
        if v and len(v) >= 8 and re.search(r"KEY|TOKEN|SECRET|PASSWORD", k, re.I):
            text = text.replace(v, "***")
    return re.sub(r"\bsk-[A-Za-z0-9_\-]{12,}", "sk-***", text)


def parse_usage(output: str) -> dict:
    """Unknown stays None (never zero)."""
    def num(s):
        s = s.lower().replace(",", "")
        return int(float(s[:-1]) * 1000) if s.endswith("k") else int(float(s))
    m = re.search(r"Tokens:\s*([\d.,]+k?)\s*sent,\s*([\d.,]+k?)\s*received", output, re.I)
    c = re.findall(r"Cost:\s*\$([\d.]+)\s*message,\s*\$([\d.]+)\s*session", output, re.I)
    return {"tokens_sent": num(m.group(1)) if m else None,
            "tokens_received": num(m.group(2)) if m else None,
            "cost_session_usd": float(c[-1][1]) if c else None}


# ---------------------------------------------------------------- process / git helpers
def run(argv, cwd=None, timeout=600, env=None):
    """Run argv (no shell). On timeout the whole process tree is killed."""
    proc = subprocess.Popen(argv, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, encoding="utf-8", errors="replace")
    try:
        out, _ = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        if os.name == "nt":
            subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"], capture_output=True)
        else:
            proc.kill()
        out, _ = proc.communicate()
        return 124, (out or "") + "\nTIMEOUT"
    return proc.returncode, out or ""


def git(*args, cwd=None, check=True):
    code, out = run(["git", *args], cwd=cwd or ROOT)
    if check and code:
        raise RuntimeError("git " + " ".join(args[:2]) + " failed: " + out[-300:])
    return out.strip()


def changed_paths(workdir: Path) -> list:
    code, raw = run(["git", "status", "--porcelain", "-uall"], cwd=workdir)
    paths = []
    for line in raw.splitlines():
        if len(line) > 3:
            p = line[3:].strip().strip('"')
            paths.append(p.split(" -> ")[-1])
    return paths


def worktree_for(tid: str, cfg: dict) -> Path:
    base = Path(cfg["worktree_root"]) if cfg.get("worktree_root") else ROOT.parent / ".skl-sf-worktrees"
    return base / (tid + "-aider")


def make_worktree(tid: str, cfg: dict) -> tuple:
    branch = "aider/" + tid.lower()
    wt = worktree_for(tid, cfg)
    if wt.exists():
        return branch, wt
    wt.parent.mkdir(parents=True, exist_ok=True)
    exists = subprocess.run(["git", "rev-parse", "--verify", "-q", "refs/heads/" + branch], cwd=ROOT,
                            capture_output=True).returncode == 0
    if exists:
        git("worktree", "add", str(wt), branch)
    else:
        git("worktree", "add", "-b", branch, str(wt), cfg["base_ref"])
    return branch, wt


def hide_images(wt: Path) -> None:
    """Aider must never see images: add them to the worktree-local exclude file."""
    code, out = run(["git", "rev-parse", "--git-path", "info/exclude"], cwd=wt)
    exclude = Path(out.strip())
    exclude = exclude if exclude.is_absolute() else wt / exclude
    exclude.parent.mkdir(parents=True, exist_ok=True)
    marker = "# aider-worker: images hidden"
    text = exclude.read_text(encoding="utf-8") if exclude.exists() else ""
    if marker not in text:
        exclude.write_text(text + "\n" + marker + "\n*.png\n*.jpg\n*.jpeg\n*.webp\n*.gif\n*.exr\n", encoding="utf-8", newline="\n")


def input_files(wt: Path, touches: list) -> list:
    files = []
    for t in touches:
        p = wt / t
        if (p.is_file() or (not p.exists() and Path(t).suffix)) and not runner_safety.is_binary_path(t):
            files.append(t)  # a missing file is created by Aider
        elif p.is_dir():
            for f in sorted(p.rglob("*")):
                rel = f.relative_to(wt).as_posix()
                if f.is_file() and not runner_safety.is_binary_path(rel) and len(files) < 25:
                    files.append(rel)
    return files


def build_message(task: dict, repair: str = "") -> str:
    msg = ("You are implementing exactly one repository task non-interactively.\n"
           "Rules: edit only files listed in `touches`; do not create or modify images, art, "
           "characters, UI or gameplay; do not commit (the worker commits); do not run shell "
           "commands that read secrets; never print credentials.\n\n"
           "touches: " + task.get("touches", "") + "\n\n=== TASK RECORD ===\n" + task["text"])
    if repair:
        msg += "\n\n=== TEST FAILURE TO FIX (edit only touches) ===\n" + repair[-3000:]
    return msg


def aider_command(exe: str, cfg: dict, wt: Path, msgfile: Path, files: list, reads: list, logdir: Path) -> list:
    cmd = [exe, "--model", cfg["main_model"], "--weak-model", cfg["weak_model"],
           "--openai-api-base", cfg["api_base"], "--edit-format", "diff",
           "--no-auto-commits", "--no-dirty-commits", "--yes-always", "--no-pretty", "--no-stream",
           "--no-check-update", "--no-analytics", "--no-show-release-notes", "--no-suggest-shell-commands",
           "--no-auto-lint", "--no-restore-chat-history", "--map-tokens", "0",
           "--chat-history-file", str(logdir / "chat.md"), "--input-history-file", str(logdir / "input.hist"),
           "--llm-history-file", str(logdir / "llm.log"), "--message-file", str(msgfile)]
    for r in reads:
        cmd += ["--read", str(r)]
    for f in files:
        cmd += ["--file", f]
    return cmd


def find_aider(cfg: dict) -> str | None:
    exe = cfg.get("aider_executable")
    if exe and Path(exe).is_file():
        return exe
    return shutil.which("aider")


def test_argv(task: dict) -> list:
    """Declared test command, only python/py + tools/run_tests.py or -m unittest. Else []."""
    try:
        argv = shlex.split(task.get("test", ""), posix=False)
    except ValueError:
        return []
    argv = [a.strip('"') for a in argv]
    if not argv or argv[0].lower() not in TEST_PYTHON:
        return []
    rest = [a for a in argv[1:] if a != "-3"]
    if rest[:1] == ["tools/run_tests.py"] or rest[:2] == ["-m", "unittest"]:
        return [sys.executable] + rest
    return []


def run_tests(task: dict, wt: Path, timeout: int) -> tuple:
    cmds = []
    declared = test_argv(task)
    if declared:
        cmds.append(declared)
    cmds.append([sys.executable, "tools/run_tests.py", "--changed"])
    tail = ""
    for argv in cmds:
        code, out = run(argv, cwd=wt, timeout=timeout)
        tail = scrub(out)[-3000:]
        if code:
            return False, tail
    return True, tail


# ---------------------------------------------------------------- run window / budget
def session_file(state_dir: Path = None) -> Path:
    return (state_dir or STATE_DIR) / "session.json"


def start_window(cfg: dict, state_dir: Path = None, at: float = None) -> dict:
    """Begin (or keep, after a restart) the bounded run window. Wall-clock based, so Sleep counts."""
    cur = read_json(session_file(state_dir), {})
    at = at if at is not None else time.time()
    if cur and cur.get("ends_at", 0) > at:
        return cur
    if cur:
        return cur  # expired: the owner must run `new-window`
    cur = {"started_at": at, "ends_at": at + cfg["run_window_hours"] * 3600}
    write_json(session_file(state_dir), cur)
    return cur


def new_window(cfg: dict, state_dir: Path = None) -> dict:
    try:
        session_file(state_dir).unlink()
    except OSError:
        pass
    return start_window(cfg, state_dir)


def window_usage(since: float, state_dir: Path = None) -> tuple:
    runs, spend = 0, 0.0
    try:
        lines = ((state_dir or STATE_DIR) / "costs.jsonl").read_text(encoding="utf-8").splitlines()
    except OSError:
        lines = []
    for line in lines:
        try:
            row = json.loads(line)
            ts = datetime.fromisoformat(row["at"]).timestamp()
        except (ValueError, KeyError):
            continue
        if ts >= since:
            runs += 1
            spend += row.get("cost_session_usd") or 0.0
    return runs, spend


def run_gate(cfg: dict, state_dir: Path = None, at: float = None) -> tuple | None:
    """(kind, reason) when paid model calls must not start; None when allowed."""
    at = at if at is not None else time.time()
    if cfg.get("max_spend_usd") is None and cfg.get("max_aider_runs") is None:
        return "budget", "no explicit spend limit (max_spend_usd or max_aider_runs) is configured"
    sess = read_json(session_file(state_dir), {})
    if not sess:
        return "window", "no run window started"
    if sess.get("ends_at", 0) <= at:
        return "window", "run window ended; start a new one with new-window"
    runs, spend = window_usage(sess["started_at"], state_dir)
    if cfg.get("max_aider_runs") is not None and runs >= cfg["max_aider_runs"]:
        return "budget", "max_aider_runs reached (%d)" % runs
    if cfg.get("max_spend_usd") is not None and spend >= cfg["max_spend_usd"]:
        return "budget", "max_spend_usd reached (%.2f)" % spend
    return None


# ---------------------------------------------------------------- main task execution
class Pause(Exception):
    def __init__(self, kind, reason):
        super().__init__(reason)
        self.kind, self.reason = kind, reason


def aider_with_retry(cmd, wt, cfg, env, log, sleep=time.sleep, runner=run):
    """Run Aider; retry transient errors after 30/60/120s (longer Retry-After wins)."""
    delays = list(cfg["transient_delays"])
    for attempt in range(len(delays) + 1):
        code, out = runner(cmd, cwd=wt, timeout=cfg["task_timeout_seconds"], env=env)
        out = scrub(out, env)
        log.write(out + "\n")
        kind = classify(out) if code else "ok"
        if kind in ("auth", "balance"):
            raise Pause(kind, "Aider reported " + kind + " failure; model calls paused")
        if kind == "ok":
            return code, out
        if attempt == len(delays):
            raise Pause("transient", "transient service errors persisted")
        sleep(max(delays[attempt], retry_after_seconds(out)))
    raise Pause("transient", "transient service errors persisted")


def run_task(task: dict, sleep=time.sleep, runner=run) -> dict:
    cfg = settings()
    if not cfg["enabled"]:
        raise RuntimeError("Aider execution is disabled (aider_execution_enabled=false)")
    tid = task["id"]
    if not acquire_lock("task-" + tid):
        return {"id": tid, "result": "already-claimed"}
    try:
        return _execute(task, cfg, sleep, runner)
    finally:
        release_lock("task-" + tid)


def _execute(task, cfg, sleep, runner):
    tid = task["id"]
    st = read_state(tid)
    if st.get("phase") in TERMINAL:
        return {"id": tid, "result": st["phase"]}
    touches = task_touches(task)  # RuntimeError -> caller blocks
    keyenv = cfg["api_key_env"]
    if not os.environ.get(keyenv):
        set_pause("auth", "environment variable %s is not set" % keyenv)
        return {"id": tid, "result": "paused"}
    exe = find_aider(cfg)
    if not exe:
        set_pause("setup", "aider executable not found")
        return {"id": tid, "result": "paused"}
    attempts = st.get("attempts", 0) + 1
    branch, wt = make_worktree(tid, cfg)
    save_state(tid, phase="worktree", attempts=attempts, branch=branch, worktree=str(wt), started_at=now())
    if st.get("phase") == "committed":  # crash after commit: do not redo
        save_state(tid, phase="done")
        return {"id": tid, "result": "done"}
    # restart safety: discard partial edits from an interrupted attempt (worker-owned worktree only)
    git("reset", "--hard", "-q", cwd=wt)
    git("clean", "-fdq", cwd=wt)
    hide_images(wt)
    rundir = STATE_DIR / "runs" / tid
    rundir.mkdir(parents=True, exist_ok=True)
    reads = [p for p in (wt / "AGENTS.md",) if p.exists()]
    taskcopy = rundir / "task.md"
    taskcopy.write_text(task["text"], encoding="utf-8", newline="\n")
    reads.append(taskcopy)
    env = dict(os.environ)
    repair = ""
    usage_total = {}
    try:
        with open(rundir / "execution.log", "a", encoding="utf-8", newline="\n") as log:
            for repair_round in range(cfg["max_repair_attempts"] + 1):
                msgfile = rundir / "message.md"
                msgfile.write_text(build_message(task, repair), encoding="utf-8", newline="\n")
                save_state(tid, phase="aider", repair_round=repair_round)
                cmd = aider_command(exe, cfg, wt, msgfile, input_files(wt, touches), reads, rundir)
                code, out = aider_with_retry(cmd, wt, cfg, env, log, sleep, runner)
                usage = parse_usage(out)
                usage_total = usage
                with open(STATE_DIR / "costs.jsonl", "a", encoding="utf-8", newline="\n") as f:
                    f.write(json.dumps({"task": tid, "at": now(), "model": cfg["main_model"], **usage}) + "\n")
                if code:
                    raise RuntimeError("aider exited with code %s" % code)
                changed = changed_paths(wt)
                if not changed:
                    raise RuntimeError("aider made no changes")
                validate_changed(changed, touches)
                save_state(tid, phase="tests")
                ok, tail = run_tests(task, wt, cfg["task_timeout_seconds"])
                log.write("TESTS %s\n%s\n" % ("PASS" if ok else "FAIL", tail))
                if ok:
                    break
                repair = tail
            else:
                raise RuntimeError("tests still failing after %d repair attempts" % cfg["max_repair_attempts"])
        title = re.search(r"(?m)^# (.+)$", task["text"])
        msg = "feat(%s): %s\n\nAgent: aider\nModel: %s\nTask: %s\nTokens-Sent: %s\nTokens-Received: %s\nCost-USD: %s\n" % (
            tid, (title.group(1) if title else tid)[:70], cfg["main_model"], tid,
            usage_total.get("tokens_sent") or "unknown", usage_total.get("tokens_received") or "unknown",
            usage_total.get("cost_session_usd") if usage_total.get("cost_session_usd") is not None else "unknown")
        git("add", "--", *changed_paths(wt), cwd=wt)
        git("commit", "-q", "-m", msg, cwd=wt)
        sha = git("rev-parse", "HEAD", cwd=wt)
        save_state(tid, phase="committed", commit=sha)
        save_state(tid, phase="done")
        return {"id": tid, "result": "done", "commit": sha}
    except Pause as p:
        if p.kind in ("auth", "balance"):
            set_pause(p.kind, p.reason)
            save_state(tid, phase="queued", reason=p.reason)  # claim released, task retried after resume
        else:
            save_state(tid, phase="deferred", reason=p.reason, retry_after=time.time() + cfg["defer_seconds"])
        return {"id": tid, "result": "paused" if p.kind in ("auth", "balance") else "deferred"}
    except RuntimeError as exc:
        save_state(tid, phase="blocked", reason=str(exc)[:400])
        return {"id": tid, "result": "blocked", "reason": str(exc)[:400]}


# ---------------------------------------------------------------- loop / CLI
def cycle(dry_run=False, sleep=time.sleep, runner=run) -> str:
    tasks = load_tasks()
    if pause_info():
        return "paused"
    task = select_next(tasks)
    if not task:
        return "idle"
    if dry_run:
        return "would-run " + task["id"]
    blocked = run_gate(settings())
    if blocked:
        set_pause(*blocked)
        return "paused"
    return run_task(task, sleep, runner)["result"]


def loop(once=False, dry_run=False) -> int:
    cfg = settings()
    if not dry_run and not cfg["enabled"]:
        print("Aider execution is disabled in .agents/planner/config.json; nothing started.")
        return 2
    if not dry_run and not acquire_lock("worker"):
        print("another worker is already running")
        return 3
    try:
        if not dry_run:
            (STATE_DIR / "stop.flag").unlink(missing_ok=True)
            start_window(cfg)
            if run_gate(cfg):
                print("gate: %s - %s" % run_gate(cfg))
        while True:
            if stop_requested():
                print("stop requested; exiting")
                return 0
            result = cycle(dry_run)
            write_json(STATE_DIR / "heartbeat.json", {"pid": os.getpid(), "at": now(), "last": result})
            if once or dry_run:
                print(result)
                return 0
            time.sleep(cfg["poll_seconds"])
    finally:
        if not dry_run:
            release_lock("worker")


def status() -> dict:
    tasks = load_tasks()
    states = {t: read_state(t) for t in tasks if read_state(t)}
    return {"enabled": settings()["enabled"], "worker_running": lock_live("worker"),
            "pause": pause_info() or None, "window": read_json(session_file(), None),
            "gate": run_gate(settings()), "stop_requested": stop_requested(),
            "heartbeat": read_json(STATE_DIR / "heartbeat.json", None),
            "tasks": {t: {"phase": s.get("phase"), "reason": s.get("reason"), "commit": s.get("commit")}
                      for t, s in states.items()}}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--once", action="store_true")
    r.add_argument("--dry-run", action="store_true")
    for name in ("status", "stop", "resume", "new-window"):
        sub.add_parser(name)
    a = ap.parse_args(argv)
    if a.cmd == "run":
        return loop(a.once, a.dry_run)
    if a.cmd == "status":
        print(json.dumps(status(), indent=2, default=str))
    elif a.cmd == "stop":
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        (STATE_DIR / "stop.flag").write_text(now(), encoding="utf-8", newline="\n")
        print("stop requested: no new claims; the current task finishes first")
    elif a.cmd == "new-window":
        print(json.dumps(new_window(settings())))
    else:
        clear_pause()
        print("pause cleared")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
