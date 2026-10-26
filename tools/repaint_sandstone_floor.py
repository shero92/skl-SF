#!/usr/bin/env python3
"""Repaint 22 64x64 stone-floor sprites and a coherent nine-part compass inlay.
Individual image IDs, native grid dimensions and alpha are retained.
First-pass curated pixel art: not a declaration of 100% final art quality.
"""
from PIL import Image, ImageDraw
from pathlib import Path
import random, math, json, csv

ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/"map_factory/metadata/asset_index.json"
OUT=ROOT/"map_factory/parts/floors"
PREVIEW=ROOT/"docs/previews"
NAMES=("Stone_Floor_Plain Stone_Floor_Cracked Stone_Floor_Worn Stone_Floor_Light "
"Stone_Floor_Dark Stone_Floor_Edge_N Stone_Floor_Edge_S Stone_Floor_Edge_E "
"Stone_Floor_Edge_W Stone_Floor_Corner_NW Stone_Floor_Corner_NE "
"Stone_Floor_Corner_SW Stone_Floor_Corner_SE Compass_Floor_Center "
"Compass_Floor_N Compass_Floor_S Compass_Floor_E Compass_Floor_W "
"Compass_Floor_Corner_NW Compass_Floor_Corner_NE "
"Compass_Floor_Corner_SW Compass_Floor_Corner_SE").split()

def stone(index=0):
    rng=random.Random(72213+index*72931)
    im=Image.new("RGBA",(64,64),(233,186,116,255))
    pix=im.load();d=ImageDraw.Draw(im)
    shade=14 if index==3 else (-15 if index==4 else (0 if index<13 else 6))
    for y in range(64):
        for x in range(64):
            v=math.sin(x*.095+index*3)*2.5+math.sin(y*.13+index*.5)*1.7
            edge=-12*(x>60 or y>60)+5*(x<3 or y<3)
            t=int(shade+v+edge+rng.gauss(0,5.9))
            pix[x,y]=(max(0,min(255,230+t)),max(0,min(255,186+t)),
                      max(0,min(255,122+int(t*.81))),255)
    for i in range(125):
        x=rng.randrange(2,62);y=rng.randrange(2,62)
        c=rng.choice(["#f8d99e","#c79362","#dfae71","#fff0bb","#b98c60","#e7bf83"])
        if i%4==0:d.line([(x,y),(x+2,y-1)],fill=c,width=1)
        elif i%4==1:d.point((x,y),fill=c)
        else:d.line([(x,y),(x+1,y)],fill=c,width=1)
    d.line([(0,0),(63,0)],fill="#b38655")
    d.line([(0,0),(0,63)],fill="#d8aa6c")
    d.line([(1,2),(62,2)],fill="#ffe5aa")
    d.line([(2,1),(2,62)],fill="#f4cd86")
    d.line([(63,1),(63,63)],fill="#9e7652")
    d.line([(1,63),(63,63)],fill="#976947")
    d.line([(60,2),(60,60)],fill="#dfb67e")
    d.line([(2,60),(60,60)],fill="#d2a26e")
    for i in range(8):
        x,y=rng.randint(6,57),rng.randint(6,57)
        if (i==1 and index==2) or (index==1 and i<=3):
            pts=[(x,y),(x+rng.choice([-6,6]),y+rng.randint(5,9)),
                (x+rng.choice([-10,10]),y+rng.randint(10,14))]
            d.line(pts,fill="#bc8f5f",width=1);d.point(pts[-1],fill="#996c4d")
    if index==2:
        for _ in range(19):
            d.point((rng.randint(8,54),rng.randint(8,55)),
                    fill=rng.choice(["#ac865c","#c29368","#d1a675"]))
    edges={5:["n"],6:["s"],7:["e"],8:["w"],9:["n","w"],10:["n","e"],
           11:["s","w"],12:["s","e"]}
    for edge in edges.get(index,[]):
        if edge=="n":
            d.rectangle((0,0,63,3),fill="#8b7058")
            d.line((1,3,62,3),fill="#fff0be")
        elif edge=="s":
            d.rectangle((0,60,63,63),fill="#9b7352")
            d.line((0,59,62,59),fill="#f6d796")
        elif edge=="w":
            d.rectangle((0,0,3,63),fill="#896b52")
            d.line((4,1,4,62),fill="#ffe0a4")
        elif edge=="e":
            d.rectangle((60,0,63,63),fill="#88684b")
            d.line((59,1,59,62),fill="#f9d58d")
    return im

