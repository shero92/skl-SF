---
id: TASK-0003
status: done
owner: coding-agent
branch: feat/agent-task-cost-accounting
agent: codex
touches: tools/agent_costs.py,tools/tests/test_agent_costs.py,.agents/monitoring/
test: python -m unittest discover -s tools/tests -p test_agent_costs.py
done_when: Token receipts and task leaderboard verifiable
started_at: unknown
cost_usd: unknown
depends_on: none
issue: none
art_request: none
---
# Track Claude and Codex usage per commit

Goal: commit one cost receipt with every coding task and build a transparent task leaderboard.

## Acceptance
- [x] Capture local Claude/Codex sessions, preserving unknown values.
- [x] Produce committed receipts and generated leaderboard, without transcripts.
- [x] Add CI/unit test checks.
- [x] PR #4 merged; Claude token/cost and Codex token capture tested on actual CLI sessions.

## Evidence / handoff
- Changes: tools/agent_costs.py, tools/tests/test_agent_costs.py, project hooks, monitoring records, GitHub Actions.
- Tests: GitHub workflow agent_costs.yml, pending real-client verification.
- PR: https://github.com/shero92/skl-SF/pull/4 (merged).
- Next: maintain model pricing and measurement coverage as clients change.
