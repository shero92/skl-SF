#!/usr/bin/env python3
"""Build independent reusable missing environmental sprites for Hero Room.

A non-destructive first pass made from existing maritime art components and
custom pixel skull/antler drawing. Not a claim of exact reference fidelity.
Creates real transparent RGBA PNGs and full production metadata; no characters.
"""
from __future__ import annotations
import json, math, random, hashlib
from copy import deepcopy
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/"map_factory/metadata/asset_index.json"
rng=random.Random(771612)
record=json.loads(INDEX.read_text(encoding="utf-8"))
catalog={a["id"]:a for a in record["assets"]}

def sprite(id):
    item=catalog[id]
    path=ROOT/item["texture_path"].removeprefix("res://")
    im=Image.open(path).convert("RGBA")
    if im.getchannel("A").getbbox() is None:
        raise ValueError("Source sprite transparent: "+id)
    return im

def add(canvas,id,x,y,w=None,h=None,mirror=False):
    image=sprite(id)
    if w is not None:
        scale=w/image.width
        image=image.resize((round(w),round(h or image.height*scale)),Image.Resampling.LANCZOS)
    if mirror:
        image=image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    canvas.alpha_composite(image,(round(x),round(y)))

def irregular_segment(width=340,height=248,right=False):
    canvas=Image.new("RGBA",(width,height))
    # Multiple existing cliffside stones provide genuine photo-consistent art.
    add(canvas,"E007",12,43,188)
    add(canvas,"E008",154,66,185,mirror=True)
    add(canvas,"W017",36,42,175)
    add(canvas,"ST010",186,68,115,mirror=True)
    add(canvas,"W012",90,22,126)
    add(canvas,"V023",18,38,112)
    add(canvas,"V004",120,13,151)
    add(canvas,"V012",192,17,62)
    add(canvas,"V011",46,49,76)
    add(canvas,"V013",240,64,75)
    if right:
        canvas=canvas.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    return canvas

def deep_corner():
    canvas=Image.new("RGBA",(246,238))
    add(canvas,"E006",20,64,206)
    add(canvas,"W008",18,32,115)
    add(canvas,"W017",114,37,122)
    add(canvas,"ST011",145,39,63)
    add(canvas,"W012",48,22,147)
    add(canvas,"V006",2,17,107)
    add(canvas,"V012",168,36,71)
    add(canvas,"V023",54,124,93)
    return canvas

def daisy(draw,x,y,r=7):
    for a in range(8):
        theta=a*math.pi/4
        px=round(x+r*.73*math.cos(theta));py=round(y+r*.73*math.sin(theta))
        draw.ellipse((px-3,py-2,px+3,py+2),fill=(247,245,224,255))
        draw.point((px-1,py-1),fill=(255,255,255,255))
    draw.ellipse((x-3,y-3,x+3,y+3),fill=(238,173,39,255))
    draw.point((x-1,y-1),fill=(255,243,105,255))

