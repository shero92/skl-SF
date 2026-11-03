---
id: TASK-0101
status: done
owner: aider
agent: aider
priority: normal
branch: aider/task-0101
depends_on: TASK-0100
issue: none
art_request: none
touches: tools/capture_map_previews.gd,tools/hero_room_capture_evidence.py,tools/tests/test_hero_room_capture_evidence.py,tools/test_map.json
test: python -m unittest discover -s tools/tests -p test_hero_room_capture_evidence.py
done_when: A repeatable Godot Map Factory capture path produces a 1536x1024 environment-only render and provenance JSON for the new room version, verifies registered source textures and exposes a concrete region-by-region discrepancy report without claiming visual approval.
estimate_minutes: 90
---
# Verifiable real Godot capture for image-target room

Reference: `docs/HERO_ROOM_20261103_VISUAL_TARGET.md`. Depends on the audited composition from TASK-0100.

## Implementation
- Make the capture and evidence generator use the **actual registered Map Factory snapshot** from a specified version; do not build a fake image with Pillow, compositing or generative imagery.
- Capture at reference canvas 1536×1024, record commit/version, target SHA256, map snapshot SHA256, render SHA256, list/count of distinct texture paths and placements, missing paths, and structural-zone findings.
- Document reproducible Godot CLI invocation and output naming; guard against accidental overwrites of historical `hero_room_01_v0012.png` or old immutable snapshots.
- Ensure the environment screenshot contains no baked-in Hero/Neru images. If a character-inclusive comparison is required, delegate a **separate** Godot gameplay scene capture to Claude, with approved existing assets, not a map layer.
- Include at least one discovered unit test covering invalid map version/missing PNG/provenance data and `tools/test_map.json` entry.
- Any image-space similarity score must be labelled non-authoritative: human comparison of the reference is still required.

## Acceptance
- Tests and `python tools/run_tests.py --changed` pass; no PNG or character assets changed by Aider.
- Operator can generate a real capture and structured discrepancy report without undocumented manual steps.

## Reply rules
Do not write the path or file name of any file that is not in `touches` anywhere in your reply or in the files you edit (not in prose, not in the `paths` list of the tools/test_map.json entry, not in comments): Aider treats such a mention as a request to add the file, discards your edits and asks again. In the test_map.json entry list in `paths` only files from `touches`; read other data files at runtime inside the test by constructing the path from parts. Use plain ASCII characters only in every reply, comment, string and file you write.
