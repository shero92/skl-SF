---
id: TASK-0051
status: done
owner: codex
branch: codex/manual-agent-launcher
agent: codex
touches: tools/run_agents_manual.ps1,tools/MANUAL_AGENTS.md,tools/manual_agents.py,tools/agent_runner.py,tools/run_local_agent.ps1,tools/runner_safety.py,tools/task_evidence.py,tools/tests/test_manual_agents.py,tools/tests/test_parallel_safety.py,tools/tests/test_runner_main_clean.py,tools/test_map.json
test: py -3 -m unittest discover -s tools/tests -p test_manual_agents.py
done_when: Manual launcher isolates user changes, dispatches independent eligible tasks with shared count/deadline, safe per-task failures, tested evidence gates, and never auto-integrates art.
started_at: 2026-10-27T10:16:51.197794+01:00
cost_usd: unknown
depends_on: none
issue: none
art_request: none
---
# Manual bounded parallel Codex and Claude launcher

**Source:** request:REQ-8804b57fa62a
**Created:** 2026-10-27
**Goal:** manual request
**Type:** feature
**Priority:** critical
**Suggested agent:** codex (routing heuristic, not a performance claim)
**File:** tools/run_agents_manual.ps1
**Line:** unspecified
**Problem:** Owner approved manual PowerShell launcher; existing scheduled worker has per-agent budgets, stops on task failure, and cannot coordinate a shared global session or ART capability gates.

## Acceptance
- [ ] Manual launcher isolates user changes, dispatches independent eligible tasks with shared count/deadline, safe per-task failures, tested evidence gates, and never auto-integrates art.
- [ ] Test: py -3 -m unittest discover -s tools/tests -p test_manual_agents.py
- [ ] PR and observed test evidence.

## Agent prompt
Outcome: Manual launcher isolates user changes, dispatches independent eligible tasks with shared count/deadline, safe per-task failures, tested evidence gates, and never auto-integrates art.. Evidence: Owner approved manual PowerShell launcher; existing scheduled worker has per-agent budgets, stops on task failure, and cannot coordinate a shared global session or ART capability gates.. Target: tools/run_agents_manual.ps1 (line unspecified). Verify with: py -3 -m unittest discover -s tools/tests -p test_manual_agents.py. Read AGENTS.md and this task, then only the target file. Verify the issue and location before changing code. Work only within Map Factory. Never generate artwork. Stop when evidence is missing. Commit the task, token receipt and summary on a PR branch, never main.

## Budget
- Aim below 12000 tokens; context estimate, not enforced cap.
- Read only targeted files, then expand if necessary.

## Evidence / handoff
- Changed files: none.
- Tests: not run.
- PR: none.
- Next: claim task after checking blockers.

## Implementation evidence
- Manual PowerShell entrypoint and shared coordinator, global count/deadline, isolated worktrees, cross-clone lease, safe independent failures, one bounded repair, review-only infrastructure/ART flow.
- Evidence gates verify approved reference bytes/provenance and separate measurements/visual approval. No art capability enabled by assumption.
- Corrected merged TASK-0036 status and promoted TASK-0039; the historical ART quality gates remain.
- Tests: manual_agents 18/18; task_evidence 12/12; runner cleanup/cancellation 15/15; runner parallel 17/17; changed Python checks 11/11. Final expanded suite pending.
- Real PowerShell DryRun succeeded; bounded fake-CLI trial succeeded; no production model launched during tests.
- Next: PR validation and independently reviewed rollout.

- Final validation: 18 manual coordinator tests, 12 evidence tests, 15 cleanup/cancellation tests and 17 runner-parallel tests passed. Expanded Python run: 26/27 suites pass in image-free worktree; candidate_room requires omitted production PNG presence. The unchanged candidate_room suite passes on the complete primary checkout. Hosted CI must validate full checkout.
- No image assets, historical snapshots, generated dashboards or user-owned working files modified.

## Approved merge verification
- Owner explicitly approved PR #44; merged as 4baa4f4394556194a52e17976b76faf96fa08d9f.
- Main verification: 26 Python groups passed; candidate_room passed after restoring deterministic validator resources (27/27 combined). Godot checks passed 3/3; both registered maps validated.
- Code workers remain image-free; renderer resources were only available in the isolated deterministic validator.
- gh CLI authentication remains an operational blocker; no production model task launched.
