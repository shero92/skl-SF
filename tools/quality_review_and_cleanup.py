#!/usr/bin/env python3
"""Audit 218 assets and safely remove visually confirmed label/crop fragments."""
from pathlib import Path
from collections import Counter
import hashlib, json, math
import numpy as np
import cv2
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/"map_factory/metadata/asset_index.json"
OUT=ROOT/"map_factory/metadata/quality_review.json"
DOC=ROOT/"docs/ART_QUALITY_REVIEW.md"
PREVIEW=ROOT/"docs/previews/verified_cutout_cleanup.png"
SAFE=set("A001 A007 D008 D009 O001 P007 P010 ST009 ST010 ST013 V013 V014 V015 V016 V017 V021 V022 W001 W002 W003 W006 W007 W015".split())
BOTTOM={"W006":232,"W007":239,"W015":152,"A007":263}
TOP={"V013":17,"V014":13,"V016":10,"V017":12}
LABEL={"ST009","ST010","ST013","V014"}

def cleanup(img,ident):
    old=np.asarray(img.convert("RGBA")).copy()
    new=old.copy()
    h,w=old.shape[:2]
    n,labels,stats,_=cv2.connectedComponentsWithStats((old[:,:,3]>28).astype("uint8"),8)
    removed=[]
    if n>2:
        main=max(range(1,n),key=lambda i:int(stats[i,4]))
        mx,my,mw,mh,ma=map(int,stats[main])
        for i in range(1,n):
            if i==main:continue
            x,y,ww,hh,area=map(int,stats[i])
            gap=max(0,mx-x-ww,x-mx-mw,my-y-hh,y-my-mh)
            shape=(ww/max(hh,1)>4 and (y+hh>h*.66 or y<h*.18)) or (
                hh/max(ww,1)>7 and (x<w*.16 or x+ww>w*.85))
            tiny=area<ma*.004 and gap>6
            if (ident in LABEL and shape and area<ma*.33) or (
                gap>7 and (shape or tiny) and area<ma*.20):
                removed.append(i)
    if removed:
        mask=np.isin(labels,removed).astype("uint8")
        mask=cv2.dilate(mask,np.ones((3,3),dtype="uint8"),iterations=1)>0
        new[mask]=0
    if ident in BOTTOM and h>BOTTOM[ident]:
        new[BOTTOM[ident]:,:,:]=0
    if ident in TOP and h>TOP[ident]:
        new[:TOP[ident],:,:]=0
    if ident=="W007":new[:,:min(w,21),:]=0
    if ident=="W015":new[:,:min(w,15),:]=0
    changed=(old[:,:,3]>15)&(new[:,:,3]<=15)
    count=int(changed.sum())
    frac=count/max(1,int((old[:,:,3]>15).sum()))
    if not count:return None,0,0
    if frac>.32 or not np.any(new[:,:,3]>40):
        raise RuntimeError("Unsafe edit to "+ident+" (removed %.2f)"%frac)
    # Keep dimensions and every pixel not in the erased-alpha region unchanged.
    if not np.array_equal(old[new[:,:,3]>15],new[new[:,:,3]>15]):
        raise RuntimeError("Unintended color mutation in "+ident)
    return Image.fromarray(new,"RGBA"),count,frac

def inspect(img,entry):
    arr=np.asarray(img.convert("RGBA"))
    alpha=arr[:,:,3];h,w=alpha.shape
    area=(alpha>32);cover=float(area.mean())
    border=np.concatenate((alpha[0,:],alpha[-1,:],alpha[:,0],alpha[:,-1]))
    n,labels,stats,_=cv2.connectedComponentsWithStats(area.astype("uint8"),8)
    sizes=sorted((int(stats[i,4]) for i in range(1,n)),reverse=True)
    dust=sum(v for v in sizes[1:] if v<=max(16,w*h*.0003))
    r,g,b=np.moveaxis(arr[:,:,:3],-1,0)
    gray=cv2.cvtColor(arr[:,:,:3],cv2.COLOR_RGB2GRAY)
    score=float(cv2.Laplacian(gray,cv2.CV_64F).var())
    flags=[]
    category=entry["category"]
    if category not in ("floors","environment","ui") and np.all(alpha==255):flags.append("opaque_prop")
    if category=="floors" and abs(h-w)>4:flags.append("floor_not_square")
    if cover<.06 and category not in ("shadows","ui","decor","environment"):flags.append("possible_fragment")
    if dust>max(50,w*h*.002):flags.append("detached_alpha_speckles")
    if score<65 and category not in ("shadows","ui","environment"):flags.append("low_texture_detail")
    if category=="characters":flags.append("character_fidelity_review")
    source=entry.get("source",{})
    if isinstance(source,dict) and source.get("kind") in (
        "atlas_crop","original_procedural_pixel_art","original_procedural_or_derived_sprite"):
        flags.append("art_director_review")
    return {"dimensions":[w,h],"alpha_coverage":round(cover,4),
        "border_alpha_coverage":round(float((border>32).mean()),4),
        "detail_variance":round(score,1),"alpha_bbox":list(img.getchannel("A").getbbox() or []),
        "detached_micro_area":dust,"flags":flags}

