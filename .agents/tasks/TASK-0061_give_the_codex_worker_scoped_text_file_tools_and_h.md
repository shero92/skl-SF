---
id: TASK-0061
status: todo
owner: unassigned
branch: none
agent: claude
touches: tools/agent_runner.py,tools/agent_file_bridge.py,tools/tests/test_agent_file_bridge.py,tools/tests/test_runner_main_clean.py
test: py -3 -m unittest discover -s tools/tests -p test_runner_main_clean.py
done_when: Provide a task-scoped text read/edit tool bridge to Codex while retaining shell/git/image restrictions, existing permission settings and workspace isolation. Limit normalized symlink-resolved paths to authorized text touches plus minimal read-only instructions/dependencies; reject traversal, outside writes, binaries and arbitrary execution. Preflight actual capability and expose sanitized terminal reason instead of generic no-code only. Fake CLI regression must read and edit a synthetic allowed file through the bridge; reject out-of-scope/image access. No model calls in tests. Infra PR; do not pretend this completes TASK-0059.
started_at: unknown
cost_usd: unknown
depends_on: none
issue: none
art_request: none
---
# Give the Codex worker scoped text file tools and honest failure evidence

**Source:** goal:GOAL-0001:recovery-agent-file-capability
**Created:** 2026-10-27
**Goal:** GOAL-0001
**Type:** feature
**Priority:** critical
**Suggested agent:** claude (routing heuristic, not a performance claim)
**File:** tools/agent_runner.py
**Line:** unspecified
**Problem:** TASK-0059 codex-exec final message states no local file read tool is available without shell, which runner forbids; it made no changes. Existing generic error hid the actual capability failure.

## Acceptance
- [ ] Provide a task-scoped text read/edit tool bridge to Codex while retaining shell/git/image restrictions, existing permission settings and workspace isolation. Limit normalized symlink-resolved paths to authorized text touches plus minimal read-only instructions/dependencies; reject traversal, outside writes, binaries and arbitrary execution. Preflight actual capability and expose sanitized terminal reason instead of generic no-code only. Fake CLI regression must read and edit a synthetic allowed file through the bridge; reject out-of-scope/image access. No model calls in tests. Infra PR; do not pretend this completes TASK-0059.
- [ ] Test: py -3 -m unittest discover -s tools/tests -p test_runner_main_clean.py
- [ ] PR and observed test evidence.

## Agent prompt
Outcome: Provide a task-scoped text read/edit tool bridge to Codex while retaining shell/git/image restrictions, existing permission settings and workspace isolation. Limit normalized symlink-resolved paths to authorized text touches plus minimal read-only instructions/dependencies; reject traversal, outside writes, binaries and arbitrary execution. Preflight actual capability and expose sanitized terminal reason instead of generic no-code only. Fake CLI regression must read and edit a synthetic allowed file through the bridge; reject out-of-scope/image access. No model calls in tests. Infra PR; do not pretend this completes TASK-0059.. Evidence: TASK-0059 codex-exec final message states no local file read tool is available without shell, which runner forbids; it made no changes. Existing generic error hid the actual capability failure.. Target: tools/agent_runner.py (line unspecified). Verify with: py -3 -m unittest discover -s tools/tests -p test_runner_main_clean.py. Read AGENTS.md and this task, then only the target file. Verify the issue and location before changing code. Work only within Map Factory. Never generate artwork. Stop when evidence is missing. Commit the task, token receipt and summary on a PR branch, never main.

## Budget
- Aim below 30000 tokens; context estimate, not enforced cap.
- Read only targeted files, then expand if necessary.

## Evidence / handoff
- Changed files: none.
- Tests: not run.
- PR: none.
- Next: claim task after checking blockers.
