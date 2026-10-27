---
id: TASK-0057
status: review
owner: claude
branch: fix/codex-pricing-gitignore
agent: claude
touches: .agents/monitoring/pricing.json,.gitignore,.agents/planner/requests/REQ-f51d5632895e.json,.agents/tasks/TASK-0057_codex_pricing_gitignore.md
test: py -3 tools/run_tests.py --only agent_costs
done_when: pricing.json carries the official OpenAI standard short-context rates for gpt-6.1-sol (input 2.00, cached 0.10, output 10.00 per 1M) and .gitignore ignores .claude/worktrees/; agent_costs tests pass
started_at: 2026-10-27
cost_usd: unknown
depends_on: none
issue: none
art_request: none
---
# Price the Codex model gpt-6.1-sol and ignore local Claude worktrees

**Source:** request:REQ-f51d5632895e
**Created:** 2026-10-27
**Goal:** manual request
**Type:** bug
**Priority:** normal
**Suggested agent:** claude (owner request)
**File:** .agents/monitoring/pricing.json
**Line:** unspecified
**Problem:** Codex receipts record model gpt-6.1-sol, which is missing from .agents/monitoring/pricing.json, so their cost stays unknown even with tokens (TASK-0009); claude -p runs leave untracked .claude/worktrees/ in the main checkout

## Acceptance
- [x] pricing.json carries the official OpenAI standard short-context rates for gpt-6.1-sol (input 2.00, cached 0.10, output 10.00 per 1M) and .gitignore ignores .claude/worktrees/; agent_costs tests pass
- [x] Test: py -3 tools/run_tests.py --only agent_costs
- [ ] PR and observed test evidence.

## Evidence / handoff
- Changed files: .agents/monitoring/pricing.json (gpt-6.1-sol 2.00/0.10/10.00 per 1M, official OpenAI page checked 2026-10-27, short-context tier), .gitignore (.claude/worktrees/).
- Tests: py -3 tools/run_tests.py --changed 30/30; cost_from_tokens on TASK-0009's recorded tokens gives 0.161225 USD. Existing receipts are not repriced (records stay as written).
- PR: none.
