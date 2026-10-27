---
id: TASK-0039
status: done
owner: codex
branch: codex/immutable-resolved-metadata
agent: codex
touches: tools/map_factory_cli.py,tools/map_factory_layers.py,tools/tests/test_map_factory.py,tools/tests/test_map_layers.py
test: py -3 tools/run_tests.py --only map_factory --only map_layers --only map_registry_validate
done_when: Catalog measurement corrections do not rewrite or invalidate historical resolved graphs; new revisions use corrected measurements; corruption remains rejected
started_at: 2026-10-27T11:14:10.315214+01:00
cost_usd: unknown
depends_on: TASK-0036
issue: none
art_request: none
---
# Preserve immutable resolved map metadata

**Source:** goal:GOAL-0001:recovery-immutable
**Created:** 2026-10-26
**Goal:** GOAL-0001
**Type:** feature
**Priority:** high
**Suggested agent:** codex (routing heuristic, not a performance claim)
**File:** tools/map_factory_cli.py
**Line:** unspecified
**Problem:** Owner-approved recovery audit: Preserve immutable resolved map metadata
**Dependency:** TASK-0036 reconciled with merged evidence.

## Acceptance
- [x] Catalog measurement corrections do not rewrite or invalidate historical resolved graphs; new revisions use corrected measurements; corruption remains rejected
- [x] Test: py -3 tools/run_tests.py --only map_factory --only map_layers --only map_registry_validate
- [ ] PR and observed test evidence.

## Agent prompt
Outcome: Catalog measurement corrections do not rewrite or invalidate historical resolved graphs; new revisions use corrected measurements; corruption remains rejected. Evidence: Owner-approved recovery audit: Preserve immutable resolved map metadata. Target: tools/map_factory_cli.py (line unspecified). Verify with: py -3 tools/run_tests.py --only map_factory --only map_layers --only map_registry_validate. Read AGENTS.md and this task, then only the target file. Verify the issue and location before changing code. Work only within Map Factory. Never generate artwork. Stop when evidence is missing. Commit the task, token receipt and summary on a PR branch, never main.

## Budget
- Aim below 12000 tokens; context estimate, not enforced cap.
- Read only targeted files, then expand if necessary.

## Evidence / handoff
- Changed files: `tools/map_factory_cli.py`, `tools/tests/test_map_factory.py`, this task record.
- Tests: `py -3 tools/run_tests.py --only map_factory --only map_layers --only map_registry_validate` passed 3/3. Full Python validation passed 26/27 groups; candidate_room cannot find excluded production delivery files in this image-free worktree (existing containment limitation, no assets restored).
- PR: none.
- Next: complete independent review, receipt and PR; no commit/push performed by the implementation subagent.

- Dependency TASK-0036 now has confirmed merged evidence. Implemented on the isolated branch; awaiting PR review.

### TASK-0039 implementation evidence
- New revisions capture only referenced `resolved_assets` (including animation frames, directional variants and shadow assets), and patches link `parent_snapshot_sha256`. New revisions compile against current catalog measurements.
- Legacy validation recovers measured origins/sizes/contracts and default physical settings from the archived block manifest, then compares source-derived layer and block manifests for every version. Existing archives are never regenerated or edited.
- `sync-blocks` only fills missing indices, refuses mismatched published artifacts, and checks all existing outputs before writing. A legacy revision lacking its measurement manifest is an explicit blocker; frozen revisions can backfill it.
- Added synthetic coverage for changed pivots/pixel sizes/collision/shadows, archive byte stability, next-revision measurements, corrupted positions/IDs/anchors/layers, missing artifacts, source changes, identity changes, animation dependencies and parent-chain tampering.
- Limitation: legacy files have no cryptographic hash chain; coordinated edits to all mutually consistent legacy records cannot be authenticated retroactively. New parent links protect their published ancestors without inventing old evidence.
- Final verification: `--all --kind python` and `--changed --kind python` each passed 26/27 groups; both only fail `candidate_room` because excluded production delivery artifacts are absent. `git diff --check` passed. The focused acceptance command passed 3/3 after the final code change. No art was restored, opened or changed.

## Approved merge and main verification
- Owner explicitly approved sequential merge: https://github.com/shero92/skl-SF/pull/47
- Merge commit: 97b85f62400e353df4b9c87b07522516bd866b76.
- Combined main 97b85f6: py -3 tools/run_tests.py --all passed 30/30 (27 Python, 3 Godot). Both registered maps validated; original reference SHA-256 matches the approved manifest. Historical map files unchanged; final_verified=false.
- Completed technical scope only. Next: specialist calibration using authenticated source and genuine current capture; no visual approval fabricated.
