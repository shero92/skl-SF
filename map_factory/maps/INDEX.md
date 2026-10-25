# Published maps

- `index.json` is the authoritative map registry with each current version and `latest` path.
- `hero_room_01/latest.json`: current Hero Room snapshot **v0010** as verified on 2026-10-25. `hero_room_01/blocks/latest.json` is derived resolved block metadata; `layers/latest.json` holds five-pass composition.
- `courtyard_demo_01/latest.json`: separate environment map, **v0002** at last check.
- `<map_id>/versions/vNNNN.json`: immutable historical snapshots; `changes/`: original version change manifests; `blocks/` and `layers/`: derived indices. Never edit historical versions or generated indices by hand.
- Art-fidelity research: `hero_room_01/reference_gaps.json` may describe an older evaluated version—verify against current `latest.json`.
- Source picture is not yet committed and v0010 has null source path/hash; approval must stay `needs_review`.

Start with [map registry](index.json), not all historic version files. [Direct entries](FILES.md).
