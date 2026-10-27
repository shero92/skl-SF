---
id: TASK-0060
status: todo
owner: unassigned
branch: none
agent: claude
touches: map_factory/maps/hero_room_01/recovery_queue_audit.json
test: py -3 -m unittest discover -s tools/tests -p test_agent_workflow.py
done_when: Write bounded text-only JSON audit for review/blocked tasks: canonical ID, branch/PR/merge SHA, observed test evidence or unknown, proposed state and exact outstanding blocker. Never mark visual work approved; distinguish infrastructure merge from art acceptance. Only propose canonical updates for main-side coordinator; no duplicate implementation or changes to art/security.
started_at: unknown
cost_usd: unknown
depends_on: none
issue: none
art_request: none
---
# Audit stale recovery review records against merged evidence

**Source:** goal:GOAL-0001:recovery-queue-evidence-audit
**Created:** 2026-10-27
**Goal:** GOAL-0001
**Type:** investigation
**Priority:** high
**Suggested agent:** claude (routing heuristic, not a performance claim)
**File:** map_factory/maps/hero_room_01/recovery_queue_audit.json
**Line:** unspecified
**Problem:** TASK-0053 and TASK-0054..0057 remain review while main log includes subsequent merged PRs. Blender candidate delivery or numerical similarity is not art approval. TASK-0007 operating evidence also needs documentary reconciliation.

## Acceptance
- [ ] Write bounded text-only JSON audit for review/blocked tasks: canonical ID, branch/PR/merge SHA, observed test evidence or unknown, proposed state and exact outstanding blocker. Never mark visual work approved; distinguish infrastructure merge from art acceptance. Only propose canonical updates for main-side coordinator; no duplicate implementation or changes to art/security.
- [ ] Test: py -3 -m unittest discover -s tools/tests -p test_agent_workflow.py
- [ ] PR and observed test evidence.

## Agent prompt
Outcome: Write bounded text-only JSON audit for review/blocked tasks: canonical ID, branch/PR/merge SHA, observed test evidence or unknown, proposed state and exact outstanding blocker. Never mark visual work approved; distinguish infrastructure merge from art acceptance. Only propose canonical updates for main-side coordinator; no duplicate implementation or changes to art/security.. Evidence: TASK-0053 and TASK-0054..0057 remain review while main log includes subsequent merged PRs. Blender candidate delivery or numerical similarity is not art approval. TASK-0007 operating evidence also needs documentary reconciliation.. Target: map_factory/maps/hero_room_01/recovery_queue_audit.json (line unspecified). Verify with: py -3 -m unittest discover -s tools/tests -p test_agent_workflow.py. Read AGENTS.md and this task, then only the target file. Verify the issue and location before changing code. Work only within Map Factory. Never generate artwork. Stop when evidence is missing. Commit the task, token receipt and summary on a PR branch, never main.

## Budget
- Aim below 30000 tokens; context estimate, not enforced cap.
- Read only targeted files, then expand if necessary.

## Evidence / handoff
- Changed files: none.
- Tests: not run.
- PR: none.
- Next: claim task after checking blockers.
