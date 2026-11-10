---
id: TASK-0130
status: review
owner: claude
agent: claude
priority: medium
branch: claude/character-cache
depends_on: TASK-0127
issue: none
art_request: none
touches: map_factory/scripts/asset_catalog.gd,scenes/player.gd,scenes/room_npc.gd,scenes/room_companion.gd,tools/verify_character_runtime.gd,tools/tests/test_character_runtime.py,tools/test_map.json
test: python tools/run_tests.py --changed
done_when: Gameplay scripts share one parsed asset catalog; the hero can optionally draw from the Game Factory manifest (complete frames only) with a legacy fallback; default look unchanged; verified headlessly.
estimate_minutes: 60
---
# Character runtime: shared catalog and opt-in Game Factory hero art

**Problem (verified):** HeroPlayer._play created a new AssetCatalog and re-parsed the whole asset_index.json on every animation state change; RoomNpc and RoomCompanion did the same at start. Separately, the Game Factory hero (4 idle + 6 walk frames per direction, approved) was only visible in the demo scenes.

**Fix:** `AssetCatalog.shared()` (parsed once, `load_count` makes it measurable, `reload()` after an index change). HeroPlayer gets `@export var use_factory_art` (default false): it builds a SpriteFrames from the manifest via GameFactoryActor.make_frames (complete animations only) and falls back to the legacy sprite for any missing animation. Nothing was removed; the shipped look is unchanged.

## Facts recorded (manifest, 2026-11-10)
Only Hero has complete map animations (8 of 8). Cely, Neru, Reef Friend, The Old Father and Temple Archer are reference_only with no animations; in the room they use the poster sprites (PosterCharacter), which are not animation frames and stay as they are. Battle animations: Hero has attack_windup and attack_execute only.

## Not done
No visual capture of the factory hero in the room (art sizes differ: 96x96 vs the legacy 144x192 scaled), so the default stays off; no change to Battle or equipment integration; no performance numbers in FPS or memory.

## Evidence / handoff
- Tests: verify_character_runtime.gd via test_character_runtime.py (id character_runtime); the parse count stays unchanged over 40 animation changes.
- Next: owner decision to switch the hero to the factory art after a side-by-side capture.
