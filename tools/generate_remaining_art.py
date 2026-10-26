#!/usr/bin/env python3
"""Generate missing Hero Room sprites: detailed compositing + individual procedural illustrations.

Never replaces an existing PNG. Creates 31 PNGs at the exact catalog paths.
Existing high-detail source sprite components are reused at native pixels when appropriate.
Everything created is subject to manual pixel-art quality control.
"""
from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageEnhance
import csv, json, math, random

ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/"map_factory/metadata/asset_index.json"
CSV=ROOT/"map_factory/metadata/production_queue.csv"
SAND=(232,189,122,255)
GOLD=(245,184,57,255)
NAVY=(15,51,113,255)
BLUE=(18,94,174,255)
WOOD=(111,62,32,255)
PIXEL="pixel_art"

def canvas(w,h):
    im=Image.new("RGBA",(w,h),(0,0,0,0))
    return im,ImageDraw.Draw(im)

def load_src(cat,id):
    catalog=load_src.catalog
    a=catalog[id]
    return Image.open(ROOT/a["texture_path"].removeprefix("res://")).convert("RGBA")

def polygon(d,pts,col,outline=None,width=2):
    d.polygon(pts,fill=col)
    if outline:
        d.line(pts+[pts[0]],fill=outline,width=width,joint="curve")

def line(d,points,col,width=2):
    d.line(points,fill=col,width=width,joint="curve")

def grad(d,w,h,top,bottom):
    for y in range(h):
        k=y/max(1,h-1)
        color=tuple(int(top[i]*(1-k)+bottom[i]*k) for i in range(3))+(255,)
        d.line((0,y,w,y),fill=color)

