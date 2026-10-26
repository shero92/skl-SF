---
id: TASK-0002
status: blocked
owner: unassigned
branch: none
agent: graphics
touches: map_factory/parts/furniture/,map_factory/metadata/
test: python tools/map_factory_cli.py validate
done_when: Approved four upright bed views integrated with verified metadata
started_at: unknown
cost_usd: unknown
depends_on: TASK-0001
issue: none
art_request: ART-0001
---
# Prepare and integrate genuine four-direction bed views

**Goal:** after source image is committed, graphics specialist prepares new north/east/south/west `P001` bed perspective variants under `ART-0001`. Coding agent then integrates reviewed outputs as registered stable IDs and tests orientation in map-only Godot preview.

**Do not generate graphics in Codex or Claude Code.** Existing `P001` is a genuine catalog asset, not a missing sprite; keep it intact.

## Acceptance
- [ ] Specialist delivery `ART-0001` reviewed with four unique real perspective images.
- [ ] Distinct registered directional IDs, origins and shadow/collision metadata; existing original preserved.
- [ ] Rotation tests plus actual Godot preview comparison.
- [ ] PR/evidence recorded, then reviewer marks task done.

## Evidence / handoff
- Changed files: none.
- Tests: not run for this task.
- PR: none.
- Blocked by TASK-0001 + ART-0001.
- Next: authentic source image; then specialist request.

## Approved recovery priority
- Original 1448x1086 room composition and owner-accepted nine HD sprites are the targets. The committed goal reference is a candidate until owner identity confirmation; do not assert it is absent or byte-identical.
- Visible authored views first; deferred additional views remain separate acceptance. Review P024/P025 before commissioning replacement bed/blanket art.
- Source identity, measured native scale and signed reviewer evidence remain blocked. No asset or map approval implied.