def antler(draw,coords,width=7):
    # Dark engraved brown silhouette with ochre edge and pale reflection.
    draw.line(coords,fill=(67,41,23,255),width=width+5,joint="curve")
    draw.line(coords,fill=(134,79,35,255),width=width,joint="curve")
    light=[(a+1,b-1) for a,b in coords]
    draw.line(light,fill=(216,148,67,255),width=max(1,width//3),joint="curve")

def shrine():
    im=Image.new("RGBA",(268,276))
    # Dense layered existing pixel foliage, no baked floor pixels.
    add(im,"V009",55,63,150)
    add(im,"V008",35,89,166)
    add(im,"V004",54,121,190)
    add(im,"V005",28,158,194)
    add(im,"V010",86,172,115)
    back=Image.new("RGBA",im.size);d=ImageDraw.Draw(back)
    for base,branches in [
        ([(125,112),(102,79),(78,59),(54,56),(43,35)],[
            [(80,61),(71,42),(74,23)],[(61,57),(49,48),(45,22)],
            [(102,78),(97,55),(104,41)],[(54,55),(27,44),(19,26)]]),
        ([(150,112),(168,76),(191,56),(207,50),(225,27)],[
            [(183,62),(178,39),(184,24)],[(205,52),(210,32),(204,17)],
            [(165,84),(168,61),(160,43)],[(212,47),(236,41),(246,24)]])
    ]:
        antler(d,base,7)
        for branch in branches:antler(d,branch,4)
    im=Image.alpha_composite(back,im)
    d=ImageDraw.Draw(im)
    # Veined skull outline, natural cream/burnished bone with large eye sockets.
    skull=[(116,91),(127,83),(146,84),(163,95),(166,116),(159,131),
           (158,147),(152,161),(141,166),(127,159),(120,151),(113,137),
           (108,119),(108,104)]
    d.polygon([(x+3,y+4) for x,y in skull],fill=(54,38,23,240))
    d.polygon(skull,fill=(245,230,187,255),outline=(83,58,35,255),width=4)
    d.polygon([(116,94),(129,88),(139,90),(132,111),(123,116),(115,110)],fill=(255,248,216,255))
    d.polygon([(142,90),(156,96),(160,111),(154,126),(145,119),(139,110)],fill=(222,195,144,255))
    d.polygon([(116,116),(129,121),(129,136),(119,134)],fill=(45,37,28,255),outline=(111,73,35,255))
    d.polygon([(145,122),(158,117),(153,137),(143,135)],fill=(43,38,29,255),outline=(104,66,36,255))
    d.polygon([(133,130),(129,147),(138,149),(141,143)],fill=(65,42,29,255))
    d.line([(117,139),(123,151),(143,156),(153,144)],fill=(108,69,38,255),width=3)
    for tx in (125,132,139,146):
        d.line((tx,152,tx-1,158),fill=(100,70,46,255),width=2)
    for a,b in [[(120,101),(117,108)],[(147,95),(152,104)],[(135,99),(133,111)]]:
        d.line([a,b],fill=(185,152,104,255),width=2)
    # Bark wreath and golden charms over the lower portion.
    for x,y in [(62,157),(76,174),(197,157),(204,179),(82,215),(185,211)]:
        d.line([(135,139),(x,y),(x+rng.randint(-7,7),min(y+19,263))],fill=(70,54,25,255),width=6)
        d.line([(134,137),(x-2,y-2)],fill=(156,98,35,255),width=2)
    # Pixel leaves and little white coastal flowers.
    for _ in range(170):
        a=rng.uniform(0,2*math.pi)
        rr=rng.uniform(63,107)
        x=round(136+math.cos(a)*rr)
        y=round(166+math.sin(a)*rr*.73)
        if not(8<x<260 and 58<y<270):continue
        col=rng.choice([(34,88,44,255),(40,110,47,255),(71,134,47,255),
                        (25,70,37,255),(134,147,50,255)])
        d.polygon([(x,y+5),(x+4,y-2),(x+9,y),(x+5,y+7)],fill=col)
    for x,y,size in [(64,123,6),(85,212,7),(179,174,6),(213,206,7),
                     (145,224,8),(45,192,7),(186,104,6),(109,249,6),
                     (219,164,6),(70,95,5),(201,237,6)]:
        daisy(d,x,y,size)
    # Tiny blue-and-gold nautical insignia hung on branches, no raster UI text.
    d.ellipse((131,176,148,193),fill=(232,170,37,255),outline=(79,48,23,255),width=3)
    d.line((139,172,139,196),fill=(35,90,156,255),width=2)
    d.line((127,184,152,184),fill=(35,90,156,255),width=2)
    return im

def sunlight_shadow():
    w,h=320,158
    gradient=Image.new("RGBA",(w,h));pix=gradient.load()
    for y in range(h):
        for x in range(w):
            # offset westward to mimic high-right light.
            q=((x-160)/136)**2+((y-75-(x-150)*.15)/43)**2
            intensity=max(0,1-q)
            alpha=round((intensity**1.8)*120)
            pix[x,y]=(37,30,22,alpha)
    return gradient.filter(ImageFilter.GaussianBlur(3.0))

def register(ident,name,category,subtype,im,origin,collision,shadow,tags,refs):
    if ident in catalog:
        # Never silently replace an existing artist-reviewed file.
        old=ROOT/catalog[ident]["texture_path"].removeprefix("res://")
        if not old.is_file():
            raise ValueError("Registered but missing image "+ident)
        return
    slug="_".join(x.capitalize() for x in name.split())
    dest=ROOT/"map_factory/parts"/category/(ident+"_"+slug+".png")
    dest.parent.mkdir(parents=True,exist_ok=True)
    im.save(dest,optimize=True)
    check=Image.open(dest)
    if check.mode!="RGBA" or check.getchannel("A").getextrema()[0]==255:
        raise ValueError("Generated sprite must retain transparent pixels: "+ident)
    sha=hashlib.sha256(dest.read_bytes()).hexdigest()
    row={
      "id":ident,"name":name,"category":category,"subtype":subtype,
      "texture_path":"res://"+dest.relative_to(ROOT).as_posix(),
      "status":"needs_cleanup","pixel_size":[im.width,im.height],
      "origin":origin,"collision":collision,"shadow":shadow,
      "tags":tags,"reusable":True,"y_sort":category not in ("shadows",),
      "source":{"kind":"procedural_pixel_art_and_registered_asset_composite",
          "tool":"tools/generate_missing_hero_art.py",
          "reused_asset_ids":refs,"sha256":sha,"approved":False},
      "qa_notes":"Independent genuine RGBA PNG, no room background. Artist/reference review required; do not claim exact original fidelity."
    }
    record["assets"].append(row)
    catalog[ident]=row
    print("Generated",ident,im.size,len(dest.read_bytes()),dest.relative_to(ROOT))

def main():
    register("O027","Antlered Skull Flower Shrine","objects","floral_skull_relic",
        shrine(),[134,266],
        {"enabled":True,"size":[86,44],"offset":[0,-25]},
        {"type":"directional_sun","opacity":0.40,"offset_x":-28,"offset_y":21},
        ["hero_room","relic","skull","antlers","ivy","white_flowers","signature_prop"],
        ["V009","V008","V004","V005","V010"])
    register("E019","Sea Cliff Ruin Edge Left","environment","cliff_wall_apron",
        irregular_segment(),[170,242],
        {"enabled":True,"size":[220,44],"offset":[0,-31]},
        {"type":"wall_base","opacity":0.28,"offset_x":12,"offset_y":12},
        ["limestone","sea_cliff","parapet","wildflowers"],["E007","E008","W017","ST010","W012","V023","V004","V012","V011","V013"])
    register("E020","Sea Cliff Ruin Edge Right","environment","cliff_wall_apron",
        irregular_segment(right=True),[170,242],
        {"enabled":True,"size":[220,44],"offset":[0,-31]},
        {"type":"wall_base","opacity":0.28,"offset_x":12,"offset_y":12},
        ["limestone","sea_cliff","parapet","wildflowers"],["E007","E008","W017","ST010","W012","V023","V004","V012","V011","V013"])
    register("W019","Deep Limestone Parapet Corner","walls","ruin_wall_corner_deep",
        deep_corner(),[123,235],
        {"enabled":True,"size":[126,42],"offset":[0,-28]},
        {"type":"wall_corner","opacity":0.32,"offset_x":7,"offset_y":9},
        ["stone","ruins","corner","ivy","flowers"],["E006","W008","W017","ST011","W012","V006","V012","V023"])
    register("S017","Directional Sun Cast Shadow","shadows","diagonal_soft_cast",
        sunlight_shadow(),[160,80],
        {"enabled":False,"size":[1,1],"offset":[0,0]},
        {"type":"none","opacity":0.25,"offset_x":0,"offset_y":0},
        ["shadow","environment","sunlight"],[])
    record["assets"].sort(key=lambda a:(a["category"],a["id"]))
    record["asset_count"]=len(record["assets"])
    record["generated_png_count"]=sum((ROOT/a["texture_path"].removeprefix("res://")).exists() for a in record["assets"])
    record["extracted_count"]=record["generated_png_count"]
    INDEX.write_text(json.dumps(record,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

if __name__=="__main__":
    main()
