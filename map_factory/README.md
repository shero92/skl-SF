# Map Factory

Reusable Godot 4 room composition pipeline.

## Directories
- `parts/`: image asset categories (each has .gitkeep until PNGs are produced)
- `metadata/asset_index.json`: planned asset records; missing PNGs have `status: "planned"`
- `metadata/asset_schema.json`: structure and permitted fields
- `rooms/hero_room.json`: sample room layout that works with provisional floor colors
- `scripts/asset_catalog.gd`: loads JSON and indexes assets
- `scripts/asset_factory.gd`: builds visual instances from IDs (placeholder for missing textures)
- `scripts/shadow_factory.gd`: creates temporary elliptical shadows
- `scripts/room_factory.gd`: arranges room floor and objects

## Usage
Open root project in Godot 4. Run F6 on `scenes/main.tscn`, or F5 for default scene. The starter scene demonstrates grid/floor and optional object factories. This is an architecture scaffold, **not** a finished asset pack.

PNG naming: `F001_Stone_Floor_Plain.png`. Never add a decorative text label into production sprite PNGs. Export transparent sprites, trim safely, and record pixel origin and collision footprint.

Assets are registered before they are used. Missing assets are drawn as magenta placeholders with IDs, intentionally.
