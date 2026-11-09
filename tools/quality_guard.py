#!/usr/bin/env python3
"""Non-destructive repository gate for PNG integrity and obvious art downgrades.

Cannot automatically assert that a visual replacement is beautiful or matches
the reference. Blocks major unreviewed resolution/detail regressions.
"""
from PIL import Image, UnidentifiedImageError
from pathlib import Path
import io,json,subprocess,sys

ROOT=Path(__file__).resolve().parents[1]
INDEX="map_factory/metadata/asset_index.json"
def git(*args):
    return subprocess.run(["git",*args],cwd=ROOT,
           capture_output=True,check=False)
def previous(path):
    r=git("show","HEAD^:"+path)
    return r.stdout if r.returncode==0 else None

def fail(message,errors):
    print("ERROR:",message)
    errors.append(message)

def retired_record(path):
    """hd_map.json entry of a low-quality original retired by TASK-0117 (path under assets_generated/)."""
    try:
        relative = path.resolve().relative_to((ROOT / "assets_generated").resolve()).as_posix()
    except ValueError:
        return None
    hd_map = ROOT / "assets_hd" / "hd_map.json"
    if not hd_map.is_file():
        return None
    config = json.loads(hd_map.read_text(encoding="utf-8"))
    entry = config["map"].get(relative)
    if entry is None or "native_size" not in entry:
        return None
    return {**entry, "scale": int(config["scale"]), "name": Path(relative).name}


def verify_retired(entry, ident, pixel_size, errors):
    """The HD runtime twin must be exactly scale x the recorded native size, and the catalog size must match."""
    twin = ROOT / "assets_hd" / "runtime" / entry["name"]
    try:
        with Image.open(twin) as image:
            image.load()
            expected = [value * entry["scale"] for value in entry["native_size"]]
            if list(image.size) != expected:
                fail("HD runtime twin size mismatch "+ident,errors)
            if not image.convert("RGBA").getchannel("A").getbbox():
                fail("Empty alpha sprite "+ident,errors)
    except (ValueError,OSError,UnidentifiedImageError):
        fail("Missing or unreadable HD runtime twin "+ident,errors)
        return
    if list(entry["native_size"]) != pixel_size:
        fail("Metadata pixel size mismatch "+ident,errors)


def main():
    curr=json.loads((ROOT/INDEX).read_text())
    oldraw=previous(INDEX)
    old={x["id"]:x for x in json.loads(oldraw)["assets"]} if oldraw else {}
    records=curr["assets"]
    errors=[]
    notes=[]
    # New reusable map blocks may grow the catalog. Never silently delete IDs.
    deleted_ids=set(old)-{a.get("id") for a in records}
    if deleted_ids:
        fail("Existing catalog IDs removed: "+", ".join(sorted(deleted_ids)),errors)
    if len(records)<len(old):
        fail("Asset count unexpectedly decreased",errors)
    ids=set()
    for a in records:
        ident=a.get("id")
        if ident in ids:
            fail("Duplicate ID "+ident,errors)
        ids.add(ident)
        path=ROOT/a["texture_path"].removeprefix("res://")
        if not path.is_file():
            retired = retired_record(path)
            if retired is not None:
                verify_retired(retired, ident, a.get("pixel_size"), errors)
                if a.get("status")=="ready" and not a.get("qa_approval"):
                    fail("Ready requires documented qa_approval: "+ident,errors)
                continue
            fail("Missing "+ident+" at "+str(path),errors)
            continue
        try:
            with Image.open(path) as im:
                im.load()
                if im.format!="PNG":
                    fail("Not PNG "+ident,errors)
                    continue
                w,h=im.size
                alpha=im.convert("RGBA").getchannel("A")
                bbox=alpha.getbbox()
        except (ValueError,OSError,UnidentifiedImageError):
            fail("Unreadable "+ident,errors)
            continue
        if not bbox:
            fail("Empty alpha sprite "+ident,errors)
        if [w,h]!=a.get("pixel_size"):
            fail("Metadata pixel size mismatch "+ident,errors)
        if a.get("status")=="ready" and not a.get("qa_approval"):
            fail("Ready requires documented qa_approval: "+ident,errors)
        if a["category"] not in ("floors","environment","ui") and bbox==(0,0,w,h):
            notes.append(ident+": edge/full alpha boundary; review for background leftovers")
    # Compare the actual changed PNG paths, not merely metadata updates.
    diff=git("diff","--name-only","HEAD^","HEAD","--","map_factory/parts")
    changed=[s for s in diff.stdout.decode("utf-8","replace").splitlines()
             if s.lower().endswith(".png")] if diff.returncode==0 else []
    by_path={a["texture_path"].removeprefix("res://"):a for a in records}
    for path in changed:
        item=by_path.get(path)
        if not item:
            fail("Unindexed PNG in parts: "+path,errors)
            continue
        olditem=old.get(item["id"])
        if olditem is None:
            notes.append("New catalog part: "+item["id"])
            continue
        old_source=olditem.get("source",{})
        old_kind=str(old_source.get("kind","")) if isinstance(old_source,dict) else str(old_source)
        oldarea=olditem.get("pixel_size",[0,0])
        oldpixels=max(1,oldarea[0]*oldarea[1])
        newpixels=item["pixel_size"][0]*item["pixel_size"][1]
        ratio=newpixels/oldpixels
        protected=("ai_sheet_crop","artist_approved","high_fidelity_source",
                   "curated_individual_crop")
        # Mathematically obvious loss of native sample information is a red flag,
        # but legitimate cropping can be allowed with recorded approval.
        if old_kind in protected and ratio<0.50:
            evidence=item.get("quality_override")
            if not isinstance(evidence,dict) or not evidence.get("reason"):
                fail(item["id"]+" drops from "+str(oldarea)+" to "+
                     str(item["pixel_size"])+" (ratio %.2f)"%ratio+
                     " without quality_override.reason",errors)
        if olditem.get("status")=="ready" and item.get("status")!="ready":
            notes.append(item["id"]+" downgraded to needs_cleanup for review")
    print(json.dumps({"registered":len(records),"changed_pngs":changed,
                      "warnings":notes[:40],"errors":errors},indent=2))
    return int(bool(errors))

if __name__=="__main__":
    sys.exit(main())
