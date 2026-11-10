"""Measure independent B1 masters and create review-only native PNGs. Never alters masters."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
SHA = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
specs = json.loads((BASE / 'production_spec.json').read_text())
records = json.loads((BASE / 'generation_records.json').read_text())
target = 'map_factory/references/hero_room_01_target_20261110.webp'
assert SHA(ROOT / target) == '4e55aeaa5a5e500760f48fed75c3ce7f6d56d55c1ca06b8c70839cce517e4323'
groups = {}
for spec in specs:
    art, key, name = spec['art'], spec['key'], spec['id']
    master = ROOT / spec['dir'] / (name + '.png')
    image = Image.open(master)
    assert image.mode == 'RGBA'
    alpha = image.getchannel('A')
    bounds = alpha.point(lambda a: 255 if a >= 128 else 0).getbbox()
    assert bounds and alpha.getextrema()[0] == 0
    x0, y0, x1, y1 = bounds
    assert 0 < x0 < x1 < image.width and 0 < y0 < y1 < image.height
    review = ROOT / 'game_factory/environment' / art / 'v001'
    (review / 'native_review').mkdir(parents=True, exist_ok=True)
    (review / 'requests').mkdir(exist_ok=True)
    (review / '.gdignore').write_text('')
    # QA derivative only: trim transparent border, retaining all nonzero-alpha pixels.
    nw, nh = spec['native']
    region = alpha.getbbox()
    visible = image.crop(region)
    scale = min(nw / visible.width, nh / visible.height)
    size = [max(1, round(visible.width * scale)), max(1, round(visible.height * scale))]
    offset = [(nw - size[0]) // 2, nh - size[1]]
    native = Image.new('RGBA', (nw, nh))
    native.paste(visible.resize(size, Image.Resampling.NEAREST), offset)
    native_path = review / 'native_review' / (name + '.png')
    native.save(native_path)
    delivery = ROOT / '.agents/graphics/deliveries' / art
    delivery.mkdir(parents=True, exist_ok=True)
    if (delivery/master.name).exists() and SHA(delivery/master.name) != SHA(master):
        raise RuntimeError('Different prior delivery must be archived before replacement: ' + str(delivery/master.name))
    shutil.copy2(master, delivery / master.name)
    prompt_key = key + '_correction' if key in ['south', 'plant'] else key
    prompt_path = review / 'requests' / (name + '.txt')
    prompt_path.write_text(records['prompts'][prompt_key], encoding='utf-8', newline='\n')
    if key in ['south', 'plant']:
        (review / 'requests' / (name + '_attempt_01.txt')).write_text(records['prompts'][key], encoding='utf-8', newline='\n')
    issues = []
    if image.width < spec['minimum'][0] or image.height < spec['minimum'][1]:
        issues.append('Actual built-in output is below the literal per-asset master minimum; original preserved without upscaling. Regeneration/owner decision required.')
    if min(x0 / image.width, y0 / image.height, (image.width-x1) / image.width, (image.height-y1) / image.height) < .025:
        issues.append('Visible pixels are inside canvas but some margins are less than the approximately 3 percent target.')
    ratio = min((x1-x0) / nw, (y1-y0) / nh)
    assert ratio >= 4, (name, ratio)
    item = dict(id=name, request_id=art, master_path=master.relative_to(ROOT).as_posix(),
        delivery_path=(delivery/master.name).relative_to(ROOT).as_posix(), sha256=SHA(master),
        pixel_size=list(image.size), mode=image.mode, alpha_extrema=list(alpha.getextrema()),
        bounds_alpha_128=list(bounds), origin=[(x0+x1)/2, y1-1], origin_rule='bottom centre of alpha-128 visible bounds',
        facing=spec['facing'], intended_native_canvas=spec['native'], requested_master_minimum=spec['minimum'],
        visible_source_pixels_per_native_canvas_pixel=ratio, meets_4x_source_rule=True,
        native_review_path=native_path.relative_to(ROOT).as_posix(), native_review_sha256=SHA(native_path),
        native_source_region_all_nonzero_alpha=list(region), native_resize_size=size, native_offset=offset, native_uniform_scale=scale,
        footprint_64px_cells=None, footprint_status='needs_scene_annotation; projected sprite bounds are not a ground footprint',
        collision_polygon=None, collision_status='integration agent annotates physical base; never full sprite box',
        mount_points=None, mount_status='stairs top sockets require scene annotation' if key=='stairs' else 'not applicable',
        baked_shadow=False, separate_shadow_path=None, shadow_status='runtime/integration responsibility',
        style_matches=['assets_hd/furniture/table_large/table_large_01.png','assets_hd/furniture/bench_plain/bench_plain_01.png'] if art in ['ART-0019','ART-0039'] else ['assets_hd/props/vase_blue/vase_blue_01.png','assets_hd/plants/flowers_white/flowers_white_01.png'] if key=='plant' else ['assets_hd/architecture/stone_block','assets_hd/architecture/connected_ruin_walls/v001'],
        prompt_path=prompt_path.relative_to(ROOT).as_posix(), prompt_text=records['prompts'][prompt_key],
        source_attempt_name=records['selection'][key], tool='built-in image_gen', generation_model='unknown',
        independent_generation=True, bitmap_flip_or_rotation=False, source_upscaled=False,
        quality_status='needs_review', owner_approved=False, production_active=False, open_issues=issues)
    groups.setdefault(art, []).append(item)

for art, items in groups.items():
    review = ROOT / 'game_factory/environment' / art / 'v001'
    rejected = []
    for directory in {str((ROOT/i['master_path']).parent/'rejected') for i in items}:
        for p in sorted(Path(directory).glob('*.png')):
            im = Image.open(p)
            rejected.append(dict(path=p.relative_to(ROOT).as_posix(), sha256=SHA(p), pixel_size=list(im.size),
                reason='Nonzero pale backdrop alpha and missing transparent cutout' if art=='ART-0019' else 'Leaf tips too near left boundary; reframed by separate edit request', quality_status='needs_regeneration'))
    manifest = dict(schema_version=1, request_id=art, task_id='TASK-0135', batch='B1', agent='codex',
        tool='built-in image_gen', model='unknown', reference_path=target, reference_sha256=SHA(ROOT/target),
        reference_use='style/composition only; no crop/paste/trace', source_count=len(items),
        generation_cache_required=False, owner_approved=False, production_active=False, quality_status='needs_review',
        items=items, rejected_attempts=rejected)
    if art == 'ART-0025':
        archive = ROOT / '.agents/graphics/deliveries/ART-0025/archive_pre_B1_20261110'
        old = json.loads((archive/'manifest.json').read_text(encoding='utf-8', newline='\n'))
        legacy = old['files']
        for entry in legacy:
            archived_png = archive / Path(entry['path']).name
            if archived_png.exists():
                entry['path'] = archived_png.relative_to(ROOT).as_posix()
        manifest['files'] = legacy
        manifest['legacy_candidate_compatibility'] = 'files retains archived Blender candidate for immutable v4 review; items contains the new unapproved image_gen delivery. Do not substitute old anchors onto new art.'
    for path in [review/'manifest.json', ROOT/'.agents/graphics/deliveries'/art/'manifest.json']:
        path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
    lines = ['# '+art+' — تسليم B1', '', 'المصادر مستقلة ولم تُكبّر أو تُعكس. نسخ native_review مشتقات QA بملاءمة موحدة وNearest Neighbor لحدود ألفا غير الصفرية مع حفظ كل بكسل مرئي؛ ليست ملفات دمج معتمدة.',
        '', 'الحالة needs_review. اعتماد المالك وتكامل Claude ومعايرة footprint والتصادم ونقاط تركيب السلم لم تتم. لا يجوز اعتماد مساحة الصورة كمساحة تصادم. المرجع للتكوين والأسلوب فقط.', '', '| الملف | SHA-256 | الأبعاد |', '|---|---|---|']
    for i in items:
        lines.append('| '+i['master_path']+' | '+i['sha256']+' | '+str(i['pixel_size'])+' |')
    lines += ['', '## النواقص المرصودة']
    for i in items:
        for issue in i['open_issues']: lines.append('- '+i['id']+': '+issue)
    lines += ['', 'لكل مصدر نسبة تفاصيل أكبر من 4x لحجم Canvas المقترح، لكن بعض الأبعاد المطلقة أقل من حد المواصفة. لم يُخفَ ذلك بتكبير المصدر. يلزم قرار المالك أو إعادة توليد بدقة أعلى قبل إعلان استيفاء المواصفة بالكامل.', '', 'التقاط Godot: godot_native_review.png وإيصال godot_review_receipt.json بعد تشغيل سكربت المعاينة المسجل. الأشكال على لوح مراجعة فقط؛ لم تتغير أي خريطة.']
    (review/'README.md').write_text('\n'.join(lines)+'\n', encoding='utf-8', newline='\n')

summary = dict(task_id='TASK-0135', batch='B1', independent_masters=len(specs), rejected_attempts=2,
    all_rgba=True, all_real_alpha=True, all_visible_bounds_inside=True, all_over_4x=True,
    unique_master_hashes=len({i['sha256'] for items in groups.values() for i in items}),
    exact_master_minimum_met=False, owner_approved=False,
    manifests=['game_factory/environment/'+a+'/v001/manifest.json' for a in groups])
(BASE/'technical_qa.json').write_text(json.dumps(summary, indent=2)+'\n', encoding='utf-8', newline='\n')
print(json.dumps(summary, indent=2))
