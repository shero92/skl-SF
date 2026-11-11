"""Audit three independent candidates without hiding the failed4x production gate."""
from pathlib import Path
import hashlib
import json
import shutil
from PIL import Image

ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
records=json.loads((BASE/'generation_records.json').read_text(encoding='utf-8'))
specs=[('ART-0044','curved_west_side_wall','hero_west_curved_side_wall',[230,470],
        [('01','west_initial'),('02','west_retry')],'east/southeast inside face; arc bulges west/left; endpoints right'),
       ('ART-0045','curved_east_side_wall','hero_east_curved_side_wall',[236,540],
        [('01','east_initial')],'west/southwest inside face; arc bulges east/right; endpoints left')]
all_candidates=[]
reference=ROOT/'map_factory/references/hero_room_01_target_20261103.png'
assert sha(reference)=='47a7855cf242302108e1a6b9eaf4bfd3422f9f8c812585fa4da5bcaea948668b'
for art,group,name,canvas,attempts,facing in specs:
    folder=ROOT/'game_factory/environment'/art/'v001';folder.mkdir(parents=True,exist_ok=True)
    delivery=ROOT/'.agents/graphics/deliveries'/art;delivery.mkdir(parents=True,exist_ok=True)
    candidates=[]
    for number,prompt_key in attempts:
        ident=name+'_attempt_'+number
        source=ROOT/'assets_hd/architecture'/group/'v001/rejected'/(ident+'.png')
        im=Image.open(source);assert im.mode=='RGBA'
        alpha=im.getchannel('A');bounds=alpha.point(lambda a:255 if a>=128 else 0).getbbox()
        assert bounds and alpha.getextrema()[0]==0
        x0,y0,x1,y1=bounds;assert x0>0 and y0>0 and x1<im.width and y1<im.height
        density=[im.width/canvas[0],im.height/canvas[1]]
        gate=min(density)>=4
        assert not gate, 'If a source unexpectedly meets4x, review it instead of classifying it rejected.'
        prompt=folder/'requests'/(ident+'.txt');prompt.parent.mkdir(exist_ok=True)
        prompt.write_text(records['prompts'][prompt_key],encoding='utf-8',newline='\n')
        native=folder/'native_review'/(ident+'.png');native.parent.mkdir(exist_ok=True)
        im.resize(canvas,Image.Resampling.NEAREST).save(native)
        dest=delivery/'rejected'/source.name;dest.parent.mkdir(exist_ok=True)
        assert not dest.exists() or sha(dest)==sha(source)
        shutil.copy2(source,dest)
        crop=ROOT/'.agents/graphics/requests/reference_crops'/(art+'_target.png')
        compare=ROOT/'.agents/graphics/requests/reference_crops'/(art+'_compare.png')
        item=dict(id=ident,request_id=art,source_path=source.relative_to(ROOT).as_posix(),delivery_candidate_path=dest.relative_to(ROOT).as_posix(),
            sha256=sha(source),pixel_size=list(im.size),mode=im.mode,alpha_extrema=list(alpha.getextrema()),bounds_alpha_128=list(bounds),
            origin=[(x0+x1)/2,y1-1],origin_rule='bottom centre of alpha128 visible bounds',facing=facing,
            native_canvas=canvas,native_width=canvas[0],native_height=canvas[1],
            native_review_path=native.relative_to(ROOT).as_posix(),native_review_sha256=sha(native),native_source_region=[0,0,im.width,im.height],
            requested_minimum_master=[canvas[0]*4,canvas[1]*4],actual_source_pixels_per_native_pixel=density,
            requested_4x_gate_passed=False,maximum_native_canvas_at4x=[im.width//4,im.height//4],
            maximum_native_note='measurement only; requested canvas is NOT silently reduced',
            alpha128_margins=[x0,y0,im.width-x1,im.height-y1],
            independent_generation=True,source_upscaled=False,bitmap_flip_or_rotation=False,
            tool='built-in image_gen',model='unknown',prompt_text=records['prompts'][prompt_key],prompt_path=prompt.relative_to(ROOT).as_posix(),
            reference_crop_path=crop.relative_to(ROOT).as_posix(),reference_crop_sha256=sha(crop),
            comparison_path=compare.relative_to(ROOT).as_posix(),comparison_sha256=sha(compare),
            collision=None,connection_sockets=None,footprint_64px_cells=None,cast_shadow=False,baked_shadow=False,
            owner_approved=True,approval_basis='owner_automatic_20261111',quality_status='needs_regeneration',production_active=False,
            reason='Below requested4x source density. Native geometry/renderable preview does not waive master resolution. No qualified production output.')
        candidates.append(item);all_candidates.append(item)
        print(art,ident,im.size,'required',item['requested_minimum_master'],'density',density,'QUALIFIED=False')
    manifest=dict(request_id=art,task_id='TASK-0157',delivery_branch='codex/art-0044-0045-side-walls',status='requested',
        agent='codex',tool='built-in image_gen',model='unknown',source_count=0,candidate_count=len(candidates),quality_status='needs_regeneration',
        production_active=False,owner_approved=True,approval_basis='owner_automatic_20261111',generation_cache_required=False,
        reference_path=reference.relative_to(ROOT).as_posix(),reference_sha256=sha(reference),reference_use='style/composition only, no pixels pasted/traced',
        items=[],rejected_attempts=candidates,files=[],
        requested_output_path=(delivery/(name+'.png')).relative_to(ROOT).as_posix(),
        blocker='Built-in outputs below requested4x size despite explicit larger-size retry; no resampling enlargement permitted.',
        limitations=['No qualified production PNG exists at requested output path.',
                     'Collision/joins/room placement and east/west normals require room calibration; no map changed.',
                     'Smaller4x-native footprint numbers are informational, not a change to the owner-approved spec.'])
    write(folder/'manifest.json',manifest);write(delivery/'manifest.json',manifest)
    write(folder/'technical_qa.json',dict(candidate_count=len(candidates),rgba=True,unique_candidate_hashes=len({i['sha256'] for i in candidates}),
        master_4x_gate_passed=False,qualified_production_count=0,owner_approved=True,production_active=False,
        actual_sizes=[i['pixel_size'] for i in candidates],required_minimum=[canvas[0]*4,canvas[1]*4]))
assert len({c['sha256'] for c in all_candidates})==3
write(BASE/'batch_manifest.json',dict(task_id='TASK-0157',generation_count=3,qualified_production_count=0,candidate_count=3,
    request_status='requested',quality_status='needs_regeneration',candidates=all_candidates,source_upscaled=False,
    owner_approved=True,production_active=False))