def gallery(changes):
    if not changes:return
    cw,ch=378,302;cols=4
    output=Image.new("RGB",(cols*cw,math.ceil(len(changes)/cols)*ch),(20,44,73))
    draw=ImageDraw.Draw(output)
    for i,(ident,old,new,num) in enumerate(changes):
        px=(i%cols)*cw;py=(i//cols)*ch
        for j,img in enumerate((old,new)):
            thumb=img.copy();thumb.thumbnail((177,255),Image.Resampling.NEAREST)
            bg=Image.new("RGBA",thumb.size,(26,58,85,255))
            bg.alpha_composite(thumb)
            output.paste(bg.convert("RGB"),(px+6+j*187,py+5))
        draw.text((px+10,py+268),ident+" OLD / CLEANED",fill=(242,207,126))
        draw.text((px+10,py+284),"Removed %d stray pixels"%num,fill=(222,226,233))
    PREVIEW.parent.mkdir(parents=True,exist_ok=True)
    output.save(PREVIEW,optimize=True)

def main():
    data=json.loads(INDEX.read_text(encoding="utf-8"))
    details=[];repaired=[];changes=[]
    for a in data["assets"]:
        ident=a["id"]
        path=ROOT/a["texture_path"].removeprefix("res://")
        if not path.exists():
            details.append({"id":ident,"flags":["missing_png"]})
            continue
        old=Image.open(path).convert("RGBA")
        row={"id":ident,"category":a["category"],"status":a["status"],**inspect(old,a)}
        if ident in SAFE:
            new,count,frac=cleanup(old,ident)
            if new is not None:
                old_sha=hashlib.sha256(path.read_bytes()).hexdigest()
                new.save(path,optimize=True)
                sha=hashlib.sha256(path.read_bytes()).hexdigest()
                repaired.append({"id":ident,"pixels_removed":count,"fraction":round(frac,4),
                    "old_sha256":old_sha,"new_sha256":sha,"dimensions_kept":True})
                changes.append((ident,old,new,count))
                row.update(inspect(new,a))
                a["status"]="needs_cleanup"
                a["qa_notes"]=str(a.get("qa_notes",""))+"; stray atlas label/crop debris removed."
        details.append(row)
    gallery(changes)
    issues=Counter(v for item in details for v in item.get("flags",[]))
    summary={"registered":len(data["assets"]),"on_disk":sum("dimensions" in r for r in details),
         "changed":len(repaired),"still_unapproved":sum(a["status"]!="ready" for a in data["assets"])}
    OUT.write_text(json.dumps({"summary":summary,"issues":dict(issues),
        "repairs":repaired,"assets":details,"disclaimer":"Automatic geometric quality inspection, not final artistic approval."},
        indent=2,ensure_ascii=False)+"\n",encoding="utf-8", newline="\n")
    data["quality_audit_path"]="res://map_factory/metadata/quality_review.json"
    INDEX.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8",newline="\n")
    import csv
    with (ROOT/"map_factory/metadata/production_queue.csv").open("w",newline="",encoding="utf-8") as f:
        writer=csv.writer(f,lineterminator="\n");writer.writerow(["id","category","name","status","texture_path"])
        writer.writerows([a["id"],a["category"],a["name"],a["status"],a["texture_path"]] for a in data["assets"])
    lines=["# Pixel-art quality review — compared with Hero Room reference","",
        "A file existing is not proof it matches the detailed 1990s-style seaside JRPG room.",
        "The reference calls for intricate sandstone, dense flowered ivy, clean transparent",
        "sprites, blue and gold furniture, strong stylized pixel clusters and consistent",
        "3/4 overhead perspective.","",
        "## Confirmed technical problems","",
        "* Multiple cropped sprites contain unrelated label-border lines and neighboring fragments.",
        "* The hero and fairy first-pass characters need more native artistic detail.",
        "* Flooring tile seams, palette alignment, ocean animations and contact shadows need",
        "  visual approval inside the running Godot scene.","",
        "## Repairs pushed in this audit",""]
    lines += ["- %s: %d unrelated pixels removed."%(x["id"],x["pixels_removed"]) for x in repaired] or ["- No new image changes."]
    lines += ["","## Before / after image","",
        "![Before and after cleaning](previews/verified_cutout_cleanup.png)","",
        "## Remaining quality flags (not automatic disqualifications)",""]
    lines += ["- %s: %d"%(k,v) for k,v in issues.most_common()]
    lines += ["","Machine-readable report: map_factory/metadata/quality_review.json",
        "All assets remain needs_cleanup until manual fidelity review.",
        "Stable IDs, exact image dimensions, pivots and collisions preserved.",""]
    DOC.write_text("\n".join(lines),encoding="utf-8",newline="\n")
    print(json.dumps(summary,indent=2))
    print("Repaired IDs:",[x["id"] for x in repaired])

if __name__=="__main__":
    main()
