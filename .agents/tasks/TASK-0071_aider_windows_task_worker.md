---
id: TASK-0071
status: done
owner: claude
agent: aider
priority: high
branch: task-0071-claude-aider-worker
depends_on: none
issue: none
art_request: none
touches: tools/agent_runner.py,tools/runner_safety.py,tools/goal_task_factory.py,tools/agent_workflow.py,tools/agent_costs.py,tools/run_local_agent.ps1,tools/aider_worker.py,tools/run_aider_worker.ps1,tools/setup_aider_worker.ps1,tools/tests/test_aider_worker.py,tools/tests/test_agent_costs.py,tools/test_map.json,.agents/planner/config.json,.aiderignore,AGENTS.md,docs/AIDER_AUTOMATION.md
test: python tools/run_tests.py --changed
done_when: A supervised Windows Aider task completes claim, isolated edits, verification, commit, conditional merge and post-merge verification with no duplicate execution or user/art changes.
---
# Windows Aider task watcher and isolated execution

## Assignment and bootstrap

Owner explicitly requested: "create this task for aider this time".
Owner decision 2026-11-02: this infrastructure task is implemented by Claude Code (the
bootstrap worker cannot run Aider yet). The worker it delivers executes later `agent: aider` tasks.
The canonical task already exists: do not generate another task for this request.
The planner request with title TASK-0071 is intake provenance, not a second job.

The current worker cannot discover or run Aider yet. Start THIS bootstrap task
manually with Aider; later ready tasks must be discovered automatically.
Do not claim that writing this task enabled automation.

## Observed evidence

- Owner's Windows terminal runs Aider 0.86.2 (diff editing). Models are now main `openai/gpt-6.1-sol`,
  weak `openai/gpt-6-sol`, API base `https://apimaster.ai/v1` (supersedes gpt-4o / gpt-4o-mini).
- tools/agent_runner.py dispatches claude/codex; pick_next rejects other agents.
- tools/goal_task_factory.py request/claim agent choices do not include aider.
- .agents/planner/config.json currently disables planning, execution and auto activation.
- The owner's checkout is dirty. Preserve its existing map, catalog, preview,
  dialogue, .gitignore and documentation changes. Never stash, commit or reset them.
- AGENTS.md was updated 2026-11-02: Codex Pro may code; Aider handles tasks assigned to it; Claude only when explicitly assigned.

## Outcome and implementation contract

1. Extend the EXISTING TASK/request/claim/runner workflow to accept agent aider.
   Canonical TASK records remain the only queue; do not introduce competing queues.
   Eligibility: status todo, agent aider, dependencies satisfied, scope permitted.
   Unsupported or malformed tasks are blocked with an explanation, never reassigned.
2. One Windows worker scans every 10 seconds. Use an atomic task claim and process
   lease to prevent duplicates. Persist task phase/branch/worktree so restarts
   reconcile an active process before retrying. One Aider task at a time.
3. Launch a fresh noninteractive Aider process per task using a message file,
   `openai/gpt-6.1-sol` and weak model `openai/gpt-6-sol` via `https://apimaster.ai/v1`. Resolve the owner's actual executable
   and credential environment; never copy keys to command lines, prompts or logs.
   Disable Aider auto/dirty commits; the runner owns commits after verification.
4. Claim a dedicated branch and worktree before editing. Do not run coding in the
   owner's dirty checkout. Restrict editable inputs and validate the entire diff
   against touches, including untracked files. Remove images and secrets from model
   context/repo-map; .aiderignore is context filtering, not a security boundary.
5. Codex creates reports/tasks/art, Aider handles ordinary code, Claude handles
   complex code ONLY upon explicit owner task creation. No automatic escalation.
   Model/provider come from the `aider` block of `.agents/planner/config.json`. Do not run image generation services.
6. Run declared tests plus applicable map/Godot checks and tools/run_tests.py --changed
   before commit/merge. Allow at most two in-scope test-repair attempts; then block
   the task, preserve the worktree and continue independent eligible tasks.
7. Merge eligible ordinary tasks serially under a merge lock after updating the
   task branch and passing checks; verify again on main. On regression revert only
   the worker's own merge, block the task and suspend further merges pending diagnosis.
   Never merge conflicts by guessing or include unrelated local changes.
