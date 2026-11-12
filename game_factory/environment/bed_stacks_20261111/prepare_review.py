"""Preserve raw sources; measure alpha, source density and native review exports."""
from pathlib import Path
import hashlib
import json
import shutil
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
records = json.loads((BASE/'generation_records.json').read_text(encoding='utf-8'))
branch = 'codex/art-0048-0049-bed-stacks'
specs = [
    ('ART-0048','furniture/double_bed_south','hero_double_bed_south',[255,290],'bed','ART-0048_target.png',True),
    ('ART-0049','background/sea_stack_islands','hero_sea_stack_arch_island',[300,160],'arch_final','ART-0049_arch_target.png',True),
    ('ART-0049','background/sea_stack_islands','hero_sea_stack_cluster',[526,190],'cluster','ART-0049_cluster_target.png',False),
]
reference = ROOT/'map_factory/references/hero_room_01_target_20261103.png'
assert sha(reference) == '47a7855cf242302108e1a6b9eaf4bfd3422f9f8c812585fa4da5bcaea948668b'
manifests = {}
for art, group, name, native_size, key, crop_name, selected in specs:
    folder = ROOT/'game_factory/environment'/art/'v001'
    folder.mkdir(parents=True, exist_ok=True)
    source_dir = ROOT/'assets_hd'/group/'v001'
    (source_dir/'.gdignore').touch()
    source = source_dir/(name+'.png') if selected else source_dir/'rejected'/(name+'_attempt_01.png')
    with Image.open(source) as im:
        im.load()
        assert im.mode == 'RGBA'
        alpha = im.getchannel('A')
        bounds = alpha.point(lambda a: 255 if a>=128 else 0).getbbox()
        assert bounds and alpha.getextrema() == (0,255)
        x0,y0,x1,y1 = bounds
        assert 0<x0<x1<im.width and 0<y0<y1<im.height
        minimum = [4*n for n in native_size]
        passed = im.width>=minimum[0] and im.height>=minimum[1]
        assert passed == selected, (name, im.size, minimum)
        scale = min(native_size[0]/im.width, native_size[1]/im.height)
        content_size = [round(im.width*scale),round(im.height*scale)]
        offset = [(native_size[0]-content_size[0])//2,(native_size[1]-content_size[1])//2]
        native = Image.new('RGBA',native_size,(0,0,0,0))
        native.paste(im.resize(content_size,Image.Resampling.NEAREST),offset)
        review = folder/'native_review'/(name+'.png')
        review.parent.mkdir(exist_ok=True)
        native.save(review)
        nb = native.getchannel('A').point(lambda a:255 if a>=128 else 0).getbbox()
        prompt = folder/'requests'/(name+'.txt')
        prompt.parent.mkdir(exist_ok=True)
        prompt.write_text(records['prompts'][key],encoding='utf-8',newline='\n')
        crop = ROOT/'.agents/graphics/requests/reference_crops'/crop_name
        compare = crop.with_name(crop.name.replace('_target.png','_compare.png'))
        item = dict(id=name,request_id=art,sha256=sha(source),pixel_size=list(im.size),mode=im.mode,
            alpha_extrema=list(alpha.getextrema()),bounds_alpha_128=list(bounds),origin=[(x0+x1)/2,y1-1],
            origin_rule='bottom centre of alpha128 visible bounds; source pixels',
            native_canvas=native_size,native_width=native_size[0],native_height=native_size[1],
            native_review_path=review.relative_to(ROOT).as_posix(),native_review_sha256=sha(review),
            native_origin=[(nb[0]+nb[2])/2,nb[3]-1],native_source_region=[0,0,im.width,im.height],
            native_content_size=content_size,native_offset=offset,
            native_method='whole-source uniform contain, nearest neighbour, transparent padding; integer rounding only; no source edit',
            minimum_master_size=minimum,minimum_master_passed=passed,
            source_pixels_per_native_pixel=[im.width/native_size[0],im.height/native_size[1]],
            prompt_text=records['prompts'][key],prompt_path=prompt.relative_to(ROOT).as_posix(),
            reference_crop_path=crop.relative_to(ROOT).as_posix(),reference_crop_sha256=sha(crop),
            comparison_path=compare.relative_to(ROOT).as_posix(),comparison_sha256=sha(compare),
            reference_use='design/style only, never pasted/traced into generated source',
            tool='built-in image_gen',model='unknown',independent_generation=True,source_upscaled=False,
            bitmap_flip_or_rotation=False,baked_shadow=False,owner_approved=True,approval_basis='owner_automatic_20261111',
            production_active=False,quality_status='needs_map_calibration' if selected else 'needs_regeneration',
            collision=None,footprint_64px_cells=None,calibration_status='not measured in room; native canvas is not navigation footprint',
            facing='south foot, north head; orthographic front/top' if art=='ART-0048' else 'distant south side-on, slight visible green tops')
        style = BASE/'references/bed_front_view_01.png' if art=='ART-0048' else ROOT/'assets_hd/background/sea_coast/v001/rock_arch_far_left.png'
        item.update(style_reference_path=style.relative_to(ROOT).as_posix(),style_reference_sha256=sha(style))
        if name=='hero_sea_stack_arch_island':
            samples = {'transparent_tunnel':[480,500],'bridge':[480,240],'left_pier':[260,500],'right_pier':[720,500]}
            measured = {k:alpha.getpixel(tuple(p)) for k,p in samples.items()}
            assert measured['transparent_tunnel']==0 and min(v for k,v in measured.items() if k!='transparent_tunnel')>=128
            item.update(arch_alpha_sample_coordinates=samples,arch_alpha_sample_values=measured,
                arch_note='Opening in left third is real transparency, open to implied waterline; no water painted in tunnel.',
                margin_note='Alpha128 margin left10/right7/top46/bottom78 source px; right margin is thinner than approximate3percent style guidance. No alpha128 clipping detected.')
        if selected:
            dest = ROOT/'.agents/graphics/deliveries'/art/(name+'.png')
            dest.parent.mkdir(parents=True,exist_ok=True)
            assert not dest.exists() or sha(dest)==sha(source)
            shutil.copy2(source,dest)
            item.update(master_path=source.relative_to(ROOT).as_posix(),delivery_path=dest.relative_to(ROOT).as_posix())
        else:
            item.update(path=source.relative_to(ROOT).as_posix(),reason='Height743 below required760; no upscale/padding or native-size reduction to bypass4x gate.',
                missing_exact_output='.agents/graphics/deliveries/ART-0049/hero_sea_stack_cluster.png')
        if art not in manifests:
            manifests[art] = dict(request_id=art,task_id='TASK-0159',delivery_branch=branch,agent='codex',
                tool='built-in image_gen',model='unknown',owner_approved=True,approval_basis='owner_automatic_20261111',
                production_active=False,generation_cache_required=False,reference_path=reference.relative_to(ROOT).as_posix(),
                reference_sha256=sha(reference),items=[],rejected_attempts=[],files=[],source_count=0,
                quality_status='needs_map_calibration' if art=='ART-0048' else 'partial_delivery_needs_regeneration',
                limitations=['Source-only Godot review, no room placement/occlusion/collision verified.',
                    'Owner main checkout unchanged. Task worktree sources are available through delivery branch.',
                    'Visual owner approval is automatic; source quality and integration gates remain separate.'])
        m = manifests[art]
        m['items' if selected else 'rejected_attempts'].append(item)
        if selected:
            m['source_count'] += 1
            m['files'].append(dict(path=item['delivery_path'],sha256=item['sha256']))

# Earlier arch generation is retained and indexed as nonselected, not a final sprite.
old = ROOT/'assets_hd/background/sea_stack_islands/v001/rejected/hero_sea_stack_arch_island_attempt_01.png'
im = Image.open(old);a=im.getchannel('A')
prompt = ROOT/'game_factory/environment/ART-0049/v001/requests/hero_sea_stack_arch_island_initial.txt'
prompt.write_text(records['prompts']['arch_initial'],encoding='utf-8',newline='\n')
manifests['ART-0049']['rejected_attempts'].append(dict(id=old.stem,path=old.relative_to(ROOT).as_posix(),
    sha256=sha(old),pixel_size=list(im.size),mode=im.mode,alpha_extrema=list(a.getextrema()),
    bounds_alpha_128=list(a.point(lambda v:255 if v>=128 else 0).getbbox()),
    reason='Too much upper blank canvas; ridge reads too low at native size. Regenerated taller rock faces.',
    quality_status='not_selected',production_active=False,prompt_path=prompt.relative_to(ROOT).as_posix(),
    prompt_text=records['prompts']['arch_initial']))
b = a.point(lambda v:255 if v>=128 else 0).getbbox()
manifests['ART-0049']['rejected_attempts'][-1].update(origin=[(b[0]+b[2])/2,b[3]-1],
    origin_rule='bottom centre alpha128 bounds',owner_approved=True,approval_basis='owner_automatic_20261111')
for art,m in manifests.items():
    m['generation_count'] = 1 if art=='ART-0048' else 3
    m['status'] = 'delivered' if art=='ART-0048' else 'requested'
    if art=='ART-0049':
        m['blocked_output'] = '.agents/graphics/deliveries/ART-0049/hero_sea_stack_cluster.png'
        m['block_reason'] = 'Source2117x743 fails required2104x760; built-in tool has no resolution parameter; prior similar gate failures retained in TASK-0157.'
    folder = ROOT/'game_factory/environment'/art/'v001'
    write(folder/'manifest.json',m)
    delivery=ROOT/'.agents/graphics/deliveries'/art
    delivery.mkdir(parents=True,exist_ok=True)
    write(delivery/'manifest.json',m)
    write(folder/'technical_qa.json',dict(request_id=art,selected_count=m['source_count'],
        selected_minimum_passed=all(i['minimum_master_passed'] for i in m['items']),
        request_complete=art=='ART-0048',rejected_count=len(m['rejected_attempts']),production_active=False))
    print(art,m['status'],'selected',m['source_count'],'rejected',len(m['rejected_attempts']))
