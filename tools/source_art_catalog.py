"""Read-only source audit and searchable art handoff catalog; never activates art.

Build with --root pointing at the owner's assembled project folder. Branch-only
deliveries retain their publication locator; this is not a runtime sprite registry.
Agent: codex. Model/usage: unknown (desktop session).
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from PIL import Image

CATALOG = "map_factory/metadata/source_art_index.json"
GUIDE = "docs/SOURCE_ART_CATALOG.md"
APPROVAL = "docs/OWNER_AUTOMATIC_ART_APPROVAL_20261111.md"
PENDING = {
    "ART-0021": ("codex/hero-room-b4-chest", 166),
    "ART-0015": ("codex/hero-room-b4-rugs", 168),
    "ART-0002": ("codex/hero-room-cloud-variants", 170),
}


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_path(root, relative):
    relative = relative.removeprefix("res://")
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f"Path outside project: {relative}")
    return path


def strings(value):
    if isinstance(value, str):
        yield value.removeprefix("res://")
    elif isinstance(value, dict):
        for child in value.values():
            yield from strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from strings(child)


def build(root):
    root = Path(root).resolve()
    records, manifests, errors = [], [], []
    map_index = load(root / "map_factory/maps/index.json")
    maps = []
    map_refs = {}
    for ident, entry in sorted(map_index["maps"].items()):
        maps.append({"map_id": ident, **entry})
        map_refs[ident] = set(strings(load(safe_path(root, entry["latest"]))))
    painted_index = map_index.get("painted_world_index")
    if painted_index:
        for ident, entry in sorted(load(safe_path(root, painted_index))["worlds"].items()):
            maps.append({"map_id": ident, "rendering_mode": "owner_requested_painted_block_ground", **entry})
            map_refs[ident] = set(strings(load(safe_path(root, entry["latest"]))))
    sources = sorted(root.glob("game_factory/environment/ART-*/v*/manifest.json"))
    character = root / "game_factory/golden_cyclone/v001/manifest.json"
    if character.exists():
        sources.append(character)
        effects = character.parent / "metadata/vfx.json"
        if effects.exists():
            sources.append(effects)
    for manifest in sources:
        data = load(manifest)
        rel = manifest.relative_to(root).as_posix()
        request = data.get("request_id", data.get("art_request", "ART-0029"))
        directory = manifest.parent.parent if manifest.name == "vfx.json" else manifest.parent
        main = subprocess.run(["git", "show", f"origin/main:{rel}"], cwd=root,
                              capture_output=True)
        on_main = main.returncode == 0 and hashlib.sha256(main.stdout).hexdigest() == digest(manifest)
        branch, pr = PENDING.get(request, (None, None))
        branch = data.get("delivery_branch", branch)
        publication = {"manifest_on_origin_main": on_main,
                       "delivery_branch": branch if not on_main else None,
                       "pull_request": data.get("pull_request", f"https://github.com/shero92/skl-SF/pull/{pr}" if pr else None) if not on_main else None}
        manifests.append({"path": rel, "sha256": digest(manifest), "request_id": request,
                          "publication": publication,
                          "context": {k: v for k, v in data.items() if k not in {"items", "frames", "effects", "rejected", "rejected_sources", "rejected_attempts"}}})
        groups = [("selected", data.get("items", data.get("frames", data.get("effects", [])))),
                  ("rejected", data.get("rejected_attempts", data.get("rejected", data.get("rejected_sources", []))))]
        for selection, items in groups:
            for item in items:
                source = next((item[k] for k in ("master_path", "source_image_path", "source_path", "path") if item.get(k)), None)
                if not source:
                    errors.append(f"{rel}: item has no source path")
                    continue
                path = safe_path(root, source)
                if not path.is_file():
                    errors.append(f"Missing source: {source}")
                    continue
                actual_sha = digest(path)
                if item.get("sha256") and actual_sha != item["sha256"]:
                    errors.append(f"SHA mismatch: {source}")
                with Image.open(path) as im:
                    im.load()
                    alpha = im.convert("RGBA").getchannel("A")
                    measured = {"pixel_size": list(im.size), "mode": im.mode,
                                "alpha_extrema": list(alpha.getextrema()),
                                "bounds_alpha_128": alpha.point(lambda x: 255 if x >= 128 else 0).getbbox()}
                if item.get("pixel_size") and measured["pixel_size"] != item["pixel_size"]:
                    errors.append(f"Dimension mismatch: {source}")
                for key, value in item.items():
                    if key.endswith("_path") and isinstance(value, str) and value.startswith(("assets", "game_factory", ".agents")):
                        linked = safe_path(root, value)
                        if not linked.is_file():
                            errors.append(f"Missing linked {key}: {value}")
                        expected = item.get(key.removesuffix("_path") + "_sha256")
                        if expected and linked.is_file() and digest(linked) != expected:
                            errors.append(f"Linked SHA mismatch: {value}")
                ident = item.get("id", item.get("frame_id", path.stem))
                category = path.parts[path.parts.index("assets_hd") + 1] if "assets_hd" in path.parts else "character"
                relevant_paths = {source, item.get("native_review_path"), item.get("game_frame_path"), item.get("runtime_path")}
                records.append({"catalog_id": f"{request}/{directory.name}/{ident}/{selection}",
                                "id": ident, "request_id": request, "category": category,
                                "selection": selection, "master_path": source, "sha256": actual_sha,
                                **measured, "manifest_path": rel, "manifest_sha256": digest(manifest),
                                "metadata": item,
                                "owner_approved": True, "approval_basis": "owner_automatic_20261111",
                                "approval_policy": APPROVAL,
                                "quality_status": item.get("quality_status", data.get("quality_status", "unknown")),
                                "integration_status": item.get("integration_status", "not_inferred_from_visual_approval"),
                                "production_active": item.get("production_active", data.get("production_active", False)),
                                "exact_path_map_references": [m for m, refs in map_refs.items() if refs & relevant_paths],
                                "publication": publication,
                                "readme_path": (directory / "README.md").relative_to(root).as_posix(),
                                "usage_rule": "Do not place rejected attempts. Use the manifest for measured anchors, scale and limitations; missing values are unknown."})
    known = {r["master_path"] for r in records}
    groups = set()
    for relative in known:
        parts = Path(relative).parts
        if relative.startswith("assets_hd/"):
            revision = next((i for i, part in enumerate(parts) if part.startswith("v") and part[1:].isdigit()), None)
            if revision is not None:
                groups.add(Path(*parts[:revision + 1]))
    unindexed = sorted({p.relative_to(root).as_posix() for group in groups
                        for p in (root / group).rglob("*.png")} - known)
    errors.extend(f"Source PNG has no piece record: {p}" for p in unindexed)
    if errors:
        raise ValueError("\n".join(errors))
    return {"schema_version": 1, "scope": "Codex environment deliveries and Golden Cyclone source frames/effects, including retained rejected attempts; derived previews are linked from metadata",
            "approval_policy": APPROVAL, "runtime_asset_index": "map_factory/metadata/asset_index.json",
            "map_index": "map_factory/maps/index.json", "map_reference_rule": "Exact source/native/runtime path matches in factory maps or registered painted worlds; no filename-based activation or inferred integration",
            "record_count": len(records), "selected_count": sum(r["selection"] == "selected" for r in records),
            "rejected_count": sum(r["selection"] == "rejected" for r in records),
            "coverage": {"source_groups_checked": len(groups), "unindexed_source_pngs": unindexed,
                         "all_linked_item_paths_exist": True},
            "manifests": manifests, "maps": maps, "assets": records}


def guide(data):
    lines = ["# دليل الصور المولدة وبيانات القطع", "",
             "الفهرس القابل للبحث: `map_factory/metadata/source_art_index.json`. ابحث بواسطة ART أو اسم القطعة أو الفئة؛ كل سجل يحتوي بيانات المصدر الأصلية وقياسات PNG وبصمته ومسار manifest وREADME وحالة النشر والموافقة.", "",
             "الأصول محفوظة مباشرة تحت `H:/shining force/skl-SF/assets_hd/<category>/<group>/vNNN/`. بياناتها ومعايناتها تحت `game_factory/environment/ART-####/vNNN/`. لا يعتمد التسليم على cache أداة التوليد. ملفات الشخصية السابقة محفوظة في مساراتها الأصلية المحمية ولا تُنقل.", "",
             "الموافقة البصرية تلقائية وفق `docs/OWNER_AUTOMATIC_ART_APPROVAL_20261111.md`. المحاولات rejected محفوظة للتتبع ولا تدخل الخريطة. وجود سجل لا يثبت التكامل؛ تُراجع المقاسات والارتكاز والتثبيت والقيود في manifest. القيم الناقصة تبقى مجهولة، ولا تُختلق collision أو اتجاه أو قياسات.", "",
             "سجل الخرائط الحالية مرفق في JSON؛ exact_path_map_references يرصد التطابق الحرفي لمسار المصدر/المعاينة/runtime في خرائط المصنع أو تعريفات العوالم المصورة المسجلة، ولا يستنتج استخدام الصور من أسمائها. لا يغيّر الفهرس الخرائط أو يعين أصولًا نشطة. القصة عبر docs/story/INDEX.md؛ العالم المصور عبر map_factory/painted_worlds/INDEX.md.", "",
             "الصور المنسوخة محليًا قد تكون في PR لم يدمج بعد؛ publication يوضح الفرع والرابط. تتحقق حالة الدمج من Git عند الاستخدام. لا تستبدل الصور بأسماء متشابهة ولا تفعّل البدائل تلقائيًا.", "",
             "بعد كل تسليم: شغّل `python tools/source_art_catalog.py --root . --write` في مجلد المشروع الجامع، ثم `python tools/source_art_catalog.py --root . --check`. تحفظ الأداة فقط هذا الفهرس ودليله؛ لا تعدّل PNG أو manifests تاريخية. فهارس INDEX.md الآلية تُحدّث على main وفق سير المشروع.", "",
             f"العدد: {data['selected_count']} مصادر مختارة و{data['rejected_count']} محاولات مرفوضة في {len(data['manifests'])} manifests.", "",
             "| ART | القطعة | الفئة | الاختيار | المصدر |", "| --- | --- | --- | --- | --- |"]
    for r in data["assets"]:
        lines.append(f"| {r['request_id']} | {r['id']} | {r['category']} | {r['selection']} | [{Path(r['master_path']).name}](../{r['master_path']}) |")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output-root", type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = build(args.root)
    output = args.output_root or args.root
    for relative, content in ((CATALOG, json.dumps(data, ensure_ascii=False, indent=2) + "\n"), (GUIDE, guide(data))):
        path = output / relative
        if args.write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
        elif not path.exists() or path.read_text(encoding="utf-8") != content:
            raise SystemExit(f"Stale catalog: {path}")
    print(f"Verified {data['record_count']} source records; {len(data['maps'])} map locators. No images or map revisions changed.")


if __name__ == "__main__":
    main()
