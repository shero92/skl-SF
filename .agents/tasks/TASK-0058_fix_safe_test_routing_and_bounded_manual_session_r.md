---
id: TASK-0058
status: review
owner: claude
branch: work/task-0058-0baf0d83
agent: claude
touches: tools/runner_safety.py,tools/manual_agents.py,tools/tests/test_manual_agents.py,tools/tests/test_runner_parallel.py
test: py -3 -m unittest discover -s tools/tests -p test_manual_agents.py
done_when: Accept explicitly trusted existing router suite names including art_delivery without shell/arbitrary command expansion; regression-test TASK-0041 command. Pulse independent of task execution budget. Explain no-ready/quota/time outcomes; respect global deadline and preserve work. One ordinary repair only; no security changes. Infrastructure PR required.
started_at: 2026-10-27T16:08:22.621530+00:00
cost_usd: unknown
depends_on: none
issue: none
art_request: none
---
# Fix safe test routing and bounded manual session readiness

**Source:** goal:GOAL-0001:recovery-runner-readiness
**Created:** 2026-10-27
**Goal:** GOAL-0001
**Type:** bug
**Priority:** critical
**Suggested agent:** claude (routing heuristic, not a performance claim)
**File:** tools/runner_safety.py
**Line:** unspecified
**Problem:** TASK-0041 was blocked with Only allowlisted router tests permitted: art_delivery is a registered suite but safe_test excludes it. A 30-minute session silently skips pulse/start because per-task timeout is also 1800 seconds.

## Acceptance
- [ ] Accept explicitly trusted existing router suite names including art_delivery without shell/arbitrary command expansion; regression-test TASK-0041 command. Pulse independent of task execution budget. Explain no-ready/quota/time outcomes; respect global deadline and preserve work. One ordinary repair only; no security changes. Infrastructure PR required.
- [ ] Test: py -3 -m unittest discover -s tools/tests -p test_manual_agents.py
- [ ] PR and observed test evidence.

## Agent prompt
Outcome: Accept explicitly trusted existing router suite names including art_delivery without shell/arbitrary command expansion; regression-test TASK-0041 command. Pulse independent of task execution budget. Explain no-ready/quota/time outcomes; respect global deadline and preserve work. One ordinary repair only; no security changes. Infrastructure PR required.. Evidence: TASK-0041 was blocked with Only allowlisted router tests permitted: art_delivery is a registered suite but safe_test excludes it. A 30-minute session silently skips pulse/start because per-task timeout is also 1800 seconds.. Target: tools/runner_safety.py (line unspecified). Verify with: py -3 -m unittest discover -s tools/tests -p test_manual_agents.py. Read AGENTS.md and this task, then only the target file. Verify the issue and location before changing code. Work only within Map Factory. Never generate artwork. Stop when evidence is missing. Commit the task, token receipt and summary on a PR branch, never main.

## Budget
- Aim below 30000 tokens; context estimate, not enforced cap.
- Read only targeted files, then expand if necessary.

## Evidence / handoff
- Changed files: none.
- Tests: not run.
- PR: none.
- Next: claim task after checking blockers.

## Runner evidence
- Claimed by local runner at 2026-10-27T16:08:22.610356+00:00

## Runner evidence
- Validated infrastructure PR: https://github.com/shero92/skl-SF/pull/57
