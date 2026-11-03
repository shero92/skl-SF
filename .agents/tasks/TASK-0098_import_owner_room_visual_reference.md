---
id: TASK-0098
status: done
owner: claude
agent: claude
priority: high
branch: task/0098-target-reference
depends_on: none
issue: none
art_request: none
touches: map_factory/references/hero_room_01_target_20261103.png,map_factory/references/hero_room_01_target_20261103.reference.json,docs/HERO_ROOM_20261103_VISUAL_TARGET.md
test: python tools/run_tests.py --changed
done_when: The exact owner-supplied 1536x1024 image with SHA256 47a7855cf242302108e1a6b9eaf4bfd3422f9f8c812585fa4da5bcaea948668b is committed as a separate reference with identity metadata and prior references unchanged; otherwise a documented blocked reason requests the image.
estimate_minutes: 30
---
# Import new Hero Room target image — Claude only

## Goal
Make the new screenshot supplied by the owner on 2026-11-03 a reproducible, immutable design reference. Read `docs/HERO_ROOM_20261103_VISUAL_TARGET.md`.

## Work
- The owner image was uploaded in chat as `3adba40a-8d9a-49fe-961b-7a900457d5e0(5).png`; it is **not** automatically present on the owner's Windows checkout or in GitHub. Obtain the *actual* local PNG from the owner/downloaded attachment, do not substitute historical `hero_room_01_original.png` or synthesize a new file.
- Place a copy at `map_factory/references/hero_room_01_target_20261103.png`; verify size 1536x1024 and exact SHA256 `47a7855cf242302108e1a6b9eaf4bfd3422f9f8c812585fa4da5bcaea948668b`.
- Write a small `.reference.json` recording source identity, SHA256, size, and approval **as reference only**, never as the generated room approval. Preserve old references. Keep the target PNG in Git so Aider can refer to it without the owner's machine.
- Run source validation and index/checks; if unavailable, mark this task blocked with the precise missing-file reason. Do not pretend import succeeded.
- **Do not edit environment PNGs, map snapshots, scenes or Aider Worktrees.** Follow the project branch/PR workflow.

## Acceptance
- [ ] Target PNG and reference record committed to a PR/main with correct hash and no older references overwritten.
- [ ] Asset is reference-only, not a flattened scene or sprite to use as the room background.
- [ ] No changes to live Aider Worker, budget or running TASK-0090.
