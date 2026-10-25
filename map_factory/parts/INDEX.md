# Reusable pixel-art parts

Stable sprite paths follow `map_factory/parts/<category>/<ID>_<Name>.png`. Individual PNGs are not final unless reviewed; use `metadata/asset_index.json` to resolve authoritative metadata and status.

| Category | Prefix | Folder / full file listing |
| --- | --- | --- |
| Architecture | A | [architecture](architecture/FILES.md) |
| Characters (OUT OF SCOPE) | CH | [characters](characters/FILES.md) |
| Decorations | D | [decor](decor/FILES.md) |
| Coast, clouds and water | E | [environment](environment/FILES.md) |
| Floor tiles/compass mosaic | F | [floors](floors/FILES.md) |
| Beds, desks, shelves | P | [furniture](furniture/FILES.md) |
| Small objects/shrine | O | [objects](objects/FILES.md) |
| Contact and cast shadows | S | [shadows](shadows/FILES.md) |
| Stairs and railings | ST | [stairs](stairs/FILES.md) |
| UI (OUT OF SCOPE) | UI | [ui](ui/FILES.md) |
| Plants and ivy | V | [vegetation](vegetation/FILES.md) |
| Stone walls and corner pieces | W | [walls](walls/FILES.md) |

New environment art requires standalone clean RGBA PNG, a stable ID, metadata, pivot/collision/shadow QA and Godot screenshot comparison. Do not replace approved art with unchecked crops. [Direct folder files](FILES.md).
