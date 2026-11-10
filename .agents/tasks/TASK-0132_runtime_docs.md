---
id: TASK-0132
status: review
owner: claude
agent: claude
priority: low
branch: claude/docs-code-org
depends_on: TASK-0131
issue: none
art_request: none
touches: docs/RUNTIME_INTEGRATION.md,docs/INDEX.md,docs/HERO_ROOM_COMPOSITION_REVIEW.md,docs/HERO_ROOM_RECOVERY_AUDIT.md,docs/MAP_FACTORY_REFERENCE_DIAGNOSIS.md,map_factory/FOUR_DIRECTION_BLOCKS.md
test: python tools/run_tests.py --changed
done_when: One current-status page lists how movement, depth sorting, characters, shadows, graphics checks and generated files work now, and the three audit documents that said otherwise point to it.
estimate_minutes: 30
---
# Runtime integration documentation

Older audit reports still said navigation was not connected and that characters used fixed z layers. Instead of rewriting history, each got a dated update line pointing to docs/RUNTIME_INTEGRATION.md (new, indexed in docs/INDEX.md). Code organization findings (checked, deliberately not refactored): JSON loading is spread over 18 call sites but each reads a different file once; the shared catalog (TASK-0130) already removed the one repeated parse; the hard-coded gameplay path in main.gd is the intended legacy data source. No code changed.
