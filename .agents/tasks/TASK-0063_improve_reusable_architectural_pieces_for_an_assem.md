---
id: TASK-0063
status: review
owner: claude
branch: work/task-0063-00ca7e6f
agent: claude
touches: tools/blender/builders.py,tools/blender/lib.py,tools/blender/specs/,tools/tests/test_blender_factory.py
test: py -3 -m unittest discover -s tools/tests -p test_blender_factory.py
done_when: Reuse existing builders/specs and ART IDs. Deliver code/spec improvements for connected wall courses and caps, corners/broken terrace cliff contacts, front stairs/rope posts and cobalt-gold compass; preserve open central arch and accepted HD originals. Stage only unapproved versioned candidate outputs through existing deterministic tools, never overwrite deliveries or parts. Run Blender scripted QA for seam anchor agreement, size/alpha/shadow direction and hashes; retain separate 8/10 depth variants where needed. No character/UI work. A production piece is not accepted by numeric image difference. Full assembled candidate is the only agent visual review artifact; no individual piece reads or permission edits. Infra/source PR only, final art needs owner room review.
started_at: 2026-10-27T16:45:13.199770+00:00
cost_usd: unknown
depends_on: none
issue: none
art_request: none
---
# Improve reusable architectural pieces for an assembled Hero Room shell

**Source:** goal:GOAL-0001:recovery-visible-shell
**Created:** 2026-10-27
**Goal:** GOAL-0001
**Type:** feature
**Priority:** high
**Suggested agent:** claude (routing heuristic, not a performance claim)
**File:** tools/blender/builders.py
**Line:** unspecified
**Problem:** Blender v4 and ART-0004/0014/0022/0024/0025 exist but are unapproved; main still publishes v0011. Owner asks for detailed warm limestone connected architecture seen in both supplied images, rather than further reporting.

## Acceptance
- [ ] Reuse existing builders/specs and ART IDs. Deliver code/spec improvements for connected wall courses and caps, corners/broken terrace cliff contacts, front stairs/rope posts and cobalt-gold compass; preserve open central arch and accepted HD originals. Stage only unapproved versioned candidate outputs through existing deterministic tools, never overwrite deliveries or parts. Run Blender scripted QA for seam anchor agreement, size/alpha/shadow direction and hashes; retain separate 8/10 depth variants where needed. No character/UI work. A production piece is not accepted by numeric image difference. Full assembled candidate is the only agent visual review artifact; no individual piece reads or permission edits. Infra/source PR only, final art needs owner room review.
- [ ] Test: py -3 -m unittest discover -s tools/tests -p test_blender_factory.py
- [ ] PR and observed test evidence.

## Agent prompt
Outcome: Reuse existing builders/specs and ART IDs. Deliver code/spec improvements for connected wall courses and caps, corners/broken terrace cliff contacts, front stairs/rope posts and cobalt-gold compass; preserve open central arch and accepted HD originals. Stage only unapproved versioned candidate outputs through existing deterministic tools, never overwrite deliveries or parts. Run Blender scripted QA for seam anchor agreement, size/alpha/shadow direction and hashes; retain separate 8/10 depth variants where needed. No character/UI work. A production piece is not accepted by numeric image difference. Full assembled candidate is the only agent visual review artifact; no individual piece reads or permission edits. Infra/source PR only, final art needs owner room review.. Evidence: Blender v4 and ART-0004/0014/0022/0024/0025 exist but are unapproved; main still publishes v0011. Owner asks for detailed warm limestone connected architecture seen in both supplied images, rather than further reporting.. Target: tools/blender/builders.py (line unspecified). Verify with: py -3 -m unittest discover -s tools/tests -p test_blender_factory.py. Read AGENTS.md and this task, then only the target file. Verify the issue and location before changing code. Work only within Map Factory. Never generate artwork. Stop when evidence is missing. Commit the task, token receipt and summary on a PR branch, never main.

## Budget
- Aim below 30000 tokens; context estimate, not enforced cap.
- Read only targeted files, then expand if necessary.

## Evidence / handoff
- Changed files: none.
- Tests: not run.
- PR: none.
- Next: claim task after checking blockers.

## Runner evidence
- Claimed by local runner at 2026-10-27T16:45:13.189837+00:00

## Runner evidence
- Validated infrastructure PR: https://github.com/shero92/skl-SF/pull/59
