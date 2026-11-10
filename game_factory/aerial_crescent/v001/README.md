# Aerial Crescent Strike — WIP review frames

Status: **needs_review** (NOT playable / NOT active)

- Planned: 32 individually illustrated weaponless Hero body frames, to be reviewed for timing.
- Camera: HERO_REAR_3Q, Hero in right foreground facing the upper-left enemy.
- Original art reference: locked Hero sources in docs/GRAPHICS_PRODUCTION_POLICY.md and user-approved Hero design.
- Weapon and all VFX belong to separate game layers; source body must not include them.
- Frame 001: stance candidate, 1254x1254 RGBA PNG, generated as a single isolated pose.
- **Known issue**: Source has a large semi-transparent alpha fringe; requires proper alpha-edge cleanup and owner visual approval before any game-size derivative or weapon-hand anchor annotation. Source saved unchanged.
- Frame 002 onward: pending upload/review; no fabricated placeholders.
- Weapon anchors / grounded alignment / Godot review: not measured, not passed.
- Never copy into assets/characters/hero/battle/ or change the active character manifest until reviewed.

Next: finish 002–032 as separate source PNGs, ensure realistic anatomy, keep relative weapon grip/right-hand fist and back-three-quarter stance continuity, then align/export and test in Godot.
