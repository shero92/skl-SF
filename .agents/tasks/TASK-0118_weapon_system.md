---
id: TASK-0118
status: done
owner: claude
agent: claude
priority: medium
branch: claude/weapon-system
depends_on: none
issue: none
art_request: ART-0036
touches: game_factory/weapons/weapon_stats.json,game_factory/weapons/README.md,scenes/battle/weapon_system.gd,tools/verify_weapon_system.gd,tools/tests/test_weapon_system.py,tools/test_map.json,.agents/graphics/requests/ART-0036_weapon_icons_and_type_sprites.md
test: python tools/run_tests.py --changed
done_when: Data-driven weapon types, classes, characters and 19 weapons exist; equip/unequip, stats, range, hit/crit/damage API is verified headlessly and routed in test_map.json; art needs are documented as a request.
estimate_minutes: 90
---
# Shining Force style weapon system

Owner request 2026-11-10: a weapon system for all character types.

## Design
- Data: `game_factory/weapons/weapon_stats.json` (types with kind and [min,max] range, 9 classes, CHAR001-CHAR006 mapped to classes, 19 weapons with attack/accuracy/crit/price/effects). Reuses `profiles.json` profiles and `catalog.json` asset ids; `asset_id` is null where no art exists.
- Code: `scenes/battle/weapon_system.gd` (plain-Dictionary units, usable by battle and inventory): can_equip, equip/unequip with 4-slot inventory, effective_stats (attack = base + weapon), attack_range (melee 1, spear 1-2, bow 2-3 no adjacent, staff magic 1-2), hit_chance, crit_chance, damage, hit_statuses, art_profile.
- Not done: wiring into a live battle scene (none exists yet), shop UI, magic spells, art (see ART-0036).

## Evidence / handoff
- Tests: `tools/verify_weapon_system.gd` + `tools/tests/test_weapon_system.py` (id weapon_system).
- PR: see branch claude/weapon-system.
- Next: owner reviews numbers; then wire WeaponSystem into the battle controller.

## Closure (Claude, 2026-11-10)
Merged in PR #127; weapon_system test passes on main. Next step: wire WeaponSystem into the battle controller.
