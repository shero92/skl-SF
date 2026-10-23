#!/usr/bin/env python3
"""Artist-guided native pixel cutout repairs: remove cropped neighbors and label strips.
No regeneration, recoloring, blurring, resampling or detail loss in retained area.
"""
from pathlib import Path
from PIL import Image
import csv,json

ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/"map_factory/metadata/asset_index.json"
# id: x0,y0,x1,y1, expected source canvas
CROPS={
    "P014":((0,0,296,269),(296,276),"discard disconnected gold label line"),
    "P015":((0,0,210,232),(248,238),"remove unrelated hanging banner and label line"),
    "O001":((0,0,117,165),(126,165),"remove adjacent black strip"),
    "P011":((28,0,140,166),(140,166),"remove neighboring sliced sprite at left"),
    "W001":((0,0,179,239),(202,239),"remove unrelated wall segment at right")
}

def main():
    data=json.loads(INDEX.read_text(encoding="utf-8"))
    updates=[]
    for a in data["assets"]:
        id=a["id"]
        if id not in CROPS:
            continue
        rect,expected,reason=CROPS[id]
        source=a.get("source",{})
        if a.get("status")=="ready" or (isinstance(source,dict) and
                                          source.get("kind")=="curated_individual_crop"):
            print("Already approved or curated:",id)
            continue
        path=ROOT/a["texture_path"].removeprefix("res://")
        with Image.open(path) as file:
            original=file.convert("RGBA")
        if original.size!=expected:
            raise RuntimeError("Unexpected source dimensions for %s: %r vs %r" %
                               (id,original.size,expected))
        clean=original.crop(rect)
        if not clean.getchannel("A").getbbox():
            raise RuntimeError("Generated an empty sprite: "+id)
        clean.save(path,optimize=True)
        a["pixel_size"]=list(clean.size)
        a["origin"]=[clean.width//2,clean.height]
        a["status"]="needs_cleanup"
        a["source"]={"kind":"curated_individual_crop","revision":3,
                     "method":"exact_source_pixel_crop",
                     "generator":"tools/curate_high_detail_sprites.py"}
        a["qa_notes"]="Removed "+reason+". High-resolution source content unchanged; art QA still pending."
        updates.append((id,expected,clean.size,reason))
    INDEX.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    with (ROOT/"map_factory/metadata/production_queue.csv").open("w",newline="",encoding="utf-8") as f:
        writer=csv.writer(f)
        writer.writerow(["id","category","name","status","texture_path"])
        writer.writerows((a["id"],a["category"],a["name"],a["status"],a["texture_path"])
                         for a in data["assets"])
    report=ROOT/"docs/ART_QUALITY_REVIEW.md"
    report.write_text(report.read_text(encoding="utf-8")+
       "\n## Five additional high-detail cutout corrections\n\n"+
       "\n".join("- **%s** %s → %s: %s. All retained source pixels unchanged." %
                 (ident,old,new,reason) for ident,old,new,reason in updates)+
       "\n\nAll five remain needs_cleanup until manual on-screen comparison.\n",
       encoding="utf-8")
    print("Curated",len(updates),"sprites:",updates)

if __name__=="__main__":
    main()
