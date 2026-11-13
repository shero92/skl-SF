"""Measure independent paintings, copy them losslessly, and author safe navigation over visible ground."""
from pathlib import Path
import hashlib
import json
import shutil
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
ART='ART-0052'
BASE=ROOT/'game_factory/environment'/ART/'v003'
MASTER=ROOT/'assets_hd/background/hidden_island_grid_painted/v001'
RUNTIME=ROOT/'map_factory/painted_worlds/hidden_island/v001'
CELL=32 # same collision-grid resolution as the current painted hero room; visual blocks are larger

SPECS={
    'home_descent':dict(name='Below Hero Room',spawn=[768,288],landmark=[768,512],
        polygons=[[[704,0],[832,0],[832,224],[864,288],[896,480],[928,704],[960,1024],[736,1024],[672,704],[640,480],[672,320],[704,224]]],
        portals=[dict(id='room_stairs',rect=[704,32,128,64],target='room'),
            dict(id='forest',rect=[736,960,128,64],target='mossveil_edge',arrival=[768,96])]),
    'mossveil_edge':dict(name='Mossveil Refuge — forest edge',story_location='Mossveil Refuge',spawn=[768,96],landmark=[768,544],
        polygons=[[[704,0],[832,0],[864,192],[832,288],[768,384],[864,512],[896,640],[928,768],[896,1024],[704,1024],[672,832],[640,704],[608,576],[608,416],[640,288],[672,192]],
            [[416,352],[640,320],[768,384],[800,544],[736,640],[448,608],[384,512]],
            [[800,512],[1056,544],[1216,512],[1344,544],[1344,608],[1184,640],[1024,640],[864,608]]],
        portals=[dict(id='home',rect=[704,0,128,64],target='home_descent',arrival=[800,928]),
            dict(id='roots',rect=[704,960,160,64],target='mossveil_roots',arrival=[768,96])]),
    'mossveil_roots':dict(name='Mossveil Refuge — roots',story_location='Mossveil Refuge',spawn=[768,96],landmark=[768,576],
        polygons=[[[704,0],[832,0],[832,192],[768,256],[736,384],[832,448],[896,512],[896,640],[704,704],[576,640],[512,512],[512,416],[576,288],[640,192]],
            [[736,512],[1536,512],[1536,608],[896,640],[736,640]],
            [[640,544],[864,544],[896,832],[832,1024],[672,1024],[640,832],[544,736]],
            [[320,512],[608,448],[768,512],[768,640],[544,640],[384,608]]],
        portals=[dict(id='forest_edge',rect=[704,0,128,64],target='mossveil_edge',arrival=[768,928]),
            dict(id='ridge',rect=[1472,512,64,96],target='stormwatch_ascent',arrival=[96,704]),
            dict(id='shore_path',rect=[704,960,128,64],target='bone_tide_shore',arrival=[768,96])]),
    'stormwatch_ascent':dict(name='Stormwatch Path — ascent',story_location='Stormwatch Path',spawn=[96,704],landmark=[768,608],
        polygons=[[[0,672],[256,640],[480,576],[736,512],[864,512],[864,672],[640,704],[384,736],[192,768],[0,768]],
            [[704,0],[832,0],[864,192],[896,384],[928,512],[864,704],[672,704],[608,576],[640,448],[704,320]],
            [[672,576],[864,576],[896,832],[832,1024],[704,1024],[640,832]]],
        portals=[dict(id='forest_west',rect=[0,672,64,96],target='mossveil_roots',arrival=[1440,576]),
            dict(id='forest_south',rect=[704,960,128,64],target='mossveil_roots',arrival=[1440,576]),
            dict(id='overlook',rect=[704,0,128,64],target='stormwatch_overlook',arrival=[768,928])]),
    'stormwatch_overlook':dict(name='Stormwatch Path — overlook',story_location='Stormwatch Path',spawn=[768,928],landmark=[800,512],
        polygons=[[[640,192],[832,192],[928,288],[1024,416],[960,704],[832,800],[640,768],[512,640],[416,608],[416,480],[544,416],[608,320]],
            [[640,640],[864,640],[864,1024],[640,1024]],
            [[768,448],[1536,448],[1536,576],[864,576]]],
        portals=[dict(id='ascent',rect=[704,960,128,64],target='stormwatch_ascent',arrival=[768,96]),
            dict(id='shore',rect=[1472,448,64,128],target='bone_tide_shore',arrival=[96,416])]),
    'bone_tide_shore':dict(name='Bone-Tide Shore — before the storm',story_location='Bone-Tide Shore',spawn=[768,96],landmark=[896,640],
        polygons=[[[704,0],[864,0],[896,384],[1024,448],[960,576],[640,576],[640,384]],
            [[0,384],[128,384],[288,432],[512,512],[704,544],[704,640],[448,608],[256,512],[128,448],[0,448]],
            [[512,416],[1120,416],[1376,512],[1376,768],[1216,864],[800,832],[448,736],[288,608],[384,512]]],
        portals=[dict(id='forest',rect=[704,0,160,64],target='mossveil_roots',arrival=[768,928]),
            dict(id='ridge',rect=[0,384,64,64],target='stormwatch_overlook',arrival=[1440,512])]),
}

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
def inside(point,poly):
    x,y=point;odd=False
    for (x0,y0),(x1,y1) in zip(poly,poly[1:]+poly[:1]):
        if (y0>y)!=(y1>y) and x<(x1-x0)*(y-y0)/(y1-y0)+x0:odd=not odd
    return odd
