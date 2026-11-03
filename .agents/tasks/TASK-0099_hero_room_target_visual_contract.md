---
id: TASK-0099
status: todo
owner: aider
agent: aider
priority: normal
branch: none
depends_on: TASK-0097,TASK-0098
issue: none
art_request: none
touches: tools/hero_room_visual_contract.py,map_factory/blueprints/hero_room_01_visual_targets_20261103.json,tools/tests/test_hero_room_visual_contract.py,tools/test_map.json
test: python -m unittest discover -s tools/tests -p test_hero_room_visual_contract.py
done_when: A validated machine-readable target contract and report describes all 11 visual zones in the owner reference, verifies required asset IDs and source paths against v2, and reports missing approved art without modifying PNGs.
estimate_minutes: 90
---
# Convert owner photo into an auditable placement contract

Reference: `docs/HERO_ROOM_20261103_VISUAL_TARGET.md`. Use imported `map_factory/references/hero_room_01_target_20261103.png` read-only; do not substitute other images.

## Implementation
- Create `hero_room_01_visual_targets_20261103.json` for the eleven review regions: sea and cliffs, rear ivy arch, connected left/right walls, floor, bed/rug, right desk/rug, compass, coastal front parapet, central stairs, light and shadows. Store approximate 1536x1024 **image-space** boxes and notes; convert to world-space targets via verified render geometry, not arbitrary sprite anchor guesses.
- Implement an auditor that reads approved v2 environment assets, source texture paths, existing post-v0013 room state and target contract. Report: asset IDs used, distinct PNGs, placed instances, approximate zone coverage, absent/misplaced feature classes and potentially missing art.
- Do not report pixel-identical similarity based on file hashes or number of assets. If critical art is missing, emit explicit requests for Codex/Claude approval instead of creating images. Characters in the screenshot are **optional separately rendered actors**, not map blocks.
- Register a dedicated test in `tools/test_map.json`. Tests must discover **at least one actual test** and fail on missing required zones, nonexistent source paths and invalid contract data.

## Scope/acceptance
- No PNG, map snapshots, Battle scenes or character sources edited. Only exact `touches` files.
- Successful `test_hero_room_visual_contract.py`, `python tools/run_tests.py --changed`, and documented real missing-art gaps.
- Use short Aider context with only relevant files and read-only visual target; do not consume tokens dumping unrelated JSON history.

## Reply rules
Do not write the path or file name of any file that is not in `touches` anywhere in your reply or in the files you edit (not in prose, not in the `paths` list of the tools/test_map.json entry, not in comments): Aider treats such a mention as a request to add the file, discards your edits and asks again. In the test_map.json entry list in `paths` only files from `touches`; read other data files at runtime inside the test by constructing the path from parts. Use plain ASCII characters only in every reply, comment, string and file you write.
