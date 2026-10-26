# Hero Room — genuine 9-sprite high-definition art pack

**2026-10-26 — created by ChatGPT graphics generation, accepted visually by the owner.** Original detailed PNG images are the default **art quality reference** for *future* environmental art. Full in-game proportions and four-way directions remain pending specialist/reviewer QA. The earlier 22 low-detail PNG drafts stay rejected.

## Stable factory asset IDs and placement

| ID | Category | Sprite | Render pass | In-game status |
|---|---|---|---|---|
| W021 | walls | Vine Covered Compass Ruin Wall | Level2 walls | owner style-approved; map QA pending |
| W022 | walls | Isometric Ivy Fantasy Wall | Level2 walls | owner style-approved; map QA pending |
| A017 | architecture | Ivy Covered Compass Shrine Pillar | Level2 walls | owner style-approved; map QA pending |
| A018 | architecture | Sapphire Compass Doorway | Level2 walls | owner style-approved; map QA pending |
| D019 | decor | Royal Blue Compass Banner | Level3 decorations | owner style-approved; map QA pending |
| P023 | furniture | Cobalt Compass Treasure Chest | Level3 decorations | provisional 2×1 stone floor cells |
| P024 | furniture | Compass Rose Fantasy Bed Frame | Level3 decorations | provisional 3×3 stone floor cells |
| P025 | furniture | Royal Blue Compass Bedspread | Level3 mounted decoration | attaches only to approved bed asset IDs |
| P026 | furniture | Nautical Compass Study Desk | Level3 decorations | provisional 4×2 stone floor cells |

**Important:** Every delivered sprite is one authored perspective. Never rotate/mirror a 3/4 sprite and claim independent north/east/south/west views. The footprints above are conservative initial metadata; they must be inspected at game scale with real contact points before setting `measurement_status=reviewed` or enabling strict production placement. The desk illustration includes a matching stool; it is one composited object, not two separated reusable props. The wall images are fully assembled wall sections; they still need genuinely separate tiles for perfect wall-to-wall seams.

## Binary delivery: the required one-time import

The nine original generated, cropped, resized-with-detail and alpha-cleaned **actual PNG files** are in the ChatGPT chat attachment `hero_room_hd_factory_pack_2026-10-26.zip` (6.4 MB). The GitHub connector supports writing code and data, but it **cannot stream binary bytes from a local chat file into GitHub directly**. Code here cannot truthfully substitute generated PNGs.

In the owner's Windows clone, in PowerShell:

```powershell
git switch main
git pull --ff-only
git switch -c art/hero-room-hd-actual-pngs
py -3 tools/install_hd_factory_pack.py "$HOME\Downloads\hero_room_hd_factory_pack_2026-10-26.zip"
py -3 tools/install_hd_factory_pack.py "$HOME\Downloads\hero_room_hd_factory_pack_2026-10-26.zip" --install --integrate
py -3 tools/map_factory_cli.py validate
py -3 tools/run_tests.py --changed
git add map_factory/parts/walls/W021_* map_factory/parts/walls/W022_* map_factory/parts/architecture/A017_* map_factory/parts/architecture/A018_* map_factory/parts/decor/D019_* map_factory/parts/furniture/P02*.png map_factory/metadata/asset_index.json map_factory/maps/hero_room_01
git commit -m "art: integrate nine HD Hero Room sprites into factory and new map version"
git push -u origin art/hero-room-hd-actual-pngs
```

Note: the `git add ...` wildcards may be interpreted differently by shell; safer use `git add map_factory/parts map_factory/metadata/asset_index.json map_factory/maps/hero_room_01` after inspecting `git status` to avoid unrelated files.

After uploading the branch, open a GitHub PR to `main`. Do not mark images `ready` or the room `visual_qa.approved` before capturing a real Godot screenshot, checking the full scene against the reference and reviewing each tile anchor. The script constructs a **new immutable version** of `hero_room_01`; it never rewrites older versions and preserves all old sprite IDs.

## Art quality for the entire game

For **all new high-quality environmental art**, treat this owner's accepted nine-image batch alongside the earlier original four high-resolution reference crops as the minimum detail and palette benchmark. Preserve bright golden limestone, layered ivy and white flowers, polished blue and gold inlaid compass details, clear volumetric forms, consistent upper-left lighting and correct 3/4 perspective. Pixel dimensions alone are not quality. Never auto-upscale or procedural-repaint the rejected low-detail sprites.

Only the ChatGPT graphics specialist or the owner's appointed dedicated graphics AI creates images; Codex and Claude Code may inspect metadata and import reviewed untouched bytes, not generate or edit graphics. See `docs/ASSET_QUALITY_POLICY.md`.
