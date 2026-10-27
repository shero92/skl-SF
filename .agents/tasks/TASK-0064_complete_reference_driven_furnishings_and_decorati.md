---
id: TASK-0064
status: blocked
owner: unassigned
branch: none
agent: claude
touches: tools/blender/builders.py,tools/blender/lib.py,tools/blender/specs/,tools/tests/test_blender_factory.py,map_factory/candidates/
test: py -3 -m unittest discover -s tools/tests -p test_blender_factory.py
done_when: Use candidate comparison and calibration to repair or author only confirmed gaps under existing ART requests (0008,0011,0015,0020,0021,0023). Reuse bed/cover/desk/chest at calibrated contacts; remove unrequested duplicates only in candidate visibility, never delete originals. Script reproducible limestone/wood/cobalt-gold/flowers details, contacts and host anchors; rebuild candidate and produce a full-room review sheet with texture inventory. Exclude characters/treant-like actor from environment unless owner explicitly classifies it as scenery; do not silently substitute O028. Keep new outputs unapproved; no automatic import, visual approval or misleading error-score success claim.
started_at: unknown
cost_usd: unknown
depends_on: TASK-0062,TASK-0063
issue: none
art_request: none
---
# Complete reference-driven furnishings and decoration in the assembled candidate

**Source:** goal:GOAL-0001:recovery-visible-furnishings
**Created:** 2026-10-27
**Goal:** GOAL-0001
**Type:** feature
**Priority:** normal
**Suggested agent:** claude (routing heuristic, not a performance claim)
**File:** tools/blender/builders.py
**Line:** unspecified
**Problem:** Calibrated gaps persist in headboard shelf, study bookshelf, blue rugs, planter/foliage, wall fixtures and centerpiece. Accepted HD assets already cover several furniture requirements; wholesale regeneration would duplicate work.
**Blocked by:** dependencies (the pulse promotes this task to todo once they are done)

## Acceptance
- [ ] Use candidate comparison and calibration to repair or author only confirmed gaps under existing ART requests (0008,0011,0015,0020,0021,0023). Reuse bed/cover/desk/chest at calibrated contacts; remove unrequested duplicates only in candidate visibility, never delete originals. Script reproducible limestone/wood/cobalt-gold/flowers details, contacts and host anchors; rebuild candidate and produce a full-room review sheet with texture inventory. Exclude characters/treant-like actor from environment unless owner explicitly classifies it as scenery; do not silently substitute O028. Keep new outputs unapproved; no automatic import, visual approval or misleading error-score success claim.
- [ ] Test: py -3 -m unittest discover -s tools/tests -p test_blender_factory.py
- [ ] PR and observed test evidence.

## Agent prompt
Outcome: Use candidate comparison and calibration to repair or author only confirmed gaps under existing ART requests (0008,0011,0015,0020,0021,0023). Reuse bed/cover/desk/chest at calibrated contacts; remove unrequested duplicates only in candidate visibility, never delete originals. Script reproducible limestone/wood/cobalt-gold/flowers details, contacts and host anchors; rebuild candidate and produce a full-room review sheet with texture inventory. Exclude characters/treant-like actor from environment unless owner explicitly classifies it as scenery; do not silently substitute O028. Keep new outputs unapproved; no automatic import, visual approval or misleading error-score success claim.. Evidence: Calibrated gaps persist in headboard shelf, study bookshelf, blue rugs, planter/foliage, wall fixtures and centerpiece. Accepted HD assets already cover several furniture requirements; wholesale regeneration would duplicate work.. Target: tools/blender/builders.py (line unspecified). Verify with: py -3 -m unittest discover -s tools/tests -p test_blender_factory.py. Read AGENTS.md and this task, then only the target file. Verify the issue and location before changing code. Work only within Map Factory. Never generate artwork. Stop when evidence is missing. Commit the task, token receipt and summary on a PR branch, never main.

## Budget
- Aim below 30000 tokens; context estimate, not enforced cap.
- Read only targeted files, then expand if necessary.

## Evidence / handoff
- Changed files: none.
- Tests: not run.
- PR: none.
- Next: claim task after checking blockers.
