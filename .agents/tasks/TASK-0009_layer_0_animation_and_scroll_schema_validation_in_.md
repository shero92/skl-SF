---
id: TASK-0009
status: in_progress
owner: codex
branch: work/task-0009-55af9186
agent: codex
touches: tools/map_factory_cli.py,tools/tests/test_map_layers.py
test: py -3 -m unittest tools.tests.test_map_layers
done_when: CLI accepts animation {frames, fps} and scroll {vx, vy} on layer 0 entries and rejects frame IDs missing from the asset catalog, with unit tests covering accept and reject cases
started_at: 2026-10-26T00:15:04.283738+00:00
cost_usd: unknown
depends_on: none
issue: none
art_request: none
---
# Layer 0 animation and scroll schema validation in map CLI

**Source:** ai:7c862146605a441a
**Created:** 2026-10-26
**Goal:** GOAL-0001
**Type:** feature
**Priority:** high
**Suggested agent:** codex (routing heuristic, not a performance claim)
**File:** tools/map_factory_cli.py
**Line:** unspecified
**Problem:** Layer 0 placements cannot describe animation frames, fps or scroll, so the Hero Room background cannot be alive (goal step g1-m2-bg-schema).

## Acceptance
- [ ] CLI accepts animation {frames, fps} and scroll {vx, vy} on layer 0 entries and rejects frame IDs missing from the asset catalog, with unit tests covering accept and reject cases
- [ ] Test: py -3 -m unittest tools.tests.test_map_layers
- [ ] PR and observed test evidence.

## Agent prompt
Outcome: CLI accepts animation {frames, fps} and scroll {vx, vy} on layer 0 entries and rejects frame IDs missing from the asset catalog, with unit tests covering accept and reject cases. Evidence: Layer 0 placements cannot describe animation frames, fps or scroll, so the Hero Room background cannot be alive (goal step g1-m2-bg-schema).. Target: tools/map_factory_cli.py (line unspecified). Verify with: py -3 -m unittest tools.tests.test_map_layers. Read AGENTS.md and this task, then only the target file. Verify the issue and location before changing code. Work only within Map Factory. Never generate artwork. Stop when evidence is missing. Commit the task, token receipt and summary on a PR branch, never main.

## Budget
- Aim below 12000 tokens; context estimate, not enforced cap.
- Read only targeted files, then expand if necessary.

## Evidence / handoff
- Changed files: none.
- Tests: not run.
- PR: none.
- Next: claim task after checking blockers.

## Allowed touches
- tools/map_factory_cli.py
- tools/tests/test_map_layers.py

## Runner evidence
- Claimed by local runner at 2026-10-26T00:15:04.275661+00:00
