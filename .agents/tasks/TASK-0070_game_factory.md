---
id: TASK-0070
status: in_progress
owner: codex
branch: codex/game-factory
depends_on: TASK-0069
issue: none
art_request: ART-0027
---
# Complete reusable Game Factory

Owner explicitly expands scope to six characters, portraits, UI icons, movement and battle presentation in master_request.txt.
Touches: game_factory/, tools/game_factory.py, tools/tests/test_game_factory.py, scenes/game_factory*, assets/characters/, assets_generated/.
Preserve existing maps, approved art and unrelated edits. Reuse RoomFactory.
Acceptance: actual independent PNG outputs, durable queue, genuine room/animation capture and reusable Godot demos; absent references remain blocked. No missing output is marked complete.
Test: python -m unittest tools.tests.test_game_factory; Godot demo smoke; python tools/run_tests.py --changed.
Evidence: in progress. Exactly six characters; Forest Fairy Archer excluded. Hero has 40 independent map frames; actual Godot movement/collision smoke passed. Environment has 128 independent assets. Latest owner correction prioritizes weaponless Hero battle revision, locked approved idle/step reference palette, per-frame grip anchors and genuine two-sword swap demonstration. Other character generation remains on hold until Hero correction is validated. Original high-resolution sources and prior native versions are preserved.
Additional touches: tools/hero_battle_correction.py, game_factory/hero_correction/, assets/weapons/, scenes/modular_battle*.

Hero correction checkpoint: 12 selected weaponless 256x256 PNGs (requested nine
attack frames plus recovery/idle/step), 12 individual grip records, locked material
palette and two independent sword PNGs delivered to the owner project and
H:/shining force/pixel-art/TASK-0070/v002/. Exact image_gen requests and raw sources
are preserved. Raw art sources remain canonical local workspace files; Git tracks
native deliverables, metadata, request logs, references and runtime evidence.
Validation: python -m unittest tools.tests.test_game_factory passed 5 tests.
Actual owner-project Godot modular demo: exit 0, 20 swap frame cases, 20 actual
frame events, unchanged body PNG hashes. Room/actor smoke: exit 0, four-direction
movement/idle/collision verified, 52 registered existing animation frames.
Color diagnostics: 12 frames checked, no current warnings. Agent compared selected
sources and genuine Godot views; owner production-art approval remains pending.
Full game library remains in progress. Next: remaining Hero weaponless battle states.
Final required check: python tools/run_tests.py --changed passed 32/32 after
using task-local TEMP/APPDATA and allowing Git fixture subprocesses outside the
managed sandbox. Initial sandbox-only failures were host TEMP/MSYS restrictions;
task newline output and test-router registration were corrected before the pass.
Existing Battle Factory integration also passed in the owner project: runtime
weapon swap during impact, map position/facing/movement restored, damage retained.
