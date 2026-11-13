"""Immutable-source audit and mechanical RGBA/native exports; no artwork synthesis."""
from pathlib import Path
import hashlib
import json
import shutil
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[4]
BASE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
records=json.loads((BASE/'generation_records.json').read_text(encoding='utf-8'))
records['prompts']['marker_active']=(BASE/'active_fix_prompt.txt').read_text(encoding='utf-8').strip()
specs=[('field_grass_a','floor/skirmish_field',[64,64],[512,512]),
       ('field_grass_b','floor/skirmish_field',[64,64],[512,512]),
       ('field_rock_block','props/skirmish_rock',[64,96],[512,768]),
       ('marker_move','decor/skirmish_markers',[64,64],[512,512]),
       ('marker_target','decor/skirmish_markers',[64,64],[512,512]),
       ('marker_active','decor/skirmish_markers',[64,64],[512,512])]
delivery=ROOT/'.agents/graphics/deliveries/ART-0041';delivery.mkdir(parents=True,exist_ok=True)
items=[];native_images={}
def core_runs(values):
    groups=[];run=[]
    for x in np.flatnonzero(values>=128).tolist():
        if run and x!=run[-1]+1:groups.append(run);run=[]
        run.append(x)
    if run:groups.append(run)
    return groups
for name,group,canvas,minimum in specs:
    master=ROOT/'assets_hd'/group/'v001'/(name+'.png')
    im=Image.open(master);assert im.mode=='RGBA' and im.width>=minimum[0] and im.height>=minimum[1]
    alpha=im.getchannel('A');bounds=alpha.point(lambda a:255 if a>=128 else 0).getbbox();assert bounds
    floor=name.startswith('field_grass')
    if floor:
        generation=BASE/'generation_sources'/(name+'_rgb.png')
        original=Image.open(generation)
        assert original.mode=='RGB' and original.size==im.size and original.tobytes()==im.convert('RGB').tobytes()
        assert alpha.getextrema()==(255,255)
    else:
        generation=master;assert alpha.getextrema()[0]==0
        assert bounds[0]>0 and bounds[1]>0 and bounds[2]<im.width and bounds[3]<im.height
    phase=[0,0];region=[0,0,im.width,im.height];offset=[0,0]
    if name=='field_rock_block':
        region=[max(0,bounds[0]-8),max(0,bounds[1]-8),min(im.width,bounds[2]+8),min(im.height,bounds[3]+8)]
        crop=im.crop(region);scale=min(canvas[0]/crop.width,canvas[1]/crop.height)
        size=[round(crop.width*scale),round(crop.height*scale)];offset=[(canvas[0]-size[0])//2,canvas[1]-size[1]]
        native=Image.new('RGBA',canvas);native.paste(crop.resize(size,Image.Resampling.NEAREST),offset)
        density=min(crop.width/size[0],crop.height/size[1])
    else:
        if name=='marker_active':
            # Native pixel-grid alignment only: trim two completely empty source rows/columns,
            # pad two empty rows/columns on the opposite side. Master pixels are never rewritten.
            assert alpha.crop((0,0,2,im.height)).getextrema()[1]==0
            assert alpha.crop((0,0,im.width,2)).getextrema()[1]==0
            phase=[2,2];region=[2,2,im.width+2,im.height+2]
        native=im.crop(region).resize(canvas,Image.Resampling.NEAREST)
        density=min(im.width/canvas[0],im.height/canvas[1])
    assert density>=4
    native_path=BASE/'native_review'/(name+'.png');native_path.parent.mkdir(exist_ok=True);native.save(native_path)
    native_images[name]=native
    prompt_path=BASE/'requests'/(name+'.txt');prompt_path.parent.mkdir(exist_ok=True)
    prompt_path.write_text(records['prompts'][name],encoding='utf-8',newline='\n')
    out=delivery/(name+'.png');assert not out.exists() or sha(out)==sha(master);shutil.copy2(master,out)
    item=dict(id=name,request_id='ART-0041',master_path=master.relative_to(ROOT).as_posix(),delivery_path=out.relative_to(ROOT).as_posix(),
        sha256=sha(master),pixel_size=list(im.size),mode=im.mode,alpha_extrema=list(alpha.getextrema()),bounds_alpha_128=list(bounds),
        origin=[(bounds[0]+bounds[2])/2,bounds[3]-1],origin_rule='bottom centre of alpha128 visible bounds',
        generation_source_path=generation.relative_to(ROOT).as_posix(),generation_source_sha256=sha(generation),
        generation_source_mode='RGB' if floor else 'RGBA',format_only_RGBA_export=floor,RGB_pixels_unchanged=True,
        native_canvas=canvas,native_width=canvas[0],native_height=canvas[1],native_review_path=native_path.relative_to(ROOT).as_posix(),
        native_review_sha256=sha(native_path),native_source_region=region,native_alignment_phase_source_px=phase,
        native_offset=offset,native_method='nearest-neighbour export; original master retained',source_pixels_per_native_pixel=density,
        floor_surface_opaque=floor,grid_anchor_native=[0,0],facing='flat top-down tile/overlay' if name!='field_rock_block' else 'three-quarter top-down rock, upper-left light',
        collision=False,base_cell_canvas=[64,64],logical_blocking=(name=='field_rock_block'),
        collision_note='Battle grid owns impassability; no new physics or gameplay rule in asset',
        draw_offset_native=[0,-32] if name=='field_rock_block' else [0,0],cast_shadow=False,baked_shadow=False,
        runtime_opacity_recommendation=0.75 if name.startswith('marker_') else 1.0,
        prompt_text=records['prompts'][name],prompt_path=prompt_path.relative_to(ROOT).as_posix(),tool='built-in image_gen',model='unknown',
        independent_generation=True,bitmap_flip_or_rotation=False,source_upscaled=False,owner_approved=True,
        approval_basis='owner_automatic_20261111',quality_status='needs_runtime_integration',production_active=False,
        import_recommendation=dict(compression='lossless',mipmaps=False,texture_filter='nearest'))
    if name.startswith('marker_'):
        a=np.asarray(native.getchannel('A'));xr=core_runs(a[32]);yr=core_runs(a[:,32])
        assert [len(r) for r in xr]==[2,2] and [len(r) for r in yr]==[2,2],(name,xr,yr)
        assert a[32,32]==0
        item.update(nominal_border_native_px=2,measured_alpha128_horizontal_core_runs=xr,
                    measured_alpha128_vertical_core_runs=yr,centre_alpha=0,
                    alignment_note='active ring uses2sourcepx sampling phase, with proof discarded rows/cols alpha0; no visible source pixel clipped')
    items.append(item)
seams=[]
for first in ['field_grass_a','field_grass_b']:
    a=np.asarray(native_images[first])[:,:,:3].astype(float)
    interior=float((abs(a[:,1:]-a[:,:-1]).mean()+abs(a[1:]-a[:-1]).mean())/2)
    for second in ['field_grass_a','field_grass_b']:
        b=np.asarray(native_images[second])[:,:,:3].astype(float)
        x=float(abs(a[:,-1]-b[:,0]).mean());y=float(abs(a[-1]-b[0]).mean())
        assert max(x,y)<=interior*1.5,(first,second,x,y,interior)
        seams.append(dict(first=first,second=second,seam_x_mean_abs=x,seam_y_mean_abs=y,interior_mean_abs=interior,
                          note='numeric evidence only; native checkerboard still reviewed in Godot'))
old=ROOT/'assets_hd/decor/skirmish_markers/v001/rejected/marker_active_attempt_01.png'
old_im=Image.open(old);old_alpha=old_im.getchannel('A')
old_prompt=BASE/'requests/marker_active_initial.txt';old_prompt.write_text(records['prompts']['marker_active_initial'],encoding='utf-8',newline='\n')
rejected=[dict(id='marker_active_attempt_01',path=old.relative_to(ROOT).as_posix(),sha256=sha(old),pixel_size=list(old_im.size),mode=old_im.mode,
    alpha_extrema=list(old_alpha.getextrema()),bounds_alpha_128=list(old_alpha.point(lambda a:255 if a>=128 else 0).getbbox()),
    quality_status='not_selected',reason='Initial native nearest sampling left a1px cardinal side. Corrected source plus explicit empty-margin sampling alignment selected.',
    prompt_path=old_prompt.relative_to(ROOT).as_posix(),prompt_text=records['prompts']['marker_active_initial'])]
reference=ROOT/'map_factory/references/hero_room_01_target_20261110.webp'
assert sha(reference)=='4e55aeaa5a5e500760f48fed75c3ce7f6d56d55c1ca06b8c70839cce517e4323'
manifest=dict(request_id='ART-0041',task_id='TASK-0161',delivery_branch='codex/art-0041-skirmish-tiles',agent='codex',tool='built-in image_gen',model='unknown',
    source_count=6,generation_count=7,items=items,rejected_attempts=rejected,files=[dict(path=i['delivery_path'],sha256=i['sha256']) for i in items],
    reference_path=reference.relative_to(ROOT).as_posix(),reference_sha256=sha(reference),reference_use='style only; new battlefield designs, no source crop pasted',
    owner_approved=True,approval_basis='owner_automatic_20261111',quality_status='needs_runtime_integration',production_active=False,generation_cache_required=False,
    limitations=['QA-only scene override, no production battle code or damage/navigation rules changed.',
                 'Grass opaque RGBA floor exception; RGB generation files preserved with exact RGB-byte equality.',
                 'Marker frames have measured64x64 padding; use whole canvas at cell top-left, no per-frame alpha-bbox fit.'])
assert len({i['sha256'] for i in items})==6
write(BASE/'manifest.json',manifest);write(delivery/'manifest.json',manifest)
write(BASE/'technical_qa.json',dict(minimum_master_sizes_passed=True,all_native_density_at_least4x=True,unique_selected_masters=6,
    RGB_floor_exports_exact=True,floors_alpha255=True,markers_cardinal_strokes_2px=True,markers_centre_alpha0=True,
    seam_metrics=seams,owner_approved=True,production_active=False))
print('ART0041:6RGBA masters,7calls,2RGB-preserving exports; native marker cardinal strokes2px; seam metrics recorded.')
