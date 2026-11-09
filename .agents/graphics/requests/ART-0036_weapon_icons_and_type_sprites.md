---
id: ART-0036
status: blocked_reference
owner: graphics-specialist
task: TASK-0118
dedupe_key: weapon_icons_and_type_sprites
existing_asset_ids: none
output_paths: .agents/graphics/deliveries/ART-0036/weapon_icon_sword.png,.agents/graphics/deliveries/ART-0036/weapon_icon_spear.png,.agents/graphics/deliveries/ART-0036/weapon_icon_axe.png,.agents/graphics/deliveries/ART-0036/weapon_icon_mace.png,.agents/graphics/deliveries/ART-0036/weapon_icon_dagger.png,.agents/graphics/deliveries/ART-0036/weapon_icon_bow.png,.agents/graphics/deliveries/ART-0036/weapon_icon_staff.png
---
# Weapon type icons and per-type weapon sprites

**Why:** (existing weapon sprites WPN_HERO_BASIC_SWORD and WPN_IRON_SWORD live in the weapon catalog, not the asset registry.) `game_factory/weapons/weapon_stats.json` defines 7 weapon types (`icon` ids `weapon_icon_*`) and 19 weapons, but the catalog only has two sword sprites (`catalog.json`). Inventory/equip UI needs one icon per type; battle needs sprites for the other types.

**Source image and SHA-256:** none yet; keep `blocked_reference` until the owner supplies or approves a style reference.

**Outputs:** one independent RGBA PNG per path above: 48x48 native icon, transparent, centered, 1px dark outline, same palette and style as the approved hero sword, no text, no shadow. Later (separate request after approval): battle sprites 128x192 with a measured `grip_pivot` for spear, axe, mace, dagger, bow and staff, following `game_factory/weapons/profiles.json` (these profiles require their own anchors).

## Request checklist
- [x] Duplicate scan against catalog and active requests.
- [ ] Original reference path and hash attached.
- [ ] Specifications reviewed; mark `requested`.
