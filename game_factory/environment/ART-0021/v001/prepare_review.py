"""Measure independent chest sources and build QA derivatives only. Masters are immutable."""
from pathlib import Path
import hashlib
import json
import shutil
from PIL import Image

ROOT = Path(__file__).resolve().parents[4]
BASE = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
records = json.loads((BASE/'generation_records.json').read_text(encoding='utf-8'))
items = []
for facing in ['south','north','east','west']:
    name = 'hero_study_chest_'+facing
    master = ROOT/'assets_hd/furniture/study_chest_views/v001'/(name+'.png')
    im = Image.open(master)
    assert im.mode == 'RGBA'
    alpha = im.getchannel('A')
    bounds = alpha.point(lambda a:255 if a>=128 else 0).getbbox()
    assert bounds and alpha.getextrema()[0] == 0
    x0,y0,x1,y1 = bounds
    assert 0 < x0 < x1 < im.width and 0 < y0 < y1 < im.height
    region = [max(0,x0-8),max(0,y0-8),min(im.width,x1+8),min(im.height,y1+8)]
    visible = im.crop(region)
    reviews = []
    for suffix, canvas in [('placement',[58,73]),('catalog',[191,157])]:
        scale = min(canvas[0]/visible.width,canvas[1]/visible.height)
        assert 1/scale >= 4
        resized = [round(visible.width*scale),round(visible.height*scale)]
        offset = [(canvas[0]-resized[0])//2,canvas[1]-resized[1]]
        native = Image.new('RGBA',canvas)
        native.paste(visible.resize(resized,Image.Resampling.NEAREST),offset)
        out = BASE/'native_review'/(name+'_'+suffix+'.png')
        out.parent.mkdir(exist_ok=True)
        native.save(out)
        reviews.append(dict(kind=suffix,path=out.relative_to(ROOT).as_posix(),sha256=sha(out),canvas=canvas,
            resized_size=resized,offset=offset,uniform_scale=scale,source_pixels_per_visible_pixel=1/scale))
    request = BASE/'requests'/(name+'.txt')
    request.write_text(records['prompts'][facing],encoding='utf-8',newline='\n')
    delivery = ROOT/'.agents/graphics/deliveries/ART-0021'
    delivery.mkdir(parents=True,exist_ok=True)
    dest = delivery/master.name
    assert not dest.exists() or sha(dest)==sha(master), 'Never overwrite a prior different delivery'
    shutil.copy2(master,dest)
    items.append(dict(id=name,request_id='ART-0021',master_path=master.relative_to(ROOT).as_posix(),
        delivery_path=dest.relative_to(ROOT).as_posix(),sha256=sha(master),pixel_size=list(im.size),mode=im.mode,
        alpha_extrema=list(alpha.getextrema()),bounds_alpha_128=list(bounds),origin=[(x0+x1)/2,y1-1],
        origin_rule='bottom centre of alpha-128 visible bounds',facing=facing,
        tool='built-in image_gen',model='unknown',independent_generation=True,source_upscaled=False,
        bitmap_flip_or_rotation=False,prompt_text=records['prompts'][facing],prompt_path=request.relative_to(ROOT).as_posix(),
        footprint_64px_cells=None,footprint_status='needs scene calibration; projected image bounds are not floor footprint',
        collision_polygon=None,collision_status='annotate base only at integration',baked_shadow=False,mount_points=None,
        native_review_region=region,native_review_note='QA alpha128 bounds plus8px; weak alpha outside may be omitted; master unchanged',
        reviews=reviews,quality_status='needs_review',owner_approved=False,production_active=False,
        style_reference='assets_hd/furniture/crate/crate_01.png'))
assert len({i['sha256'] for i in items})==4
reference = ROOT/'map_factory/references/hero_room_01_target_20261110.webp'
assert sha(reference)=='4e55aeaa5a5e500760f48fed75c3ce7f6d56d55c1ca06b8c70839cce517e4323'
manifest=dict(request_id='ART-0021',task_id='TASK-0032',agent='codex',tool='built-in image_gen',model='unknown',
    source_count=4,quality_status='needs_review',owner_approved=False,production_active=False,generation_cache_required=False,
    reference_path=reference.relative_to(ROOT).as_posix(),reference_sha256=sha(reference),reference_use='style/composition only; never pasted/cropped/traced',
    items=items,rejected_attempts=records.get('rejected_attempts',[]),
    limitations=['58x73 placement and191x157 catalog canvases are provisional; uniform fit preserves source proportions.',
                 'Footprint/collider/depth and exact placement require scene calibration. Owner approval and integration pending.'])
for p in [BASE/'manifest.json',ROOT/'.agents/graphics/deliveries/ART-0021/manifest.json']:
    p.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
(BASE/'technical_qa.json').write_text(json.dumps(dict(independent_sources=4,unique_hashes=4,rgba=True,real_alpha=True,
    visible_bounds_inside=True,all_reviews_at_least_4x=True,owner_approved=False),indent=2)+'\n',encoding='utf-8',newline='\n')
print('ART-0021 four independent sources verified; eight native QA derivatives generated')
