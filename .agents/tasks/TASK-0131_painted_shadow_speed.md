---
id: TASK-0131
status: review
owner: claude
agent: claude
priority: medium
branch: claude/render-perf
depends_on: none
issue: none
art_request: none
touches: map_factory/scripts/shadow_painter.gd,tools/measure_room_build.gd,tools/verify_shadow_speed.gd,tools/tests/test_shadow_speed.py,tools/tests/fixtures/shadow_painter_reference.gd,tools/test_map.json
test: python tools/run_tests.py --changed
done_when: Room build time is measured, the dominant cost is reduced without changing a single shadow pixel, and a test proves byte-identical output against the kept reference.
estimate_minutes: 90
---
# Painted shadows dominated the room build: measure, then speed up

## Measurement first (headless Godot 4.7.2, hero_room_01 v0021, this machine, warm runs)
tools/measure_room_build.gd: 955 nodes, 505 sprites, 293 unique textures (~27.7 MB decoded), 12 collision bodies; catalog parse 18 ms and snapshot parse 14 ms. A temporary phase timer showed: background+ground ~7 ms, walls ~3 ms, decor ~4 ms, strip shadows ~4 ms, **painted shadows + light ~600 ms of ~650 ms (about 90%)**. The first run adds ~150 ms of texture loading.

## Fix
ShadowPainter.paint kept its algorithm; the per-pixel GDScript API calls were removed: alpha read from the image byte buffer through a 256-entry float32 lookup, thresholds as byte constants (25 / 76, exact), Dictionary lookups hoisted out of the pixel loop, the 3x3 blur's interior sums the nine neighbours inline in the original order, and the result is written to one PackedByteArray with the same truncating 8-bit conversion Image.set_pixel uses (checked on 50,000 random alphas).

## Result
Room build ~650 ms -> ~425 ms (about -35%); paint() over the 46 shadow textures 597 ms -> 376 ms. Headless wall-clock on one machine: not an FPS or GPU claim. All 46 shadow images are byte-identical to the kept reference (tools/tests/fixtures/shadow_painter_reference.gd), so the look is unchanged.

## Not done
No TileMapLayer experiment (floors are ~150 of 505 sprites, build phase ~7 ms, not a bottleneck); no atlas; no memory change; the remaining ~370 ms is the per-pixel shadow projection itself (a cache keyed by texture hash or a shader would be the next step, both changing behaviour or adding files).

## Evidence / handoff
- Tests: verify_shadow_speed.gd via test_shadow_speed.py (id shadow_speed).
- Next: cache painted shadows across builds (keyed by texture sha + light config) if load time still matters.
