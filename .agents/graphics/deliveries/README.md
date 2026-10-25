# Graphics specialist delivery staging

Every ART request gets a dedicated `ART-####/` folder. The graphics agent places actual PNG files exactly at the paths specified by the request and a `manifest.json` with:
```json
{
  "request_id": "ART-0001",
  "files": [
    {"path": ".agents/graphics/deliveries/ART-0001/hero_bed_north.png", "sha256": "<actual 64-char hex sha256>"}
  ]
}
```
The example is illustrative only; list EVERY delivered PNG with real hashes. Never declare `delivered` without complete images and verified manifest. Do not commit placeholder graphics. Never overwrite approved `map_factory/parts` images directly.
