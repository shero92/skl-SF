---
id: TASK-0155
status: review
owner: claude
agent: claude
priority: medium
branch: claude/skirmish-animations
depends_on: TASK-0147
issue: none
art_request: none
touches: .agents/tasks/TASK-0155_skirmish_attack_animations.md,scenes/battle/tactical_battle_scene.gd,tools/verify_tactical_battle.gd
test: python tools/run_tests.py --changed
done_when: An attack in the playable skirmish plays the existing battle animation sequence (BattleDirector) before the result is applied; input is locked while it plays; the headless test still finishes a full battle.
estimate_minutes: 90
---
# Skirmish: play attack animations

Planned 2026-11-11 after hero_room_01 v0026 (owner asked for the next tasks for Claude and for Codex).

- Use the existing BattleDirector and timelines; no new art.
- Units without battle art fall back to the current instant result.

## Evidence / handoff
- The scene queues every resolved attack (and its counter) on BattleDirector; PoseActor stand-ins receive the controller poses and are drawn as a wind-up lean, a lunge and a hurt flash. Damage text appears on the hit frame.
- The rules still resolve at once (the director design): what waits for the hit frame is the display (hp bar, defeated unit leaving, damage text). Clicks, Space and enemy turns are locked while a playback runs.
- `tools/verify_tactical_battle.gd` checks: playback starts, drawn hp waits for the hit, input is locked, playback ends, drawn hp equals real hp, attacker returns to idle.
- Opened in a real window for about six seconds without script errors; nobody has played a full battle by hand.
- Units are still plain shapes; real battle sprites need art (ART-0041 covers the field only).
