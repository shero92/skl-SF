#!/usr/bin/env python3
"""High-detail looping 512px maritime pixel-art sea, with four alpha wave frames.

Single water source + four independent overlay PNGs. Deterministic, seamless
periodic texture; never changes existing ID paths. Art QA still required.
"""
from PIL import Image,ImageDraw
from pathlib import Path
import math,random,json,csv

ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/"map_factory/metadata/asset_index.json"
PREVIEW=ROOT/"docs/previews"
S=512

def base():
    im=Image.new("RGBA",(S,S));pixels=im.load()
    for y in range(S):
        for x in range(S):
            a=x*math.tau/S;b=y*math.tau/S
            wave=(math.sin(a*2+b*3)*.36+math.cos(a*5-b*2)*.26+
                  math.sin(a*11+b*7)*.17+math.cos(a*13-b*9)*.12+
                  math.sin(a*21+b*23)*.08)
            v=(max(-1,min(1,wave))+1)/2
            pixels[x,y]=(int(7+19*v),int(67+102*v),int(160+82*v),255)
    rng=random.Random(1212)
    d=ImageDraw.Draw(im)
    for k in range(1000):
        x=rng.randrange(S);y=rng.randrange(S);length=rng.randrange(3,10)
        c=rng.choice(((36,166,238,145),(72,197,246,143),
                      (14,117,202,158),(11,81,179,128)))
        for dx in (-S,0,S):
            for dy in (-S,0,S):
                d.line((x+dx,y+dy,x+length+dx,y+dy-k%3),fill=c)
    return im

def overlay(frame):
    im=Image.new("RGBA",(S,S))
    d=ImageDraw.Draw(im)
    rng=random.Random(5352)
    for k in range(73):
        x=rng.randrange(S);y=rng.randrange(S)
        radius=rng.randrange(12,46)
        px=(x+frame*8+k%3)%S
        py=(y+frame*3)%S
        height=rng.randrange(5,13)
        coords=[]
        for q in range(-radius,radius+1,2):
            u=q/radius
            h=height*(1-u*u)+math.sin(q*.3+k)*1.6
            coords.append((int(px+q),int(py-h)))
        for tx in (-S,0,S):
            for ty in (-S,0,S):
                d.line([(a+tx,b+ty+5) for a,b in coords],
                       fill=(15,130,224,90),width=4)
                d.line([(a+tx,b+ty+2) for a,b in coords],
                       fill=(87,204,251,165),width=2)
                for i,(a,b) in enumerate(coords):
                    if (i+k)%3:
                        d.rectangle((a+tx,b+ty,a+tx+3,b+ty),
                                    fill=(221,247,253,213))
        for _ in range(18):
            x2=px+rng.randint(-radius,radius)
            y2=py+rng.randint(0,15)
            length=rng.choice((1,1,2,3))
            color=rng.choice(((237,253,253,194),(163,231,250,170),
                              (40,161,230,136)))
            for tx in (-S,0,S):
                for ty in (-S,0,S):
                    d.line((x2+tx,y2+ty,x2+tx+length,y2+ty),fill=color)
    for j in range(20):
        x=(j*47+frame*9)%S;y=(j*64+frame*7)%S
        points=[((x+step*6)%S,
                 (y+int(3*math.sin(step*.55+j))+step*2)%S)
                for step in range(13)]
        for (x0,y0),(x1,y1) in zip(points,points[1:]):
            if abs(x0-x1)>S//2 or abs(y0-y1)>S//2:
                continue
            d.line((x0,y0,x1,y1),fill=(84,210,247,125))
    return im

def main():
    data=json.loads(INDEX.read_text(encoding="utf-8"))
    by={a["id"]:a for a in data["assets"]}
    ocean=base()
    frames=[overlay(i) for i in range(4)]
    for ident,image in [("E010",ocean)]+[("E%03d"%(11+i),f)
                                           for i,f in enumerate(frames)]:
        a=by[ident]
        assert a["category"]=="environment"
        path=ROOT/a["texture_path"].removeprefix("res://")
        path.parent.mkdir(parents=True,exist_ok=True)
        image.save(path,optimize=True)
        a["pixel_size"]=[S,S]
        a["origin"]=[0,0]
        a["source"]={"kind":"multi_scale_maritime_pixel_art_revision",
                     "revision":2,"generator":"tools/repaint_ocean.py"}
        a["status"]="needs_cleanup"
        a["qa_notes"]="Cobalt/cyan sea with wrap-safe white foam. Validate looping, tint, light direction and visual fidelity before ready."
    data["status_note"]="All 218 PNGs present. Material upgrades remain needs_cleanup until reviewed."
    INDEX.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    with (ROOT/"map_factory/metadata/production_queue.csv").open("w",newline="",encoding="utf-8") as f:
        writer=csv.writer(f)
        writer.writerow(("id","category","name","status","texture_path"))
        writer.writerows((a["id"],a["category"],a["name"],a["status"],a["texture_path"])
                         for a in data["assets"])
    PREVIEW.mkdir(parents=True,exist_ok=True)
    sample=Image.alpha_composite(ocean,frames[1])
    composite=Image.new("RGBA",(1024,1024))
    for yy in range(2):
        for xx in range(2):
            composite.alpha_composite(sample,(xx*S,yy*S))
    composite.save(PREVIEW/"ocean_seam_review.png",optimize=True)
    print("Repainted high-detail 512px ocean tile and four transparent wave frames")

if __name__=="__main__":
    main()
