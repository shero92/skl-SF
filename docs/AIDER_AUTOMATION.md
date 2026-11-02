# Aider automation (TASK-0071)

Unattended coding worker that executes canonical `.agents/tasks/TASK-*.md` records assigned to `agent: aider`.
It is **disabled** until the owner sets `aider_execution_enabled: true` in `.agents/planner/config.json`.

## Models and credentials
- Main `openai/gpt-6.1-sol`, weak `openai/gpt-6-sol`, API base `https://apimaster.ai/v1` (`aider` block in the config).
- The key is read by Aider from the environment variable named by `aider.api_key_env` (default `OPENAI_API_KEY`) of the
  worker process. Set it yourself in your own terminal/secure store, e.g. user-level `setx OPENAI_API_KEY ...`
  typed by you. The worker never reads, copies, prints or logs it; all logs pass through a scrubber.
  If the variable is missing the worker pauses with a visible reason.

## What one cycle does (every 10 s)
1. Pause/stop checks, then scan `.agents/tasks/` (the only queue).
2. Eligible: `status: todo`, `agent: aider`, all `depends_on` tasks `done`, valid `touches` (no art/generated/policy/character/UI paths),
   no overlap with an `in_progress` task or a live claim. Malformed scope => task `blocked` locally, never reassigned.
3. Atomic claim: `O_EXCL` lock `task-<id>.lock` with PID (dead-PID locks are taken over); one task at a time; single worker lock.
4. Dedicated worktree `../.skl-sf-worktrees/<id>-aider` on branch `aider/<id>`, cut from `main`. The owner checkout is never edited.
5. Non-interactive Aider: `--message-file`, `--file` for each touched text file, `--read AGENTS.md` and the task record,
   `--no-auto-commits --no-dirty-commits --yes-always --map-tokens 0`; images are excluded in the worktree.
6. Whole diff (tracked + untracked) validated against `touches`; then the task's `test:` (python / `-m unittest` only)
   plus `tools/run_tests.py --changed`. Up to 2 repair rounds, then the task is `blocked` and the worktree preserved.
7. Commit on the task branch with trailers `Agent: aider`, `Model:`, tokens/cost (`unknown` when not reported). Next task.
   **The worker never merges or pushes**; merging stays a reviewed owner/PR step. Infrastructure tasks (touching `AGENTS.md`, config, etc.) fail
   scope validation and are never run unattended.

Transient errors (429/5xx/timeouts) retry after 30/60/120 s (a longer `Retry-After` wins), then the task is deferred 10 min.
Authentication or balance errors write `pause.json`, stop all model calls and re-queue the task; run `resume` after fixing.
Restart is safe: state lives in `.agents/monitoring/.local/aider/` (git-ignored), finished tasks are never re-run, interrupted
attempts restart from a clean reset of the worker-owned worktree.

## Commands
```
powershell.exe -NoProfile -File tools\run_aider_worker.ps1 start    # background (Scheduled Task if installed)
powershell.exe -NoProfile -File tools\run_aider_worker.ps1 status
powershell.exe -NoProfile -File tools\run_aider_worker.ps1 stop     # no new claims; current task finishes
powershell.exe -NoProfile -File tools\run_aider_worker.ps1 resume   # clear an auth/balance pause
python tools\aider_worker.py run --dry-run                          # lists what would run; no API use
powershell.exe -NoProfile -File tools\setup_aider_worker.ps1 -Install    # owner approval required; -Uninstall removes
```
The scheduled task `SklSfAiderWorker` (at logon, restart on failure, no time limit, hidden `powershell.exe -NoProfile`) is a
separate task; `SyncAISkills` is never touched.

## Activation gate
Registration, `aider_execution_enabled: true` and the first real supervised end-to-end run need explicit owner approval.
Until then only the unit tests (fake Aider) have been run.
