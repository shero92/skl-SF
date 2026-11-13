# Map graphics rules

Owner decision 2026-11-13. These rules bind **every agent (Codex, Claude Code, Aider) whenever the owner asks to generate a map, a map picture or the graphics of a map.** They sit on top of [GRAPHICS_PRODUCTION_POLICY.md](GRAPHICS_PRODUCTION_POLICY.md), [REFERENCE_ART_DIRECTION.md](REFERENCE_ART_DIRECTION.md), [.agents/workflows/GRAPHICS.md](../.agents/workflows/GRAPHICS.md), [map_factory/MAP_FACTORY_RULES.md](../map_factory/MAP_FACTORY_RULES.md) and the story in [story/INDEX.md](story/INDEX.md); they do not replace them. When two rules disagree, the stricter one wins and the conflict is reported to the owner.

## The one-line rule

**A map is built from independent high-quality blocks in the same design as the hero room, it comes from the story, and it is connected to the maps and the story around it.** A map, its story scene and its graphics are one chain: nothing is generated that is not linked on both sides.

```
story scene -> map brief -> target board -> block list -> blocks -> assembled map -> QA against the board -> connected to neighbours
```

## Hard rules

1. **Blocks, not pictures.** The shipped graphic of a map is made of independent pieces (floor tiles, walls, cliffs, water, plants, props, light and animation frames), each its own transparent PNG, placed by the Map Factory. One painting of the whole map is allowed only as the **target board** (stage 2): it is a reference, never the map. Interim exception: see [Interim painted maps](#interim-painted-maps).
2. **Same design as the hero room.** Same camera, light, palette family and detail density as the owner's hero room target (`map_factory/references/hero_room_01_target_20261103.png`). New maps may look different in subject (jungle, cliff, shore) and never in quality or style.
3. **High quality is measurable** ([quality bar](#quality-bar)). Blurred, muddy, upscaled, repeated-flat or generic output is rejected and logged as a failed attempt; it is never integrated "for now".
4. **Story first.** No map is generated without a map brief that names its story file and scene. Only approved story text is fact; open decisions are the owner's ([.agents/workflows/STORY.md](../.agents/workflows/STORY.md)).
5. **Connected.** Every map names its neighbours, the exits and the return square, uses the shared block kit and the same scale and light as its neighbours, and appears in [maps/INDEX.md](maps/INDEX.md).
6. **One block, one request, one file.** No sheets, collages or multi-piece images as final assets; no crops of a generated board as final assets; each block is requested from the board crop it comes from ([reference crop rule](../.agents/workflows/GRAPHICS.md)).
7. **Nothing is approved by an agent.** Numbers and technical checks never count as visual approval. Status stops at `delivered` / `review`; the owner approves the assembled map in the real Godot window.
8. **Owner references win.** A picture the owner supplied is never replaced by an agent's idea of a nicer design.

## The stages

### 1. Map brief (before any image)
Copy [.agents/templates/MAP_BRIEF.md](../.agents/templates/MAP_BRIEF.md) to `docs/maps/briefs/<map_id>.md` and fill every line. It fixes: map id and name, story source (file, scene id, marker approved/proposed), purpose (walk, battle or both), size in 64 px squares, exits with their neighbour maps and return squares, mood and time of day, light direction, what the story allows and forbids on this map, secrets that must not show, creatures and NPCs that stay **separate** from the environment, and the moving touches (sea, lanterns, fog, petals). An empty or invented line blocks the next stage.

### 2. Target board (one picture, reference only)
- Exactly one composition picture for the map, same canvas rules as the hero room target (1536x1024 per screen), three-quarter top-down, light upper left, shadows lower right.
- It is generated from the brief and quotes it. No text, labels, UI, characters or NPCs in it.
- Saved as `map_factory/references/<map_id>_target_<yyyymmdd>.png` with its SHA-256 and the generation record (tool, prompt, attempts kept including rejected ones).
- **Owner gate:** the board is shown to the owner before any block is cut or requested. Without the owner's yes, stop.

### 3. Block list
From the approved board list every piece the map needs: id-style name, category, footprint in squares, height class (floor, low, wall-high, tall), facings needed, variants needed, animated or not. Run the duplicate scan against `map_factory/metadata/asset_index.json` and the open ART requests first: reuse before requesting. Cut a reference crop for every piece with `python tools/art_reference_crop.py` and keep it in the request.

**Minimum kit for a walkable outdoor or indoor map**
- ground: at least 3 seamless variants per ground type, plus edge, inner-corner, outer-corner and transition tiles to every neighbouring ground type;
- vertical masses (cliffs, walls, ruins): separate faces and tops, tall pieces split so the hero can walk behind them;
- water: seamless water tile plus separate foam, wave and shore pieces;
- vegetation, rocks, roots, flowers, vines: each its own piece, never baked into terrain or walls;
- props and furniture: one file per piece and per facing needed;
- light: separate light pools or glow pieces; shadows separate from objects.

### 4. Block production
- One independent RGBA PNG per block, true transparency, no background, no baked neighbours, characters, text or shadows.
- Master at least 4x the native size, kept untouched; the native file is a clean reduction on the same pixel grid, checked at the real on-screen size.
- Anchor at the foot of the piece, footprint measured, direction named.
- Tiles are seamless on every side they claim; variants differ visibly, not by a colour shift.
- Animation frames are separate files, same anchor, same palette.
- Every request and delivery follows [templates/ART_REQUEST.md](../.agents/templates/ART_REQUEST.md); a delivery lists size, hash, anchor, footprint and facing per file.

### 5. Assembly
Build the map in the Map Factory (`tools/map_factory_cli.py`, `tools/room_design.py` or the in-game editor F2): grid blocks for walking squares, free-transform blocks for decoration, depth for tall pieces, shadows by height, navigation from the real footprints, and a gameplay file only for what the story approves. The hero walks square by square ([map_factory/PHOTO_ROOMS.md](../map_factory/PHOTO_ROOMS.md) lists the behaviours every map shares). Map versions are immutable.

### 6. QA against the board
Capture the real game window ([tools/capture_game_window.gd](../tools/capture_game_window.gd)), put it beside the target board, run `python tools/room_region_report.py` with a regions file for the map, and list every region that is still different. Walk the hero to every edge square and look (stand-in and edge cases are the usual defects). Report what is not done. Status `delivered` or `review`, never approved.

### 7. Connection
- Both maps of an exit list each other; the return square is walkable and on a step square.
- Neighbours share the block kit, scale, camera and light direction; a ground type has one look everywhere.
- The story file for the scene and the map brief link to each other; [maps/INDEX.md](maps/INDEX.md) gets the map with its story file, brief, version, state and open problems.
- Events the story says happen later (visions, battles, earthquake) are not baked into the early map.

## Quality bar

A block or map is rejected when any line below is true:

- it is blurrier, flatter or less detailed than the hero room at native scale, or looks upscaled, smeared or "AI mush";
- it uses a different camera, light direction or palette family without the owner asking;
- stone, wood, foliage or water lacks the surface detail of the hero room (visible blocks and cracks, grain, leaf layers, foam);
- it repeats one flat tile or one symmetric decoration across a large area;
- it contains text, a UI, a label, a character, an NPC, or a neighbour's slivers;
- its edges show halos, boxes or clipped outlines;
- it contradicts the story canon (see below) or invents a place the story does not name;
- tall pieces cannot be walked behind, or shadows do not fall to the lower right by height.

## Story links

Read [story/INDEX.md](story/INDEX.md) and [design/STORY_CANON_AR.md](design/STORY_CANON_AR.md), then only the scene file. Current canon that maps must keep: Hidden Island is hidden and wild; the hero is the only known human at the start; no human settlement, guards, markets, harbours, maintained lighthouses or gardens outside the hero's shelter; ruins are old and overgrown; creatures are not all hostile; environment pictures never contain baked heroes or NPCs; secrets in [story/shared/visions_creatures_and_secrets.md](story/shared/visions_creatures_and_secrets.md) never show on an early map. If the brief needs something the story leaves open, ask the owner instead of filling it.

## Interim painted maps

These exist as whole paintings and are accepted by the owner as stand-ins until their blocks exist: the hero room photo backdrop (`map_factory/photo_rooms/hero_room_01.json`) and the Hidden Island boards (`map_factory/painted_worlds/hidden_island/`). They are not the standard for new maps and are not deleted. Replacing them with block-built maps follows stages 1 to 7, with the existing painting as the target board.

## Requests and reports

- Every generation request quotes the brief id, the camera and light sentence of [GRAPHICS.md](../.agents/workflows/GRAPHICS.md), the palette family, and the explicit "do not draw" list.
- Keep failed attempts with their reason; one generation call per attempt is recorded.
- A delivery report says: what was generated (count, files, hashes), what was assembled, the capture, the regions still different, what is not done, and which story lines it relies on.
- Generation tools are used only as the owner has allowed for the task; record the real tool and model.
