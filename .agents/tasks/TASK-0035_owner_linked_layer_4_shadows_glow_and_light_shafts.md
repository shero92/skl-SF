---
id: TASK-0035
status: todo
owner: unassigned
branch: none
agent: claude
touches: map_factory/scripts/shadow_factory.gd
test: py -3 tools/run_tests.py --only godot_map_smoke
done_when: Every placement with shadow data gets an owner-linked shadow at z 20; lantern/candle glow (D015/D016) and light-shaft entries are supported
started_at: unknown
cost_usd: unknown
depends_on: none
issue: none
art_request: none
---
# Owner-linked layer 4 shadows, glow and light shafts

**Source:** goal:GOAL-0001:g1-m5-shadow-light
**Created:** 2026-10-27
**Goal:** GOAL-0001
**Type:** feature
**Priority:** normal
**Suggested agent:** claude (owner reassigned from codex on 2026-10-26 to run in parallel with TASK-0033; routing heuristic, not a performance claim)
**File:** map_factory/scripts/shadow_factory.gd
**Line:** unspecified
**Problem:** Shadows must be linked to their owner and drawn at z 20 under it; light shafts are not supported

## Acceptance
- [ ] Every placement with shadow data gets an owner-linked shadow at z 20; lantern/candle glow (D015/D016) and light-shaft entries are supported
- [ ] Test: py -3 tools/run_tests.py --only godot_map_smoke
- [ ] PR and observed test evidence.

## Agent prompt
Outcome: Every placement with shadow data gets an owner-linked shadow at z 20; lantern/candle glow (D015/D016) and light-shaft entries are supported. Evidence: Shadows must be linked to their owner and drawn at z 20 under it; light shafts are not supported. Target: map_factory/scripts/shadow_factory.gd (line unspecified). Verify with: py -3 tools/run_tests.py --only godot_map_smoke. Read AGENTS.md and this task, then only the target file. Verify the issue and location before changing code. Work only within Map Factory. Never generate artwork. Stop when evidence is missing. Commit the task, token receipt and summary on a PR branch, never main.

## Budget
- Aim below 12000 tokens; context estimate, not enforced cap.
- Read only targeted files, then expand if necessary.

## Evidence / handoff
- Changed files: none.
- Tests: not run.
- PR: none.
- Next: claim task after checking blockers.
