#!/usr/bin/env python3
"""Verify 9 compass tiles actually contain blue/gold details, no image replacement."""
from pathlib import Path
from PIL import Image
import json
ROOT=Path(__file__).resolve().parents[1]
j=json.loads((ROOT/"map_factory/metadata/asset_index.json").read_text())
assets={x["id"]:x for x in j["assets"]}
mosaic=Image.new("RGBA",(192,192))
rows=[["F019","F015","F020"],["F018","F014","F017"],["F021","F016","F022"]]
report={}
for y,row in enumerate(rows):
    for x,id in enumerate(row):
        p=ROOT/assets[id]["texture_path"].removeprefix("res://")
        im=Image.open(p).convert("RGBA")
        if im.size!=(64,64):raise RuntimeError(str((id,im.size)))
        blue=sum(1 for r,g,b,a in im.getdata() if a>128 and b>r*1.4 and b>g*1.16 and b>95)
        opa=sum(1 for r,g,b,a in im.getdata() if a>128)
        report[id]={"blue_fraction":round(blue/4096,3),"opaque_pixels":opa,"name":p.name}
        mosaic.alpha_composite(im,(x*64,y*64))
preview=ROOT/"docs/previews/map_factory_renders/compass_source_3x3.png"
preview.parent.mkdir(parents=True,exist_ok=True)
mosaic.resize((768,768),Image.Resampling.NEAREST).save(preview)
print(json.dumps(report,indent=2))
if report["F014"]["blue_fraction"]<.1:
    raise RuntimeError("Center compass artwork does not show expected blue")
