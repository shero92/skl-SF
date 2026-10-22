#!/usr/bin/env python3
"""Original transparent pixel-art sprite strips for the playable starter room.
All images are drafts needing visual QA, never auto-promote to ready.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import json, csv
ROOT=Path(__file__).resolve().parents[1]
IX=ROOT/'map_factory/metadata/asset_index.json'
CS=ROOT/'map_factory/metadata/production_queue.csv'
I='#17213b'; G='#f5c45b'; B='#185d9d'; L='#35a3c8'
H='#854a2d'; HS='#c0793c'; S='#f5c48f'; SD='#cb8b6b'
W='#e2e9ee'; D='#223259'; V='#2c764c'; VL='#80be75'
F=(72,96)
def poly(d,p,c,outline=I):
    d.polygon(p,fill=c)
    if outline:d.line(p+[p[0]],fill=outline,width=2)
def box(d,xy,c):d.rectangle(xy,fill=c)
def ell(d,xy,c,outline=I):d.ellipse(xy,fill=c,outline=outline,width=2)
def ln(d,p,c,w=2):d.line(p,fill=c,width=w)
def human(kind,view,step,walking=False):
    im=Image.new('RGBA',F);d=ImageDraw.Draw(im);x=36
    bob=([0,-1,0,1][step%4] if walking else [0,-1][step%2]);y=bob
    leg=([-4,4,-4,4][step%4] if walking else 0)
    fairy=kind=='fairy';back=view=='up';side=view in ('left','right')
    if fairy:
        poly(d,[(25,47+y),(8,30+y),(10,60+y),(27,70+y)],'#a4efd3','#299a8c')
        poly(d,[(45,46+y),(64,29+y),(61,61+y),(46,69+y)],'#a4efd3','#299a8c')
        ln(d,[(25,52+y),(12,39+y)],'#defad9')
        ln(d,[(45,52+y),(59,40+y)],'#defad9')
    else:
        poly(d,[(23,48+y),(49,48+y),(58,79+y),(40,72+y),(17,85+y),(15,60+y)],'#14214a')
        poly(d,[(20,52+y),(16,75+y),(18,81+y),(24,66+y)],'#2a84a3',None)
    for xx,change in [(28,leg),(44,-leg)]:
        poly(d,[(xx-4,68+y),(xx+5,68+y),(xx+change+5,86+y),(xx+change-5,86+y)],'#734b35')
        poly(d,[(xx+change-5,84+y),(xx+change+7,84+y),(xx+change+8,90+y),(xx+change-7,90+y)],'#293a5b')
        box(d,(xx+change-3,85+y,xx+change+5,86+y),G)
    poly(d,[(23,47+y),(49,47+y),(52,68+y),(48,76+y),(22,76+y),(19,67+y)],'#f0e9d6' if fairy else B)
    for xx in (21,51):
        poly(d,[(xx-3,50+y),(xx+2,48+y),(xx+6,67+y),(xx,72+y)],S if fairy else '#bb884d')
        box(d,(xx,63+y,xx+3,67+y),G)
    if fairy:
        poly(d,[(25,60+y),(47,60+y),(54,80+y),(43,76+y),(35,83+y),(28,76+y),(17,80+y)],'#257450')
        for xx in (25,36,47):ln(d,[(xx,65+y),(xx-2,76+y)],G)
        ln(d,[(29,51+y),(45,67+y)],G)
    else:
        poly(d,[(26,51+y),(44,51+y),(45,68+y),(25,68+y)],'#267db7',None)
        ln(d,[(23,61+y),(49,61+y)],G)
        ln(d,[(30,57+y),(41,67+y)],G)
        ln(d,[(41,57+y),(30,67+y)],G)
        box(d,(33,58+y,38,61+y),'#fbe7a3')
        ln(d,[(23,73+y),(48,73+y)],G,3)
    if not back:
        ell(d,(24,23+y,49,49+y),S)
        if side:
            ex=42 if view=='right' else 27
            box(d,(ex-2,36+y,ex+2,40+y),D)
            box(d,(ex-1,36+y,ex,37+y),L)
        else:
            for ex in (30,42):
                box(d,(ex-2,36+y,ex+2,40+y),D)
                box(d,(ex-1,36+y,ex,37+y),'#7cd8ff')
                ln(d,[(ex-3,34+y),(ex+2,34+y)],H if not fairy else V)
            box(d,(35,44+y,38,45+y),SD)
        if fairy:
            poly(d,[(24,37+y),(19,35+y),(25,44+y)],S)
            poly(d,[(49,37+y),(55,35+y),(49,44+y)],S)
    hc=V if fairy else H;hi=VL if fairy else HS
    poly(d,[(21,34+y),(20,22+y),(27,15+y),(34,18+y),
      (39,11+y),(45,18+y),(49,16+y),(53,27+y),
      (49,47+y),(45,41+y),(46,31+y),(27,30+y),(26,48+y),(20,46+y)],hc)
    for p in [[(23,30+y),(27,21+y),(32,29+y)],
       [(31,24+y),(40,15+y),(42,29+y)],
       [(42,25+y),(49,22+y),(48,34+y)]]:
        ln(d,p,hi,2)
    if fairy:
        for xx,yy in [(29,20+y),(45,24+y)]:
            ell(d,(xx-3,yy-3,xx+3,yy+3),'#ffede7',None)
            box(d,(xx,yy,xx+1,yy+1),G)
        ln(d,[(51,73+y),(57,39+y)],H,3)
        ell(d,(52,35+y,61,44+y),G)
    else:
        # side sword with metallic edge, a compass bearing on the hilt
        xx=18 if view=='right' else 55
        poly(d,[(xx-2,69+y),(xx+4,70+y),(xx+3,88+y),(xx-3,93+y)],W)
        ln(d,[(xx,73+y),(xx,87+y)],'#61b6c7',1)
        ln(d,[(xx-7,69+y),(xx+8,70+y)],G,3)
        box(d,(xx-2,64+y,xx+2,69+y),'#b5833d')
    return im.resize((144,192),Image.Resampling.NEAREST)
def creature(step,walk):
    im=Image.new('RGBA',F);d=ImageDraw.Draw(im)
    y=([0,-2,0,1][step%4] if walk else [0,-1][step%2])
    poly(d,[(21,63+y),(8,60+y),(14,75+y),(25,77+y)],'#2071b2')
    ell(d,(19,52+y,56,82+y),'#2fa1cf')
    for xx,yy in [(21,47),(29,40),(38,42)]:
        poly(d,[(xx-7,yy+y),(xx,yy-14+y),(xx+8,yy+y)],'#34bff0')
        ln(d,[(xx,yy-12+y),(xx,yy-3+y)],'#cdeeff')
    ell(d,(30,39+y,61,70+y),'#38acd9')
    ell(d,(42,54+y,61,72+y),'#f0dfae')
    ell(d,(46,49+y,58,62+y),'#fffbdf')
    ell(d,(49,51+y,55,59+y),D)
    box(d,(51,52+y,53,54+y),'#ffffff')
    for xx in (25,48):
        ell(d,(xx-6,77+y,xx+6,90+y),'#ebdcaf')
        box(d,(xx-3,87+y,xx+3,88+y),'#a6815b')
    ln(d,[(25,69+y),(35,77+y)],'#db6252',4)
    return im.resize((144,192),Image.Resampling.NEAREST)
def portrait(fairy):
    im=Image.new('RGBA',(136,160));d=ImageDraw.Draw(im)
    poly(d,[(4,160),(18,130),(43,118),(64,130),(85,118),(114,129),(136,160)],
         V if fairy else '#162e68')
    poly(d,[(22,157),(45,125),(67,153),(88,125),(112,156)],
         '#f1efda' if fairy else B)
    ln(d,[(18,153),(43,127),(63,153)],G,4)
    poly(d,[(55,103),(83,104),(86,132),(67,141),(53,130)],SD)
    ell(d,(30,51,106,119),S)
    if fairy:
        poly(d,[(34,95),(12,83),(33,112)],S)
        poly(d,[(99,96),(124,84),(102,112)],S)
    for x in (50,83):
        box(d,(x-5,85,x+8,97),'#fcf8e9')
        box(d,(x,86,x+6,98),'#248f83' if fairy else B)
        box(d,(x+2,88,x+5,95),D)
        box(d,(x+2,89,x+3,90),'#ffffff')
        ln(d,[(x-8,79),(x+7,77)],V if fairy else H,3)
    ln(d,[(68,95),(65,103),(72,106)],SD)
    ln(d,[(56,115),(68,118),(79,114)],'#a85856' if fairy else H,2)
    c=V if fairy else H;hi=VL if fairy else HS
    poly(d,[(19,95),(19,62),(25,42),(45,29),(59,19),(68,25),(83,19),
         (100,29),(116,49),(113,88),(99,76),(96,58),
         (76,62),(66,54),(51,67),(35,82),(28,110)],c)
    for pts in [[(25,67),(40,41),(54,50),(45,74)],
      [(48,46),(62,28),(71,51),(60,68)],
      [(77,43),(90,34),(107,55),(102,75)],
      [(28,84),(24,121),(30,133)]]:
        ln(d,pts,hi,4)
    if fairy:
        for x,y in [(37,39),(83,30),(102,56)]:
            for xx,yy in [(-5,0),(5,0),(0,-5),(0,5)]:
                ell(d,(x+xx-3,y+yy-3,x+xx+3,y+yy+3),'#ffffff',None)
            ell(d,(x-2,y-2,x+2,y+2),G,None)
    else:
        ln(d,[(17,135),(34,122),(51,138)],'#3a9bab',4)
    return im.resize((272,320),Image.Resampling.NEAREST)
CONFIG={
"CH001":("hero","down",False,2),"CH002":("hero","up",False,2),
"CH003":("hero","left",False,2),"CH004":("hero","right",False,2),
"CH005":("hero","down",True,4),"CH006":("hero","up",True,4),
"CH007":("hero","left",True,4),"CH008":("hero","right",True,4),
"CH009":("companion","down",False,2),"CH010":("companion","down",True,4),
"CH011":("fairy","down",False,2),"CH012":("fairy","down",True,4)}
def main():
    catalog=json.loads(IX.read_text(encoding='utf-8'))
    byid={a['id']:a for a in catalog['assets']}
    created=0
    for ident,(kind,view,walking,count) in CONFIG.items():
        a=byid[ident];path=ROOT/a['texture_path'].removeprefix('res://')
        if path.exists():continue
        sheet=Image.new('RGBA',(144*count,192))
        for f in range(count):
            sprite=creature(f,walking) if kind=='companion' else human(kind,view,f,walking)
            sheet.alpha_composite(sprite,(144*f,0))
        path.parent.mkdir(parents=True,exist_ok=True);sheet.save(path,optimize=True)
        a.update(status='needs_cleanup',pixel_size=list(sheet.size),
                 origin=[72,188],frame_size=[144,192],animation_frames=count,
                 fps=7 if walking else 2,y_sort=True,
                 shadow={'type':'character','opacity':0.4,'offset_x':0,'offset_y':-3},
                 source={'kind':'original_procedural_pixel_art','generator':'tools/generate_character_art.py'},
                 qa_notes='Transparent original pixel-art animation; visual QA pending.')
        created+=1
    for ident,is_fairy in [('UI007',False),('UI008',True)]:
        a=byid[ident];path=ROOT/a['texture_path'].removeprefix('res://')
        if path.exists():continue
        image=portrait(is_fairy);path.parent.mkdir(parents=True,exist_ok=True)
        image.save(path,optimize=True)
        a.update(status='needs_cleanup',pixel_size=list(image.size),
                 origin=[0,0],shadow={'type':'none'},source={'kind':'original_procedural_pixel_art','generator':'tools/generate_character_art.py'},
                 qa_notes='Transparent portrait; visual QA pending.')
        created+=1
    IX.write_text(json.dumps(catalog,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    with CS.open('w',newline='',encoding='utf-8') as f:
        writer=csv.writer(f);writer.writerow(['id','category','name','status','texture_path'])
        writer.writerows([a['id'],a['category'],a['name'],a['status'],a['texture_path']] for a in catalog['assets'])
    print('Created',created,'separate transparent PNG sprite/portrait files')
if __name__=='__main__':main()
