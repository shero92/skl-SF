---
id: TASK-0125
status: review
owner: claude
agent: claude
priority: high
branch: claude/ci-regen-main
depends_on: none
issue: none
art_request: none
touches: tools/regenerate_main_outputs.py,tools/tests/test_regenerate_main_outputs.py,.github/workflows/regenerate_main_outputs.yml,tools/test_map.json
test: python tools/run_tests.py --changed
done_when: A post-merge job on main regenerates task boards, folder indexes, the cost report and the test index so the three strict main checks stop failing after every merge.
estimate_minutes: 45
---
# Stop main going stale after every merge

**Problem (verified 2026-11-10):** on main the workflows "Verify multi-agent task and graphics handoffs", "Verify project navigation indexes" and "Verify agent cost receipts" fail on every push with "Stale queues", "Stale folder indexes" and "Stale report". ADR-006 forbids generated files on task branches, but no job ever regenerated them on main (the last such commits were manual). Running the four writers on a main checkout fixes all four strict checks, so the data is sound; only the automation was missing.

**Fix:** tools/regenerate_main_outputs.py runs the four writers and then the strict checks; .github/workflows/regenerate_main_outputs.yml runs it on push to main and commits refreshed files as github-actions[bot] (no force push, rebase before push). The existing strict checks stay unchanged.

## Evidence / handoff
- Tests: test_regenerate_main_outputs.py (id regenerate_main_outputs).
- Risk: if main has branch protection that blocks the bot push, the job fails visibly; then run the script manually.
- Next: after merge confirm the bot commit lands and the three workflows turn green.