def noise_on_layer(im,seed,count,colors,region=None,pointsize=2):
    rng=random.Random(seed)
    w,h=im.size
    d=ImageDraw.Draw(im)
    x0,y0,x1,y1=region or (0,0,w,h)
    for _ in range(count):
        x=rng.randint(x0,max(x0,x1-1));y=rng.randint(y0,max(y0,y1-1))
        c=rng.choice(colors)
        d.rectangle((x,y,x+pointsize,y+max(1,pointsize//2)),fill=c)

def stone_stair(idx):
    w,h=192,76
    im,d=canvas(w,h)
    seed=idx*1021
    polygon(d,[(4,16),(186,16),(191,23),(187,70),(5,70),(0,62)],(109,77,47,255),(73,56,41,255),2)
    polygon(d,[(2,15),(27,2),(168,2),(189,16),(180,50),(19,50)],(234,191,124,255),(127,92,57,255),3)
    polygon(d,[(4,46),(186,46),(185,59),(4,60)],(166,111,67,255),(120,79,47,255),1)
    polygon(d,[(16,6),(172,6),(184,16),(10,16)],(246,215,160,255))
    noise_on_layer(im,seed,700,[(255,232,173,130),(192,149,94,210),(131,91,53,190),(233,174,89,145)],
        (11,10,179,43),pointsize=2)
    rng=random.Random(seed+3)
    for j in range(13):
        x=rng.randint(15,176)
        y=rng.randint(19,46)
        d.line((x,y,x+rng.randint(-8,7),y+rng.randint(0,8)),fill=(146,109,74,160),width=1)
    if idx==1:
        polygon(d,[(1,0),(189,0),(180,8),(9,8)],(251,221,173,255),(151,114,77,255),2)
        line(d,[(0,18),(192,18)],(112,82,54,255),2)
    if idx==3:
        polygon(d,[(10,47),(182,47),(174,58),(20,58)],(240,203,145,255),(136,88,53,255),2)
    if idx==6:
        polygon(d,[(3,1),(188,1),(188,61),(4,61)],(230,190,133,255),(127,92,62,255),2)
        for x in (3,66,129,188):
            line(d,[(x,1),(x,61)],(125,93,65,255),2)
        for y in (1,60):
            line(d,[(4,y),(187,y)],(128,99,67,255),2)
        noise_on_layer(im,1422,350,[(248,213,154,155),(178,138,98,190)],(5,3,185,59),2)
    return im

def water_base(seed=23,w=256,h=256):
    # Seamless by construction: trigonometric periodic fields and wrapped pixels.
    img=Image.new("RGBA",(w,h),(0,0,0,0));px=img.load()
    for y in range(h):
        for x in range(w):
            a=x*math.tau/w;b=y*math.tau/h
            f=(math.sin(a*3+b*2)+0.6*math.sin(a*6-b*4)+
               0.44*math.cos(a*9+b*8)+0.26*math.cos(a*17-b*11))
            g=max(-1.8,min(1.8,f))
            t=(g+1.8)/3.6
            px[x,y]=(int(6+18*t),int(72+85*t),int(145+97*t),255)
    rng=random.Random(seed)
    d=ImageDraw.Draw(img)
    for _ in range(235):
        x=rng.randrange(w); y=rng.randrange(h)
        length=rng.randint(3,22)
        col=rng.choice([(58,186,239,125),(16,125,220,140),(122,207,242,120),(12,93,194,175)])
        for shift in (-w,0,w):
            for dy in (-h,0,h):
                d.line((x+shift,y+dy,x+length+shift,y+dy-rng.randint(0,2)),fill=col,width=rng.choice([1,2]))
    return img

def waves(frame,base=False):
    w=h=256
    im=water_base(34) if base else Image.new("RGBA",(w,h))
    d=ImageDraw.Draw(im)
    rng=random.Random(211)
    phase=frame*7
    for i in range(75):
        cx=rng.randint(-15,w+15)
        cy=rng.randint(-10,h+10)
        x=(cx+phase+i%3*3)%w
        y=(cy+phase//2)%h
        length=rng.randint(9,35)
        color=rng.choice([(243,253,251,210),(187,238,255,190),
                         (98,202,244,160),(30,150,238,130)])
        for xx in (-w,0,w):
            for yy in (-h,0,h):
                d.arc((x+xx,y+yy,x+length+xx,y+rng.randint(3,8)+yy),
                      188,348,fill=color,width=rng.choice([1,2,3]))
    return im

def foam():
    w,h=320,102
    im,d=canvas(w,h)
    rng=random.Random(911)
    # Transparent breakwater foam, with organic blue/white pixel clusters
    for layer,c,weight in [
        (0,(39,149,221,122),6),(1,(131,222,253,180),4),
        (2,(246,252,251,230),3)]:
        pts=[]
        for x in range(-10,w+10,3):
            yy=int(22+math.sin(x*0.034)*12+math.cos(x*0.087)*4+layer*8)
            pts.append((x,yy))
        d.line(pts,fill=c,width=weight,joint="curve")
        for _ in range(180):
            x=rng.randrange(w);yy=int(24+math.sin(x*.034)*12+math.cos(x*.087)*4)
            y=yy+rng.randint(-8,26)
            radius=rng.choice([1,2,3])
            d.ellipse((x-radius,y-radius,x+radius,y+radius),
                      fill=(235,254,253,rng.randint(70,219)))
    return im

def island(id):
    src=load_src("environment","E004" if id=="E015" else "E005")
    if id=="E015":
        w,h=320,260
        src.thumbnail((235,220),Image.Resampling.LANCZOS)
    else:
        w,h=465,310
        src.thumbnail((405,255),Image.Resampling.LANCZOS)
    im,d=canvas(w,h)
    x=(w-src.width)//2
    y=max(15,h-src.height-40)
    im.alpha_composite(src,(x,y))
    foamimg=foam()
    foamimg=foamimg.resize((int(w*.87),65),Image.Resampling.NEAREST)
    im.alpha_composite(foamimg,(int(w*.065),h-70))
    # Re-apply rock over rear foam to keep coherent shoreline
    im.alpha_composite(src,(x,y))
    return im

def island_arch():
    w,h=600,370
    im,d=canvas(w,h)
    for rockid,x,y,size in [("E004",76,154,(250,200)),("E005",351,157,(192,205))]:
        src=load_src("environment",rockid)
        src.thumbnail(size,Image.Resampling.LANCZOS)
        im.alpha_composite(src,(x,y))
    bridge=load_src("architecture","A005")
    bridge.thumbnail((390,240),Image.Resampling.LANCZOS)
    im.alpha_composite(bridge,((w-bridge.width)//2,48))
    splash=foam().resize((425,70),Image.Resampling.NEAREST)
    im.alpha_composite(splash,(90,297))
    return im

def clouds():
    w,h=1024,272
    im,d=canvas(w,h)
    grad(d,w,h,(58,162,251),(154,222,255))
    rng=random.Random(84)
    for cx,cy,sz in [(105,75,58),(350,48,48),(610,91,73),(854,58,65),(1005,130,49)]:
        for ring,col in [(1.04,(109,189,236,255)),(0.98,(235,248,253,255))]:
            for dx,dy,r in [(-.75,.14,.61),(-.25,-.17,.77),(.31,-.16,.66),(.74,.14,.53),(.03,.35,.72)]:
                rr=int(sz*r*ring);x=int(cx+dx*sz);y=int(cy+dy*sz)
                d.ellipse((x-rr,y-rr,x+rr,y+rr),fill=col)
        for _ in range(70):
            x=int(rng.gauss(cx,sz*.53));y=int(rng.gauss(cy,sz*.41))
            if 0<=x<w and 0<=y<h:
                d.rectangle((x,y,x+rng.randint(2,8),y+2),fill=(255,255,244,255))
    return im

def recolor(im,what):
    rgba=im.convert("RGBA")
    data=[]
    for r,g,b,a in rgba.getdata():
        if what=="rug" and b>r*1.1 and b>g*1.05:
            data.append((int(r*.63),min(255,int(g*1.26)),int(b*.89),a))
        elif what=="book" and b>r*.78:
            data.append((min(200,int(r*.84+55)),int(g*.63+33),int(b*.46+23),a))
        elif what=="wood":
            data.append((min(235,int(r*.99+9)),min(202,int(g*.77+20)),int(b*.52+22),a))
        else:data.append((r,g,b,a))
    out=Image.new("RGBA",rgba.size)
    out.putdata(data)
    return out

def blanket():
    src=load_src("furniture","P001")
    w,h=src.size
    return src.crop((int(w*.22),int(h*.28),int(w*.85),int(h*.78)))

def pillow():
    src=load_src("furniture","P001");w,h=src.size
    part=src.crop((int(w*.25),int(h*.07),int(w*.80),int(h*.33)))
    return part

def bedframe():
    src=load_src("furniture","P001");w,h=src.size
    # base/headboard are detailed source art; cover blanket area with alpha to
    # isolate the frame as an independent foreground-capable decorative asset.
    out=src.copy()
    mask=Image.new("L",(w,h),255);m=ImageDraw.Draw(mask)
    m.rounded_rectangle((int(w*.19),int(h*.24),int(w*.85),int(h*.77)),
                        radius=17,fill=0)
    out.putalpha(ImageChops.multiply(out.getchannel("A"),mask))
    return out

def bench():
    w,h=320,186;im,d=canvas(w,h)
    poly=[(37,70),(271,70),(309,102),(75,111)]
    polygon(d,[(55,105),(88,121),(91,166),(76,172),(64,138)],(105,61,35,255),(60,40,31,255),3)
    polygon(d,[(246,101),(271,98),(279,159),(263,170),(248,139)],(117,66,38,255),(63,39,30,255),3)
    polygon(d,[(29,65),(258,56),(306,94),(72,105)],(134,76,43,255),(66,43,31,255),4)
    polygon(d,[(38,64),(251,56),(284,78),(74,89)],(168,95,49,255))
    for k in range(4):
        y=66+k*8
        line(d,[(45,y),(261,y-7)],(86,50,31,215),2)
        line(d,[(58,y-3),(191,y-7)],(205,130,67,255),2)
    for x in (88,252):
        line(d,[(x,120),(x,156)],(206,135,68,255),3)
    noise_on_layer(im,44,500,[(216,146,72,165),(75,44,31,130)],(38,56,285,99),2)
    return im

def cabinet():
    base=load_src("furniture","P014")
    w,h=base.size
    im=base.copy();d=ImageDraw.Draw(im)
    # retain the original rich shelf frame, overlay hinged blue-gold doors
    inset=(int(w*.16),int(h*.30),int(w*.84),int(h*.87))
    d.rectangle(inset,fill=(83,47,30,243),outline=(39,29,27,255),width=6)
    middle=(inset[0]+inset[2])//2
    for x1,x2 in [(inset[0]+5,middle-3),(middle+3,inset[2]-4)]:
        polygon(d,[(x1,inset[1]+5),(x2,inset[1]+5),
                   (x2,inset[3]-6),(x1,inset[3]-6)],
                (126,73,39,255),(217,149,65,255),3)
        line(d,[(x1+8,inset[1]+12),(x2-8,inset[1]+12)],(214,141,61,255),3)
        line(d,[(x1+7,inset[3]-16),(x2-8,inset[3]-16)],(58,42,32,255),3)
        d.ellipse((middle-12 if x1<middle else middle+8,
                   int(h*.58),middle-7 if x1<middle else middle+13,
                   int(h*.58)+6),fill=GOLD)
    return im

def chest_open():
    src=load_src("furniture","P017");w,h=src.size
    im,d=canvas(w,h+73)
    lid=src.crop((0,0,w,int(h*.46)))
    base=src.crop((0,int(h*.37),w,h))
    im.alpha_composite(base,(0,83))
    polygon(d,[(24,93),(w-24,84),(w-18,118),(25,122)],(26,17,27,255),(206,133,52,255),4)
    polygon(d,[(42,101),(w-38,97),(w-43,112),(43,114)],(12,9,19,255))
    im.alpha_composite(lid,(0,9))
    line(d,[(34,85),(w-29,79)],GOLD,4)
    return im

def wooden_box():
    src=load_src("furniture","P020")
    return recolor(src,"wood")

def storage():
    src=load_src("furniture","P017")
    big=src.resize((int(src.width*1.28),int(src.height*1.10)),Image.Resampling.NEAREST)
    d=ImageDraw.Draw(big)
    for x in (36,big.width//2,big.width-31):
        line(d,[(x,21),(x-4,big.height-22)],(211,164,82,230),5)
    return big

def apple(green=False):
    im,d=canvas(104,108)
    main=(106,184,61,255) if green else (218,47,42,255)
    dark=(46,110,49,255) if green else (117,24,32,255)
    light=(187,239,117,255) if green else (255,143,92,255)
    polygon(d,[(52,36),(35,27),(20,33),(11,50),(12,75),(26,94),
          (43,102),(56,99),(74,101),(90,84),(92,54),(80,32),(65,29)],dark)
    polygon(d,[(18,47),(33,35),(48,41),(61,39),(76,36),(85,51),
        (84,76),(69,91),(55,89),(40,95),(23,82)],main)
    d.ellipse((20,42,40,68),fill=light)
    d.ellipse((27,43,39,57),fill=(255,239,201,230))
    line(d,[(52,39),(54,23),(60,10)],(79,54,29,255),4)
    polygon(d,[(55,25),(70,13),(84,20),(68,29)],(50,133,60,255),(31,78,42,255),2)
    line(d,[(59,19),(72,20)],(155,218,87,255),2)
    noise_on_layer(im,127 if green else 67,130,[(246,219,99,80),(39,78,41,60)],(28,40,79,87),1)
    return im

def scroll_bundle():
    scroll=load_src("objects","O011")
    scroll.thumbnail((135,105),Image.Resampling.LANCZOS)
    im,d=canvas(270,165)
    for idx,(xx,yy,angle) in enumerate([(11,42,20),(62,20,-13),(100,47,9)]):
        piece=scroll.rotate(angle,expand=True,resample=Image.Resampling.NEAREST)
        im.alpha_composite(piece,(xx,yy))
    line(d,[(111,32),(121,125)],(145,92,37,255),5)
    line(d,[(105,34),(115,126)],GOLD,2)
    return im

def rolled_map():
    src=load_src("objects","O011")
    src=src.rotate(16,expand=True,resample=Image.Resampling.BICUBIC)
    d=ImageDraw.Draw(src)
    d.arc((int(src.width*.25),int(src.height*.18),int(src.width*.70),
           int(src.height*.85)),25,250,fill=(193,153,77,240),width=4)
    return src

def book_open():
    im,d=canvas(230,163)
    polygon(d,[(17,60),(55,42),(111,61),(168,42),(213,55),
               (215,127),(152,128),(115,143),(65,124),(16,136)],
            (65,43,35,255),(31,23,29,255),4)
    polygon(d,[(28,54),(57,38),(111,56),(111,128),(57,113),(28,124)],
            (244,224,173,255),(148,111,72,255),3)
    polygon(d,[(118,56),(173,38),(207,51),(206,118),(166,112),(118,129)],
            (241,217,163,255),(148,111,72,255),3)
    polygon(d,[(107,60),(114,68),(118,58),(118,136),(111,140),(108,133)],
            (176,133,78,255))
    for k in range(6):
        line(d,[(42,65+k*8),(64,60+k*8),(96,68+k*8)],(169,138,102,190),2)
        line(d,[(133,68+k*8),(162,58+k*8),(197,65+k*8)],(173,138,101,175),2)
    polygon(d,[(148,60),(154,63),(151,106),(145,108)],(25,86,145,200))
    return im

def compass():
    im,d=canvas(210,210);cx=cy=105
    d.ellipse((18,18,192,192),fill=(111,67,32,255),outline=GOLD,width=8)
    d.ellipse((29,29,181,181),fill=(13,58,129,255),outline=(251,213,113,255),width=5)
    for deg in range(0,360,15):
        a=math.radians(deg)
        outer=(cx+73*math.cos(a),cy+73*math.sin(a))
        inner=(cx+(56 if deg%45 else 47)*math.cos(a),
               cy+(56 if deg%45 else 47)*math.sin(a))
        line(d,[inner,outer],GOLD,2)
    for deg in range(0,360,45):
        a=math.radians(deg)
        r=60 if deg%90==0 else 48
        bx=math.cos(a+math.pi/2)*10;by=math.sin(a+math.pi/2)*10
        polygon(d,[(cx+bx,cy+by),(cx+r*math.cos(a),cy+r*math.sin(a)),
                   (cx-bx,cy-by),(cx,cy)],GOLD,(99,62,32,255),2)
    d.ellipse((94,94,116,116),fill=(254,229,149,255),outline=(119,75,36,255),width=3)
    return im

def banner_anchor():
    src=load_src("decor","D001")
    im=src.copy();d=ImageDraw.Draw(im)
    w,h=im.size;cx=w//2;cy=int(h*.53)
    # The exact source banner textile is preserved; new nautical golden anchor stitched over emblem.
    line(d,[(cx,cy-35),(cx,cy+40)],(24,48,111,255),8)
    line(d,[(cx,cy-35),(cx,cy+40)],GOLD,4)
    d.ellipse((cx-9,cy-48,cx+9,cy-30),outline=GOLD,width=5)
    line(d,[(cx-29,cy+11),(cx+29,cy+11)],GOLD,5)
    d.arc((cx-41,cy+7,cx+41,cy+58),2,179,fill=GOLD,width=6)
    line(d,[(cx-35,cy+27),(cx-24,cy+39)],GOLD,5)
    line(d,[(cx+35,cy+27),(cx+24,cy+39)],GOLD,5)
    return im

def make(id):
    if id.startswith("ST"):
        return stone_stair(int(id[2:]))
    if id=="E009":return foam()
    if id=="E010":return water_base()
    if id in ("E011","E012","E013","E014"):return waves(int(id[1:])-11)
    if id in ("E015","E016"):return island(id)
    if id=="E017":return island_arch()
    if id=="E018":return clouds()
    if id=="P002":return blanket()
    if id=="P003":return pillow()
    if id=="P004":return bedframe()
    if id=="P006":return recolor(load_src("furniture","P005"),"rug")
    if id=="P013":return bench()
    if id=="P016":return cabinet()
    if id=="P018":return chest_open()
    if id=="P021":return wooden_box()
    if id=="P022":return storage()
    if id=="O007":return apple()
    if id=="O008":return apple(True)
    if id=="O010":return rolled_map()
    if id=="O012":return scroll_bundle()
    if id=="O014":return recolor(load_src("objects","O013"),"book")
    if id=="O015":return book_open()
    if id=="O020":return compass()
    if id=="D005":return banner_anchor()
    raise ValueError("Unknown missing ID: "+id)

def main():
    data=json.loads(INDEX.read_text(encoding="utf-8"))
    catalog={a["id"]:a for a in data["assets"]}
    load_src.catalog=catalog
    created=[]
    for a in data["assets"]:
        path=ROOT/a["texture_path"].removeprefix("res://")
        if path.is_file():
            continue
        id=a["id"]
        image=make(id)
        if image.mode!="RGBA":image=image.convert("RGBA")
        if image.width<40 or image.height<40:
            raise RuntimeError("Suspiciously small generated asset: "+id)
        path.parent.mkdir(parents=True,exist_ok=True)
        image.save(path,optimize=True)
        a["pixel_size"]=list(image.size)
        a["status"]="needs_cleanup"
        a["origin"]=[0,0] if id in ("E010","E011","E012","E013","E014","E018","ST006") else [image.width//2,image.height]
        a["source"]={"kind":"original_procedural_or_derived_sprite","generator":"tools/generate_remaining_art.py","reference_style":"hero_room_seaside_pixel_art"}
        a["qa_notes"]="First-pass art; manual visual QA needed for quality, transparent cropping, anchors and consistency."
        if id in ("E010","E011","E012","E013","E014"):
            a["origin"]=[0,0]
            a["tags"]=list(dict.fromkeys(a.get("tags",[])+["ocean","seamless_256","wave_cycle"]))
            a["animation_frames"]=1
            a["frame_group"]="ocean_wave_4" if id!="E010" else "ocean_base"
        if id in ("E010","E018"):
            a["qa_notes"]="Opaque reusable background artwork; verify visual quality with Hero Room, not a transparent object."
        if id.startswith("P") and id not in ("P002","P003","P004","P006"):
            a["collision"]={"enabled":True,"size":[max(30,int(image.width*.48)),max(16,int(image.height*.14))],
                            "offset":[0,-max(8,int(image.height*.06))]}
            a["shadow"]={"type":"contact_medium","opacity":0.36,"offset_x":4,"offset_y":-3}
        created.append(id)
    count=sum((ROOT/a["texture_path"].removeprefix("res://")).is_file() for a in data["assets"])
    data["extracted_count"]=count
    data["generated_png_count"]=count
    data["status_note"]="PNG presence completed; all 218 assets need visual review. No new image was automatically approved."
    INDEX.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    with CSV.open("w",newline="",encoding="utf-8") as f:
        writer=csv.writer(f,lineterminator="\n");writer.writerow(["id","category","name","status","texture_path"])
        writer.writerows((a["id"],a["category"],a["name"],a["status"],a["texture_path"]) for a in data["assets"])
    print(json.dumps({"new_count":len(created),"new_ids":created,"total_present":count},indent=2))
    if len(created)!=31 or count!=218:
        raise RuntimeError("Unexpected asset counts - investigate before commit")

if __name__=="__main__":
    from PIL import ImageChops
    main()
