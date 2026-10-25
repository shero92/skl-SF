---
id: TASK-0001
status: blocked
owner: unassigned
branch: none
depends_on: none
issue: none
art_request: none
---
# Preserve original Hero Room reference and establish reproducible QA

**Goal:** save the original user-provided room image in `map_factory/references/` (do not invent it), register its SHA-256 in a **new version** of Hero Room after v0010 and produce equal-scale source-versus-Godot comparison.

**Current blocker:** original image was supplied in a chat but is not committed as a source file in the repo. A coding agent must not generate an artificial substitute.

## Acceptance
- [ ] Reference authentic, committed and hash checked.
- [ ] Next valid map version references the source path/hash; historical snapshots untouched.
- [ ] Actual Godot screenshot at known scale, before/after evidence and reviewer notes.
- [ ] Tests and PR evidence linked.

## Evidence / handoff
- Changed files: none.
- Tests: not run for this task.
- PR: none.
- Next: obtain/commit genuine reference and unblock.
