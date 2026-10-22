# skl-SF asset pack — first extraction pass

This pack has **152 separate transparent PNGs** with exact catalog file names, alongside a full **218-record metadata index**. The remaining **66 catalog entries** are placeholders in the index and do not yet have PNG files.

The sprites cropped from AI concept sheets are marked `needs_cleanup` because some can have colored halos, cropped pieces or labels and floor art is not yet seamless. They are NOT production approved. UI + shadow PNGs are `ready` for first-pass review.

To use in Godot: copy `map_factory/parts` into the repository and **merge** `map_factory/metadata/asset_index.json` (it updates statuses, sizes, filenames and sources). Do not overwrite your repo scripts with anything in this pack. Manually QA each asset before changing status to `ready`.

Next steps: artist cleanup, correct collision/origin for each item, seam-checked 48x48 TileSet, sprite animations for character group.