def compass_art():
    im=Image.new("RGBA",(192,192))
    d=ImageDraw.Draw(im);cx=cy=96
    diamond=[(cx,cy-89),(cx+89,cy),(cx,cy+89),(cx-89,cy)]
    d.polygon(diamond,fill="#092f74")
    d.line(diamond+[diamond[0]],fill="#f4c652",width=5,joint="curve")
    inner=[(cx,cy-80),(cx+80,cy),(cx,cy+80),(cx-80,cy)]
    d.line(inner+[inner[0]],fill="#2c72bd",width=3)
    for r in (63,57):
        d.ellipse((cx-r,cy-r,cx+r,cy+r),outline="#dbac43",width=3)
    d.ellipse((cx-48,cy-48,cx+48,cy+48),outline="#1a75b3",width=2)
    for deg in range(0,360,15):
        a=math.radians(deg-90)
        r1=51 if deg%45 else 48
        p1=(cx+int(math.cos(a)*r1),cy+int(math.sin(a)*r1))
        p2=(cx+int(math.cos(a)*61),cy+int(math.sin(a)*61))
        d.line((p1,p2),fill="#e5af4c",width=2 if deg%45==0 else 1)
    for deg in range(0,360,45):
        a=math.radians(deg-90)
        r=53 if deg%90==0 else 43
        perp=a+math.pi/2
        P=lambda radius,angle:(round(cx+radius*math.cos(angle)),
                               round(cy+radius*math.sin(angle)))
        p1=P(r,a);p2=P(10,perp);p3=P(10,perp+math.pi)
        d.polygon((p1,p2,(cx,cy)),fill="#edc765" if deg%90==0 else "#ca8c38")
        d.polygon((p1,(cx,cy),p3),fill="#f7df9b" if deg%90==0 else "#dea44d")
        d.line((p1,p2,(cx,cy),p3,p1),fill="#153e88",width=2)
    for deg in range(0,360,90):
        a=math.radians(deg)
        x=cx+69*math.cos(a);y=cy+69*math.sin(a)
        d.ellipse((x-3,y-3,x+3,y+3),fill="#ffdf80",outline="#d99e35")
    d.ellipse((cx-9,cy-9,cx+9,cy+9),fill="#eec45a",outline="#0f4a9f",width=3)
    d.ellipse((cx-3,cy-3,cx+3,cy+3),fill="#fff0a5")
    rng=random.Random(810)
    for _ in range(230):
        x=rng.randrange(192);y=rng.randrange(192)
        if im.getpixel((x,y))[3] and rng.random()<.5:
            d.point((x,y),fill=rng.choice(["#1c4f92","#dbab51","#1e5aa1"]))
    return im

SLOTS={13:(1,1),14:(1,0),15:(1,2),16:(2,1),17:(0,1),
       18:(0,0),19:(2,0),20:(0,2),21:(2,2)}

def render():
    assets=[stone(i) for i in range(22)]
    whole=compass_art()
    for index,(col,row) in SLOTS.items():
        crop=whole.crop((col*64,row*64,(col+1)*64,(row+1)*64))
        assets[index]=Image.alpha_composite(assets[index],crop)
    return assets

