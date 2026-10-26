---
id: TASK-0007
status: blocked
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
- [x] Claude settings deny image reads; agent worktrees exclude images while code agents run.
- [x] Owner art request Issue helper; non-visual PNG delivery checks and gated asset registration.
- [x] Isolated genuine Godot goal QA capture and owner-only final signoff.
- [ ] Execute one supervised real task using local Windows subscription CLIs.
- [ ] Enable execution_enabled=true only after successful supervised end-to-end test.

## Evidence / handoff
- Changes: task schema, local runner, safe path validation, receipt integration,
  graphics delivery pipeline, reference render verification and owner policy.
- Tests: CI and supervised Windows E2E outstanding.
- PR: https://github.com/shero92/skl-SF/pull/8 (CI successful; infrastructure merge pending).
- Next: supervised Windows end-to-end task and image containment test. Configuration stays disabled until owner accepts actual results.

## Recovery reconciliation (supersedes stale configuration wording)
- Current config has execution_enabled=true and supervised_e2e_passed=true, with TASK-0009 merge 1bd74a054e698232d00c20f631fb9eab6a054717 at 2026-10-26T09:55:22.840855+00:00.
- This is recorded historical evidence, not a new containment certification. Remaining image-containment evidence must be independently checked before declaring this broad task complete. No configuration changed here.
