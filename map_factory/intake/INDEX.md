# AI image / map change intake

1. `tools/prepare_map_reference.py` takes an actual source image, saves a SHA-256-linked original and creates an unapproved draft under [drafts/](drafts/FILES.md).
2. Match existing asset IDs, create standalone images only for missing environmental parts, review placements and metadata.
3. Reviewed manifests go to [pending/](pending/FILES.md); scripts/workflow process these into immutable map versions; receipts appear in [processed/](processed/FILES.md).
4. New PNG staging is [assets/](assets/FILES.md). [examples/](examples/FILES.md) are templates, **not manifests to apply repeatedly**.

Never publish `pending_review` as complete or claim the factory automatically extracts hidden sprite art. See [workflow](../MAP_FACTORY_WORKFLOW.md) and [all entries](FILES.md).
