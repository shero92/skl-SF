# Remaining missing PNGs: ZERO

**All 218 catalog IDs now have their own physical PNG files** inside map_factory/parts/.

Asset presence is complete, but **artistic production is not complete**: all 218 images remain tagged `needs_cleanup`. A large number of images are first-pass art or extracts from labeled source sheets, and need human approval against the provided sanctuary reference image.

Next production milestones:
1. Visually compare every object to the original high-quality reference and reject clipped/halo-rimmed crops.
2. Check seamless ocean and floors in an actual Godot map at native scale.
3. Review inventory artwork and sprite anchoring/collision/lighting.
4. Improve the 12 character sprite animations and two dialogue portraits with more detailed native art.
5. Promote images to `ready` only after real review; never based solely on dimensions.
6. Re-run the Godot headless validator and asset QA report after each change.

See [ASSET_GALLERY.md](ASSET_GALLERY.md) and [ASSET_AUDIT.md](ASSET_AUDIT.md).
