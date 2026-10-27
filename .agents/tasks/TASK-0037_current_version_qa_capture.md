---
id: TASK-0037
status: done
owner: codex
branch: codex/current-map-qa-final
agent: codex
touches: tools/goal_qa.py,tools/capture_map_previews.gd,tools/tests/test_art_delivery.py
test: py -3 -m unittest discover -s tools/tests -p test_art_delivery.py
done_when: Capture registry-selected immutable revisions without v0010 assumptions; intermediate capture permits unfinished goals, final comparison retains owner gates; stale captures fail
started_at: 2026-10-26T19:25:53.983512+01:00
cost_usd: unknown
depends_on: TASK-0036
issue: none
art_request: none
---
# Current-version QA capture

**Source:** goal:GOAL-0001:recovery-capture
**Created:** 2026-10-26
**Goal:** GOAL-0001
**Type:** feature
**Priority:** high
**Suggested agent:** codex (routing heuristic, not a performance claim)
**File:** tools/goal_qa.py
**Line:** unspecified
**Problem:** Owner-approved recovery audit: Current-version QA capture

## Acceptance
- [ ] Capture registry-selected immutable revisions without v0010 assumptions; intermediate capture permits unfinished goals, final comparison retains owner gates; stale captures fail
- [ ] Test: py -3 -m unittest discover -s tools/tests -p test_art_delivery.py
- [ ] PR and observed test evidence.

## Agent prompt
Outcome: Capture registry-selected immutable revisions without v0010 assumptions; intermediate capture permits unfinished goals, final comparison retains owner gates; stale captures fail. Evidence: Owner-approved recovery audit: Current-version QA capture. Target: tools/goal_qa.py (line unspecified). Verify with: py -3 -m unittest discover -s tools/tests -p test_art_delivery.py. Read AGENTS.md and this task, then only the target file. Verify the issue and location before changing code. Work only within Map Factory. Never generate artwork. Stop when evidence is missing. Commit the task, token receipt and summary on a PR branch, never main.

## Budget
- Aim below 12000 tokens; context estimate, not enforced cap.
- Read only targeted files, then expand if necessary.

## Evidence / handoff
- Changed files: none.
- Tests: not run.
- PR: none.
- Next: claim task after checking blockers.

- Integration note: existing art_delivery suite contains the new QA tests; test registry/index stay main-owned and unchanged in this worktree.

## Resumed existing implementation
- Existing capture code recovered unchanged from current-map-qa worktree; original worktree and its pending evidence preserved.
- New branch integrates authenticated-reference selection and current capture receipts. No production image opened.

## Validation evidence (2026-10-27)
- 24 art_delivery/QA unit tests passed, including registry version selection, intermediate/final gating, authenticated source, stale nonce/hash/version/camera rejection.
- task_evidence and LF writer routed suites passed.
- Godot 4.7.2 text-only capture parser fixture passed editor import and --check-only.
- Changed-path Python run: see receipt below; candidate_room requires omitted production assets in the image-free worktree. No test or production asset altered to hide this limitation.
- No owner visual approval or room completion claimed. Next: PR review and genuine isolated current-version capture.

- Final changed-path run: 26/27 Python suites passed; candidate_room fails only on unavailable delivery manifests/assets in this intentionally sparse worktree. Targeted rerun after committed-tree guard: 3/3 passed.

## Genuine isolated Godot capture
- Command: py -3 tools/goal_qa.py capture GOAL-0001 (exit 0).
- Rendered hero_room_01 v0011 at 1536x1024 from commit c4f93d76a04a728e22cb28b1212edd3d7b135463.
- Snapshot SHA-256: e5dc4ebc34fcbce693957c22fe65d072b640cf35ea7b53046dde83e2a35cd3b2.
- PNG SHA-256: c8558d87da0ce61b978b2801f4d8885a6742a58b61a883a8bd6335e4a0a2ebb5.
- Camera center [768,512], zoom [1,1], run 43e6d5492f754057bc4981e3119edb69.
- PNG and receipt preserved locally under .agents/monitoring/.local/qa-evidence/GOAL-0001 (not committed). Intermediate evidence only; owner_final_signoff=false.
- PR: https://github.com/shero92/skl-SF/pull/46

## Approved merge and main verification
- Owner explicitly approved sequential merge: https://github.com/shero92/skl-SF/pull/46
- Merge commit: b81796be88bf6fe1fd57b4eb7a06ea6fcc50d768.
- Combined main 97b85f6: py -3 tools/run_tests.py --all passed 30/30 (27 Python, 3 Godot). Both registered maps validated; original reference SHA-256 matches the approved manifest. Historical map files unchanged; final_verified=false.
- Completed technical scope only. Next: specialist calibration using authenticated source and genuine current capture; no visual approval fabricated.
