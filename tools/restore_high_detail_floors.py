#!/usr/bin/env python3
"""Restore high-detail source sheet floor art where it beats a procedural repaint.
This is a targeted quality-preserving rollback of 4 files only.
"""
import csv
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
GOOD_COMMIT="a881c847897eadcdc6c58761b968726a921918a7"
IDS=("F001","F002","F006","F010")
INDEX=ROOT/"map_factory/metadata/asset_index.json"

def from_git(path: str) -> bytes:
    return subprocess.check_output(["git","show",GOOD_COMMIT+":"+path],cwd=ROOT)

def main():
    current=json.loads(INDEX.read_text())
    previous=json.loads(from_git("map_factory/metadata/asset_index.json"))
    old={x["id"]:x for x in previous["assets"]}
    for a in current["assets"]:
        if a["id"] not in IDS:continue
        older=old[a["id"]]
        path=older["texture_path"].removeprefix("res://")
        artifact=ROOT/path
        original=from_git(path)
        assert len(original)>1500
        artifact.write_bytes(original)
        a["pixel_size"]=older["pixel_size"]
        a["origin"]=older["origin"]
        a["source"]=older["source"]
        a["status"]="needs_cleanup"
        a["qa_notes"]="Restored native high-detail source sprite; visually superior to flat procedural 64px repaint. Needs alpha/seam review."
        print("Restored",a["id"],a["pixel_size"],len(original),"bytes")
    INDEX.write_text(json.dumps(current,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    with (ROOT/"map_factory/metadata/production_queue.csv").open("w",newline="",encoding="utf-8") as out:
        w=csv.writer(out)
        w.writerow(["id","category","name","status","texture_path"])
        w.writerows((a["id"],a["category"],a["name"],a["status"],a["texture_path"]) for a in current["assets"])
    doc=ROOT/"docs/FLOOR_REPAINT_QA.md"
    previous_doc=doc.read_text(encoding="utf-8") if doc.exists() else ""
    doc.write_text(previous_doc+
      "\n## High-resolution source preservation\n\n"
      "Visual QA showed four earlier cropped source textures contained genuinely "
      "richer stone detail than the 64px procedural replacements. "
      "**F001 F002 F006 F010 were restored byte-for-byte** from Git commit "+
      GOOD_COMMIT+". Their original dimensions/source metadata were restored. "
      "The nine-part compass correction F014–F022 remains installed. "
      "Other plain/edge draft tiles remain for visual review; none are approved "
      "as a 100% visual match to the reference.\n",encoding="utf-8")
    print("Restored original source art in",len(IDS),"files")

if __name__=="__main__":main()
