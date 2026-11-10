# Runtime integration status (2026-11-10)

Short, current facts for agents; older reports in `docs/` describe earlier states. Source of truth is the code, `map_factory/maps/index.json` and the task files.

| Area | Current behaviour | Where |
| --- | --- | --- |
| Player movement | `HeroPlayer` and `GameFactoryActor` ask one validator, `NavigationGrid.allowed_motion()`, built from the snapshot `navigation` block (schema 1). Cells no region/link opens are closed; diagonals slide along edges. Only the `walk` mode is wired; `fly`/`swim` are parsed, unused. Furniture obstacles still rely on StaticBody2D collision. Maps without a block are unrestricted. | `map_factory/scripts/navigation_grid.gd`, TASK-0127 |
| Depth sorting | Maps with `occlusion_mode: world_y_sort` (hero_room_01 since v0021) put the hero, companion and NPCs into `WorldDepthSort` at the same effective z as walls and decor, so the contact Y decides who is in front. Other maps keep the legacy fixed layer (characters z 35). | `RoomFactory.entities_parent()`, TASK-0128 |
| Characters | `AssetCatalog.shared()` parses `asset_index.json` once. `HeroPlayer.use_factory_art` (default off) draws the hero from the Game Factory manifest, complete animations only. Only Hero has complete map animations; the other five are reference-only and appear as poster sprites. | `scenes/player.gd`, TASK-0130 |
| Painted shadows | About 35% faster, byte-identical to the unoptimised reference kept in `tools/tests/fixtures/`. Measure with `tools/measure_room_build.gd`. Remaining cost is the per-pixel projection. | `map_factory/scripts/shadow_painter.gd`, TASK-0131 |
| Graphics checks | `tools/graphics_validation.py --changed|--all` (read-only): PNG integrity, alpha policy, catalog/hd_map/manifest consistency, character frames. Technical only, never an approval. | `.github/workflows/quality_guard.yml`, TASK-0129 |
| Generated files | `main` regenerates task boards, folder indexes, the cost report and the test index after each merge (`tools/regenerate_main_outputs.py`, bot commit). `.github/workflows/` is excluded from inventories because the Actions token cannot write there. | `.github/workflows/regenerate_main_outputs.yml`, TASK-0125/0126 |
| Weapons and battle | `WeaponSystem`, `BattleResolver`, `TurnManager`, `EnemyAI` (data: `game_factory/weapons/weapon_stats.json`); not yet wired into a playable scene. | `scenes/battle/`, TASK-0118..0121 |

## Known gaps
- hero_room_01 navigation is `needs_review`; the hero is confined to its safe-walk region.
- Long diagonal wall pieces anchored at their far end can cover neighbours under Y-sorting (v0021 vs v0020: about 1% of pixels differ).
- Missing art goes through `.agents/graphics/requests/`; no agent generates images here.
