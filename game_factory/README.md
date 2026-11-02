# Game Factory

قواعد الإنتاج الملزمة: [السياسة الرسومية الموحدة](../docs/GRAPHICS_PRODUCTION_POLICY.md). كل إطار شخصية يولد مستقلاً بمصدر كامل الجودة؛ الأوراق تُجمع من الملفات الفردية بعد التحقق فقط. لا مصادر collage ولا تغيير active manifest قبل الموافقة.

Authoritative scope amendment: exactly SIX characters: Hero, Cely, Neru,
Reef Friend, The Old Father, Temple Archer. The original supplied master request
is preserved as provenance; its seventh-character requirement is superseded.
No seventh character or substitute is authorized.

Production targets: 240 map frames, 228 battle frames, 30 expression portraits,
6 UI icons, 6 key artworks, 36 separate turnarounds and 19 detail/weapon images:
565 independent PNG outputs. These are queue targets, never completion claims.
The existing environment library contains 128 independent assets/facings.

Hero's modular battle correction is documented in `hero_correction/README.md`:
12 selected weaponless body PNGs, two independent swords and an actual Godot
swap demo. New body versions remain needs_review; original design-reference
approval does not automatically approve revised production art. Weapon profiles
are separate per category; existing weapon-embedded body candidates are archived
and excluded from active animation registration.

`python tools/game_factory.py init` reconciles the queue without resetting jobs.
`next --character hero` reserves ONE item and returns built-in image_gen arguments.
Call the built-in tool once, then `ingest --id ID --source PATH` saves the raw source,
nearest-neighbor uniform native derivative, provenance and actual-file registry.
No API client, paid external service or key is used.
`fail --id ID --reason TEXT` explicitly recovers an interrupted reservation.
Never fail a pending request while its tool call is still running.
`previews --character hero` assembles GIF derivatives from saved independent PNGs.

All new output remains needs_review. Technical checks cannot approve identity,
native pixel quality, facing or temporal motion. Partial animation sequences
are intentionally not played as complete animations. Original gameplay and
immutable map history remain untouched.

Godot entrypoint: scenes/game_factory_demo.tscn, user argument mode=room,
mode=interactive, mode=viewer or mode=battle. F1 debug, 0-4 logical passes.
Viewer: TAB character, arrows facing, I idle, W walk, P pause.
Battle: A attack, D defend, M magic, H hurt, V victory. SPACE from interactive.
Missing required frames keep the corresponding demo incomplete.

Room reconstruction is a review candidate assembled with the existing
RoomFactory, independent PNGs and a separate catalog; it is not visually approved.
