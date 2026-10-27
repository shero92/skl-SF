---
id: TASK-0056
status: review
owner: claude
branch: fix/agent-costs-hook-worktrees
agent: claude
touches: tools/agent_costs.py,tools/tests/test_agent_costs.py,.agents/planner/requests/REQ-0ba1e02edd6b.json,.agents/tasks/TASK-0056_agent_costs_hook_worktrees.md
test: py -3 tools/run_tests.py --only agent_costs
done_when: When its own checkout has no active task for the agent, the hook records the session in the single other worktree of the same repository that has one; zero or several candidates record nothing; regression test with a real git worktree
started_at: 2026-10-27
cost_usd: unknown
depends_on: none
issue: none
art_request: none
---
# agent_costs hook: record sessions for a task started in another worktree

**Source:** request:REQ-0ba1e02edd6b
**Created:** 2026-10-27
**Goal:** manual request
**Type:** bug
**Priority:** high
**Suggested agent:** claude (owner request)
**File:** tools/agent_costs.py
**Line:** unspecified
**Problem:** The hook writes session files only into its own checkout's .agents/monitoring/.local; when a session runs in the main checkout (or another worktree) and agent_costs start runs in the task worktree, no session is recorded and the receipt stays unknown (TASK-0055)

## Acceptance
- [x] When its own checkout has no active task for the agent, the hook records the session in the single other worktree of the same repository that has one; zero or several candidates record nothing; regression test with a real git worktree
- [x] Test: py -3 tools/run_tests.py --only agent_costs
- [ ] PR and observed test evidence.

## Evidence / handoff
- Changed files: tools/agent_costs.py (hook_local: own checkout first, else the single other worktree of the repo tracking the agent; zero or several -> nothing recorded), tools/tests/test_agent_costs.py (2 regression tests with a real git worktree).
- Tests: test_agent_costs 15/15; the main-checkout hook test fails on the old code and passes with the fix; py -3 tools/run_tests.py --changed passed.
- Note: this session's hook still runs main's old agent_costs.py until this merges, so TASK-0056's own receipt stays unknown.
- PR: none.
