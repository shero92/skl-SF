#!/usr/bin/env python3
"""Repaint ornate navy-gold JRPG frames at original pixel dimensions.
Five assets only. Existing artist-approved or externally-replaced images are never overwritten.
"""
from PIL import Image, ImageDraw
from pathlib import Path
import math,random,json,csv

ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/"map_factory/metadata/asset_index.json"
PREVIEW=ROOT/"docs/previews"
GOLD="#f7cd5a";DEEP="#bd8122";PALE="#ffecac"

def base(w,h,transparent=False):
    im=Image.new("RGBA",(w,h),(0,0,0,0) if transparent else (5,19,50,255))
    d=ImageDraw.Draw(im)
    if not transparent:
        px=im.load()
        for y in range(h):
            for x in range(w):
                n=math.sin(x/37+y/14)*3+math.cos(x/16-y/29)*2
                v=int(11+6*(1-y/max(1,h))+n)
                px[x,y]=(4,11+v,29+v,255)
        rng=random.Random(400)
        for _ in range(int(w*h/580)):
            x=rng.randint(14,w-15);y=rng.randint(9,h-10)
            d.point((x,y),fill=rng.choice(["#12365d","#1c456a","#0b2c5c"]))
    return im,d

def frame(im,d):
    w,h=im.size
    d.rectangle((1,1,w-2,h-2),outline="#120f23",width=2)
    d.rectangle((3,3,w-4,h-4),outline=DEEP,width=3)
    d.rectangle((6,6,w-7,h-7),outline=GOLD,width=2)
    d.rectangle((10,10,w-11,h-11),outline="#40658d")
    d.line((14,13,w-15,13),fill="#1c4b80")
    for ox,oy,sx,sy in ((6,6,1,1),(w-7,6,-1,1),(6,h-7,1,-1),(w-7,h-7,-1,-1)):
        C=lambda x,y:(ox+sx*x,oy+sy*y)
        d.line((C(0,20),C(0,0),C(20,0)),fill=PALE,width=3,joint="curve")
        d.line((C(4,19),C(10,9),C(19,4)),fill=GOLD,width=2,joint="curve")
        d.line((C(6,29),C(11,15),C(15,11),C(29,6)),fill=DEEP,width=2)
        d.polygon((C(11,13),C(15,9),C(19,13),C(15,18)),fill=GOLD)
        p1=C(21,20);p2=C(25,24)
        d.ellipse((min(p1[0],p2[0]),min(p1[1],p2[1]),
                   max(p1[0],p2[0]),max(p1[1],p2[1])),fill=PALE)
        d.line((C(16,28),C(17,21),C(21,16),C(28,15)),fill=GOLD)
    return im

def panel():
    im,d=base(860,168);frame(im,d)
    d.line((44,15,816,15),fill="#173760",width=2)
    d.line((45,146,816,146),fill="#16325e",width=2)
    d.line((52,31,808,31),fill="#233d68")
    return im

def title():
    im,d=base(360,72);frame(im,d)
    d.line((51,12,309,12),fill="#3865a0")
    d.line((53,60,310,60),fill="#233b6f")
    return im

def portrait_frame():
    im,d=base(142,160,True)
    d.rectangle((0,0,141,159),outline=DEEP,width=6)
    d.rectangle((4,4,137,155),outline=GOLD,width=3)
    d.rectangle((9,9,132,150),outline="#d99b37",width=2)
    for ox,oy,sx,sy in ((6,6,1,1),(135,6,-1,1),(6,153,1,-1),(135,153,-1,-1)):
        C=lambda x,y:(ox+sx*x,oy+sy*y)
        d.line((C(0,18),C(0,0),C(18,0)),fill=PALE,width=3)
        d.polygon((C(7,7),C(14,8),C(8,14)),fill=GOLD)
    return im

def arrow():
    im,d=base(64,64,True)
    d.polygon(((18,23),(48,23),(33,43)),fill="#080d2b")
    d.polygon(((20,20),(47,20),(33,41)),fill=DEEP)
    d.polygon(((24,21),(43,21),(33,36)),fill=GOLD)
    d.line(((27,22),(33,30),(38,22)),fill=PALE,width=2)
    return im

def corner():
    im,d=base(64,64,True)
    d.line(((3,50),(3,4),(53,4)),fill=DEEP,width=5)
    d.line(((6,49),(6,8),(53,8)),fill=GOLD,width=3)
    d.line(((15,46),(14,24),(24,13),(48,13)),fill=PALE,width=2)
    d.polygon(((13,14),(20,10),(24,16),(18,24)),fill=GOLD)
    d.polygon(((13,33),(19,27),(26,33),(20,39)),fill=DEEP)
    return im

ART={"UI001":panel,"UI011":title,"UI004":portrait_frame,
     "UI005":arrow,"UI012":corner}

def main():
    data=json.loads(INDEX.read_text(encoding="utf-8"))
    by={a["id"]:a for a in data["assets"]}
    images={}
    for id,generate in ART.items():
        a=by[id];source=a.get("source",{})
        if a.get("status")=="ready" or (
            isinstance(source,dict) and source.get("kind") not in
            ("procedural","handcrafted_pixel_ui_revision")
        ):
            print("Preserving newer or approved artwork",id)
            continue
        if isinstance(source,dict) and source.get("kind")=="handcrafted_pixel_ui_revision":
            print("Already generated once",id)
            continue
        image=generate()
        path=ROOT/a["texture_path"].removeprefix("res://")
        assert image.size==tuple(a["pixel_size"]), (id,image.size,a["pixel_size"])
        path.parent.mkdir(parents=True,exist_ok=True)
        image.save(path,optimize=True)
        a["source"]={"kind":"handcrafted_pixel_ui_revision","revision":1,
                     "generator":"tools/repaint_dialogue_ui.py"}
        a["status"]="needs_cleanup"
        a["qa_notes"]="More detailed deep navy/gold ornaments matching the Hero Room reference; visual QA pending."
        images[id]=image
    if images:
        PREVIEW.mkdir(parents=True,exist_ok=True)
        preview=Image.new("RGBA",(900,430),"#0d2e5d")
        for id,x,y in (("UI001",20,210),("UI011",20,18),("UI004",50,207),
                       ("UI005",795,278)):
            if id in images:
                preview.alpha_composite(images[id],(x,y))
        preview.save(PREVIEW/"ornate_dialogue_ui_review.png",optimize=True)
    INDEX.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    with (ROOT/"map_factory/metadata/production_queue.csv").open("w",newline="",encoding="utf-8") as f:
        writer=csv.writer(f)
        writer.writerow(("id","category","name","status","texture_path"))
        writer.writerows((a["id"],a["category"],a["name"],a["status"],a["texture_path"])
                         for a in data["assets"])
    print("Upgraded individual UI files:",sorted(images))

if __name__=="__main__":main()
