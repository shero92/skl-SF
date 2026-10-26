---
id: TASK-0033
status: review
owner: codex
branch: work/task-0033-background-runtime
agent: codex
touches: map_factory/scripts/background_factory.gd,map_factory/scripts/room_factory.gd,tools/map_factory_godot_smoke.gd,tools/tests/test_map_layers.py,tools/map_factory_layers.py
test: py -3 tools/run_tests.py --only map_layers --only godot_map_smoke
done_when: Sea cycles E010-E014 wave frames at the JSON fps, clouds scroll, foam animates, all at z 0; Godot smoke asserts animated background nodes exist
started_at: 2026-10-26T18:46:16.643405+01:00
cost_usd: unknown
depends_on: TASK-0009
issue: none
art_request: none
---
# Render the living layer 0 background in Godot

**Source:** goal:GOAL-0001:g1-m4-bg-render
**Created:** 2026-10-27
**Goal:** GOAL-0001
**Type:** feature
**Priority:** high
**Suggested agent:** codex (routing heuristic, not a performance claim)
**File:** map_factory/scripts/room_factory.gd
**Line:** unspecified
**Problem:** room_factory.gd has no animated background: sea, sky and foam render static

## Acceptance
- [ ] Sea cycles E010-E014 wave frames at the JSON fps, clouds scroll, foam animates, all at z 0; Godot smoke asserts animated background nodes exist
- [ ] Test: py -3 tools/run_tests.py --only map_layers --only godot_map_smoke
- [ ] PR and observed test evidence.

## Agent prompt
Outcome: Sea cycles E010-E014 wave frames at the JSON fps, clouds scroll, foam animates, all at z 0; Godot smoke asserts animated background nodes exist. Evidence: room_factory.gd has no animated background: sea, sky and foam render static. Target: map_factory/scripts/room_factory.gd (line unspecified). Verify with: py -3 tools/run_tests.py --only map_layers --only godot_map_smoke. Read AGENTS.md and this task, then only the target file. Verify the issue and location before changing code. Work only within Map Factory. Never generate artwork. Stop when evidence is missing. Commit the task, token receipt and summary on a PR branch, never main.

## Budget
- Aim below 12000 tokens; context estimate, not enforced cap.
- Read only targeted files, then expand if necessary.

## Evidence / handoff
- Changed files: background_factory.gd, room_factory.gd, map_factory_layers.py, map_factory_godot_smoke.gd, test_map_layers.py.
- Tests: `py -3 tools/run_tests.py --all --kind python`: 21/21 suites passed. Godot 4.7.2 headless image-free fixture: background runtime passed (fps, sea/foam loops, scroll/wrap, origins, static compatibility, removal and legacy JSON).
- PR: task branch work/task-0033-background-runtime, targeting main.
- Next: hosted full map smoke and PR review; then owner visual comparison. No visual approval claimed.

## Runner evidence
- Claimed by local runner at 2026-10-26T13:16:00.408854+00:00

## Runner evidence
- Runner failed: Agent CLI failed; code not merged

## Runner evidence
- Reset to todo: previous attempt (codex, 2026-10-26 14:16) stopped before any code: Codex CLI usage limit ("try again at 3:53 PM"). Not a code failure; retry once Codex usage is available. Error log saved in .agents/monitoring/.local/TASK-0033-e2b138c2/.

## Runner evidence
- Claimed by local runner at 2026-10-26T14:15:59.736769+00:00

## Runner evidence
- Runner failed: Agent CLI failed; code not merged

## Direct-session resume
- Owner asked Codex to perform this task here. Resume bypasses the failed CLI invocation only; no sandbox or image-firewall bypass.
- Prior runner worktree has no uncommitted code. Fresh task branch is based on current origin/main; primary art-integration checkout is untouched.
- Test touches include the existing Godot smoke harness and layer tests for the task acceptance checks.

- Verified compiler defect: create_layer_stack copies neither animation nor scroll; include tools/map_factory_layers.py to preserve these validated fields before runtime integration.

## Implementation evidence
- Preserve optional animation/scroll dictionaries through compilation, with copy isolation.
- Reuse existing layer-0 Sprite2D placements for registered-frame animation and velocity-based scrolling, preserving transforms and per-frame origins.
- Local Godot fixture uses text-only PlaceholderTexture2D resources; production art was never opened or restored. Full asset-backed smoke is delegated to existing hosted CI.
- Token/cost measurement is unknown when unavailable; completion receipt records actual provenance as codex.
