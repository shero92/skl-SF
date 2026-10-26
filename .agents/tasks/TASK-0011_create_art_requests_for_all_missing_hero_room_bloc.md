---
id: TASK-0011
status: review
owner: codex
branch: work/task-0011-art-requests
agent: codex
touches: .agents/graphics/requests/,.agents/tasks/
test: py -3 -m unittest discover -s tools/tests -p test_art_delivery.py
done_when: One complete request per gap using canonical GRAPHICS.md request records (native size, reference path, palette, 4 filenames where orientation matters, shadow, layer, quality criteria) with a linked blocked_on_art task; no art generated
started_at: 2026-10-26T12:46:00.409046+01:00
cost_usd: unknown
depends_on: TASK-0008
issue: none
art_request: none
---
# Create ART requests for all missing Hero Room blocks

**Source:** goal:GOAL-0001:g1-m8-art-requests
**Created:** 2026-10-26
**Goal:** GOAL-0001
**Type:** investigation
**Priority:** critical
**Suggested agent:** claude (routing heuristic, not a performance claim)
**File:** tools/art_requests.py
**Line:** unspecified
**Problem:** Missing blocks by name/metadata audit, every uncertain item treated as missing (owner rejects a request if an existing asset fits). L0: drifting transparent cloud sprites (2-3); cliff-base foam loop frames (3-4); palm plants for the cliff edge. L1: broken/irregular front floor edge tiles; second blue rug for the study zone. L2: east- and west-facing side wall segments; arched wooden door with compass emblem; short stair posts with stone sphere finials (x2). L3: brass globe; wall shelf; headboard shelf with books and plants; large plant in blue-white vase; blue/gold compass-pattern bed blanket; west-facing direction variants for furniture against the right wall. L4: sun light shafts through the arch; large arch/column floor shadow; door and wide front stair shadows

## Acceptance
- [x] One complete request per gap using canonical GRAPHICS.md request records (native size, reference path, palette, 4 filenames where orientation matters, shadow, layer, quality criteria) with a linked blocked_on_art task; no art generated
- [x] Test: py -3 -m unittest discover -s tools/tests -p test_art_delivery.py
- [ ] PR and observed test evidence.

## Agent prompt
Outcome: One complete request per gap using canonical GRAPHICS.md request records (native size, reference path, palette, 4 filenames where orientation matters, shadow, layer, quality criteria) with a linked blocked_on_art task; no art generated. Evidence: Missing blocks by name/metadata audit, every uncertain item treated as missing (owner rejects a request if an existing asset fits). L0: drifting transparent cloud sprites (2-3); cliff-base foam loop frames (3-4); palm plants for the cliff edge. L1: broken/irregular front floor edge tiles; second blue rug for the study zone. L2: east- and west-facing side wall segments; arched wooden door with compass emblem; short stair posts with stone sphere finials (x2). L3: brass globe; wall shelf; headboard shelf with books and plants; large plant in blue-white vase; blue/gold compass-pattern bed blanket; west-facing direction variants for furniture against the right wall. L4: sun light shafts through the arch; large arch/column floor shadow; door and wide front stair shadows. Target: tools/art_requests.py (line unspecified). Verify with: py -3 -m unittest discover -s tools/tests -p test_art_delivery.py. Read AGENTS.md and this task, then only the target file. Verify the issue and location before changing code. Work only within Map Factory. Never generate artwork. Stop when evidence is missing. Commit the task, token receipt and summary on a PR branch, never main.

## Budget
- Aim below 30000 tokens; context estimate, not enforced cap.
- Read only targeted files, then expand if necessary.

## Evidence / handoff
- Changed files: none.
- Tests: not run.
- PR: none.
- Next: claim task after checking blockers.

## Claim / implementation choice
- Codex is executing the owner-requested next task; the original Claude route was a suggestion.
- The art_requests.py helper requires clean main and four upright PNG views even for clouds, foam and flat decals. Use the canonical ART_REQUEST.md / GRAPHICS.md text-record workflow on the task branch; no helper bypass and no production graphics.
- Added task-record touches for the required linked blocked_on_art handoffs. QUEUE.md remains main-only.

## Request-record implementation evidence
- Created ART-0002 through ART-0021 and linked blocked_on_art specialist tasks TASK-0013 through TASK-0032.
- Coverage: all 12 audited gaps plus 8 explicit m8 refinements/directional needs. Existing ART-0001 is reused for the full bed and its stale reference-location statement is corrected from Git metadata.
- Canonical manifest: .agents/graphics/requests/GOAL-0001_request_coverage.json. Native dimensions are proposals; all new requests remain blocked_reference pending source SHA-256/provenance and scale confirmation.
- Wrote only Markdown/JSON request/task records. No images were opened, generated, replaced or approved; no catalog/map revisions changed; no generated boards were written on this branch.
- Tests: py -3 tools/run_tests.py --changed --kind python: 2/2 applicable suites passed; task-specific test_art_delivery.py passed. All three --sources-only checks passed. Read-only coverage validation passed 12/12 audited gaps, 20 unique request/task pairs, 50 unique proposed output paths and Markdown/JSON-only allowed changes.
- Next: review this request-record PR; owner confirms reference provenance/scale and existing-asset reuse before specialist production.