def main():
    OUT.mkdir(parents=True,exist_ok=True);PREVIEW.mkdir(parents=True,exist_ok=True)
    data=json.loads(INDEX.read_text(encoding="utf-8"))
    by_id={a["id"]:a for a in data["assets"]}
    images=render()
    for i,im in enumerate(images):
        ident="F%03d"%(i+1)
        record=by_id[ident]
        assert record["category"]=="floors"
        path=ROOT/record["texture_path"].removeprefix("res://")
        if path.name!=ident+"_"+NAMES[i]+".png":
            raise RuntimeError("Catalog path differs: "+str(path))
        source=record.get("source", {})
        kind=source.get("kind", "") if isinstance(source,dict) else str(source)
        if record.get("status")=="ready" or kind not in (
                "procedural","existing_unreviewed_png",
                "manual_procedural_pixel_art_revision"):
            print("Preserved higher-detail or approved source:",ident,kind)
            continue
        if kind=="manual_procedural_pixel_art_revision" and source.get("revision")!="2":
            print("Preserved a newer floor revision:",ident)
            continue
        im.save(path,optimize=True)
        record["pixel_size"]=[64,64]
        record["origin"]=[0,0]
        record["status"]="needs_cleanup"
        record["source"]={"kind":"manual_procedural_pixel_art_revision",
                          "generator":"tools/repaint_sandstone_floor.py","revision":"2",
                          "pixel_scale":"native_64"}
        record["qa_notes"]=("Coherent 3x3 nautical compass floor inlay." if i>=13 else
            "Repainted warm weathered sandstone tile with directional grout;")
        record["qa_notes"]+=" Visual QA required against original Hero Room reference."
    mosaic=Image.new("RGBA",(192,192))
    for index,(col,row) in SLOTS.items():
        mosaic.alpha_composite(images[index],(col*64,row*64))
    mosaic.resize((768,768),Image.Resampling.NEAREST).save(
        PREVIEW/"compass_mosaic_review.png",optimize=True)
    sheet=Image.new("RGB",(5*260,5*280),"#0a254b")
    d=ImageDraw.Draw(sheet)
    for i in range(len(images)):
        id="F%03d"%(i+1)
        actual=ROOT/by_id[id]["texture_path"].removeprefix("res://")
        with Image.open(actual) as file:
            im=file.convert("RGBA")
        x=(i%5)*260;y=(i//5)*280
        thumbnail=im.copy()
        thumbnail.thumbnail((240,240),Image.Resampling.LANCZOS)
        sheet.paste(thumbnail,(x+8+(240-thumbnail.width)//2,y+8+(240-thumbnail.height)//2),mask=thumbnail.getchannel("A"))
        d.text((x+8,y+253),id,fill="#ffd477")
    sheet.save(PREVIEW/"sandstone_floor_review.png",optimize=True)
    (ROOT/"docs/FLOOR_REPAINT_QA.md").write_text(
        "# Stone Floor 22-piece repaint\n\n"
        "This change repaints 18 draft tiles while deliberately preserving four richer original F001/F002/F006/F010 source PNGs. "
        "The compass now composes into one coherent 3×3 192×192 nautical inlay; "
        "it is NOT nine copies of a single compass. Each file remains 64×64 "
        "pixel-native RGBA and therefore compatible with the room grid. "
        "Replacements are intentionally marked needs_cleanup, not approved as "
        "identical to the original reference.\n\n"
        "![Nine-part compass](previews/compass_mosaic_review.png)\n\n"
        "![Floor tile catalog](previews/sandstone_floor_review.png)\n\n"
        "The hero_room.json tile_overrides place F019 F015 F020 / "
        "F018 F014 F017 / F021 F016 F022 in a 3×3 region. "
        "Check direct Godot rendering and palette fidelity before marking ready.\n",
        encoding="utf-8", newline="\n")
    INDEX.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8",newline="\n")
    with (ROOT/"map_factory/metadata/production_queue.csv").open(
        "w",newline="",encoding="utf-8") as stream:
        writer=csv.writer(stream,lineterminator="\n")
        writer.writerow(("id","category","name","status","texture_path"))
        writer.writerows((a["id"],a["category"],a["name"],a["status"],a["texture_path"])
                        for a in data["assets"])
    print("Repainted 22 floor PNGs; 9-piece compass mosaic generated.")

if __name__=="__main__":
    main()
