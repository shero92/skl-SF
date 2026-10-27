---
id: TASK-0040
status: review
owner: claude
branch: work/task-0040-48a1ae7a
agent: claude
touches: map_factory/scripts/room_factory.gd,map_factory/scripts/shadow_factory.gd,tools/map_factory_layers.py,tools/map_factory_godot_smoke.gd,tools/tests/test_map_layers.py
test: py -3 tools/run_tests.py --only map_layers --only godot_map_smoke
done_when: Image-free runtime tests prove host move/remove, mounted offsets, independent owner shadows and front/back occlusion; no production fallback artwork
started_at: 2026-10-27T12:23:49.819851+00:00
cost_usd: unknown
depends_on: TASK-0033,TASK-0038
issue: none
art_request: none
---
# Complete depth sorting mounts and owner-linked shadows

**Source:** goal:GOAL-0001:g1-m6-sort-mount
**Created:** 2026-10-27
**Goal:** GOAL-0001
**Type:** feature
**Priority:** high
**Suggested agent:** claude (owner reassigned 2026-10-27: Codex usage limit; was codex) (routing heuristic, not a performance claim)
**File:** map_factory/scripts/room_factory.gd
**Line:** unspecified
**Problem:** Owner-approved recovery audit: Complete depth sorting mounts and owner-linked shadows

## Acceptance
- [ ] Image-free runtime tests prove host move/remove, mounted offsets, independent owner shadows and front/back occlusion; no production fallback artwork
- [ ] Test: py -3 tools/run_tests.py --only map_layers --only godot_map_smoke
- [ ] PR and observed test evidence.

## Agent prompt
Outcome: Image-free runtime tests prove host move/remove, mounted offsets, independent owner shadows and front/back occlusion; no production fallback artwork. Evidence: Owner-approved recovery audit: Complete depth sorting mounts and owner-linked shadows. Target: map_factory/scripts/room_factory.gd (line unspecified). Verify with: py -3 tools/run_tests.py --only map_layers --only godot_map_smoke. Read AGENTS.md and this task, then only the target file. Verify the issue and location before changing code. Work only within Map Factory. Never generate artwork. Stop when evidence is missing. Commit the task, token receipt and summary on a PR branch, never main.

## Budget
- Aim below 12000 tokens; context estimate, not enforced cap.
- Read only targeted files, then expand if necessary.

## Evidence / handoff
- Changed files: none.
- Tests: not run.
- PR: none.
- Next: claim task after checking blockers.

## Runner evidence
- Claimed by local runner at 2026-10-27T12:10:38.489525+00:00

## Runner evidence
- Released to todo: codex CLI usage limit, no code merged ({"type":"error","message":"You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 4:01 PM."}).

## Runner evidence
- Claimed by local runner at 2026-10-27T12:23:49.810313+00:00

## Runner evidence
- Validated infrastructure PR: https://github.com/shero92/skl-SF/pull/50
