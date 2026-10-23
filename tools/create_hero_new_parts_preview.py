#!/usr/bin/env python3
"""Visual QA only: contact sheet of new independently registered map sprites."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json
ROOT=Path(__file__).resolve().parents[1]
record=json.loads((ROOT/"map_factory/metadata/asset_index.json").read_text())
by={x["id"]:x for x in record["assets"]}
ids=["O028","E023","E024","W020","S017"]
w,h=330,350
sheet=Image.new("RGBA",(w*len(ids),h),(16,33,54,255))
d=ImageDraw.Draw(sheet)
for i,id in enumerate(ids):
    rec=by[id]
    p=ROOT/rec["texture_path"].removeprefix("res://")
    src=Image.open(p).convert("RGBA")
    x=i*w
    for y in range(25,h-40,20):
        for xx in range(15,w-15,20):
            color=(197,202,198,255) if ((xx//20+y//20)%2) else (226,232,224,255)
            d.rectangle((x+xx,y,x+xx+19,y+19),fill=color)
    factor=min(285/src.width,266/src.height)
    scaled=src.resize((int(src.width*factor),int(src.height*factor)),Image.Resampling.NEAREST)
    sheet.alpha_composite(scaled,(x+(w-scaled.width)//2,35+(260-scaled.height)//2))
    d.text((x+12,6),id+" — "+rec["name"],fill=(244,211,104),stroke_width=0)
    d.text((x+12,322),f'{src.width}x{src.height} • {rec["status"]}',fill=(246,247,251))
out=ROOT/"docs/previews/map_factory_renders/new_hero_parts_v10.png"
out.parent.mkdir(parents=True,exist_ok=True)
sheet.convert("RGB").save(out)
print("Created real sprite contact sheet",out, "bytes",out.stat().st_size)
