---
id: TASK-0001
status: blocked
owner: unassigned
branch: none
agent: graphics
touches: map_factory/references/,map_factory/maps/
test: python tools/map_factory_cli.py validate
done_when: Authentic source reference committed and map comparison reviewed
started_at: unknown
cost_usd: unknown
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

## Approved recovery priority
- Original 1448x1086 room composition and owner-accepted nine HD sprites are the targets. The committed goal reference is a candidate until owner identity confirmation; do not assert it is absent or byte-identical.
- Visible authored views first; deferred additional views remain separate acceptance. Review P024/P025 before commissioning replacement bed/blanket art.
- Source identity, measured native scale and signed reviewer evidence remain blocked. No asset or map approval implied.