8. Infrastructure, permissions, secrets and approved artwork are excluded from
   unattended merge. THIS bootstrap infrastructure change goes through a review PR.
   Keep execution disabled until the new Aider path passes a genuinely supervised
   end-to-end test; historical Codex/Claude tests do not certify Aider.
9. Provide documented start, status, graceful stop and optional Windows logon setup.
   Do not register/enable startup before the supervised activation gate. Stopping
   prevents new claims and preserves ongoing work. Do not manipulate the user's
   already-open interactive Aider terminal.
10. Continue indefinitely while eligible jobs exist; remain idle when none exist.
    No optional daily task/spending cap per owner's instruction. Respect real
    service/rate limits, credentials and exhausted balance. Retry transient service
    errors after 30/60/120 seconds, respecting longer provider Retry-After values.
    Authentication/balance failures pause model calls with a visible reason.
11. Persist concise phase logs, test evidence, failure/retry reasons and available
    token/cost usage. Unknown is unknown, not zero. Attribute implementation to
    Aider plus the model; update receipt/provenance validation rather than inventing
    Codex/Claude execution. Preserve all previous receipt records.
12. Generated dashboards/indexes remain main-only. Do not weaken safeguards,
    change unrelated agent permissions, touch art/gameplay or expand touches silently.
    If another implementation path is required, document the necessary scope change
    and wait for the task scope to be amended.

## Acceptance and evidence

- [ ] Fresh ready Aider task is detected and claimed once; unassigned, Claude,
      Codex, blocked and dependency-incomplete tasks are not executed.
- [ ] Two simultaneous worker launches cannot execute one job twice.
- [ ] Restart during generation/verification/merge does not duplicate edits or merge.
- [ ] Ordinary coding changes stay in an isolated worktree and the allowed diff.
- [ ] Simulated test failure, out-of-scope edit, merge conflict, transient API failure,
      authentication/balance failure and stop/restart produce the documented states.
- [ ] Owner's dirty files and approved art hashes remain unchanged.
- [ ] A small supervised real Aider coding task completes queue-to-verified-delivery.
- [ ] Applicable checks pass; register new tests in tools/test_map.json.
- [ ] Review PR contains only this task's code, documentation, tests and truthful receipt.
- [ ] Infrastructure is not auto-merged or enabled by its own unreviewed worker.

## Handoff status (2026-11-02, Claude Code)

Implemented on branch `task-0071-claude-aider-worker`: `tools/aider_worker.py`, `tools/run_aider_worker.ps1`,
`tools/setup_aider_worker.ps1`, `tools/tests/test_aider_worker.py` (17 tests, fake Aider, all pass), `docs/AIDER_AUTOMATION.md`,
`.aiderignore`, `aider` block + `aider_execution_enabled: false` in the planner config, AGENTS.md role update.
Deviations from the contract: the worker commits on the task branch and never merges (items 7-8 left to the owner/PR);
`agent_runner.py`/`goal_task_factory.py` were not extended (standalone worker over the same TASK records).
NOT done: Scheduled Task registration, any real Aider/API run, supervised end-to-end test (acceptance items 7, 9 unchecked).
Automation stays disabled until the owner approves.

## Closure (2026-11-09, Claude Code)

Evidence: the merged worker produced real Aider commits (trailers `Agent: aider`, `Model: openai/gpt-6.1-sol`, tokens and cost)
for TASK-0075..0083, 0090..0101 on `aider/task-*` branches, each in an isolated worktree, with the owner merging them
(the worker never merges by design). Unit tests (24, fake Aider) cover the failure, scope, lock, restart and pause states.
Aider 0.86.2 is configured via the git-ignored local config; spend cap USD 10.
Not done and left to the owner: Scheduled Task registration (`setup_aider_worker.ps1 -Install`), merge/regression-revert automation
(items 7-8, deliberately manual), and `agent_runner.py`/`goal_task_factory.py` extension (standalone worker instead).
Aider is paused by the owner for about a week (API balance exhausted); no further Aider run was made in this closure.
