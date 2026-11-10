---
id: TASK-0135
status: review
owner: claude
agent: claude
priority: medium
branch: claude/room-v0022-props
depends_on: TASK-0128
issue: none
art_request: none
touches: tools/build_v0022_patch.py,map_factory/maps/hero_room_01/,map_factory/maps/index.json,docs/previews/map_factory_renders/t0135_v0022/
test: python tools/run_tests.py --all
done_when: hero_room_01 v0022 is published with registered props from the owner target placed (no new art), a real Godot capture passes the evidence gate, visual_approval stays false.
estimate_minutes: 40
---
# Hero Room v0022: place registered props from the target

Placement-only (docs/HERO_ROOM_TARGET_20261110_ASSET_SPEC.md section 4: items marked M). Added through Map Factory on top of v0021, nothing moved: two blue urns (O001) near the arch, conch shells (R13) on the bedside table and near the front right, a small blue vase (O003), the brass armillary (R12) on the right bookshelf, and a wooden stool (P012) at the study table. Capture: docs/previews/map_factory_renders/t0135_v0022/.

## Notes
- P012 and O001/O003 are registered `needs_cleanup` parts (HD runtime twins), used as the spec allows until ART-0039 and later deliveries replace them.
- The right urn stands in the open floor below the bookcase (the v0021 arch/bookcase layout differs from the target); moving furniture to the target positions is a composition change left for owner review.
- Not owner-reviewed.
