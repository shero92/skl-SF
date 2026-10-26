#!/usr/bin/env python3
"""Import authentic high-detail ChatGPT PNG bytes and version Hero Room in Godot.

This tool never generates, repaints, edits, or upscales a graphic.
All nine PNGs must come from the exact downloaded ChatGPT art-pack ZIP.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path, PurePosixPath
import struct
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
CATALOG = Path("map_factory/metadata/asset_index.json")
MANIFEST_SHA = "3583a2c7c9df7c456a960cb88de6932215004b4784b205804607ec0e777402d2"
ASSET_IDS = {"W021","W022","A017","A018","D019","P023","P024","P025","P026"}
SIG = bytes.fromhex("89504e470d0a1a0a")

def verify(archive: Path):
    with zipfile.ZipFile(archive) as z:
        info = z.infolist()
        names = [i.filename for i in info if not i.is_dir()]
        if len(names) != len(set(names)):
            raise ValueError("Duplicate archive paths")
        if any(PurePosixPath(n).is_absolute() or ".." in PurePosixPath(n).parts
               or "\\" in n or "\0" in n for n in names):
            raise ValueError("Unsafe archive path")
        if any(i.file_size > 8_000_000 for i in info) or sum(i.file_size for i in info)>18_000_000:
            raise ValueError("Oversized art pack")
        raw = z.read("manifest.json")
        if hashlib.sha256(raw).hexdigest() != MANIFEST_SHA:
            raise ValueError("Not the verified ChatGPT Hero Room HD art pack")
        m = json.loads(raw)
        assets = m.get("assets", [])
        if len(assets)!=9 or {a["id"] for a in assets} != ASSET_IDS:
            raise ValueError("Unexpected art ID or count")
        expected = set()
        for a in assets:
            path = a["path"]
            destination = a["factory_path"]
            correct = "sprites/{}/{}_{}.png".format(
                a["category"], a["id"], a["name"].replace(" ", "_"))
            if path != correct or destination != "map_factory/parts/" + path.removeprefix("sprites/"):
                raise ValueError("Incorrect factory filename or path")
            if path not in names:
                raise ValueError("Missing sprite: " + path)
            content = z.read(path)
            if len(content) < 33 or content[:8] != SIG or content[12:16] != b"IHDR":
                raise ValueError("Invalid PNG header: " + path)
            w,h=struct.unpack(">II",content[16:24])
            if [w,h] != a["pixel_size"] or content[24]!=8 or content[25]!=6:
                raise ValueError("Wrong native RGBA size: " + path)
            if not 20<=w<=1600 or not 20<=h<=1600:
                raise ValueError("Invalid native sprite dimensions")
            if hashlib.sha256(content).hexdigest()!=a["sha256"]:
                raise ValueError("Sprite SHA256 mismatch: " + path)
            expected.add(path)
        if {x for x in names if x.endswith(".png")} != expected:
            raise ValueError("Unlisted PNG sprite")
        return m

def catalog_record(a):
    out = {
      "id":a["id"],"name":a["name"],"category":a["category"],
      "subtype":a["subtype"],"texture_path":"res://"+a["factory_path"],
      "status":"needs_cleanup","pixel_size":a["pixel_size"],"origin":a["origin"],
      "collision":{"enabled":False,"size":[32,16],"offset":[0,0]},
      "y_sort":True,"shadow":{"type":"none","opacity":0.25,"offset_x":4,"offset_y":2},
      "tags":[a["category"],a["subtype"],"compass","blue_gold","owner_accepted_hd_style"],
      "reusable":True,
      "source":{"kind":"chatgpt_hd_solo_png","source_file":a["source_file"],
                "sha256":a["sha256"],"art_pack":"hero_room_hd_factory_pack_2026-10-26.zip"},
      "qa_notes":"Visual style liked by owner. Scene-scale, four-view art and grid footprint not yet reviewed in Godot."
    }
    if "placement_contract" in a:
        out["placement_contract"]=deepcopy(a["placement_contract"])
    return out

def room_patch(latest):
    """Initial playable-world visibility; layout still needs real Godot visual QA."""
    return {"map_id":"hero_room_01", "base_version":latest["version"],
      "note":"Show nine independently generated high-detail PNGs in the real Godot Hero Room; pending in-game placement review.",
      "changes":[
       {"op":"update_block","instance_id":"HeroBed",
        "set":{"id":"P024","scale":0.42,"shadow":{"type":"bed","opacity":0.35,"offset_x":0,"offset_y":0}}},
       {"op":"update_block","instance_id":"WritingTable","set":{"id":"P026","scale":0.46}},
       {"op":"update_block","instance_id":"TreasureChest","set":{"id":"P023","scale":0.31}},
       {"op":"add_block","layer":"back_objects","block":{"id":"W021","instance_id":"HeroHDLeftWall",
        "x":385,"y":445,"scale":0.38,"render_layer":"walls"}},
       {"op":"add_block","layer":"back_objects","block":{"id":"W022","instance_id":"HeroHDRightWall",
        "x":1165,"y":446,"scale":0.38,"render_layer":"walls"}},
       {"op":"add_block","layer":"back_objects","block":{"id":"A017","instance_id":"HeroHDPillar",
        "x":580,"y":416,"scale":0.40,"render_layer":"walls"}},
       {"op":"add_block","layer":"back_objects","block":{"id":"A018","instance_id":"HeroHDDoor",
        "x":773,"y":436,"scale":0.43,"render_layer":"walls"}},
       {"op":"add_block","layer":"front_objects","block":{"id":"D019","instance_id":"HeroHDBanner",
        "x":985,"y":366,"scale":0.31,"render_layer":"decorations"}},
       {"op":"add_block","layer":"objects","block":{"id":"P025","instance_id":"HeroHDBedCover",
        "x":410,"y":550,"scale":0.37,"mount_on":"HeroBed","mount_offset":[0,-25],
        "render_layer":"decorations","shadow":{"type":"none"}}},
       {"op":"set_property","key":"visual_qa",
        "value":{"status":"needs_review","notes":"9 HD sprites visible; Godot native screenshot and ground pivot review needed"}}
      ]}

def install(archive:Path, root:Path, integrate=False):
    m=verify(archive)
    catalog_path=root/CATALOG
    initial=catalog_path.read_bytes()
    cat=json.loads(initial)
    collisions={a["id"] for a in cat["assets"]}&ASSET_IDS
    if collisions:
        raise ValueError("Never replace existing catalog IDs: "+str(sorted(collisions)))
    destinations=[root/a["factory_path"] for a in m["assets"]]
    if any(p.exists() for p in destinations):
        raise FileExistsError("Art already installed; do not overwrite")
    if integrate:
        sys.path.insert(0,str(root/"tools"))
        import map_factory_cli as mf
        latest=mf.get_latest(root,"hero_room_01")
        ids={a["instance_id"] for layer in mf.LAYERS for a in latest.get(layer,[])}
        if not {"HeroBed","WritingTable","TreasureChest"}.issubset(ids):
            raise ValueError("Expected Hero Room furniture not found")
        if (root/mf.version_file("hero_room_01",latest["version"]+1)).exists():
            raise ValueError("Next immutable map version already exists")
    copied=[]
    try:
        with zipfile.ZipFile(archive) as z:
            for a,p in zip(m["assets"],destinations):
                p.parent.mkdir(parents=True,exist_ok=True)
                with p.open("xb") as fd:
                    fd.write(z.read(a["path"]))
                copied.append(p)
        cat["assets"].extend(catalog_record(a) for a in m["assets"])
        cat["asset_count"]=len(cat["assets"])
        catalog_path.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
        if integrate:
            patch=room_patch(latest)
            candidate=mf.apply_changes(latest,patch,mf.asset_catalog(root))
            mf.write_revision(root,"hero_room_01",candidate,mf.registry(root),patch)
        print("SUCCESS: 9 real high-detail transparent PNGs installed under map_factory/parts")
        print("SUCCESS: 9 catalog records with IDs, native dimensions, true sha256, anchors and block contracts")
        if integrate:
            print("SUCCESS: new immutable Hero Room map version with the new art; visual QA still pending")
    except BaseException:
        catalog_path.write_bytes(initial)
        for p in copied:
            p.unlink(missing_ok=True)
        raise

def main(argv=None):
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument("zip_path",type=Path)
    cli.add_argument("--install",action="store_true")
    cli.add_argument("--integrate",action="store_true")
    cli.add_argument("--root",type=Path,default=ROOT,help=argparse.SUPPRESS)
    args=cli.parse_args(argv)
    archive=args.zip_path.expanduser().resolve()
    verify(archive)
    print("PASS: all nine art PNG bytes/dimensions and stable factory filenames verified")
    if args.integrate and not args.install:
        cli.error("--integrate requires --install")
    if args.install:
        install(archive,args.root.resolve(),integrate=args.integrate)
    else:
        print("Dry run; use --install --integrate to add assets into the actual Hero Room")

if __name__=="__main__":
    main()
