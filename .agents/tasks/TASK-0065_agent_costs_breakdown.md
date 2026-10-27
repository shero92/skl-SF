---
id: TASK-0065
status: review
owner: claude
branch: feat/agent-costs-breakdown
agent: claude
touches: tools/agent_costs.py,tools/tests/test_agent_costs.py,.agents/planner/requests/REQ-78002c7041d9.json,.agents/tasks/TASK-0065_agent_costs_breakdown.md
test: py -3 tools/run_tests.py --only agent_costs
done_when: py -3 tools/agent_costs.py breakdown prints per receipt the API-equivalent USD and its split into uncached input, cache read, cache write and output from receipts and pricing.json, lists receipts without tokens or price as unknown, and --json gives the same data; read-only
started_at: 2026-10-27
cost_usd: unknown
depends_on: none
issue: none
art_request: none
---
# agent_costs breakdown: cost share per receipt

**Source:** request:REQ-78002c7041d9
**Created:** 2026-10-27
**Goal:** manual request
**Type:** feature
**Priority:** normal
**Suggested agent:** claude (owner request)
**File:** tools/agent_costs.py
**Line:** unspecified
**Problem:** Cost analysis needed an ad-hoc script to see that about half of each Claude task's cost is 1h cache writes and a third is output; there is no built-in command

## Acceptance
- [x] py -3 tools/agent_costs.py breakdown prints per receipt the API-equivalent USD and its split into uncached input, cache read, cache write and output from receipts and pricing.json, lists receipts without tokens or price as unknown, and --json gives the same data; read-only
- [x] Test: py -3 tools/run_tests.py --only agent_costs
- [ ] PR and observed test evidence.

## Evidence / handoff
- Changed files: tools/agent_costs.py (cost_parts shared by cost_from_tokens and the new read-only `breakdown [--json]` command), tools/tests/test_agent_costs.py (breakdown test).
- Tests: test_agent_costs 16/16; py -3 tools/run_tests.py --changed 5/5.
- Real run on main receipts: 2.577 USD known over 7 of 35 receipts; overall input 3%, cache read 13%, cache write 49%, output 35%.
- PR: none.
