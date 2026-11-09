#!/usr/bin/env python3
"""Read-only physical PNG and five-pass completeness audit.

Existence, dimensions, alpha and ID integrity can be verified automatically.
Visual similarity / beauty of artwork cannot be certified algorithmically.
"""
from pathlib import Path
import hashlib,json,collections,sys
from PIL import Image
from map_factory_cli import ROOT,registry,asset_catalog,get_latest
from map_factory_layers import create_layer_stack

OUT=ROOT/"map_factory/metadata/room_block_quality.json"
DOC=ROOT/"docs/ROOM_BLOCK_QA.md"

def audit_map_ids(map_json, v2, legacy):
    """Classify resolved_assets IDs without changing maps or registries.

    Direct registry keys and asset_id values resolve through v2. Legacy
    spellings remain in legacy_only, with an explicit v2_target when bridged.
    A bridge does not promote the legacy record's status or QA approval.
    """
    assets = v2["assets"]
    direct_ids = set(assets)
    direct_ids.update(record["asset_id"] for record in assets.values())
    aliases = v2.get("legacy_aliases", {})
    legacy_assets = legacy.get("assets", legacy)
    if isinstance(legacy_assets, list):
        legacy_assets = {record["id"]: record for record in legacy_assets}
    result = {"v2_resolved": [], "legacy_only": {}, "unresolved": []}
    for asset_id in sorted(map_json["resolved_assets"]):
        if asset_id in direct_ids:
            result["v2_resolved"].append(asset_id)
            continue
        target = aliases.get(asset_id)
        if asset_id in legacy_assets:
            record = legacy_assets[asset_id]
            result["legacy_only"][asset_id] = {
                "status": record.get("status", "unknown"),
                "qa_approval": bool(record.get("qa_approval")),
                "v2_target": target if target in assets else None,
            }
        elif target in assets:
            result["v2_resolved"].append(asset_id)
        else:
            result["unresolved"].append(asset_id)
    return result


def retired_entry(root, file):
    """hd_map.json entry of a retired low-quality PNG (path under assets_generated/), or None."""
    try:
        relative = file.resolve().relative_to((root / "assets_generated").resolve()).as_posix()
    except ValueError:
        return None
    path = root / "assets_hd" / "hd_map.json"
    if not path.is_file():
        return None
    entry = json.loads(path.read_text(encoding="utf-8"))["map"].get(relative)
    return None if entry is None or "low_sha256" not in entry else {**entry, "_relative": relative,
                                                                     "_scale": json.loads(path.read_text(encoding="utf-8"))["scale"]}


def verify_retired(root, entry, record, key):
    """The retired original is proven by its recorded hash and size plus an HD runtime twin of SCALE x size."""
    problems = []
    if entry["low_sha256"] != record["sha256"]:
        problems.append("SHA-256 mismatch " + key)
    if list(entry["native_size"]) != list(record["sprite_dimensions"]):
        problems.append("Sprite dimensions mismatch " + key)
    twin = root / "assets_hd" / "runtime" / Path(entry["_relative"]).name
    try:
        with Image.open(twin) as image:
            image.load()
            expected = [value * int(entry["_scale"]) for value in entry["native_size"]]
            if list(image.size) != expected:
                problems.append("HD runtime twin size mismatch " + key)
    except (OSError, ValueError):
        problems.append("Missing HD runtime twin " + key)
    return problems


