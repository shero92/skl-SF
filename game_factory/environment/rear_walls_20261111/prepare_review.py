"""Measure independent wall masters, preserve them and derive fixed-canvas native QA."""
from pathlib import Path
from collections import deque
import hashlib
import json
import shutil
from PIL import Image

ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
records=json.loads((BASE/'generation_records.json').read_text(encoding='utf-8'))
specs=[('0042','rear_left_window_wall','hero_rear_left_ruined_wall_window',[470,200],[1880,800]),
       ('0043','rear_right_door_niche','hero_rear_right_wall_arched_door_niche',[310,250],[1240,1000])]
all_items=[]
reference=ROOT/'map_factory/references/hero_room_01_target_20261103.png'
assert sha(reference)=='47a7855cf242302108e1a6b9eaf4bfd3422f9f8c812585fa4da5bcaea948668b'
for number,group,name,native_size,minimum in specs:
    art='ART-'+number
    folder=ROOT/'game_factory/environment'/art/'v001'
    folder.mkdir(parents=True,exist_ok=True)
    master=ROOT/'assets_hd/architecture'/group/'v001'/(name+'.png')
    im=Image.open(master)
    assert im.mode=='RGBA' and im.width>=minimum[0] and im.height>=minimum[1]
    alpha=im.getchannel('A');bounds=alpha.point(lambda a:255 if a>=128 else 0).getbbox()
    assert bounds and alpha.getextrema()[0]==0
    x0,y0,x1,y1=bounds
    assert x0>0 and y0>0 and x1<im.width and y1<im.height
    native=im.resize(native_size,Image.Resampling.NEAREST)
    review=folder/'native_review'/(name+'.png');review.parent.mkdir(exist_ok=True);native.save(review)
    prompts=folder/'requests';prompts.mkdir(exist_ok=True)
    prompt=prompts/(name+'.txt')
    prompt.write_text(records['prompts']['final42' if number=='0042' else 'final43'],encoding='utf-8',newline='\n')
    delivery=ROOT/'.agents/graphics/deliveries'/art;delivery.mkdir(parents=True,exist_ok=True)
    dest=delivery/master.name
    assert not dest.exists() or sha(dest)==sha(master) or (number=='0043' and sha(dest)==sha(ROOT/'assets_hd/architecture/rear_right_door_niche/v001/rejected/hero_rear_right_wall_arched_door_niche_attempt_01.png')), 'Never replace an unrelated prior delivery'
    shutil.copy2(master,dest)
    crop=ROOT/'.agents/graphics/requests/reference_crops'/(art+'_target.png')
    compare=ROOT/'.agents/graphics/requests/reference_crops'/(art+'_compare.png')
    assert crop.is_file() and compare.is_file()
    item=dict(id=name,request_id=art,master_path=master.relative_to(ROOT).as_posix(),delivery_path=dest.relative_to(ROOT).as_posix(),
        sha256=sha(master),pixel_size=list(im.size),mode=im.mode,alpha_extrema=list(alpha.getextrema()),bounds_alpha_128=list(bounds),
        origin=[(x0+x1)/2,y1-1],origin_rule='bottom centre of alpha128 visible bounds',facing='south-facing wall; camera south looking north/down',
        native_canvas=native_size,native_width=native_size[0],native_height=native_size[1],
        native_review_path=review.relative_to(ROOT).as_posix(),native_review_sha256=sha(review),native_source_region=[0,0,im.width,im.height],
        source_pixels_per_native_pixel=[im.width/native_size[0],im.height/native_size[1]],
        native_method='whole canvas nearest-neighbour; no crop/flip/rotation/upscale; pixel dimensions rounded',
        prompt_text=records['prompts']['final42' if number=='0042' else 'final43'],prompt_path=prompt.relative_to(ROOT).as_posix(),
        reference_crop_path=crop.relative_to(ROOT).as_posix(),reference_crop_sha256=sha(crop),
        comparison_path=compare.relative_to(ROOT).as_posix(),comparison_sha256=sha(compare),
        tool='built-in image_gen',model='unknown',independent_generation=True,source_upscaled=False,bitmap_flip_or_rotation=False,
        collision=None,collision_status='needs wall navigation annotation at integration',footprint_64px_cells=None,
        connection_sockets=None,connection_status='wall endpoint/arch join calibration not measured',cast_shadow=False,baked_shadow=False,
        owner_approved=True,approval_basis='owner_automatic_20261111',quality_status='needs_map_calibration',production_active=False)
    rejected=[]
    if number=='0042':
        # A bounded low-alpha component proves a real enclosed opening, not a painted sea patch.
        pixels=alpha.load();q=deque([(650,490)]);seen={(650,490)}
        assert pixels[650,490]==0
        while q:
            x,y=q.popleft()
            for nx,ny in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
                if 0<=nx<im.width and 0<=ny<im.height and (nx,ny) not in seen and pixels[nx,ny]<=8:
                    seen.add((nx,ny));q.append((nx,ny))
        xs=[p[0] for p in seen];ys=[p[1] for p in seen]
        hole=[min(xs),min(ys),max(xs)+1,max(ys)+1]
        assert 0<hole[0]<hole[2]<im.width and 0<hole[1]<hole[3]<im.height
        measured=[(hole[2]-hole[0])*native_size[0]/im.width,(hole[3]-hole[1])*native_size[1]/im.height]
        assert 0.9<measured[0]/measured[1]<1.1
        item.update(window_aperture_bounds_alpha_le8=hole,window_aperture_native_extent=measured,
                    window_alpha0_sample=[650,490],window_proof='enclosed alpha<=8 flood component; alpha0 centre',
                    aperture_note='Approximately square44x44 maximum low-alpha extent; request about40x40. Do not report exact40x40.')
        initial=prompts/(name+'_initial.txt');initial.write_text(records['prompts']['initial42'],encoding='utf-8',newline='\n')
        old=ROOT/records['rejected_attempts'][0]['path']
        rejected=[dict(id=name+'_attempt_01',path=old.relative_to(ROOT).as_posix(),sha256=sha(old),pixel_size=list(Image.open(old).size),
            reason=records['rejected_attempts'][0]['reason'],quality_status='not_selected',prompt_path=initial.relative_to(ROOT).as_posix(),
            prompt_text=records['prompts']['initial42'])]
        item['initial_prompt_path']=initial.relative_to(ROOT).as_posix()
    else:
        for attempt in [v for v in records['rejected_attempts'] if v['request_id']=='ART-0043']:
            old=ROOT/attempt['path'];key=attempt['prompt_key']
            old_prompt=prompts/(name+'_'+key+'.txt');old_prompt.write_text(records['prompts'][key],encoding='utf-8',newline='\n')
            rejected.append(dict(id=old.stem,path=attempt['path'],sha256=sha(old),pixel_size=list(Image.open(old).size),
                reason=attempt['reason'],quality_status='not_selected',prompt_path=old_prompt.relative_to(ROOT).as_posix(),prompt_text=records['prompts'][key]))
        niche=[524,584,858,1057]
        item.update(door_niche_bounds_manual=niche,door_niche_bounds_status='manual visual bounding estimate, not collision/interaction geometry',
                    door_niche_native_extent=[(niche[2]-niche[0])*310/im.width,(niche[3]-niche[1])*250/im.height],
                    door_closed=True,material_reference_path=all_items[0]['master_path'],material_reference_sha256=all_items[0]['sha256'])
    for attempt in rejected:
        attempt_im=Image.open(ROOT/attempt['path']);attempt_alpha=attempt_im.getchannel('A')
        attempt.update(mode=attempt_im.mode,alpha_extrema=list(attempt_alpha.getextrema()),
                       bounds_alpha_128=list(attempt_alpha.point(lambda a:255 if a>=128 else 0).getbbox()))
    manifest=dict(request_id=art,task_id='TASK-0156',delivery_branch='codex/art-0042-0043-rear-walls',agent='codex',tool='built-in image_gen',model='unknown',
        source_count=1,generation_count=2 if number=='0042' else 3,owner_approved=True,approval_basis='owner_automatic_20261111',
        quality_status='needs_map_calibration',production_active=False,generation_cache_required=False,
        reference_path=reference.relative_to(ROOT).as_posix(),reference_sha256=sha(reference),
        reference_use='style/composition only; no reference crop pasted/traced as art',items=[item],rejected_attempts=rejected,
        files=[dict(path=dest.relative_to(ROOT).as_posix(),sha256=sha(dest))],
        limitations=['No room placement, collisions, endpoint joins or occlusion verified; source-only Godot review.',
                     'Course counts/block widths are approximate authored geometry; native canvas includes transparent margins.',
                     'Owner main checkout unchanged; files live in isolated task worktree until branch integration.'])
    write(folder/'manifest.json',manifest);write(delivery/'manifest.json',manifest)
    write(folder/'technical_qa.json',dict(rgba=True,minimum_master_passed=True,minimum_source_density_passed=min(item['source_pixels_per_native_pixel'])>=4,
        visible_alpha128_bounds_inside=True,unique_source_sha256=item['sha256'],source_canvas=list(im.size),native_canvas=native_size,
        window_aperture_native_extent=item.get('window_aperture_native_extent'),door_niche_native_extent=item.get('door_niche_native_extent'),
        owner_approved=True,production_active=False,room_integration_verified=False))
    all_items.append(item)
    print(art,im.size,'->',native_size,'source density',item['source_pixels_per_native_pixel'])
assert len({item['sha256'] for item in all_items})==2
write(BASE/'batch_manifest.json',dict(task_id='TASK-0156',delivery_branch='codex/art-0042-0043-rear-walls',sources=all_items,
    generation_count=5,selected_source_count=2,earlier_nonselected_attempts=3,owner_approved=True,production_active=False))
