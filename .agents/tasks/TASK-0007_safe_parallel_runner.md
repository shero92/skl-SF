---
id: TASK-0007
status: review
owner: chatgpt
branch: feat/safe-parallel-agent-runner
agent: codex
touches: tools/agent_runner.py,tools/agent_workflow.py,tools/goal_task_factory.py,.agents/project/,.claude/settings.json
test: python -m unittest discover -s tools/tests -p test_parallel_safety.py
done_when: Supervised worktree safety tests pass before allowing direct merges
started_at: unknown
cost_usd: unknown
depends_on: TASK-0006
issue: none
art_request: none
---
# Safe local parallel task execution and merge runner

**Goal:** Allow Claude and Codex to run independently in temporary worktrees, while claims,
paths, tests, sequential merge locks and rollback protect main.

## Acceptance
- [x] Canonical task agent, touches, test, done_when enforced and collisions rejected.
- [x] ACTIVE.md generated on main from claims, no generated dashboards in task branches.
- [x] CLAUDE settings deny image reads and main runner refuses art paths.
- [ ] Execute one supervised real task using local Windows subscription CLIs.
- [ ] Enable execution_enabled=true only after successful supervised end-to-end test.

## Evidence / handoff
- Changes: task schema, local runner, safe path validation, receipt integration,
  graphics delivery pipeline, reference render verification and owner policy.
- Tests: CI and supervised Windows E2E outstanding.
- PR: review required.
- Next: supervised local E2E, only then enable execution.