def verify_v2_assets(v2, root):
    """Read every v2 PNG and validate hashes, dimensions and bridge targets."""
    root = Path(root)
    assets = v2["assets"]
    errors = []
    verified = []
    groups = collections.defaultdict(list)
    directions = {"north", "east", "south", "west"}
    if len(assets) != 128 or v2.get("count") != len(assets):
        errors.append("Expected exactly 128 v2 entries and a matching count")
    for alias, target in sorted(v2.get("legacy_aliases", {}).items()):
        if target not in assets:
            errors.append("Missing alias target " + alias + ": " + str(target))
    for key, record in sorted(assets.items()):
        direction = record.get("facing_direction", "default")
        if direction != "default":
            groups[record["category"]].append(direction)
        if record.get("registry_key") != key:
            errors.append("Registry key mismatch " + key)
        file = root / record["source_texture_path"].removeprefix("res://")
        if not file.is_file():
            retired = retired_entry(root, file)
            if retired is None:
                errors.append("Missing v2 PNG " + key)
                continue
            retired_errors = verify_retired(root, retired, record, key)
            errors.extend(retired_errors)
            if not retired_errors:
                verified.append(key)
            continue
        entry_errors = []
        try:
            digest = hashlib.sha256(file.read_bytes()).hexdigest()
            if digest != record["sha256"]:
                entry_errors.append("SHA-256 mismatch " + key)
            with Image.open(file) as image:
                image.load()
                if image.format != "PNG":
                    entry_errors.append("Non-PNG v2 sprite " + key)
                if list(image.size) != record["sprite_dimensions"]:
                    entry_errors.append("Sprite dimensions mismatch " + key)
        except (OSError, ValueError) as exc:
            entry_errors.append("Unreadable v2 PNG " + key + ": " + str(exc))
        errors.extend(entry_errors)
        if not entry_errors:
            verified.append(key)
    for category, facings in sorted(groups.items()):
        if len(facings) != 4 or set(facings) != directions:
            errors.append("Incomplete directional group " + category)
    return {"verified": verified, "errors": errors}


