"""Read-only technical rejection evidence and review-only native tiles; never repair a failed source."""
from pathlib import Path
import hashlib
import json
import shutil
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
source_dir = ROOT/'assets_hd/background/sea_light_lattice/v001/rejected'
review = ROOT/'game_factory/environment/ART-0037/v001'
delivery = ROOT/'.agents/graphics/deliveries/ART-0037/rejected'
(review/'native_review').mkdir(parents=True, exist_ok=True)
(review/'requests').mkdir(exist_ok=True)
(review/'.gdignore').write_text('')
delivery.mkdir(parents=True, exist_ok=True)
records = json.loads((BASE/'generation_records.json').read_text(encoding='utf-8'))
attempts = []
for index in [1,2]:
    path = source_dir/f'sea_light_lattice_tile_attempt_{index:02d}.png'
    im = Image.open(path)
    assert im.mode == 'RGBA'
    a = np.asarray(im.getchannel('A')).astype(float)
    rgba = np.asarray(im).astype(float)
    premult = rgba[:,:,:3] * (a[:,:,None]/255)
    left_right = float(np.abs(premult[:,0]-premult[:,-1]).mean())
    top_bottom = float(np.abs(premult[0]-premult[-1]).mean())
    local_x = float(np.abs(premult[:,1:]-premult[:,:-1]).mean())
    local_y = float(np.abs(premult[1:]-premult[:-1]).mean())
    failures = []
    if im.width < 2048 or im.height < 2048:
        failures.append('Master below required 2048x2048 and below 4x the 512x512 display tile.')
    if a.max() > 178:
        failures.append('Alpha exceeds specified 70 percent maximum (178/255).')
    if a.min() != 0:
        failures.append('No fully transparent gap pixels.')
    failures.append('Seamless continuity is not verified; 2x2 actual Godot capture and boundary-jump metrics are evidence, not approval.')
    prompt = records['prompts']['sea_lattice' if index==1 else 'sea_lattice_retry']
    prompt_path = review/'requests'/f'sea_light_lattice_tile_attempt_{index:02d}.txt'
    prompt_path.write_text(prompt, encoding='utf-8', newline='\n')
    native = review/'native_review'/path.name
    im.resize((512,512),Image.Resampling.NEAREST).save(native)
    shutil.copy2(path,delivery/path.name)
    bbox = im.getchannel('A').point(lambda x:255 if x>=128 else 0).getbbox()
    attempts.append(dict(request_id='ART-0037', id=path.stem, source_path=path.relative_to(ROOT).as_posix(),
        sha256=sha(path), pixel_size=list(im.size), mode=im.mode, alpha_extrema=[int(a.min()),int(a.max())],
        bounds_alpha_128=list(bbox), origin=[im.width/2,im.height-1], origin_rule='tile canvas bottom centre; tile edges intentionally continue',
        tool='built-in image_gen', model='unknown', prompt_text=prompt, prompt_path=prompt_path.relative_to(ROOT).as_posix(),
        independent_generation=True, source_upscaled=False, footprint_64px_cells=None, footprint_status='not annotated; candidate rejected',
        collision=False, shadow=False, requested_native_size=[512,512], source_pixels_per_native_pixel=im.width/512,
        native_review_path=native.relative_to(ROOT).as_posix(), native_review_sha256=sha(native),
        boundary_metrics=dict(left_right_premult_rgb_abs_mean=left_right,top_bottom_premult_rgb_abs_mean=top_bottom,
            local_horizontal_abs_mean=local_x,local_vertical_abs_mean=local_y,
            alpha_above_178_fraction=float((a>178).mean()),alpha_zero_fraction=float((a==0).mean())),
        quality_status='needs_regeneration', failures=failures, owner_approved=False, production_active=False))
manifest = dict(request_id='ART-0037',task_id='TASK-0016',batch='B3',status='requested',quality_status='needs_regeneration',
    source_count=0,candidate_count=2,items=[],rejected_attempts=attempts, owner_approved=False,production_active=False,
    exact_requested_delivery_png=None, generation_cache_required=False,
    reference_path='map_factory/references/hero_room_01_target_20261110.webp',
    reference_sha256=sha(ROOT/'map_factory/references/hero_room_01_target_20261110.webp'),
    note='Neither attempt satisfies the hard size/alpha requirements. No delivered production tile, no upscaling or procedural substitute.')
for p in [review/'manifest.json',delivery.parent/'manifest.json']:
    p.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
(review/'README.md').write_text('# ART-0037 — غير مكتمل\n\nمحاولتان مستقلتان محفوظتان في rejected، ولا ملف إنتاجي معتمد أو مسلّم. الأداة أعادت1254x1254 في المحاولتين بدل2048x2048، وتجاوزت بعض قيم ألفا178. لم يُستخدم تكبير أو بديل إجرائي. الطلب يبقى requested / needs_regeneration.\n\nمعاينة Godot تعرض2x2 بحجم512 للبلاطة فوق مشتق QA من بحر المشروع؛ لا تثبت اللقطة استيفاء الحجم أو الموافقة. مقاييس القفز بين الحواف في manifest للمراجعة، وليست شهادة seamless.\n',encoding='utf-8',newline='\n')
print('ART-0037: 2 rejected candidates; no valid delivered tile')
