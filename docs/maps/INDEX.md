# Maps — story, brief, graphics and connections

One row per map. A map is not "done" until its story file, brief, target board, blocks, assembled version and neighbours are all linked here. Rules: [../MAP_GRAPHICS_RULES.md](../MAP_GRAPHICS_RULES.md). Briefs live in `briefs/<map_id>.md` ([template](../../.agents/templates/MAP_BRIEF.md)).

| Map id | Story scene | Built as | Version / state | Exits | Open problems |
| --- | --- | --- | --- | --- | --- |
| `hero_room_01` (Hero's Home room) | [01_home_and_storm.md](../story/chapter_01/01_home_and_storm.md) SC01 | Map Factory blocks (v0029) **and** the owner's target painting as an interim photo room ([PHOTO_ROOMS.md](../../map_factory/PHOTO_ROOMS.md)) | Painting is the shown picture; block version is the walk and sort source; owner approval not given | Stairs down to `hidden_island_opening` / `home_descent` | Curved walls, parapet, cliff base, double bed, sea stacks still need art (ART-0042 to ART-0049); clean painting without painted figures (ART-0050); waves, clouds and flyers (ART-0053, ART-0055, ART-0051) |
| `hidden_island_opening` (6 zones: home_descent, mossveil_edge, mossveil_roots, stormwatch_ascent, stormwatch_overlook, bone_tide_shore) | Chapter 1 parts 01 and 02 | Whole painted boards on a square grid (Codex, ART-0052), interim | `needs_map_review` | Room stairs to `home_descent`; zones connected in [PAINTED_COAST.md](../PAINTED_COAST.md) | Not block-built: needs stages 1 to 7 with these boards as targets; hero in it still uses the old small drawing and no depth or shadows |
| `seabreak_coast_01` | None: not a story place | Map Factory blocks (v0003) from existing pieces | Earlier outdoor experiment, superseded as default by `hidden_island_opening` | Via room exit definition | Story link missing; keep or retire by owner decision |
| `courtyard_demo_01` | None | Map Factory blocks (v0002) | Demo | None | Demo only |

Maps not listed here have no brief and must not be generated.
