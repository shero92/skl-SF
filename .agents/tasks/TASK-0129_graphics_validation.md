---
id: TASK-0129
status: review
owner: claude
agent: claude
priority: medium
branch: claude/graphics-validation
depends_on: none
issue: none
art_request: none
touches: tools/graphics_validation.py,tools/tests/test_graphics_validation.py,.github/workflows/quality_guard.yml,tools/test_map.json
test: python tools/run_tests.py --changed
done_when: Production PNGs under assets/characters, assets_generated, assets_hd/runtime and map_factory/parts are technically validated (changed-only on pull requests, everything on main) with clear messages; no QA/approval state is touched.
estimate_minutes: 60
---
# Graphics validation beyond map_factory/parts

**Problem (verified):** quality_guard.yml ran only when map_factory/parts PNGs or the asset index changed, and tools/quality_guard.py only reads asset_index.json. Edits to assets/characters, assets_generated or assets_hd/runtime, to hd_map.json and to the character manifest ran no graphics check at all.

**Fix:** tools/graphics_validation.py (read-only, never edits a PNG or an approval state): PNG integrity/format, non-empty pixels, alpha for sprites (tiles/backgrounds/UI marked in metadata may be opaque), catalog size/path/duplicate checks (asset_id plus orientation, since directional variants legitimately share an id), HD runtime = scale x native size, character animation frames (files exist, one canvas per animation, "complete" needs frames, frame lists consistent). Reference images, QA captures, rejected attempts and per-generation caches are skipped as archives. `--changed` limits the PNG scan to files that differ from the base; a metadata edit validates that metadata family fully. quality_guard.yml now also runs on pull requests and for the new paths; quality_guard.py itself is unchanged.

## Baseline
`--all` over 665 production PNGs: 0 errors on the current repository (after treating archive folders and orientation variants correctly). Warnings are advisory (manifest canvas differences).

## Not done
Source-hash verification of masters (the masters are local, not in git), visual quality, artistic approval.

## Evidence / handoff
- Tests: test_graphics_validation.py (id graphics_validation), 12 cases incl. a real repo baseline.
- Next: add source SHA checks when masters are available in CI.
