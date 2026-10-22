#!/usr/bin/env python3
"""Create missing modular fragments from existing detailed art (no upscaling),
plus reusable RGBA flame and glow effects. New files remain needs_cleanup.
"""
from PIL import Image, ImageDraw, ImageFilter, ImageOps
from pathlib import Path
import csv, json, math
ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/"map_factory/metadata/asset_index.json"
QUEUE=ROOT/"map_factory/metadata/production_queue.csv"
DESTS={
 "W008":("W006","mirror","Mirrored source; corner orientation needs manual art QA"),
 "W009":("W007","mirror","Mirrored source; corner orientation needs manual art QA"),
 "A002":("A001","arch_top","Top segment; verify seams with adjoining arch parts"),
 "A003":("A001","arch_left","Left segment; verify connecting seams and proportions"),
 "A004":("A001","arch_right","Right segment; verify connecting seams and proportions"),
 "A016":("W016","door","Decorated door segment; crop needs manual refinement"),
 "D006":("D001","banner_mount","Banner upper mount detail; attachment needs review")
}

def cut(img,method):
    w,h=img.size
    if method=="mirror":
        return ImageOps.mirror(img)
    if method=="arch_top":
        part=img.crop((0,0,w,round(h*.56)))
    elif method=="arch_left":
        part=img.crop((0,0,round(w*.39),h))
    elif method=="arch_right":
        part=img.crop((round(w*.61),0,w,h))
    elif method=="door":
        part=img.crop((round(w*.22),round(h*.13),round(w*.80),h))
    elif method=="banner_mount":
        part=img.crop((0,0,w,round(h*.22)))
    else:
        part=img
    alpha=part.getchannel("A").getbbox()
    if alpha:
        return part.crop(alpha)
    return part

def flame(frame):
    im=Image.new("RGBA",(96,128),(0,0,0,0))
    d=ImageDraw.Draw(im)
    x=48;shift=[-4,0,5][frame]
    y=[13,4,9][frame]
    def poly(points,fill):d.polygon(points,fill=fill)
    poly([(x-21,108),(x-24,85),(x-14,60+y),(x-10,34+y),
          (x-2,44+y),(x+10,12+y),(x+16,51+y),(x+27,70+y),
          (x+16,104)],(224,80,19,202))
    poly([(x-15,106),(x-14,80),(x-4,52+y),(x+3,62+y),
          (x+8+shift,27+y),(x+15,69+y),(x+17,102)],(255,174,42,250))
    poly([(x-9,106),(x-5,89),(x+3,63+y),(x+9,84),
          (x+11,106)],(255,242,150,255))
    d.ellipse((x-9,100,x+13,121),fill=(255,230,122,236))
    return im

def glow(radius):
    s=256;im=Image.new("RGBA",(s,s),(0,0,0,0))
    pixels=im.load()
    for y in range(s):
        for x in range(s):
            dx=(x-127.5)/radius;dy=(y-127.5)/radius
            t=dx*dx+dy*dy
            if t<9:
                alpha=max(0,min(140,round(135*math.exp(-1.6*t))))
                pixels[x,y]=(255,162,42,alpha)
    return im

def main():
    data=json.loads(INDEX.read_text(encoding="utf-8"))
    by={x["id"]:x for x in data["assets"]}
    created=0
    for target,(source,method,notes) in DESTS.items():
        a=by[target];dst=ROOT/a["texture_path"].removeprefix("res://")
        if dst.exists():continue
        src=ROOT/by[source]["texture_path"].removeprefix("res://")
        if not src.is_file():
            print("Source missing",src)
            continue
        image=Image.open(src).convert("RGBA")
        image=cut(image,method)
        dst.parent.mkdir(parents=True,exist_ok=True)
        image.save(dst,optimize=True)
        a["pixel_size"]=list(image.size)
        a["origin"]=[image.width//2,image.height] if a["category"]!="ui" else [0,0]
        a["status"]="needs_cleanup"
        a["source"]={"kind":"derived_high_detail_source_fragment","parent_id":source,"method":method}
        a["qa_notes"]=notes+"; preserves source-native pixels; visually inspect before approval."
        created+=1
    for id in ("D012","D013","D014","D015","D016"):
        a=by[id];dst=ROOT/a["texture_path"].removeprefix("res://")
        if dst.exists():continue
        if id in ("D012","D013","D014"):
            image=flame(int(id[-1])-2)
            a["origin"]=[image.width//2,image.height-6]
            a["qa_notes"]="One of 3-frame independent candle flame RGBA effects; compare light and timing."
        else:
            image=glow(77 if id=="D015" else 95)
            a["origin"]=[128,128]
            a["qa_notes"]="Soft independent translucent orange light overlay. Blend/tint in Godot after visual QA."
        dst.parent.mkdir(parents=True,exist_ok=True)
        image.save(dst,optimize=True)
        a["pixel_size"]=list(image.size)
        a["status"]="needs_cleanup"
        a["source"]={"kind":"original_procedural_fx","generator":"tools/generate_missing_details.py"}
        created+=1
    data["extracted_count"]=sum((ROOT/a["texture_path"].removeprefix("res://")).is_file() for a in data["assets"])
    INDEX.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    with QUEUE.open("w",newline="",encoding="utf-8") as f:
        writer=csv.writer(f);writer.writerow(["id","category","name","status","texture_path"])
        writer.writerows([a["id"],a["category"],a["name"],a["status"],a["texture_path"]] for a in data["assets"])
    print("Created",created,"modular detail PNGs. New assets require art QA.")
if __name__=="__main__":
    main()
