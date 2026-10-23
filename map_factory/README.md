# Map Factory — versioned AI-assisted map composition (no characters)

All reusable environmental components are indexed. For layout compilation, AI-generated room imagery is converted to **layered per-block metadata** and **immutable map versions**, building on the last published map revision.

Start here: **[mandatory map factory rules](MAP_FACTORY_RULES.md)** and [the workflow](MAP_FACTORY_WORKFLOW.md).

A separate Godot map-only preview renders the latest room from `map_factory/maps/index.json`. Characters, NPCs, dialogue portraits and interface elements are explicitly excluded from this subsystem.

See [asset index](metadata/asset_index.json), [map registry](maps/index.json), and [intake manifest examples](intake/examples/).

## Ready to use for future room images

Start with the [deployed factory instructions](DEPLOYED_FACTORY.md). Five independent map presets and a hashed image-to-draft intake CLI are available. A second map (`courtyard_demo_01`) has been assembled via the versioned pipeline to verify generality. The [mandatory rules](MAP_FACTORY_RULES.md) still apply. Auto-segmentation and actor flying physics are not yet implemented.
