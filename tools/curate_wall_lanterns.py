#!/usr/bin/env python3
"""Remove visibly unrelated neighboring lantern crops, retaining high-detail source pixels."""
from pathlib import Path
from PIL import Image
import json,csv

ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/"map_factory/metadata/asset_index.json"
CROPS={"D008":(0,0,94,175),"D009":(24,0,140,166)}

def main():
    data=json.loads(INDEX.read_text(encoding="utf-8"))
    upgraded=[]
    for record in data["assets"]:
        id=record["id"]
        if id not in CROPS:continue
        path=ROOT/record["texture_path"].removeprefix("res://")
        source=record.get("source",{})
        if record["status"]=="ready" or (isinstance(source,dict) and
                source.get("kind")=="curated_individual_crop"):
            print("Preserved already approved or curated sprite",id)
            continue
        with Image.open(path) as file:
            img=file.convert("RGBA")
        rect=CROPS[id]
        if img.size!=(164,175) and id=="D008":
            raise RuntimeError("Unexpected D008 size: "+str(img.size))
        if img.size!=(140,166) and id=="D009":
            raise RuntimeError("Unexpected D009 size: "+str(img.size))
        output=img.crop(rect)
        # No recoloring, upscaling, new shapes, or pasted pixels: source detail is retained.
        assert output.getchannel("A").getbbox()
        output.save(path,optimize=True)
        record["pixel_size"]=list(output.size)
        record["origin"]=[output.width//2,output.height]
        record["source"]={"kind":"curated_individual_crop","parent":"original_high_detail_atlas",
                           "tool":"tools/curate_wall_lanterns.py","revision":2}
        record["qa_notes"]="Removed unrelated adjacent lantern or wall from high-detail source; verify at game scale."
        record["status"]="needs_cleanup"
        upgraded.append({"id":id,"new_size":output.size,"crop":rect})
    INDEX.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    with (ROOT/"map_factory/metadata/production_queue.csv").open("w",newline="",encoding="utf-8") as f:
        wr=csv.writer(f);wr.writerow(["id","category","name","status","texture_path"])
        wr.writerows((a["id"],a["category"],a["name"],a["status"],a["texture_path"]) for a in data["assets"])
    doc=ROOT/"docs/ART_QUALITY_REVIEW.md"
    doc.write_text(doc.read_text(encoding="utf-8")+
        "\n## Individual wall-lantern cutout corrections\n\n"
        "D008 and D009 previously contained unrelated neighboring objects from a concept-sheet crop. "
        "The cleaned sprites preserve their actual source pixels; the PNG canvas now tightly fits "
        "each wall-mounted lantern. Metadata pixel_size and bottom-center origin have been updated. "
        "Art review for shadows and alpha fringing is still pending.\n",encoding="utf-8")
    print("Curated individual lantern images:",upgraded)

if __name__=="__main__":main()
