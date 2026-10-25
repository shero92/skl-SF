---
id: TASK-0003
status: review
owner: coding-agent
branch: feat/agent-task-cost-accounting
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
- [ ] Review PR and test on one real session from each CLI.

## Evidence / handoff
- Changes: tools/agent_costs.py, tools/tests/test_agent_costs.py, project hooks, monitoring records, GitHub Actions.
- Tests: GitHub workflow agent_costs.yml, pending real-client verification.
- PR: branch feat/agent-task-cost-accounting.
- Next: verify the hooks on both local agents and merge after review.