def main():
    catalog=asset_catalog(ROOT)
    with (ROOT / "map_factory/metadata/environment_assets_v2.json").open(
            encoding="utf-8") as handle:
        v2 = json.load(handle)
    v2_verification = verify_v2_assets(v2, ROOT)
    state=registry(ROOT)
    inspected={}
    summaries=[]
    errors=list(v2_verification["errors"])
    for map_id in sorted(state["maps"]):
        current=get_latest(ROOT,map_id,state)
        id_audit = audit_map_ids(current, v2, catalog)
        errors.extend("Unresolved map asset " + map_id + ": " + asset_id
                      for asset_id in id_audit["unresolved"])
        stack=create_layer_stack(current,catalog)
        used=stack["unique_asset_ids"]
        for asset_id in used:
            if asset_id in inspected:continue
            record=catalog.get(asset_id)
            if not record:
                errors.append("Unregistered asset "+asset_id)
                continue
            relative=record["texture_path"].removeprefix("res://")
            file=ROOT/relative
            if not file.is_file():
                errors.append("Missing PNG "+asset_id+" at "+relative)
                continue
            try:
                with Image.open(file) as img:
                    img.load()
                    if img.format!="PNG":
                        errors.append("Non PNG "+asset_id)
                    if list(img.size)!=record.get("pixel_size"):
                        errors.append("Wrong metadata dimensions "+asset_id)
                    alpha=img.convert("RGBA").getchannel("A")
                    bounds=alpha.getbbox()
                    if bounds is None:
                        errors.append("Transparent/empty "+asset_id)
                    inspected[asset_id]={
                      "id":asset_id,"category":record["category"],
                      "status":record.get("status","planned"),
                      "dimensions":list(img.size),
                      "alpha_bbox":list(bounds) if bounds else None,
                      "file_bytes":file.stat().st_size,
                      "sha256":hashlib.sha256(file.read_bytes()).hexdigest(),
                      "texture_path":record["texture_path"]
                    }
            except Exception as exc:
                errors.append("Unreadable "+asset_id+": "+str(exc))
        attachments=[x for x in stack["passes"]["decorations"] if x["attachment"]]
        count=dict(stack["counts"])
        blocked=[x["instance_id"] for x in stack["passes"]["walls"]
                 if x["category"]=="characters"] if False else []
        summary={"map_id":map_id,"version":current["version"],"counts":count,
                 "placed_instances":sum(count[k] for k in ("background","ground","walls","decorations")),
                 "mounted_details":len(attachments),"owned_shadows":count["shadows"],
                 "unique_asset_ids":len(used),
                 "visual_qa_status":current.get("visual_qa",{}).get("status","needs_review"),
                 "reference_sha256":current.get("composition_reference",{}).get("reference_sha256")}
        summary["registry_ids"] = id_audit
        summaries.append(summary)
        if count["shadows"] != sum(
              x["shadow"].get("type","none")!="none" for key in ("background","ground","walls","decorations") for x in stack["passes"][key]):
            errors.append("Shadow pass count mismatch "+map_id)
    # Inspect every environmental PNG, not only images used in current maps.
    # Characters and UI are strictly excluded.
    all_map_ids=[ident for ident,record in sorted(catalog.items())
                 if record.get("category") not in ("characters","ui")]
    for asset_id in all_map_ids:
        if asset_id in inspected:
            continue
        record=catalog[asset_id]
        relative=record["texture_path"].removeprefix("res://")
        file=ROOT/relative
        if not file.is_file():
            errors.append("Missing reusable map PNG "+asset_id)
            continue
        try:
            with Image.open(file) as img:
                img.load()
                if img.format!="PNG":
                    errors.append("Non-PNG reusable sprite "+asset_id)
                if list(img.size)!=record.get("pixel_size"):
                    errors.append("Metadata pixel size mismatch "+asset_id)
                bounds=img.convert("RGBA").getchannel("A").getbbox()
                if not bounds:
                    errors.append("Empty alpha for "+asset_id)
                inspected[asset_id]={
                    "id":asset_id,"category":record["category"],
                    "status":record.get("status","planned"),
                    "dimensions":list(img.size),
                    "alpha_bbox":list(bounds) if bounds else None,
                    "file_bytes":file.stat().st_size,
                    "sha256":hashlib.sha256(file.read_bytes()).hexdigest(),
                    "texture_path":record["texture_path"]}
        except Exception as exc:
            errors.append("Unreadable environmental sprite "+asset_id+": "+str(exc))
    if len(inspected)!=len(all_map_ids):
        errors.append("Map catalog incomplete: %d/%d PNGs verified"%(len(inspected),len(all_map_ids)))

    by_status=collections.Counter(x["status"] for x in inspected.values())
    response={"maps":summaries,"v2_verification":v2_verification,
              "verified_environment_png_files":len(inspected),
              "environment_catalog_count":len(all_map_ids),
              "catalog_total":len(catalog),"catalog_status":dict(collections.Counter(x.get("status","planned") for x in catalog.values())),
              "referenced_status":dict(by_status),"errors":errors,
              "artistic_qa":"NOT APPROVED: image file presence and alpha cannot confirm full fidelity.",
              "assets":sorted(inspected.values(),key=lambda a:a["id"])}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(response,indent=2,ensure_ascii=False)+"\n",encoding="utf-8",newline="\n")
    md=["# Room Map Factory — physical art and layer QA","",
        "This report only certifies file/metadata integrity. It **does not certify that artwork matches the user's reference**.","",
        "| Map | Revision | Background | Ground detail | Walls | Decorations | Independent shadows | Mounted |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for s in summaries:
        c=s["counts"]
        md.append(f'| {s["map_id"]} | v{s["version"]:04d} | {c["background"]} | {c["ground"]} | {c["walls"]} | {c["decorations"]} | {c["shadows"]} | {s["mounted_details"]} |')
    md += ["",f"- Registered catalog images: **{len(catalog)}**.",
           f"- Verified environmental and shadow PNG files: **{len(inspected)} / {len(all_map_ids)}**.",
           f"- Integrity errors: **{len(errors)}**.",
           f"- Catalog QA statuses: **{dict(response['catalog_status'])}**.",
           "- Reference fidelity still needs artist comparison of exported Godot room render.",
           "- Only environment sprites and their independent shadow images are included; no characters/UI are added.",
           "", "Detailed per-ID PNG SHA-256, pixel bounds and paths: map_factory/metadata/room_block_quality.json.",""]
    if errors:md+=["## Errors",""]+["- "+x for x in errors]
    DOC.write_text("\n".join(md),encoding="utf-8",newline="\n")
    print(json.dumps({k:v for k,v in response.items() if k!="assets"},indent=2))
    return bool(errors)

if __name__=="__main__":
    sys.exit(main())
