---
id: TASK-0134
status: review
owner: claude
agent: claude
priority: high
branch: claude/target-art-spec
depends_on: none
issue: none
art_request: none
touches: docs/HERO_ROOM_TARGET_20261110_ASSET_SPEC.md,map_factory/references/hero_room_01_target_20261110.webp,map_factory/references/hero_room_01_target_20261110.reference.json,.agents/graphics/CODEX_PROMPT_HERO_ROOM_TARGET.md,.agents/graphics/requests/ART-0037_hero_room_sea_light_lattice.md,.agents/graphics/requests/ART-0038_hero_room_window_wall_piece.md,.agents/graphics/requests/ART-0039_hero_room_wooden_stool.md
test: python tools/agent_workflow.py --sources-only --base origin/main
done_when: One spec tells Codex exactly which images are still needed to match the owner's target picture, with per-asset size, view and rules, the unblocked and new ART requests, and a ready prompt.
estimate_minutes: 60
---
# Hero Room target: exact art needs for Codex

Owner request 2026-11-10 (picture attached in chat). Findings: the picture is the same design as the 2026-11-03 target (mean abs diff 6.5/255), so it is committed as a second reference copy with its SHA-256; most props already exist as HD masters; real new art is limited to wrong or missing views.

## Result (Claude, 2026-11-10)
docs/HERO_ROOM_TARGET_20261110_ASSET_SPEC.md (gap matrix, batches B1-B4, per-asset spec, integration plan, checklist); new requests ART-0037 (sea light lattice overlay), ART-0038 (wall run with window opening), ART-0039 (wooden stool); ready-to-paste prompt in .agents/graphics/CODEX_PROMPT_HERO_ROOM_TARGET.md. No art generated, no map or catalog changed, no existing request edited.

## Not done
Old blocked_reference requests were not flipped to requested (owner/Claude decision after reading each). Sizes in the spec are approximate boxes read from the picture; Codex must measure the committed file.
Next: Codex produces batch B1; Claude integrates as hero_room_01 v0022.
