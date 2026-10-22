# ZIP-based asset import

Drop the existing `skl_sf_individual_assets.zip` file here using GitHub: **Add file → Upload files**, then commit it to the main branch.

The `.github/workflows/import_asset_pack.yml` workflow will unpack verified standalone PNGs and update the catalog. New IDs are placed under `map_factory/parts/`; replacements to existing sprites are placed in `map_factory/candidates/` for visual QA rather than automatically overwriting verified art.

Your existing 152-image ZIP contains concept-sheet crops, **not** a final artist-approved collection. Files should retain the status `needs_cleanup` until reviewed.

This staging method avoids transferring 152 binary PNGs individually through the GitHub connector.