def walk_cells(polygons,size):
    return {(x,y) for y in range(size[1]//CELL) for x in range(size[0]//CELL)
        if any(all(inside((x*CELL+dx,y*CELL+dy),p) for dx,dy in [(1,1),(CELL-1,1),(1,CELL-1),(CELL-1,CELL-1)]) for p in polygons)}
def nav_for(cells,size):
    regions=[]
    for y in range(size[1]//CELL):
        xs=sorted(x for x,yy in cells if yy==y);runs=[]
        for x in xs:
            if runs and runs[-1][1]+1==x:runs[-1][1]=x
            else:runs.append([x,x])
        for i,(a,b) in enumerate(runs):
            regions.append(dict(id=f'safe_row_{y}_{i}',rect=[a,y,b-a+1,1],allow=['walk'],surface='other',floor_height=0,ceiling_height=None,review_status='needs_review'))
    return dict(schema_version=1,origin=[0,0],cell_size=CELL,grid_size=[size[0]//CELL,size[1]//CELL],
        default={'walk':False,'fly':False,'swim':False},regions=regions,obstacles=[],links=[])

def main():
    items=[];zones={}
    source_ref=ROOT/'map_factory/references/hero_room_01_target_20261103.png'
    for key,spec in SPECS.items():
        name='hidden_island_'+key
        master=MASTER/(name+'.png')
        if not master.exists():continue
        with Image.open(master) as im:
            im.load();size=list(im.size);mode=im.mode
            assert size==[1536,1024],(key,size)
            assert mode in ['RGB','RGBA']
            alpha=im.convert('RGBA').getchannel('A')
            assert alpha.getextrema()==(255,255)
        runtime=RUNTIME/(name+'.png');runtime.parent.mkdir(parents=True,exist_ok=True)
        delivery=ROOT/'.agents/graphics/deliveries'/ART/(name+'.png');delivery.parent.mkdir(parents=True,exist_ok=True)
        # Preserve the tool's RGB master. Production PNGs add a fully opaque alpha channel losslessly.
        with Image.open(master) as original:
            rgba=original.convert('RGBA')
            for destination in [runtime,delivery]:
                if destination.exists():
                    with Image.open(destination) as previous:
                        assert previous.size==original.size and previous.convert('RGB').tobytes()==original.convert('RGB').tobytes(), 'Never replace different artwork'
                rgba.save(destination)
                with Image.open(destination) as exported:
                    assert exported.mode=='RGBA' and exported.getchannel('A').getextrema()==(255,255)
                    assert exported.convert('RGB').tobytes()==original.convert('RGB').tobytes()
        prompt=BASE/'requests'/(key+'.txt')
        item=dict(id=name,request_id=ART,master_path=master.relative_to(ROOT).as_posix(),
            delivery_path=delivery.relative_to(ROOT).as_posix(),runtime_path=runtime.relative_to(ROOT).as_posix(),
            sha256=digest(master),master_sha256=digest(master),runtime_sha256=digest(runtime),delivery_sha256=digest(delivery),
            pixel_size=size,mode=mode,alpha_extrema=[255,255],bounds_alpha_128=[0,0,*size],
            origin=[size[0]/2,size[1]-1],origin_rule='full-scene bottom centre; not a character or prop foot anchor',
            runtime_origin=[0,0],native_canvas=size,runtime_mode='RGBA',delivery_mode='RGBA',
            native_method='RGB master unchanged; lossless RGBA export adds alpha255 only; exact RGB bytes; source1:1, no upscale/crop/flip/rotation',
            source_pixels_per_native_pixel=1.0,full_scene_owner_exception='docs/OWNER_PHOTO_WORLD_20261113.md',
            prompt_path=prompt.relative_to(ROOT).as_posix(),prompt_text=prompt.read_text(encoding='utf-8'),
            reference_path=source_ref.relative_to(ROOT).as_posix(),reference_sha256=digest(source_ref),
            tool='built-in image_gen',model='unknown',independent_generation=True,source_upscaled=False,
            owner_approved=True,approval_basis='owner_automatic_20261111',production_active=True,
            quality_status='runtime_integrated_needs_map_review',asset_kind='complete_world_background',reusable_as_piece=False,
            story_reference_path='docs/design/STORY_CANON_AR.md',story_reference_sha256=digest(ROOT/'docs/design/STORY_CANON_AR.md'),
            facing='same fixed south-looking-north orthographic three-quarter view as hero room',
            visual_grid_note='painted square ground blocks approximately64px; authored collision subgrid32px as room, not a claim of exact pixel-perfect generated seams',
            navigation_annotation='manual conservative walk polygons over visible unobstructed ground; not extracted automatically from colour')
        items.append(item)
        cells=walk_cells(spec['polygons'],size)
        zones[key]=dict(id=key,name=spec['name'],background='res://'+runtime.relative_to(ROOT).as_posix(),
            background_sha256=digest(runtime),canvas_size=size,spawn=spec['spawn'],landmark=spec['landmark'],
            walk_polygons=spec['polygons'],navigation=nav_for(cells,size),portals=spec['portals'],walk_cells=len(cells),
            story_phase='opening_before_storm_and_sword_reveal',story_location=spec.get('story_location',"Hero's Home exterior"))
    world=dict(schema_version=1,world_id='hidden_island_opening',request_id=ART,default_zone='home_descent',
        room_scene='res://scenes/main.tscn',camera_zoom=0.84375,hero_scale=1.2,hero_height_if_supported=128,
        geometry_reference=dict(room_map='hero_room_01',exit_side='south',first_scene_arrival_side='north',
            room_trigger=[704,864,128,64],room_return=[768,832],first_scene_spawn=[768,288]),
        story_canon='docs/design/STORY_CANON_AR.md',zones=zones,
        limitations=['Only manually annotated open ground is walkable; painted foreground vegetation is not a separate occlusion layer.',
            'Pictures are complete scene art by owner instruction, not sources for cut-out reusable pieces.',
            'Story events, NPCs, creatures and sword reveals are not baked into opening backgrounds.'])
    write(RUNTIME/'world.json',world)
    manifest=dict(request_id=ART,task_id='TASK-0170',delivery_branch='codex/seabreak-painted-world',agent='codex',tool='built-in image_gen',model='unknown',
        source_count=len(items),items=items,rejected_attempts=[],files=[dict(path=i['delivery_path'],sha256=i['delivery_sha256']) for i in items],
        owner_approved=True,approval_basis='owner_automatic_20261111',production_active=True,quality_status='runtime_integrated_needs_map_review',
        generation_cache_required=False,generation_count=6,total_generation_calls_in_request=14,
        retained_earlier_candidate_count=8,full_scene_exception='docs/OWNER_PHOTO_WORLD_20261113.md',
        world_path=(RUNTIME/'world.json').relative_to(ROOT).as_posix(),world_sha256=digest(RUNTIME/'world.json'))
    write(BASE/'manifest.json',manifest);write(ROOT/'.agents/graphics/deliveries'/ART/'manifest.json',manifest)
    print('Native paintings:',len(items),'zones:',len(zones),'RGB masters preserved; RGBA exports exact in colour, no upscaling.')
if __name__=='__main__':main()
