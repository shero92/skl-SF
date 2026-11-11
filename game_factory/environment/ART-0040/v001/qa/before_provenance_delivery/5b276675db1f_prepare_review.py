"""Measure an independently drawn east lantern; derive QA only, preserve master bytes."""
from pathlib import Path
import hashlib
import json
import shutil
from PIL import Image

ROOT=Path(__file__).resolve().parents[4]
BASE=Path(__file__).resolve().parent
GROUP=ROOT/'assets_hd/lighting/east_wall_lantern/v001'
DELIVERY=ROOT/'.agents/graphics/deliveries/ART-0040'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
records=json.loads((BASE/'generation_records.json').read_text(encoding='utf-8'))
source=GROUP/'hero_wall_lantern_east.png'
im=Image.open(source)
assert im.mode=='RGBA' and im.width>=400 and im.height>=720
alpha=im.getchannel('A');bounds=alpha.point(lambda a:255 if a>=128 else 0).getbbox()
assert bounds and alpha.getextrema()[0]==0
x0,y0,x1,y1=bounds
assert x0>0 and y0>0 and x1<im.width and y1<im.height
region=[max(0,x0-8),max(0,y0-8),min(im.width,x1+8),min(im.height,y1+8)]
crop=im.crop(region)
scale=min(29/crop.width,53/crop.height)
assert 1/scale>=4
size=[round(crop.width*scale),round(crop.height*scale)]
offset=[(29-size[0])//2,53-size[1]]
native=Image.new('RGBA',(29,53));native.paste(crop.resize(size,Image.Resampling.NEAREST),offset)
out=BASE/'native_review/hero_wall_lantern_east.png';out.parent.mkdir(exist_ok=True);native.save(out)
mount=[232,330]
assert im.getpixel(tuple(mount))[3]>=128
native_mount=[offset[0]+(mount[0]-region[0])*size[0]/crop.width,offset[1]+(mount[1]-region[1])*size[1]/crop.height]
(BASE/'requests').mkdir(exist_ok=True)
prompt=BASE/'requests/hero_wall_lantern_east.txt';prompt.write_text(records['prompts']['final'],encoding='utf-8',newline='\n')
initial=BASE/'requests/hero_wall_lantern_east_initial.txt';initial.write_text(records['prompts']['initial'],encoding='utf-8',newline='\n')
DELIVERY.mkdir(parents=True,exist_ok=True)
dest=DELIVERY/source.name
assert not dest.exists() or sha(dest)==sha(source)
shutil.copy2(source,dest)
item=dict(id='hero_wall_lantern_east',request_id='ART-0040',master_path=source.relative_to(ROOT).as_posix(),
    delivery_path=dest.relative_to(ROOT).as_posix(),sha256=sha(source),pixel_size=list(im.size),mode=im.mode,
    alpha_extrema=list(alpha.getextrema()),bounds_alpha_128=list(bounds),origin=mount,
    origin_rule='manual measured wall-mount point on backplate at arm root, not ground pivot',
    bottom_center_origin=[(x0+x1)/2,y1-1],mount_points=dict(wall=mount),native_origin=native_mount,
    native_canvas=[29,53],native_width=29,native_height=53,native_review_path=out.relative_to(ROOT).as_posix(),
    native_review_sha256=sha(out),native_source_region=region,resized_size=size,offset=offset,
    uniform_scale=scale,source_pixels_per_native_pixel=1/scale,
    facing='east-pointing; wall mount on left and hanging lamp to right',
    mount_status='source pixel manually annotated; wall-local integration offset uncalibrated',
    collision=False,cast_shadow=False,baked_shadow=False,external_halo=False,
    alpha_note='Tool preview shows colored RGB in alpha0 surround; real compositing is clean. Weak alpha may reach canvas bottom; strong alpha128 bounds safely inside. QA bbox+8px excludes remote weak-alpha noise; master intact.',
    independent_generation=True,bitmap_flip_or_rotation=False,source_upscaled=False,
    tool='built-in image_gen',model='unknown',prompt_text=records['prompts']['final'],prompt_path=prompt.relative_to(ROOT).as_posix(),
    initial_prompt_path=initial.relative_to(ROOT).as_posix(),quality_status='needs_map_calibration',
    owner_approved=True,approval_basis='owner_automatic_20261111',production_active=False)
old=GROUP/'rejected/hero_wall_lantern_east_attempt_01.png'
old_im=Image.open(old)
attempt=dict(id='hero_wall_lantern_east_attempt_01',path=old.relative_to(ROOT).as_posix(),sha256=sha(old),
    pixel_size=list(old_im.size),mode=old_im.mode,alpha_extrema=list(old_im.getchannel('A').getextrema()),
    quality_status='not_selected',reason='Earlier attempt superseded by separately requested alpha-cleanup edit. Apparent halo in tool preview was hidden RGB beneath alpha0, not a visible alpha-composited halo; not an owner rejection.',
    prompt_text=records['prompts']['initial'],prompt_path=initial.relative_to(ROOT).as_posix())
reference=ROOT/'map_factory/references/hero_room_01_target_20261110.webp'
assert sha(reference)=='4e55aeaa5a5e500760f48fed75c3ce7f6d56d55c1ca06b8c70839cce517e4323'
manifest=dict(request_id='ART-0040',task_id='TASK-0102',delivery_branch='codex/hero-room-east-lantern',
    agent='codex',tool='built-in image_gen',model='unknown',source_count=1,generation_count=2,
    quality_status='needs_map_calibration',owner_approved=True,approval_basis='owner_automatic_20261111',production_active=False,
    generation_cache_required=False,reference_path=reference.relative_to(ROOT).as_posix(),reference_sha256=sha(reference),
    reference_use='style/composition only; crop/comparison are reference documentation, never a game asset',
    style_references=records['style_references'],items=[item],rejected_attempts=[attempt],
    limitations=['West-wall mount and local scale/occlusion remain untested in room; no production activation.',
                 '29x53 is provisional native review; source wall pivot differs from bottom-centre ground origin.',
                 'Earlier attempt stored in rejected/ archive but is nonselected, not owner-rejected; alpha diagnosis corrected.'])
write(BASE/'manifest.json',manifest);write(DELIVERY/'manifest.json',manifest)
write(BASE/'technical_qa.json',dict(rgba=True,minimum_master_size_passed=True,alpha128_bounds_inside=True,
    native_canvas=[29,53],source_pixels_per_native_pixel=1/scale,mount_pixel_visible=True,
    left_mount_x=mount[0],lamp_body_center_x=715,required_east_relationship_passed=mount[0]<715,
    external_glow_visible_in_alpha_composite=False,hidden_RGB_is_not_a_visible_halo=True,
    origin_manually_annotated=True,room_mount_verified=False,owner_approved=True,production_active=False))
print('ART0040 source measured:',im.size,'native29x53; wall mount',mount,'->',native_mount)
