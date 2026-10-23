# Map Factory four-direction blocks

Map Creator supplies environment art and the blocks layout. Map Factory reads the blocks and renders them. Characters are outside this workflow.

Four quarter turns:
- north: 0 degrees
- east: 90 degrees
- south: 180 degrees
- west: 270 degrees
- 360 degrees: north again

## Mode A — physically rotate an environmental sprite and collider

Manifest example:

    {
      "op": "add_block",
      "layer": "objects",
      "block": {
        "id": "P001", "instance_id": "RotatedBedExample",
        "x": 650, "y": 490, "scale": 0.7,
        "facing": "east", "orientation_mode": "rotate"
      }
    }

This rotates the Godot root Node2D by 90 degrees, including its collider. WARNING: a 3/4 perspective bed will visually tip sideways, so the example is a functional test, NOT the recommended artistic use. Use rotate for flat tiles and truly rotationally suitable pieces.

## Mode B — FOUR distinctly drawn direction sprites

Manifest example (P101–P104 are hypothetical, not existing assets):

    {
      "op": "add_block", "layer": "objects",
      "block": {
        "id": "P101", "instance_id": "RealFourViewBed",
        "x": 650, "y": 490,
        "facing": "west", "orientation_mode": "variants",
        "direction_asset_ids": {
          "north": "P101", "east": "P102",
          "south": "P103", "west": "P104"
        }
      }
    }

Register all four actual PNGs in the environment catalog before using. All IDs must exist, be DISTINCT, belong to the same environment asset category and have correct pivots, visual orientation and collision information. Godot chooses the requested illustration and keeps it upright. Never invent a reversed 3D angle just by rotating a single image.

## Tile override

The set_tile manifest operation supports cardinal facing, including east facing as shown:

    {"op": "set_tile", "x": 3, "y": 5, "id": "F014", "facing": "east"}

The compiler preserves the facing in tile_overrides and the renderer rotates at tile center, not the top-left.

## Mounted details

Decorations may use mount_on and mount_offset. If a mounted wall turns east, its offset [30,10] rotates to [-10,30]. Block rotation never changes individual character art.

## Optional wall/furniture occlusion

    {"op":"set_property","key":"occlusion_mode","value":"world_y_sort"}

Creates the WorldDepthSort node with y-sorted wall and prop containers at shared z depth, so a front wall can hide a prop behind it and a back wall can sit behind a prop. This requires reviewed bottom contact pivots and must be tested per map. The default remains fixed_layers for old screenshots.

Current Hero Room v0010 has ZERO facing assignments and no four-direction variant sets for its architecture. It is not artistically 360-degree ready even though the Factory NOW implements both rendering modes. Generating 4-view art belongs to Map Creator, not the rendering factory.

See docs/MAP_FACTORY_REFERENCE_DIAGNOSIS.md for why the user screenshot still differs from the reference.
