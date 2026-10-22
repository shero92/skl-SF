#!/usr/bin/env python3
"""Godot 4 starter PNG renderer. Creates transparent RGBA artwork without dependencies.
Procedural floors/UI are first-pass drafts, not extracted or production-approved image art.
Existing PNGs are never overwritten."""
import json, struct, zlib, random, math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/'map_factory/metadata/asset_index.json'

def png(path,w,h,pixels):
    raw=b''.join(b'\x00'+bytes(pixels[y*w*4:(y+1)*w*4]) for y in range(h))
    def ch(t,v):return struct.pack('>I',len(v))+t+v+struct.pack('>I',zlib.crc32(t+v)&0xffffffff)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>2I5B',w,h,8,6,0,0,0))+ch(b'IDAT',zlib.compress(raw,9))+ch(b'IEND',b''))

def image(w,h):
    data=bytearray(4*w*h)
    def put(x,y,r,g,b,a=255):
        if 0<=x<w and 0<=y<h:data[(y*w+x)*4:(y*w+x)*4+4]=bytes((r,g,b,a))
    def line(x,y,x2,y2,c):
        steps=max(1,round(max(abs(x2-x),abs(y2-y))))
        for i in range(steps+1):put(round(x+(x2-x)*i/steps),round(y+(y2-y)*i/steps),*c)
    def rect(x,y,x2,y2,c):
        for yy in range(max(0,y),min(h,y2+1)):
            for xx in range(max(0,x),min(w,x2+1)):put(xx,yy,*c)
    return data,put,line,rect

def floor(n):
    w=h=64;data,dot,line,rect=image(w,h)
    rng=random.Random(n*1247+71)
    colors=[(207,159,98),(221,176,113),(232,190,129),(242,201,142),(251,220,166),(178,136,88),(133,98,68)]
    for y in range(h):
        for x in range(w):
            k=min(6,int(rng.random()*6.5));dot(x,y,*colors[k])
    for _ in range(100):
        x=rng.randrange(w);y=rng.randrange(h);dot(x,y,*rng.choice([(255,236,185),(148,109,72),(243,189,114)]))
    for i in range(64):
        dot(i,0,144,104,70);dot(i,63,129,95,68)
        dot(0,i,164,114,66);dot(63,i,126,94,68)
    if n in (2,3,5):
        for (x,y),(xx,yy) in zip([(8,14),(22,30),(38,27),(51,48)],[(22,30),(38,27),(51,48),(57,55)]):line(x,y,xx,yy,(116,84,57))
    if 6<=n<=13:
        nedge=n in (6,10,11);sedge=n in (7,12,13);wedge=n in (9,10,12);eedge=n in (8,11,13)
        for y in range(h):
            for x in range(w):
                if (nedge and y<5) or (sedge and y>58) or (wedge and x<5) or (eedge and x>58):dot(x,y,123,86,56)
    if n>=14:
        for ang in range(0,360,3):
            a=math.radians(ang);dot(round(32+25*math.cos(a)),round(32+25*math.sin(a)),10,66,155)
        for a in range(0,360,45):
            rad=math.radians(a);line(32,32,round(32+22*math.cos(rad)),round(32+22*math.sin(rad)),(238,182,49))
        line(32,5,32,59,(14,78,172));line(5,32,59,32,(14,78,172))
        rect(29,29,34,34,(241,185,66))
    return w,h,data

def shadow(n):
    w,h=164,80;data,put,_,_=image(w,h)
    dims=[(15,6),(26,9),(46,13),(26,11),(62,18),(47,14),(19,9),(68,15),(34,10),(23,10),(32,14),(68,19),(74,9),(46,16),(72,11),(61,21)]
    rx,ry=dims[n-1]
    for y in range(h):
        for x in range(w):
            dx=x-w/2-(12 if n in (12,16) else 0);dy=y-h/2
            if n in (11,12,16):dx-=dy*.7
            alpha=max(0,min(126,round(112*math.exp(-2.35*((dx/rx)**2+(dy/ry)**2)))))
            put(x,y,9,19,42,alpha)
    return w,h,data

def ui(n):
    sizes={1:(512,144),2:(300,96),3:(235,56),4:(132,160),5:(64,64),6:(250,60),9:(64,64),10:(64,64),11:(340,80),12:(64,64)}
    w,h=sizes[n];data,put,line,rect=image(w,h)
    gold=(242,182,62);pale=(255,233,159);navy=(8,28,75)
    if n in (1,2,3,4,6,11):
        rect(1,1,w-2,h-2,(16,13,27));rect(4,4,w-5,h-5,gold)
        rect(7,7,w-8,h-8,navy);rect(12,12,w-13,h-13,(16,50,107))
        line(12,12,w-13,12,pale)
        for x,y,sx,sy in [(8,8,1,1),(w-9,8,-1,1),(8,h-9,1,-1),(w-9,h-9,-1,-1)]:
            line(x,y,x+15*sx,y,gold);line(x,y,x,y+15*sy,gold)
            put(x+4*sx,y+4*sy,*pale)
    elif n==5:
        for y in range(16,44):
            for x in range(13,52):
                if abs(x-32)*.9+abs(y-20)*1.5<24:put(x,y,*gold)
    elif n==9:
        for y in range(5,59):
            for x in range(5,59):
                t=(x-32)**2+(y-32)**2
                if 310<t<680:put(x,y,*gold)
                elif t<=310:put(x,y,*navy)
        rect(29,17,34,45,pale)
    elif n==10:
        rect(10,8,53,54,gold);rect(13,11,50,51,navy)
        line(25,21,25,41,pale);line(25,21,36,21,pale);line(25,31,34,31,pale);line(25,41,36,41,pale)
    elif n==12:
        for x in range(8,56):
            for y in range(8,56):
                if abs(x-32)+abs(y-32)<23 and (abs(x-32)<4 or abs(y-32)<4):put(x,y,*gold)
    return w,h,data

def main():
    obj=json.loads(INDEX.read_text());created=0
    for a in obj['assets']:
        aid=a['id'];cat=a['category'];n=int(''.join(c for c in aid if c.isdigit()))
        if cat=='floors':fn=floor
        elif cat=='shadows':fn=shadow
        elif cat=='ui' and n not in (7,8):fn=ui
        else:continue
        path=ROOT/a['texture_path'].replace('res://','')
        if not path.is_file():
            w,h,pixels=fn(n);png(path,w,h,pixels);created+=1
        a['pixel_size']=[w,h] if 'w' in locals() else a['pixel_size']
        a['status']='ready' if cat=='shadows' else 'needs_cleanup'
        a['source']='procedural_starter_v1'
    obj['note']='Generated floor/UI drafts need art QA; PNGs are real independent textures. Unprocessed items remain planned.'
    INDEX.write_text(json.dumps(obj,indent=2)+'\n')
    print('Created',created,'new PNGs')
if __name__=='__main__':main()
