# Story folder — what it is

`docs/story/` holds the written story of the game (working title **The Ancient Seal**, a Shining Force style tactical RPG). The text is in **Arabic**; names of places, characters and creatures are kept in English. Start at [INDEX.md](INDEX.md), which says which file answers which question. Do not read every chapter.

## Status in one table

| File | Covers | Canon state (from the file's own header) |
| --- | --- | --- |
| [INDEX.md](INDEX.md) | Reading path, task-to-file table, order of chapter 1, authority limits, dragon update | Official entry point for any agent |
| [chapter_01/01_home_and_storm.md](chapter_01/01_home_and_storm.md) | Hero's Home, the father, Neru, the childhood friend (Reef Friend), the storm, Stormwatch Path | Structure approved; dialogue wording is a draft |
| [chapter_01/02_sword_visions.md](chapter_01/02_sword_visions.md) | Bone-Tide Shore, the sword, twelve visions | Sword reaction and vision kinds approved; cut timing is draft |
| [chapter_01/03_first_battle.md](chapter_01/03_first_battle.md) | Battle 01 "The Ruins Stir": five skeletons, escape, return to the father | Five enemies and surviving with the friend approved; role and shadow dialogue draft |
| [chapter_01/04_temple_and_second_battle.md](chapter_01/04_temple_and_second_battle.md) | Forgotten Stones, Temple of the First Seal, Battle 02, the archer joining mid-battle, the father's sentence, the inner shrine | Event, archer joining and father's sentence approved; dialogue, route order and timing proposed |
| [chapter_01/05_giant_door_shrine_earthquake.md](chapter_01/05_giant_door_shrine_earthquake.md) | Battle 02 in front of the giant stone door, wave carvings, sword glow, shrine touch, island earthquake | Door, carvings, glow, touch and earthquake approved; cinematic text draft |
| [chapter_01/06_third_battle_islands_fury.md](chapter_01/06_third_battle_islands_fury.md) | Battle 03 "The Island's Fury": rampaging creatures, survive, then calm a dragon instead of killing it | Multi-objective battle and calming approved; enemy counts, stats, turns, calming skill and tile layout proposed |
| [chapter_01/07_jungle_rescue.md](chapter_01/07_jungle_rescue.md) | After Battle 03: the team runs into the jungle to rescue other creatures | Running to the jungle approved; the route and details are draft, not a fourth battle |
| [chapter_02/README.md](chapter_02/README.md) | Hidden Island's veil weakening, the island becoming visible | **Open**: nothing in it is approved |
| [shared/three_battles_monsters.md](shared/three_battles_monsters.md) | Monster kinds, roles and goals for the three battles | Battle 01 confirmed; Battles 02 and 03 counts and abilities proposed |
| [shared/visions_creatures_and_secrets.md](shared/visions_creatures_and_secrets.md) | Creatures seen in the sword vision, proposed visual puzzles, secrets that must not be revealed early | Roles unresolved; puzzles proposed one by one |

## Markers

Files mark what is decided: **[معتمد]** approved by the owner, **[مقترح]** proposed, **[تطويري]** development draft, **[مفتوح]** open. Only approved text may be built as fact. Approved by the owner and already in the INDEX: after calming, the dragon **joins the team, stays and fights with it** (any older text saying it leaves is superseded).

## Known open decisions

- When Silent Gate Forest is visited (before or after the shrine scene) and where chapter 1 ends are **not decided**. Do not change either on your own.
- Final names, the final look and the size mechanic of the team dragon are not decided.
- Chapter 2 is open: only the weakening veil around Hidden Island is a confirmed storyline.
- Secrets that must not be revealed early: the sword's link to Lemon, the warrior in the vision, the origin of the blue marks, who inherits the power, the source of the veil's power, the meaning of the eye and chains, why the father knows the deer, the archer's group, the truth of the shrine, the origin of the dark side. The link of the skeletons to the world of Zeon is behind-the-scenes only.

## Reference files

- [../design/STORY_CANON_AR.md](../design/STORY_CANON_AR.md) is the compiled shared canon (world, father, friend, coastal home, mystery rules, source order, the latest Reef Friend correction and the owner's 2026-11-13 direction that the island is hidden and wild with no human settlement). It exists in this repository.
- INDEX.md points the JSON contract question to [../RUNTIME_INTEGRATION.md](../RUNTIME_INTEGRATION.md) and the Map Factory. The older `content_contracts.md` and `story_bible.md` of the first repository (`The-Ancient-Seal`) are not here.

## How agents use this folder

See [.agents/workflows/STORY.md](../../.agents/workflows/STORY.md).

Nothing here proves that a story event is implemented in Godot: dialogue, battles and maps built from it are separate tasks with their own tests.
