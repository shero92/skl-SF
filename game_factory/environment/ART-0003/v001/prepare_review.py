"""Measure four independently drawn sources; fixed-canvas QA derivatives only."""
from pathlib import Path
import hashlib
import json
import shutil
from PIL import Image, ImageChops, ImageStat

ROOT = Path(__file__).resolve().parents[4]
BASE = Path(__file__).resolve().parent
MASTER = ROOT / 'assets_hd/background/cliff_foam_loop/v001'
DELIVERY = ROOT / '.agents/graphics/deliveries/ART-0003'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
write = lambda p, d: p.write_text(json.dumps(d, indent=2, ensure_ascii=False)+'\n', encoding='utf-8', newline='\n')
records = json.loads((BASE/'generation_records.json').read_text(encoding='utf-8'))
items, reviews, ridge_rows = [], [], []
for suffix in ['01', '02', '03', '04']:
    name = 'hero_cliff_foam_' + suffix
    source = MASTER / (name+'.png')
    im = Image.open(source)
    assert im.mode == 'RGBA' and im.size == (1774, 887)
    a = im.getchannel('A')
    bounds = a.point(lambda v: 255 if v >= 128 else 0).getbbox()
    assert bounds and a.getextrema()[0] == 0
    x0,y0,x1,y1 = bounds
    assert x0 > 0 and y0 > 0 and x1 < im.width and y1 < im.height
    pixels = im.load()
    ridge = max(range(240, 300), key=lambda y: sum(min(pixels[x,y][:3]) > 205 and pixels[x,y][3] > 220 for x in range(150,1624)))
    ridge_rows.append(ridge)
    # Whole canvas uniformly resized; no per-frame bbox normalization or translation.
    review = im.resize((96,48), Image.Resampling.NEAREST)
    reviews.append(review)
    target = BASE/'native_review'/(name+'.png')
    target.parent.mkdir(exist_ok=True)
    review.save(target)
    prompt = BASE/'requests'/(name+'.txt')
    prompt.parent.mkdir(exist_ok=True)
    prompt.write_text(records['prompts'][suffix],encoding='utf-8',newline='\n')
    DELIVERY.mkdir(parents=True,exist_ok=True)
    dest = DELIVERY / source.name
    assert not dest.exists() or sha(dest) == sha(source)
    shutil.copy2(source,dest)
    items.append(dict(id=name,request_id='ART-0003',master_path=source.relative_to(ROOT).as_posix(),
        delivery_path=dest.relative_to(ROOT).as_posix(),sha256=sha(source),pixel_size=list(im.size),mode=im.mode,
        alpha_extrema=list(a.getextrema()),bounds_alpha_128=list(bounds),origin=[(x0+x1)/2,y1-1],
        origin_rule='bottom centre of visible alpha128 bounds; do NOT use to align animated frames',
        contact_anchor=[887,280],contact_anchor_rule='fixed canvas registration near measured white crest row280-281; map mount still provisional',
        measured_white_crest_row=ridge,facing='three-quarter top-down horizontal cliff contact strip',
        frame_order=int(suffix)-1,frame_duration_ms=250,native_canvas=[96,48],native_width=96,native_height=48,
        native_review_path=target.relative_to(ROOT).as_posix(),native_review_sha256=sha(target),
        native_source_region=[0,0,1774,887],uniform_scale=96/1774,source_pixels_per_native_pixel=1774/96,
        independent_generation=True,source_generation_mode='individual_request',tool='built-in image_gen',model='unknown',
        edit_reference_id=records['image_edit_dependencies'].get(suffix),bitmap_flip_or_rotation=False,source_upscaled=False,
        prompt_text=records['prompts'][suffix],prompt_path=prompt.relative_to(ROOT).as_posix(),
        collision=False,cast_shadow=False,baked_shadow=False,footprint_64px_cells=None,
        footprint_status='not applicable to non-colliding water overlay',mount_on='cliff-base contact; exact terrain offset uncalibrated',
        quality_status='needs_map_calibration',owner_approved=True,approval_basis='owner_automatic_20261111',production_active=False))
assert len({i['sha256'] for i in items}) == 4
reference=ROOT/'map_factory/references/hero_room_01_target_20261110.webp'
assert sha(reference)=='4e55aeaa5a5e500760f48fed75c3ce7f6d56d55c1ca06b8c70839cce517e4323'
manifest=dict(request_id='ART-0003',task_id='TASK-0014',delivery_branch='codex/hero-room-cliff-foam',agent='codex',tool='built-in image_gen',model='unknown',
    source_count=4,quality_status='needs_map_calibration',owner_approved=True,approval_basis='owner_automatic_20261111',
    production_active=False,generation_cache_required=False,reference_path=reference.relative_to(ROOT).as_posix(),reference_sha256=sha(reference),
    reference_use='style/composition only, never pasted/cropped/traced',style_references=records['style_references'],items=items,rejected_attempts=[],
    animation=dict(frame_ids=[i['id'] for i in items],fps=4,frame_duration_ms=250,cycle_duration_ms=1000,
                   cadence_source='map_factory/maps/hero_room_01/latest.json ocean.fps=4',loop=True,
                   registration='identical full source canvas, no per-frame bbox fit'),
    limitations=['96x48 native canvas remains provisional until cliff terrain integration.',
                 'No room placement, terrain occlusion, ocean blending or runtime map activation tested.',
                 'Four authored phases at4fps; visible shape/mass changes are not optical-flow interpolation.'])
write(BASE/'manifest.json',manifest)
write(DELIVERY/'manifest.json',manifest)
metrics=[]
for i in range(4):
    b1=Image.new('RGBA',(96,48),(15,100,160,255));b1.alpha_composite(reviews[i])
    b2=Image.new('RGBA',(96,48),(15,100,160,255));b2.alpha_composite(reviews[(i+1)%4])
    metrics.append(dict(from_frame=i,to_frame=(i+1)%4,mean_rgb_abs_difference=ImageStat.Stat(ImageChops.difference(b1.convert('RGB'),b2.convert('RGB'))).mean))
sheet=Image.new('RGBA',(384,48))
for i,im in enumerate(reviews):sheet.paste(im,(i*96,0))
sheet.save(BASE/'native_frames_strip.png')
write(BASE/'technical_qa.json',dict(rgba=True,unique_source_hashes=4,equal_canvases=True,
    source_pixels_per_native_pixel=1774/96,real_alpha0=True,alpha128_bounds_inside=True,
    white_crest_rows=ridge_rows,crest_registration_spread_native_px=(max(ridge_rows)-min(ridge_rows))*96/1774,
    adjacent_composited_differences=metrics,metrics_are_not_visual_approval=True,
    owner_approved=True,approval_basis='owner_automatic_20261111',production_active=False))
print('ART0003: four unique RGBA sources; fixed native96x48; crest spread', (max(ridge_rows)-min(ridge_rows))*96/1774)
