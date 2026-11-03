---
id: TASK-0100
status: done
owner: aider
agent: aider
priority: high
branch: aider/task-0100
depends_on: TASK-0099
issue: none
art_request: none
touches: tools/build_hero_room_blueprint.py,tools/room_assembly.py,tools/tests/test_hero_room_reference_relayout.py,tools/test_map.json
test: python -m unittest discover -s tools/tests -p test_hero_room_reference_relayout.py
done_when: The room blueprint generator produces a separately versioned post-v0013 layout that respects the audited target zone placements for rear arch, connected enclosing walls, left bed and rug, right desk and rug, center compass, front stairs and coastal parapet with no missing asset references or invalid overlaps.
estimate_minutes: 120
---
# Rebuild Hero Room composition close to owner's image, from independent assets

Reference: `docs/HERO_ROOM_20261103_VISUAL_TARGET.md` and machine contract from TASK-0099. Respect TASK-0090–0097 implementations; do not duplicate them or overwrite any existing version.

## Implementation
- Extend `build_hero_room_blueprint.py` and shared `room_assembly.py` so the **next available map version after v0013** is produced from v2-approved registered Blocks using explicit placements. Aider edits **generator code and tests only**; the operator applies/publishes the compiled map files and actual Godot screenshot in a separate PR.
- Correct visual hierarchy against target: central ocean-facing flowered arch and back columns; enclosed side/back ruins; left blue-gold bed on rug; right desk/books/maps/fruit on rug; center large blue/gold compass; centered south stairs with posts; low front masonry and cliff below. Preserve the ocean view through arch and positive floor coverage.
- Enforce four facings via correct directional PNGs and anchors, perspective-safe scale, distinct ground/walls/furniture/shadow layers; never fake wall depth by stretching or mirroring a perspective-aware image.
- Keep room **environment-only**. Hero and Neru appear in the owner image, but belong to optional Game Factory character scene, not the built environment.
- Report any art that cannot be made visually faithful using the approved 128-PNG library. Do not generate art or rasterize a whole screenshot into floor/walls. Do not mark visual approval.

## Acceptance
- Unit tests actually discover tests and check key feature placements, allowed overlap, walkable space and exact asset references.
- `python tools/run_tests.py --changed` passes, no PNG changes, old v0012/v0013 snapshots retained.
- Provide deterministic command for operator to generate the new version after merge.

## Reply rules
Do not write the path or file name of any file that is not in `touches` anywhere in your reply or in the files you edit (not in prose, not in the `paths` list of the tools/test_map.json entry, not in comments): Aider treats such a mention as a request to add the file, discards your edits and asks again. In the test_map.json entry list in `paths` only files from `touches`; read other data files at runtime inside the test by constructing the path from parts. Use plain ASCII characters only in every reply, comment, string and file you write.
