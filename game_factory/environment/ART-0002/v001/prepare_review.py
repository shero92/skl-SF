"""Measure independently generated rugs; all resizing is confined to QA derivatives."""
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
for kind,canvas in [('01',[192,64]),('02',[192,64]),('03',[192,64])]:
    name = 'hero_cloud_'+kind
    master = ROOT/'assets_hd/background/drifting_clouds/v001'/(name+'.png')
    im = Image.open(master)
    assert im.mode == 'RGBA'
    alpha = im.getchannel('A')
    bounds = alpha.point(lambda a:255 if a>=128 else 0).getbbox()
    assert bounds and alpha.getextrema()[0]==0
    x0,y0,x1,y1 = bounds
    assert 0<x0<x1<im.width and 0<y0<y1<im.height
    region = [max(0,x0-8),max(0,y0-8),min(im.width,x1+8),min(im.height,y1+8)]
    visible = im.crop(region)
    scale = min(canvas[0]/visible.width,canvas[1]/visible.height)
    assert 1/scale>=4, (name,1/scale)
    resized = [round(visible.width*scale),round(visible.height*scale)]
    offset = [(canvas[0]-resized[0])//2,canvas[1]-resized[1]]
    native = Image.new('RGBA',canvas)
    native.paste(visible.resize(resized,Image.Resampling.NEAREST),offset)
    out = BASE/'native_review'/(name+'.png')
    out.parent.mkdir(exist_ok=True)
    native.save(out)
    request = BASE/'requests'/(name+'.txt')
    request.write_text(records['prompts'][kind],encoding='utf-8',newline='\n')
    delivery = ROOT/'.agents/graphics/deliveries/ART-0002'
    delivery.mkdir(parents=True,exist_ok=True)
    dest = delivery/master.name
    assert not dest.exists() or sha(dest)==sha(master), 'Different prior delivery must be preserved first'
    shutil.copy2(master,dest)
    items.append(dict(id=name,request_id='ART-0002',master_path=master.relative_to(ROOT).as_posix(),
        delivery_path=dest.relative_to(ROOT).as_posix(),sha256=sha(master),pixel_size=list(im.size),mode=im.mode,
        alpha_extrema=list(alpha.getextrema()),bounds_alpha_128=list(bounds),origin=[(x0+x1)/2,y1-1],
        origin_rule='bottom centre of alpha-128 visible bounds',facing='non-directional background silhouette',
        tool='built-in image_gen',model='unknown',independent_generation=True,source_upscaled=False,bitmap_flip_or_rotation=False,
        prompt_text=records['prompts'][kind],prompt_path=request.relative_to(ROOT).as_posix(),
        footprint_64px_cells=None,footprint_status='not applicable: non-colliding sky background',
        collision=False,cast_shadow=False,baked_shadow=False,mount_points=None,
        native_canvas=canvas,native_review_path=out.relative_to(ROOT).as_posix(),native_review_sha256=sha(out),
        native_source_region=region,native_review_note='QA alpha128 plus8px; weak alpha outside may be omitted; full master preserved',
        resized_size=resized,offset=offset,uniform_scale=scale,source_pixels_per_visible_pixel=1/scale,
        projected_visible_aspect=(x1-x0)/(y1-y0),quality_status='needs_review',owner_approved=False,production_active=False))
assert len({i['sha256'] for i in items})==3
reference = ROOT/'map_factory/references/hero_room_01_target_20261110.webp'
assert sha(reference)=='4e55aeaa5a5e500760f48fed75c3ce7f6d56d55c1ca06b8c70839cce517e4323'
manifest=dict(request_id='ART-0002',task_id='TASK-0013',agent='codex',tool='built-in image_gen',model='unknown',
    source_count=3,quality_status='needs_review',owner_approved=False,production_active=False,generation_cache_required=False,
    reference_path=reference.relative_to(ROOT).as_posix(),reference_sha256=sha(reference),reference_use='style/composition only; never pasted/cropped/traced',
    style_references=records['style_references'],items=items,rejected_attempts=records.get('rejected_attempts',[]),
    limitations=['Native192x64 is a provisional QA canvas; uniform fit preserves cloud proportions.',
                 'Runtime scrolling, wrap spacing/edge popping and owner approval remain pending. No collider/shadow.'])
for p in [BASE/'manifest.json',ROOT/'.agents/graphics/deliveries/ART-0002/manifest.json']:
    p.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
(BASE/'technical_qa.json').write_text(json.dumps(dict(independent_sources=3,unique_hashes=3,rgba=True,real_alpha=True,
    visible_bounds_inside=True,all_reviews_at_least_4x=True,owner_approved=False),indent=2)+'\n',encoding='utf-8',newline='\n')
print('ART-0002 three independent sources verified; native QA derivatives generated')
