# Hero weaponless battle revision

The owner selected the original `idle_ready_01__attempt_01` and
`step_01__attempt_01` sources as approved DESIGN/COLOR references. Their hashes
are locked in `hero_battle_palette.json`. This does not approve new revisions.

Current selection: 12 independent transparent 256x256 body PNGs: four wind-up,
six execute/recovery, one idle base and one step base. The nine explicitly
requested attack frames are included. All original attempts and prior native
versions remain locally preserved. New selected versions remain `needs_review`.

`queue.json` records the selected files; `requests/` preserves exact built-in
image_gen calls. Sources are in each asset's `sources/` directory, with canonical
copies under `H:/shining force/pixel-art/TASK-0070/v002/`. No external image API.

`hero_weapon_anchors.json` contains 12 individually measured hand locations,
clockwise rotations from an upward blade, scale, render order and grip type.
Coordinates are native body-image pixels; frame indices start at zero.
Native derivatives preserve uniform scale, use nearest sampling and anchor both
feet at `[128,240]`. One source needed an alpha-noise cutoff of 8/255 in its
DERIVATIVE only; its visible silhouette was fully inside the source canvas.

Weapon PNGs and pivots are independent in `assets/weapons/swords/` and
`game_factory/weapons/catalog.json`. Hero's calibrated attachment multiplier is
2/3, applied to each weapon's catalog scale. Changing equipment never edits the
body PNGs. `HandOcclusion` redraws the original hand region over a front weapon;
raised swings may place the weapon behind the body.

Run `scenes/modular_battle_demo.tscn`. SPACE swaps the two swords at runtime.
The existing `scenes/game_factory_battle.tscn` also uses the modular renderer;
B swaps equipment during battle. Its attacks still emit the original impact
event and restore map context after presentation.

Verification mode: `Godot --path PROJECT scenes/modular_battle_demo.tscn -- verify capture quit`.
The receipt checks every attack frame with both swords, actual animation signals,
grip-pivot coincidence and unchanged body PNG hashes. Captures/GIFs are genuine
Godot output, not generated battle mockups. Color diagnostics compare material
ramps and saturation; they do not replace owner review of identity and motion.

Other characters have not been regenerated. The six-character manifest declares
separate sword/spear/bow/staff/natural profiles; Reef Friend's equipment category
awaits original-reference review. Each category requires its own measured
anchors and compatible animation profile. `python -m tools.weapon_factory
register-anchors --character SLUG --annotations FILE` registers existing
weaponless frames only. Neru can use body-only natural attacks.

The full game factory goal is still in progress. Remaining Hero battle states,
supporting assets and other characters are not marked completed.
