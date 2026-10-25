# Local subscription planner (Part 2)

One owner-goal folder per GOAL-#### with goal.md (owner's original text),
state.json (draft/active, milestone approval) and optional references/.
Reference images are NEVER fed to scheduled jobs; agents must not open project
graphics. One-time goal planning and final verification are separate reviewed
steps. The existing goals.json is a compatibility index until goal migration
is completed; never silently mark the first goal active.

## Schedule
Windows Task Scheduler, using the signed-in user's existing Claude Pro and
ChatGPT plan CLI login. Four times daily in Europe/Berlin local time:
08:13 Claude, 12:13 Codex, 16:13 Claude, 20:13 Codex.
Times, auto_activate (false), timeout and flags live in config.json.
The PC must be on AND the user session signed in; never put tokens or API
keys in Task Scheduler, GitHub Actions or the repository.

Windows (run from repo root in PowerShell after merging Part 2):
  py -3 tools/local_planner.py --agent claude --dry-run
  powershell -NoProfile -File tools/setup_local_planner.ps1

Remove schedules safely:
  powershell -NoProfile -File tools/setup_local_planner.ps1 -Uninstall

Pause everything: set planning_enabled=false and execution_enabled=false in
config.json, then run -Uninstall. Existing code and tasks remain intact.

## Read-only guarantees and expenses
Agents run LOCAL on subscriptions, no paid API keys or cloud AI calls:
- Claude: claude -p --permission-mode plan --tools "" --effort low
          --output-format json --json-schema ...
- Codex: codex exec --sandbox read-only --skip-git-repo-check
         --output-schema ... --output-last-message ... -
Both analyze a temporary TEXT-ONLY folder containing bounded inputs.
The host collects limited data from goals, task files, index and git log.
No model may inspect art or map images in routine analysis.
Model output is a JSON proposal: at most four tasks, with paths checked
against real existing non-image source files. Only the deterministic
goal_task_factory.py apply-proposal command edits task files.
An input SHA and fingerprint are tracked in checkpoint.json. If unchanged,
the model is not called at all. Rate-limits create cooldowns.json with a
6-hour cooldown; the other agent may be used once, never retry in a loop.
Runs produce sanitized JSON metadata in runs/. Raw prompts, model responses,
auth data or transcripts are never committed. Token/cost values may be unknown;
equivalent API cost is not an actual subscription charge.

Every planner branch is planning/YYYYMMDD-HHMMSS-agent, with a PR.
Automatic merge is allowed only if every CI check is successful and all paths
are restricted to .agents/tasks/, .agents/planner/ and generated FILES.md /
task dashboards. If CI fails or cannot be verified, PR stays open.
Code-task execution is *not* enabled here.
