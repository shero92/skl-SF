#!/usr/bin/env python3
"""Build optional review contact sheets; production sprites remain standalone PNGs.

These previews are clearly QA-only and never loaded by the game.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json, math

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "map_factory/metadata/asset_index.json"
OUTPUT = ROOT / "docs/previews"
GALLERY = ROOT / "docs/ASSET_GALLERY.md"
THUMB = (164, 152)
MARGIN = 10
COLUMNS = 6

def main():
    catalog = json.loads(INDEX.read_text(encoding="utf-8"))["assets"]
    OUTPUT.mkdir(parents=True,exist_ok=True)
    groups={}
    for asset in catalog:
        src=ROOT / asset["texture_path"].removeprefix("res://")
        if src.is_file():
            groups.setdefault(asset["category"],[]).append((asset,src))
    md=["# Sprite review gallery","",
        "These are review thumbnails ONLY. Production textures live as separate PNGs under map_factory/parts/.","",
        "Draft art is not approved until a person checks native pixel detail, clean alpha, lighting, tile seams, scale, origin, collisions and shadow.",""]
    for category,items in sorted(groups.items()):
        rows=math.ceil(len(items)/COLUMNS)
        cellw=THUMB[0]+MARGIN*2;cellh=THUMB[1]+MARGIN*2+40
        sheet=Image.new("RGBA",(cellw*COLUMNS,cellh*rows),(15,34,60,255))
        draw=ImageDraw.Draw(sheet)
        for i,(a,p) in enumerate(items):
            x=(i%COLUMNS)*cellw+MARGIN
            y=(i//COLUMNS)*cellh+MARGIN
            draw.rectangle((x-2,y-2,x+THUMB[0]+2,y+THUMB[1]+2),outline=(90,119,147,255),width=1)
            try:
                with Image.open(p) as img:
                    sprite=img.convert("RGBA")
                sprite.thumbnail(THUMB,Image.Resampling.NEAREST)
                # Checkerboard makes transparency visually inspectable.
                for yy in range(y,y+THUMB[1],12):
                    for xx in range(x,x+THUMB[0],12):
                        shade=(27,51,77,255) if (xx//12+yy//12)%2 else (39,61,89,255)
                        draw.rectangle((xx,yy,min(xx+11,x+THUMB[0]-1),min(yy+11,y+THUMB[1]-1)),fill=shade)
                sheet.alpha_composite(sprite,(x+(THUMB[0]-sprite.width)//2,y+(THUMB[1]-sprite.height)//2))
            except OSError:
                draw.text((x+8,y+8),"Invalid PNG",fill=(240,108,111))
            draw.text((x+8,y+THUMB[1]+4),a["id"],fill=(255,211,114),font=ImageFont.load_default())
            draw.text((x+8,y+THUMB[1]+19),a["status"][:17],fill=(206,215,227),font=ImageFont.load_default())
        out=OUTPUT / (category+".png")
        sheet.convert("RGB").save(out,optimize=True)
        md.extend(["## "+category.title(),"",f"![{category} sprites](previews/{category}.png)","",
                   f"**{len(items)} PNGs** | Actual files: [map_factory/parts/{category}](../map_factory/parts/{category})",""])
    GALLERY.write_text("\n".join(md),encoding="utf-8",newline="\n")
    print("Generated",len(groups),"category review sheets.")

if __name__=="__main__":
    main()
