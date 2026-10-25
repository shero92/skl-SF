# Map asset metadata

**Authoritative lookup:** [asset_index.json](asset_index.json) keyed by stable `id`. Current inspected catalog: 229 PNG records, all `needs_cleanup`; do not confuse presence with artistic approval.

| File | Meaning |
| --- | --- |
| `asset_index.json` | ID, category, path, pixel size, pivot/origin, collision, shadow, provenance and status |
| `asset_schema.json` | registry schema |
| `asset_audit.json` | programmatic art/metadata audit output |
| `quality_review.json` | art review information |
| `room_block_quality.json` | placed map-block QA |
| `extraction_manifest.json` | imported source-sheet lineage |
| `production_queue.csv` | production and cleanup backlog |
| `navigation_example.json` | illustrative navigation contract |

**Token tip:** search ID/string in the large JSON; do not paste the full catalog into context. For art, consult [parts index](../parts/INDEX.md). [Files](FILES.md).
