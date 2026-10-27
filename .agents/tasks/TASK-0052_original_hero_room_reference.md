---
id: TASK-0052
status: review
owner: codex
branch: codex/hero-original-reference
agent: codex
touches: map_factory/references/hero_room_01_original.png,map_factory/references/hero_room_01_original.reference.json,.agents/planner/goals.json,.agents/planner/goals/GOAL-0001/goal.md,.agents/planner/goals/GOAL-0001/state.json,.agents/graphics/requests/,.agents/tasks/TASK-0001_reference_baseline.md
test: py -3 tools/run_tests.py --only map_reference --only task_evidence
done_when: Original user source bytes and SHA256 provenance preserved and linked; no artistic approval or map publication
started_at: 2026-10-27T11:06:11.210116+01:00
cost_usd: unknown
depends_on: none
issue: none
art_request: none
---
# Preserve authentic original Hero Room reference

**Goal:** GOAL-0001
**Source:** request:REQ-ba7a6e74f1ad

Owner explicitly supplied the reference and approved exact-byte preservation. This is supervised source intake, not an unattended coding/art-generation task. Preserve the previous reference, all production assets and historical map revisions. Source identity approval is separate from room visual approval.

## Acceptance
- [ ] Actual SHA256 equals recorded original 42511e4e05176d9057775fa05562ca5b91675d32ba70ae9b8ba1012b41df25a7; PNG header is 1448x1086.
- [ ] Record owner-provided provenance and reference-only evidence; no fabricated measurements or asset approval.
- [ ] Goal and requests identify authentic source; keep measurement and room-approval gates.
- [ ] Tests and PR recorded.

## Evidence
- Exact source SHA256 and PNG header verified before copying; copied bytes hash identically. Previous reference and historical maps unchanged.
- Goal state/ART records now distinguish verified original reference from pending calibration and visual approval.
- No production sprite, map version or approval changed. Next: current-version Godot capture and calibration.

- Validation: reference evidence check passed; Python run 26/27 suites passed, with candidate_room requiring omitted production images in the sparse checkout. Hosted full-checkout validation remains required.
