---
id: TASK-0137
status: review
owner: claude
agent: claude
priority: medium
branch: claude/shadow-cache
depends_on: TASK-0131
issue: none
art_request: none
touches: map_factory/scripts/shadow_painter.gd,tools/verify_shadow_cache.gd,tools/tests/test_shadow_cache.py,tools/test_map.json,docs/RUNTIME_INTEGRATION.md
test: python tools/run_tests.py --changed
done_when: Painted shadows are cached by (source pixels, light, algorithm version) in memory and under user://, results stay byte-identical to a fresh paint, and a cached room build is measurably faster.
estimate_minutes: 60
---
# Cache painted shadows

After TASK-0131 the remaining ~370 ms of a hero_room_01 build was the per-pixel shadow projection, which is a pure function of its inputs. `ShadowPainter.paint_cached` keys on a SHA-256 of the source bytes + merged light + size + CACHE_VERSION; entries are PNG + JSON in `user://shadow_cache/` (JSON written last, corrupt or missing entries repaint), plus an in-memory map for rebuilds in one run. `build_layer` uses it; `paint()` is unchanged.

## Measured (headless, this machine, hero_room_01 v0022)
cold build ~725 ms (includes hashing and writing 46 entries), disk-cached ~268 ms, memory-cached ~236 ms. Hit/miss counters are exposed. Not an FPS claim.

## Not done
No cache pruning (entries are tiny; stale ones only accumulate when textures or light change), no shipping of a pre-baked cache, no cache for the light-pool layer (it is cheap).

## Evidence / handoff
- Tests: verify_shadow_cache.gd via test_shadow_cache.py (id shadow_cache). The corrupt-entry case prints an expected engine image-load error.
- Next: prune old cache entries if the folder grows.
