---
id: TASK-0055
status: review
owner: claude
branch: fix/agent-costs-started-at
agent: claude
touches: tools/agent_costs.py,tools/tests/test_agent_costs.py,.agents/planner/requests/REQ-7f6df8e5f890.json,.agents/tasks/TASK-0055_agent_costs_started_at.md
test: py -3 tools/run_tests.py --only agent_costs
done_when: A session that started before start contributes only the usage of transcript messages timestamped at or after started_at; untimestamped usage in such a session stays unknown; fresh sessions are unchanged; regression tests cover Claude and Codex transcripts
started_at: 2026-10-27
cost_usd: unknown
depends_on: none
issue: none
art_request: none
---
# agent_costs: count usage after started_at for sessions opened before start

**Source:** request:REQ-7f6df8e5f890
**Created:** 2026-10-27
**Goal:** manual request
**Type:** bug
**Priority:** high
**Suggested agent:** claude (owner request)
**File:** tools/agent_costs.py
**Line:** unspecified
**Problem:** Prompt-driven runs (claude -p) and interactive sessions run agent_costs start inside an already-open session; finish drops the whole session as old_session_unattributable, so receipts record unknown tokens/cost (19 of 23 tasks, e.g. TASK-0038, TASK-0054)

## Acceptance
- [x] A session that started before start contributes only the usage of transcript messages timestamped at or after started_at; untimestamped usage in such a session stays unknown; fresh sessions are unchanged; regression tests cover Claude and Codex transcripts
- [x] Test: py -3 tools/run_tests.py --only agent_costs
- [ ] PR and observed test evidence.

## Evidence / handoff
- Changed files: tools/agent_costs.py (read_transcript since= cutoff, Codex cumulative baseline subtraction, finish uses it for sessions opened before start; whole-session statusline cost no longer billed to such tasks), tools/tests/test_agent_costs.py (3 regression tests).
- Tests: test_agent_costs 13/13; the two new attribution tests fail on the old code (2 errors) and pass with the fix; py -3 tools/run_tests.py --changed 5/5.
- Known gap (not in scope): the hook records sessions in the checkout it runs in, so a session whose cwd is the main checkout while start runs in a worktree still has no session file (diagnose shows none for this task); this receipt therefore stays unknown.
- PR: https://github.com/shero92/skl-SF/pull/53
