"""Local game production registry and durable one-image queue. No network client."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
from collections import deque
import math
from datetime import datetime, timezone
from PIL import Image, ImageChops, ImageStat

ROOT = Path(__file__).resolve().parents[1]
CHARACTERS = ['hero', 'cely', 'neru', 'reef_friend', 'old_father', 'temple_archer']
NAMES = ['Hero', 'Cely', 'Neru', 'Reef Friend', 'The Old Father', 'Temple Archer']
BATTLE = {'idle_ready':4, 'step':4, 'attack_windup':4, 'attack_execute':6, 'cast_magic':6, 'use_item':4, 'hurt':3, 'defend':3, 'victory':4}
IDENTITIES = [
 'brown tousled hair, blue eyes, blue and cream layered coastal clothes, shell necklace, coral ornaments, blue arm markings, decorated sword, sandals',
 'long white hair, red scarf, coral ornaments, polearm, pale mount; rider and mount are ONE inseparable gameplay unit',
 'small friendly cream companion creature, blue crystal formations, blue and gold accessories, large expressive eyes; natural creature anatomy',
 'pale blond hair, coral ornaments, turquoise and cream clothes, sea jewelry, distinctive original melee weapon',
 'ancient wooden leafy druid, layered vegetation, white flowers, tall staff with hanging lantern',
 'green hair, flowers, nature clothing, turquoise and gold accessories, original bow and quiver; no invented wings',
]
DETAILS = [['sword','shell_pendant','arm_marking','cloth_pattern'], ['spear','scarf','saddle'], ['blue_crystal','necklace','head_ornament'], ['weapon','coral_crown','shell_accessory'], ['lantern_staff','leaf_cloak','floral_ornament'], ['bow','quiver','floral_crown']]

def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))

def write(p, data):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True)
    temp=p.with_suffix(p.suffix+'.tmp')
    temp.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
    temp.replace(p)

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def safe(rel):
    p=(ROOT/rel).resolve()
    if not p.is_relative_to(ROOT): raise ValueError('Path outside project')
    return p

def battle_pose(slug,state,frame):
    common={
        'idle_ready':['neutral combat guard','subtle inhale, weapon lifts one native pixel','breathing peak, tiny cloth movement','exhale toward neutral guard'],
        'step':['lead foot contacts ahead toward right','body weight transfers to lead foot, trailing knee bends','rear foot passes forward, torso advances','settle into combat stance after the step'],
        'cast_magic':['prepare focus, hand or staff low','lift casting hand/staff toward right','gather focus, open hand and lean forward','release casting gesture toward right; spell release event','hold follow-through, relaxed casting fingers','lower casting hand/staff and recover stance'],
        'use_item':['reach toward belt pouch','bring free hand to chest, preparing separate item attachment','use-item gesture near face; keep separate item/VFX out of body sprite','lower hand and return to stance'],
        'hurt':['brief recoil from impact on torso','compress stance and flinch, preserve all limbs','recover balance, return toward guard'],
        'defend':['raise weapon/forearms into guard','brace behind guard, weight on rear foot','ease guard and recover balance'],
        'victory':['relax after combat','lift original weapon or arms triumphantly','hold joyful victory posture, preserve original face','settle toward neutral proud stance']}
    if state in common:return common[state][frame-1]
    if slug=='temple_archer':
        windup=['reach to original quiver','nock a single arrow on original bow','raise bow toward right, begin drawing string','draw fully with hand anchored near cheek, aim right']
        execute=['hold full draw, bow upright','settle aim with taut string','final draw anticipation, arrow still nocked','release fingers and bowstring; arrow projectile is a SEPARATE asset, no arrow in flight baked into body','follow through with relaxed draw hand and empty bowstring','lower bow slightly and recover ready stance']
    elif slug=='cely':
        windup=['mounted guard, pale mount balanced','rider draws polearm back, mount shifts weight','lower original spear toward right, rider leans forward','poised mounted thrust, synchronized rider and quadruped']
        execute=['mount begins short forward stride','rider drives spear toward right','extend polearm with controlled forward lean','full spear-thrust contact, rider remains seated and mount anatomically stable','retract polearm as mount stabilizes','return to mounted guard']
    elif slug=='neru':
        windup=['creature lowers body naturally','hind legs compress, front paw prepares','small creature crouch anticipation, crystals unchanged','front paw drawn back for creature strike']
        execute=['creature pushes forward from hind legs','front paw swings toward right','body reaches forward in a natural creature lunge','front-paw strike contact, no human fist or weapon','front paw lands, creature absorbs weight','return to balanced creature stance']
    elif slug=='old_father':
        windup=['tree druid braces roots/feet','draw original lantern staff back','rotate wooden torso, raise staff slightly','poise original staff for controlled rightward strike, lantern remains attached']
        execute=['begin staff sweep toward right','wooden arms extend original staff','staff approaches target','staff strike contact, stable wooden druid anatomy','staff follows through, attached lantern sways','recover slow grounded druid guard']
    else:
        weapon='original decorated sword' if slug=='hero' else 'original reference melee weapon'
        windup=[f'combat guard with {weapon}',f'flex knees and draw {weapon} back',f'rotate hips and lift {weapon} behind right shoulder',f'hold strong anticipation before swinging {weapon}']
        execute=[f'begin forward swing of {weapon}',f'accelerate {weapon} through downward arc toward right',f'extend arms as {weapon} approaches target',f'full contact extension of {weapon} toward right at chest height',f'controlled follow-through of {weapon} across body',f'recover {weapon} toward guard']
    return (windup if state=='attack_windup' else execute)[frame-1]

def environment():
    library=ROOT/'assets_generated'
    manifest=read(library/'library_manifest.json')
    records=[]; audit={'missing':[],'incompatible':[],'duplicates':[], 'approved':[], 'existing':[]}
    hashes={}
    for entry in manifest['assets']:
        p=library/entry['filename']; key=entry['asset_id']+'__'+entry['orientation']
        if not p.is_file(): audit['missing'].append(key); continue
        d=read(p.with_suffix('.json'))
        with Image.open(p) as im:
            dims=list(im.size)
            if dims!=[d['native_width'],d['native_height']] or any(v%64 for v in dims): audit['incompatible'].append(key)
            if d.get('transparent_background') and im.convert('RGBA').getchannel('A').getextrema()[0]!=0:
                audit['incompatible'].append(key+':alpha')
        digest=sha(p)
        if digest!=entry['sha256']: audit['incompatible'].append(key+':hash')
        if digest in hashes: audit['duplicates'].append([hashes[digest],key])
        hashes[digest]=key; audit['existing'].append(key)
        if d['approval_status']=='approved': audit['approved'].append(key)
        records.append({'id':key,'category':d['category'],'texture_path':'res://assets_generated/'+entry['filename'],
            'pixel_size':dims,'origin':[dims[0]/2,dims[1] if d['category']!='background' and d['category']!='floor' else 0],
            'status':d['approval_status'],'footprint':[d['footprint_tiles_x'],d['footprint_tiles_y']],
            'source_metadata':str(p.with_suffix('.json').relative_to(ROOT)).replace('\\','/'), 'sha256':digest,
            'shadow':{'type':'none'},'collision':{'enabled':False}})
    write(ROOT/'game_factory/environment/catalog.json',{'assets':records})
    write(ROOT/'game_factory/environment/audit.json',audit)
    if audit['missing'] or audit['incompatible']: raise ValueError(audit)
    available={r['id']:r for r in records}
    passes={k:[] for k in ['background','ground','walls','decorations','shadows']}
    def place(asset,x,y,group='walls',scale=1,host=None,offset=None,solid=False):
        k=asset if '__' in asset else asset+'__default'
        if k not in available: raise ValueError(k)
        r=available[k]; ident=f'{asset}_{sum(map(len,passes.values()))}'
        item={'asset_id':k,'instance_id':ident,'position':[x,y],'scale':scale,
              'sprite_pixel_size':r['pixel_size'],'collision':{'enabled':solid,'size':[r['footprint'][0]*64*scale,r['footprint'][1]*64*scale],
              'offset':[0,-r['footprint'][1]*32*scale]},'shadow':{'type':'none'}}
        if host: item['attachment']={'parent_instance_id':host,'mount_offset':offset or [0,0]}
        passes[group].append(item)
        if solid:
            passes['shadows'].append({'instance_id':ident+'_contact','owner_instance_id':ident,
                'position':[x,y-6],'sprite_pixel_size':r['pixel_size'],'scale':scale,
                'settings':{'type':'contact_medium','opacity':0.28,'offset_x':0,'offset_y':-4}})
        return ident
    # Square-grid platform with an entrance gap and irregular outer silhouette.
    for y in range(0,1024,256):
        for x in range(128,1664,256): place('B01',x,y,'background')
    for x in (-256,768,1792): place('B10',x,-850,'background',4)
    for a,x,y in [('B05',180,50),('B06',1300,70),('B11',1020,-20)]: place(a,x,y,'background',.8)
    for row in range(10):
        for col in range(14):
            if (row==0 and col in (0,13)) or (row==9 and col in (0,13)): continue
            place('G0'+str(1+(row+col)%3),256+col*64+32,288+row*64,'ground')
    place('D01',480,780,'ground',1.3);place('D02',1024,760,'ground');place('D03',768,800,'ground')
    for c in list(range(0,5))+list(range(9,14)):
        host=place('W02' if c%3 else 'W03',288+c*64,340,solid=True)
        if c in (2,10): place('D04',288+c*64,310,'decorations',host=host,offset=[0,-30])
        if c in (1,11): place('L01',288+c*64,320,'decorations',host=host,offset=[0,-20])
    for row in range(2,10):
        for x in (270,1138): place('W10',x,320+row*64,solid=True)
    for c in list(range(1,6))+list(range(8,13)): place('W10',288+c*64,910,solid=True)
    place('A05',736,352,scale=2.5)
    for x in (590,880): place('A01',x,365,scale=1.5,solid=True)
    place('A09',1010,352)
    place('A10',704,990);place('A13',630,930);place('A13',840,930)
    place('F06__south',438,450,solid=True);place('F07__south',1000,458,solid=True)
    place('F01__south',480,748,solid=True);place('F05__south',332,680,solid=True)
    table=place('F08__south',1010,724,solid=True)
    for x in (860,1148): place('F10__south',x,744,solid=True)
    for a,off in [('R09',[-25,-82]),('R10',[40,-70]),('R11',[-75,-62]),('L04',[70,-110])]:
        place(a,1010+off[0],724+off[1],'decorations',host=table,offset=off)
    for a,x,y in [('P03',570,330),('P12',300,400),('P13',1120,520),('P11',1120,450),('P14',430,900),('P05',950,900),('P08',310,840),('P10',1100,830),('R02',900,420)]: place(a,x,y,'decorations')
    room={'map_id':'game_factory_original_room','version':1,'canvas_size':[1536,1024],'tile_size':64,
          'size':[0,0],'background_color':'#169ada','occlusion_mode':'world_y_sort',
          'layer_stack':{'schema_version':1,'passes':passes},'visual_qa':{'status':'needs_review','layout':'inferred from original reference; not approved'},
          'logical_levels':['ground','structures_and_furniture','decorations','shadows_and_lighting'],'background_separate':True}
    room['navigation']={'schema_version':1,'origin':[256,288],'cell_size':64,'grid_size':[14,10],
        'default':{'walk':False,'fly':False,'swim':False},'regions':[], 'obstacles':[], 'links':[],
        'note':'Candidate floor support only; physics colliders handle structures. No flight or swimming abilities granted.'}
    for row in range(10):
        start=1 if row in (0,9) else 0
        room['navigation']['regions'].append({'id':f'floor_row_{row}','surface':'stone','rect':[start,row,12 if start else 14,1],
            'allow':['walk'],'requires':{'walk':[]},'floor_height':0,'ceiling_height':None,'review_status':'needs_review'})
    write(ROOT/'game_factory/environment/room.json',room)
    return audit

def build_queue():
    path=ROOT/'game_factory/queue.json'
    old=read(path) if path.exists() else {'items':[]}
    prior={i['id']:i for i in old['items']}; jobs=[]; characters=[]
    for idx,slug in enumerate(CHARACTERS):
        ref=ROOT/f'map_factory/references/characters/{slug}.png.png'
        cid=f'CHAR{idx+1:03}'; dims=[128,128] if slug in ('cely','old_father') else [96,96]
        if slug=='neru': dims=[96,96]
        battle_dims=[320,320] if slug in ('cely','old_father') else [256,256]
        battle_anchor=[battle_dims[0]//2,battle_dims[1]-16]
        rec={'character_id':cid,'slug':slug,'display_name':NAMES[idx],'source_reference_images':[],
             'reference_status':'available' if ref.exists() else 'blocked_missing_reference','map_sprite_canvas_size':dims,
             'battle_sprite_canvas_size':battle_dims,'map_ground_footprint':[2,2] if slug=='cely' else [1,1],
             'map_anchor':[dims[0]//2,dims[1]-6],'battle_anchor':battle_anchor,
             'supported_directions':['down','left','right','up'],'movement_speed':180,'collision_shape':{'size':[24,18],'offset':[0,-9]},
             'animations':{},'portraits':{},'turnaround':{},'details':{},'approval_status':'pending','production_complete':False}
        if ref.exists(): rec['source_reference_images']=[{'path':str(ref.relative_to(ROOT)).replace('\\','/'),'sha256':sha(ref)}]
        def add(kind,state,frame=1,direction='',size=None,anchor=None):
            name=f'{slug}_{kind}_{direction+"_" if direction else ""}{state}_{frame:02}.png'
            folder=f'map/{direction}' if kind=='map' else f'battle/{state}' if kind=='battle' else kind
            out=f'assets/characters/{slug}/{folder}/{name}'
            ident=f'{cid}_{kind}_{direction}_{state}_{frame:02}'
            motion=''
            if kind=='map':
                motion=(['neutral stance, feet fixed','subtle inhale, chest and cloth lift, feet fixed','breath peak, tiny hair movement, feet fixed','exhale returning to neutral, feet fixed'] if state=='idle' else ['left foot forward contact, right foot behind','left foot supporting, right foot passing','right foot forward contact, left behind','weight transfer over right foot','right supporting, left foot passing','left foot approaching contact, cycle returning'])[frame-1]
                if slug=='cely': motion+='; natural quadruped mount gait with synchronized seated rider'
                if slug=='neru': motion+='; natural small creature gait and anatomy'
            elif kind=='battle': motion=f'{state} action frame {frame} of {BATTLE[state]}: {battle_pose(slug,state,frame)}. No slash trail, airborne projectile or magic VFX baked into body.'
            else: motion=f'{state}, one isolated {kind} view'
            facing={'down':'front facing viewer toward bottom edge','up':'back view facing top edge, back of head and outfit, no front face','left':'true left facing profile, nose and toes toward left edge','right':'true right facing profile, nose and toes toward right edge'}.get(direction,'')
            canvas=size or dims
            prompt=f'''Use case: stylized-concept. ONE isolated production pixel-art {kind} image, {cid} {NAMES[idx]}, {state}, frame {frame:02}. Input 1 is the STRICT original character identity poster: extract design identity only, do not copy poster composition, captions or other views. Preserve {IDENTITIES[idx]}. {facing}. {motion}. Premium handcrafted crisp pixel clusters, restrained coherent palette, clean outlines, no blur, antialiasing or painterly rendering. {'Square-grid player-facing elevated 3/4 RPG map camera; readable compact proportions and silhouette compatible with 64x64 floor grid.' if kind=='map' else 'Independent detailed combat representation, substantially more anatomical detail than map chibi.' if kind=='battle' else 'Identity faithful isolated art.'} Target native canvas {canvas[0]}x{canvas[1]}, transparent RGBA. Design the pixels at native scale; if larger renderer output is needed use integer-enlarged native pixel blocks. Preserve full silhouette, head, weapon, feet with no clipping. Ground contact anchor {anchor or rec['map_anchor']}; leave margins. Warm upper-left light. {'Additional reference is same-character prior frame for identical scale/costume only; CHANGE limbs and secondary motion as requested, never duplicate a static pose.' if kind in ('map','battle') else ''} No floor, cast shadow, background, poster, border, text, labels, collage, sprite sheet, multiple poses, extra character, or checkerboard. Exactly ONE image of this single asset/frame.'''
            if kind=='map':
                prompt+=f' CRITICAL NATIVE SPRITE DESIGN: compact MAP SPRITES of original poster define proportions, NOT tall key art. Design on underlying {canvas[0]}x{canvas[1]} logical pixel grid, 1-3 native pixel clusters. Elevated 3/4 camera shows top of head. NOT a detailed illustration shrunk down.'
                if slug in ('hero','reef_friend','temple_archer'):
                    prompt+=' Large readable head, exactly 3 heads tall overall, short stout torso and legs. Head about 25 native pixels; body height about 78. No realistic adult proportions.'
                elif slug=='neru':
                    prompt+=' Preserve the compact friendly original creature proportions, cream quadruped body and blue crystals. Do not impose humanoid proportions or a human walk cycle.'
                elif slug=='cely':
                    prompt+=' Full pale quadruped mount AND seated rider fit in the one 128x128 unit canvas. Preserve mount anatomy, saddle and polearm. No unmounted substitute. Rider and mount are a single animated unit.'
                else:
                    prompt+=' Preserve the taller wooden druid silhouette, staff, leaves and hanging lantern within the 128x128 map canvas; naturally slow movement, no generic human redesign.'
            elif kind=='battle':
                prompt+=' Battle stage camera: character stands on left, facing RIGHT in a clear side/three-quarter combat view. Same camera, body scale and weapon hand throughout all states.'
            elif kind in ('weapons','details'):
                prompt=f'''Use case: stylized-concept. Generate exactly ONE isolated pixel-art production component: {cid} {NAMES[idx]} {state.replace('_',' ')}. Input 1 original character poster is the strict shape/material/color/detail reference for this component only. Match the exact corresponding weapon or accessory/marking/pattern on that poster; no redesign or substitute. Show only that single named component, fully visible, centered with margins, native {canvas[0]}x{canvas[1]} logical pixels, transparent RGBA, warm upper-left light, crisp designed pixel clusters and outlines. No entire character, hands, other accessories, floor, shadow, labels, text, border, sheet or collage. For arm marking or cloth pattern show one isolated original detail patch only. Exactly one asset PNG.'''
            elif kind in ('portraits','ui'):
                prompt+=f' COMPOSITION OVERRIDE: single head-and-shoulders portrait, face clearly readable and filling most of canvas; expression {state.replace("_"," ")}. No full-body pose. Same framing and eye line across expressions. Preserve exact face, eye color, hair and ornaments.'
            elif kind=='turnaround':
                prompt+=f' Show a single full-body {state.replace("_"," ")} design view ONLY, stable neutral stance, exact accessory placement. A back view must show back of head with no front face. Left and right are genuine separately drawn views, not flipped images.'
            item={'id':ident,'character_id':cid,'slug':slug,'kind':kind,'state':state,'direction':direction,'frame':frame,
                  'output':out,'source_reference':str(ref.relative_to(ROOT)).replace('\\','/'),'prompt':prompt,'target_dimensions':canvas,
                  'anchor':anchor or rec['map_anchor'],'transparent_background':True,'status':'pending' if ref.exists() else 'blocked',
                  'attempts':0,'validation_result':None,'approval_status':'pending'}
            if ident in prior:
                planned=item
                item=prior[ident]
                if item['status']=='pending' and item['attempts']==0:
                    for field in ('prompt','target_dimensions','anchor','output'):
                        item[field]=planned[field]
                if item['status']=='blocked' and ref.exists(): item['status']='pending'
            jobs.append(item)
        for direction in rec['supported_directions']:
            for state,count in [('idle',4),('walk',6)]:
                for n in range(1,count+1): add('map',state,n,direction)
        for state,count in BATTLE.items():
            for n in range(1,count+1): add('battle',state,n,size=battle_dims,anchor=battle_anchor)
        for expression in ['neutral','happy','serious','hurt','battle_ready']: add('portraits',expression,size=[256,256],anchor=[128,256])
        add('ui','face',size=[64,64],anchor=[32,64])
        add('key_art','full_body',size=[512,768],anchor=[256,744])
        for direction in ['front','left','right','back','three_quarter_front','three_quarter_back']: add('turnaround',direction,size=[256,384],anchor=[128,368])
        for detail in DETAILS[idx]:
            add('weapons' if detail in ('sword','spear','weapon','lantern_staff','bow') else 'details',detail,size=[128,128],anchor=[64,120])
        characters.append(rec)
    write(path,{'schema_version':1,'provider':'builtin_image_gen','limits':old.get('limits',{'max_attempts':3,'max_requests_per_run':40,'min_seconds_between_requests':1}),'items':jobs})
    write(ROOT/'game_factory/character_manifest.json',{'characters':characters})
    refresh()
    return {'queued':len(jobs),'missing_references':[c['display_name'] for c in characters if c['reference_status']!='available']}

def refresh():
    q=read(ROOT/'game_factory/queue.json'); manifest=read(ROOT/'game_factory/character_manifest.json')
    for c in manifest['characters']:
        c['animations']={}; c['portraits']={}; c['turnaround']={}; c['details']={}
        c['character_role']=['swordsman','mounted_lancer','creature_companion','sea_melee_fighter','nature_caster','archer'][CHARACTERS.index(c['slug'])]
        for section in ('ui','key_art','weapons','effects'):c[section]={}
        for i in q['items']:
            if i['character_id']!=c['character_id'] or i['status'] not in ('needs_review','approved') or not safe(i['output']).is_file(): continue
            if i['kind']=='battle' and i.get('weapon_embedded') is not False:continue
            if i['kind'] in ('map','battle'):
                key=f"{i['kind']}_{i['direction']+'_' if i['direction'] else ''}{i['state']}"
                a=c['animations'].setdefault(key,{'frames':[],'duration':.2 if i['state']=='idle' else .12,'loop':i['state'] in ('idle','walk','idle_ready'),'complete':False})
                a['frames'].append('res://'+i['output'])
                expected=(4 if i['state']=='idle' else 6) if i['kind']=='map' else BATTLE[i['state']]
                a['complete']=len(a['frames'])==expected
            else: c.setdefault(i['kind'],{})[i['state']]='res://'+i['output']
        c['map_idle_frames']={d:c['animations'].get('map_'+d+'_idle',{}).get('frames',[]) for d in c['supported_directions']}
        c['map_walk_frames']={d:c['animations'].get('map_'+d+'_walk',{}).get('frames',[]) for d in c['supported_directions']}
        c['battle_animation_frames']={s:c['animations'].get('battle_'+s,{}).get('frames',[]) for s in BATTLE}
        c['available_battle_actions']=[s for s in BATTLE if c['animations'].get('battle_'+s,{}).get('complete',False)]
        c['equipment_profile']={'hero':'sword','cely':'spear','neru':'natural','reef_friend':'melee_reference_pending','old_father':'staff','temple_archer':'bow'}[c['slug']]
        c['battle_body_policy']='no_embedded_equipment'
        battle_palette='game_factory/hero_correction/hero_battle_palette.json'
        c['battle_palette_reference']='res://'+battle_palette if c['slug']=='hero' and safe(battle_palette).exists() else None
        attachment=f"game_factory/characters/{c['slug']}/weapon_anchors.json"
        if c['slug']=='hero' and not safe(attachment).exists():attachment='game_factory/hero_correction/hero_weapon_anchors.json'
        c['weapon_attachment_metadata']='res://'+attachment if safe(attachment).exists() else None
        c['animation_frame_durations']={k:v['duration'] for k,v in c['animations'].items()}
        c['animation_loop_modes']={k:v['loop'] for k,v in c['animations'].items()}
        c['animation_quality_approval']='pending_visual_sequence_review'
        c['color_palette']=[]
        first=next((i for i in q['items'] if i['slug']==c['slug'] and i['kind']=='map' and i['status'] in ('needs_review','approved') and safe(i['output']).exists()),None)
        if first:
            from collections import Counter
            with Image.open(safe(first['output'])) as im:
                pixels=im.convert('RGBA').tobytes()
                colors=Counter(tuple((pixels[n+j]//16)*16+8 for j in range(3)) for n in range(0,len(pixels),4) if pixels[n+3]>=128)
                c['color_palette']=['#%02x%02x%02x'%rgb for rgb,count in colors.most_common(16)]
        own=[i for i in q['items'] if i['character_id']==c['character_id']]
        c['production_complete']=all(i['status']=='approved' for i in own)
    write(ROOT/'game_factory/character_manifest.json',manifest)

def next_job(slug='hero'):
    if (ROOT/'game_factory/checkpoint_hold').exists(): raise ValueError('Production checkpoint: native anchor validation in progress')
    p=ROOT/'game_factory/queue.json'; q=read(p)
    active=[i for i in q['items'] if i['status']=='generating']
    if active: raise ValueError('Unresolved generation: '+active[0]['id']+'; ingest returned image or explicitly fail before retry')
    for i in q['items']:
        if i['slug']!=slug or i['status'] not in ('pending','failed'): continue
        if i['attempts']>=i.get('max_attempts',q['limits']['max_attempts']): continue
        if safe(i['output']).exists(): raise ValueError('Protected existing output: '+i['output'])
        ref=safe(i['source_reference'])
        if not ref.exists(): i['status']='blocked'; write(p,q); continue
        i['status']='generating'; i['attempts']+=1; i['started_at']=datetime.now(timezone.utc).isoformat(); write(p,q)
        refs=[str(ref)]
        prior=[v for v in q['items'] if v['slug']==slug and v['kind']==i['kind'] and v['direction']==i['direction'] and v['status'] in ('needs_review','approved') and (i['kind']!='battle' or v.get('weapon_embedded') is False)]
        if prior and i['kind']=='map':
            first=prior[0]
            if i['state']=='walk':
                wanted={2:1,3:1,4:3,5:4,6:1}.get(i['frame'])
                first=next((v for v in prior if v['state']=='walk' and v['frame']==wanted),first)
            refs=[str(safe(first.get('source_png',first['output'])))]
            idle_changes={1:'neutral standing',2:'tiny inhale: lift chest cloth by one native pixel, both feet and head stay fixed',3:'small secondary scarf and mantle movement, both feet and head stay fixed',4:'exhale and return toward neutral cloth pose, both feet and head stay fixed'}
            action=idle_changes[i['frame']] if i['state']=='idle' else 'CHANGE THE LEG POSE for the mandatory gait instruction below; make the anatomical stride change clearly visible'
            i['prompt']=f'''Use case: precise-object-edit. Edit the ONE supplied transparent {i['slug']} sprite to produce exactly one new animation frame: {i['id']}, {i['direction']} facing, {i['state']} frame {i['frame']:02}. The edit target already embodies the original poster identity. Preserve exact canvas, camera, face, hair silhouette, head position, torso, costume patterns, ornaments, palette, weapon hand and body proportions. Do not redraw or redesign these protected regions. Change only limbs and secondary cloth motion as necessary: {action}. Keep full sprite and weapon visible; preserve real transparency. Original handcrafted pixel style and native {i['target_dimensions'][0]}x{i['target_dimensions'][1]} logical grid. No text, floor, shadow, extra limbs, extra figure, sheet or collage. ONE sprite only.'''
            write(p,q)
        elif prior and i['kind']=='battle':
            first=next((v for v in prior if v['state']==i['state'] and v['frame']==i['frame']-1),prior[0])
            if i['state']=='attack_execute' and i['frame']==1:
                first=next((v for v in prior if v['state']=='attack_windup' and v['frame']==4),first)
            refs=[str(safe(first.get('source_png',first['output'])))]
            pose=battle_pose(i['slug'],i['state'],i['frame'])
            i['prompt']=f'''Use case: precise-object-edit. Create exactly ONE new combat animation frame by editing the supplied {i['slug']} battle sprite: {i['id']}, {i['state']}, frame {i['frame']} of {BATTLE[i['state']]}. Preserve this exact character identity, face, hair, outfit construction, ornaments, colors, weapon, pixel density, canvas, camera and body scale. Same right-facing three-quarter combat camera throughout. Change the anatomy and action pose as required for THIS phase: {pose}. Make the progression visible, not a duplicate static pose. Preserve proper anatomy and stable ground baseline. Do not zoom or reframe the character. Keep full head, limbs and original weapon visible with margins. Native canvas {i['target_dimensions'][0]}x{i['target_dimensions'][1]}, crisp detailed handcrafted pixels; no blur or painterly smoothing. ONE character only. True transparent RGBA, no floor, cast shadow, captions, collage or additional poses. No baked slash arc, airborne projectile, magic particles or battle background; effects are separate assets.'''
            write(p,q)
        elif prior and i['kind'] in ('portraits','turnaround'): refs.append(str(safe(prior[0]['output'])))
        if i['kind']=='map' and i['state']=='walk':
            phase=i['frame']
            if i['direction'] in ('left','right'):
                forward='LEFT' if i['direction']=='left' else 'RIGHT'
                back='RIGHT' if forward=='LEFT' else 'LEFT'
                poses={1:f'near visible leg stretched {forward}, far leg stretched {back}, wide contact stride',
                       2:'near leg supporting directly under hip; far knee bent and passing underneath; narrow passing silhouette',
                       3:f'REVERSE the contact legs: near visible leg stretched {back}, far leg stretched {forward}, opposite wide stride',
                       4:'far leg bears weight forward; near heel lifts and knee bends behind',
                       5:'far leg under hip; near knee lifted passing through; narrow silhouette visibly different from contact',
                       6:f'near leg reaches {forward} again, far leg pushes off {back}'}
            else:
                lead='LOWER toward bottom edge' if i['direction']=='down' else 'HIGHER toward top edge'
                trail='HIGHER toward top edge' if i['direction']=='down' else 'LOWER toward bottom edge'
                poses={1:f'SCREEN-LEFT boot leads {lead}; SCREEN-RIGHT boot trails {trail}',
                       2:'SCREEN-LEFT leg supports beneath hip; SCREEN-RIGHT knee bent passing; feet close together',
                       3:f'OPPOSITE CONTACT: SCREEN-RIGHT boot must lead {lead}; SCREEN-LEFT boot must trail {trail}. CLEARLY REVERSE BOTH LEGS from frame 01, never repeat its stance',
                       4:f'SCREEN-RIGHT foot supports {lead}; SCREEN-LEFT heel raised behind {trail}',
                       5:'SCREEN-RIGHT leg supports beneath hip; SCREEN-LEFT knee lifted and passing, feet close together',
                       6:f'SCREEN-LEFT boot reaches {lead} again, SCREEN-RIGHT toe pushes off behind'}
            if i['slug'] in ('cely','neru'):
                poses={1:'near foreleg reaches forward, opposite far hindleg reaches forward; the other diagonal pair trails',
                       2:'near foreleg supports; far foreleg swings past; hind legs perform coordinated passing phase',
                       3:'OPPOSITE diagonal contact: far foreleg and near hindleg now reach forward; near foreleg and far hindleg trail',
                       4:'far foreleg and near hindleg bear weight; opposite diagonal pair begins lifting',
                       5:'opposite fore/hind pair passes under quadruped torso, natural four-leg gait',
                       6:'near foreleg and far hindleg reach forward again; other pair pushes off'}
                if i['slug']=='cely':
                    i['prompt']+=' All gait instructions apply to the FOUR LEGS OF THE PALE MOUNT. Rider stays seated in the original saddle, both rider feet in stirrups, synchronized slight rider motion; never stretch rider legs into mount legs.'
                else:i['prompt']+=' Use the original small creature FOUR-PAW anatomy and natural gait, not human legs, boots or fingers.'
            i['prompt']+=' FINAL GAIT POSE OVERRIDE: '+poses[phase]+'. Foot alternation and changing leg silhouette are mandatory; do not return another standing pose or repeat the same forward leg across every frame. Keep face, torso and costume identity unchanged.'
            if phase==3 and i['slug'] not in ('cely','neru'):
                targets={'left':'Foreground knee moves RIGHT of the hip; foreground boot goes to approximately x=70%, y=90% of canvas. Far boot goes to x=36%, y=90%. Reverse the legs from the input image.',
                         'right':'Foreground knee moves LEFT of the hip; foreground boot goes to approximately x=36%, y=90%. Far boot goes to x=70%, y=90%. Reverse the legs from the input image.',
                         'down':'Boot on SCREEN RIGHT must be the LOWEST foot (about y=94%); boot on SCREEN LEFT is lifted behind (about y=83%). Reverse which foot leads.',
                         'up':'Boot on SCREEN RIGHT reaches toward TOP (about y=83%); boot on SCREEN LEFT trails near bottom (about y=94%). Reverse which foot leads.'}
                i['prompt']+=' '+targets[i['direction']]
            write(p,q)
        if i['slug']=='hero' and i['kind'] in ('map','battle'):
            i['prompt']+=' Preserve anatomical asymmetry: blue marking stays on the CHARACTER LEFT upper arm; sword stays in the CHARACTER RIGHT hand. Do not mirror the costume or move the marking to the other arm to make it visible. In right-facing profile the marking is on the far shoulder and may be occluded.'
        if i['kind']=='battle':
            i['prompt']+=' ARCHITECTURE OVERRIDE: this is a WEAPONLESS BODY sprite. References define costume identity only. Do NOT draw any equipped sword, hilt, spear, bow, staff or shield into the character body. Keep the original weapon-hand motion with a naturally curled EMPTY grip; separate Weapon Factory supplies the equipment. Natural creature attacks remain body-only. Preserve head, hands, feet and cloth with transparent margins. Weapon grip annotation is required before equipment rendering.'
            i['weapon_embedded']=False
            palette_path=ROOT/'game_factory/hero_correction/hero_battle_palette.json'
            if slug=='hero' and palette_path.exists():
                locked=read(palette_path)
                for reference in locked['owner_approved_design_references']:
                    path=str(safe(reference['path']))
                    if path not in refs:refs.append(path)
                swatch=palette_path.with_suffix('.png')
                if swatch.exists():refs.append(str(swatch))
                colors='; '.join(k+': '+v['midtone'] for k,v in locked['materials'].items())
                i['prompt']+=' LOCKED HERO COLORS: input 1 supplies the weaponless pose. Original idle/step masters and the final palette swatch supply costume COLORS ONLY, never their embedded weapons. Preserve broad cream/white feather bands, muted teal/navy, sparse muted coral accents, olive, chestnut hair and dark brown pants under identical warm upper-left lighting. No extra saturated blue or red during attacks. Material midtones: '+colors+'.'
                i['palette_reference']='game_factory/hero_correction/hero_battle_palette.json'
        write(p,q)
        job={'id':i['id'],'arguments':{'prompt':i['prompt'],'referenced_image_paths':refs,'transparent_background':True}}
        write(ROOT/f"game_factory/requests/{i['id']}/attempt_{i['attempts']:02}.json",job)
        return job
    return {'complete':False,'no_eligible_jobs':True,'slug':slug}

def normalize(src,i,q):
    src=src.convert('RGBA'); alpha=src.getchannel('A')
    # Tool PNGs can contain alpha=1 noise across otherwise empty canvas.
    # Preserve originals; remove only these invisible pixels in native derivatives.
    noise_cutoff=i.get('alpha_noise_cutoff',1)
    if not 0<=noise_cutoff<=8:raise ValueError('Alpha noise cutoff exceeds conservative derivative limit')
    alpha=alpha.point(lambda v:0 if v<=noise_cutoff else v);src.putalpha(alpha);bbox=alpha.getbbox()
    if not bbox or alpha.getextrema()[0]!=0: raise ValueError('Missing real transparency or empty sprite')
    if i['kind'] in ('map','battle') and (bbox[0]<2 or bbox[1]<2 or bbox[2]>src.width-2 or bbox[3]>src.height-2):
        raise ValueError('Source silhouette touches canvas boundary; regenerate complete weapon/limbs with transparent margins')
    crop=src.crop(bbox); w,h=i['target_dimensions']; anchor=i['anchor']
    contact_x=(bbox[0]+bbox[2])/2
    if i['kind'] in ('map','battle'):
        solid=alpha.point(lambda v:255 if v>=128 else 0)
        solid_box=solid.getbbox()
        # The lowest toe alone shifts the torso sideways when feet alternate.
        # Find the two dominant foot/leg components; ignore an outlying sword tip.
        step=4
        strip_top=max(solid_box[1],solid_box[3]-round((solid_box[3]-solid_box[1])*.18))
        coarse=solid.crop((0,strip_top,src.width,solid_box[3])).resize((math.ceil(src.width/step),max(1,math.ceil((solid_box[3]-strip_top)/step))),Image.Resampling.NEAREST)
        pixels=coarse.load();seen=set();components=[]
        for yy in range(coarse.height):
            for xx in range(coarse.width):
                if not pixels[xx,yy] or (xx,yy) in seen:continue
                todo=deque([(xx,yy)]);seen.add((xx,yy));points=[]
                while todo:
                    x,y=todo.popleft();points.append((x,y))
                    for dx,dy in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)):
                        nx,ny=x+dx,y+dy
                        if 0<=nx<coarse.width and 0<=ny<coarse.height and pixels[nx,ny] and (nx,ny) not in seen:
                            seen.add((nx,ny));todo.append((nx,ny))
                lo=min(x for x,y in points)*src.width/coarse.width
                hi=(max(x for x,y in points)+1)*src.width/coarse.width
                reach=.8 if i['kind']=='battle' else .5 if i['slug'] in ('cely','neru') else .24
                if abs((lo+hi)/2-src.width/2)<(solid_box[3]-solid_box[1])*reach:
                    components.append((len(points),lo,hi))
        components.sort(reverse=True)
        if components:
            feet=[c for c in components[:2] if c[0]>=components[0][0]*.15]
            contact_x=(min(c[1] for c in feet)+max(c[2] for c in feet))/2
    left=max(1,contact_x-bbox[0]);right=max(1,bbox[2]-contact_x)
    fit=min((anchor[0]-6)/left,(w-anchor[0]-6)/right,(min(h-6,anchor[1])-6)/crop.height)
    ratio=fit*(.85 if i['kind']=='battle' else .95)  # Fixed combat scale leaves room for raised weapons.
    for previous in q['items']:
        if previous['id']==i['id'] or previous['slug']!=i['slug'] or previous['kind']!=i['kind']:continue
        if i['kind']=='map' and previous['direction']!=i['direction']:continue
        norm=previous.get('normalization',{})
        if norm.get('kind')=='fixed_ground_contact' and i['kind'] in ('map','battle'):
            ratio=norm['scale']*norm['source_size'][0]/src.width
            if ratio>fit*1.02:raise ValueError('Pose exceeds fixed-scale canvas; reframe asset, do not shrink character')
            break
    dims=(max(1,round(crop.width*ratio)),max(1,round(crop.height*ratio)))
    xy=(round(anchor[0]-(contact_x-bbox[0])*ratio),round(anchor[1]-crop.height*ratio))
    if xy[0]<0 or xy[1]<0 or xy[0]+dims[0]>w or xy[1]+dims[1]>h:raise ValueError('Native silhouette would be clipped')
    native=Image.new('RGBA',(w,h));native.alpha_composite(crop.resize(dims,Image.Resampling.NEAREST),xy)
    return native,{'kind':'fixed_ground_contact','alpha_noise_cutoff':noise_cutoff,'source_size':list(src.size),'source_bbox':list(bbox),'source_contact_x':contact_x,'scale':ratio,'native_bounds':list(native.getbbox()),'paste_position':list(xy)}

def ingest(ident,source):
    qp=ROOT/'game_factory/queue.json'; q=read(qp); i=next(v for v in q['items'] if v['id']==ident)
    if i['status']!='generating': raise ValueError('Only active jobs can be ingested')
    dest=safe(i['output']); dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists() or i.get('approval_status')=='approved': raise ValueError('Protected output')
    raw=dest.parent/'sources'/f"{dest.stem}__attempt_{i['attempts']:02}.png"
    if raw.exists() and sha(raw)!=sha(source): raise ValueError('Protected raw source')
    raw.parent.mkdir(exist_ok=True)
    (raw.parent/'.gdignore').touch(exist_ok=True)
    if not raw.exists():shutil.copy2(source,raw)
    with Image.open(raw) as src:
        if src.format!='PNG':raise ValueError('Returned source must be PNG')
        native,normalization=normalize(src,i,q)
        w,h=i['target_dimensions']
        for other in q['items']:
            if other['slug']==i['slug'] and other['kind']==i['kind'] and other['state']==i['state'] and other['direction']==i['direction'] and other['status'] in ('needs_review','approved'):
                with Image.open(safe(other['output'])) as prev:
                    if prev.size==native.size and prev.convert('RGBA').tobytes()==native.tobytes(): raise ValueError('Identical animation frame')
        native.save(dest)
    definition=next(c for c in read(ROOT/'game_factory/character_manifest.json')['characters'] if c['character_id']==i['character_id'])
    i.update(status='needs_review',source_png=str(raw.relative_to(ROOT)).replace('\\','/'),sha256=sha(dest),
             source_reference_sha256=sha(safe(i['source_reference'])),pixel_dimensions=[w,h],
             footprint=definition['map_ground_footprint'] if i['kind']=='map' else None,
             orientation=i['direction'] or ('right' if i['kind']=='battle' else i['state']),
             validation_result={'png':True,'dimensions':[w,h],'alpha':True,'normalization':'NEAREST uniform fit alpha bounds; ground anchor; source preserved',
             'native_visual_review':'required','identity':'unapproved','sequence':'unapproved'},normalization=normalization)
    write(dest.with_suffix('.json'),i); write(qp,q); refresh()
    return {'id':ident,'output':str(dest),'status':i['status']}

def fail(ident,reason):
    p=ROOT/'game_factory/queue.json';q=read(p);i=next(v for v in q['items'] if v['id']==ident)
    if i['status']=='approved': raise ValueError('Protected approved item')
    i.update(status='failed',last_error=reason);write(p,q)

def reject(ident,reason):
    p=ROOT/'game_factory/queue.json';q=read(p);i=next(v for v in q['items'] if v['id']==ident)
    if i.get('approval_status')=='approved' or i['status']=='approved':raise ValueError('Protected approved asset')
    old=i['output'];old_path=safe(old)
    if not old_path.exists():raise ValueError('No candidate to reject')
    i.setdefault('rejected_candidates',[]).append({'output':old,'sha256':sha(old_path),'source_png':i.get('source_png'),'reason':reason})
    for base in [ROOT,Path('H:/shining force/skl-SF'),Path('H:/shining force/pixel-art/TASK-0070/v001')]:
        meta=(base/old).with_suffix('.json')
        if meta.exists():
            previous=read(meta)
            if previous.get('approval_status')=='approved':raise ValueError('Protected approved metadata')
            previous.update(status='failed',rejection_reason=reason);write(meta,previous)
    name=f"{i['slug']}_{i['kind']}_{i['direction']+'_' if i['direction'] else ''}{i['state']}_{i['frame']:02}_v{i['attempts']+1:03}.png"
    i.update(output=str(Path(old).with_name(name)).replace('\\','/'),status='failed',last_error=reason,validation_result=None)
    write(p,q);refresh()
    return {'id':ident,'status':'failed','preserved_candidate':old,'next_output':i['output']}

def previews(slug):
    c=next(c for c in read(ROOT/'game_factory/character_manifest.json')['characters'] if c['slug']==slug)
    output=[]; report={}
    for key,a in c['animations'].items():
        frames=[Image.open(safe(p.removeprefix('res://'))).convert('RGBA') for p in a['frames']]
        if not frames: continue
        pairs=[]
        following=frames[1:]+([frames[0]] if a['loop'] and len(frames)>1 else [])
        for index,(left,right) in enumerate(zip(frames,following),1):
            if left.size!=right.size:
                pairs.append({'from_frame':index,'dimensions_mismatch':True});continue
            backgrounds=[]
            for source in (left,right):
                composite=Image.new('RGB',source.size,(40,49,65));composite.paste(source,mask=source.getchannel('A'));backgrounds.append(composite)
            diff=ImageChops.difference(*backgrounds)
            score=sum(ImageStat.Stat(diff).mean)/(3*255)
            pairs.append({'from_frame':index,'to_frame':index+1 if index<len(frames) else 1,
                          'normalized_pixel_difference':round(score,6),'identical':left.tobytes()==right.tobytes(),
                          'near_identical_warning':score<.003})
        report[key]={'frame_count':len(frames),'frame_count_complete':a['complete'],'adjacent_pairs':pairs,
                     'visual_status':'needs_review','checks':['identity','facing','costume continuity','gait alternation','anchor stability']}
        # GIF is a preview derivative only; original transparent PNG frames stay intact.
        p=ROOT/f'game_factory/previews/{slug}/{key}.gif';p.parent.mkdir(parents=True,exist_ok=True)
        frames[0].save(p,save_all=True,append_images=frames[1:],duration=int(a['duration']*1000),loop=0,disposal=2)
        output.append(str(p))
    write(ROOT/f'game_factory/previews/{slug}/sequence_qa.json',report)
    return output

def publish():
    """Copy actual saved images to owner project and canonical art workspace, never replace."""
    q=read(ROOT/'game_factory/queue.json'); count=0
    targets=[Path('H:/shining force/skl-SF'),Path('H:/shining force/pixel-art/TASK-0070/v001')]
    for i in q['items']:
        if i['status'] not in ('needs_review','approved'): continue
        for rel in [i['output'],str(Path(i['output']).with_suffix('.json')),i['source_png']]:
            src=safe(rel)
            if not src.exists(): raise ValueError('Missing saved file: '+rel)
            for target in targets:
                dest=target/rel;dest.parent.mkdir(parents=True,exist_ok=True)
                if dest.exists():
                    if sha(dest)!=sha(src): raise ValueError('Protected destination conflict: '+str(dest))
                else: shutil.copy2(src,dest)
        count+=1
    return {'published_current_outputs':count,'targets':[str(t) for t in targets]}

def main():
    p=argparse.ArgumentParser();p.add_argument('command',choices=['environment','init','next','ingest','fail','reject','previews','publish','status']);p.add_argument('--character',default='hero');p.add_argument('--id');p.add_argument('--source');p.add_argument('--reason',default='Interrupted without returned image')
    a=p.parse_args()
    if a.command=='environment': r=environment()
    elif a.command=='init': r=build_queue()
    elif a.command=='next': r=next_job(a.character)
    elif a.command=='ingest': r=ingest(a.id,a.source)
    elif a.command=='fail': r=fail(a.id,a.reason)
    elif a.command=='reject': r=reject(a.id,a.reason)
    elif a.command=='previews': r=previews(a.character)
    elif a.command=='publish': r=publish()
    else:
        from collections import Counter
        r=dict(Counter(i['status'] for i in read(ROOT/'game_factory/queue.json')['items']))
    print(json.dumps(r,ensure_ascii=False))

if __name__=='__main__': main()
