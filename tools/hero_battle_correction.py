"""Owner-requested weaponless Hero revision. Built-in image_gen only; no API client."""
from __future__ import annotations
import argparse
import colorsys
from collections import Counter
import json
from pathlib import Path
import shutil
from PIL import Image, ImageDraw
from tools import game_factory as factory

ROOT = factory.ROOT
BASE = ROOT / 'game_factory/hero_correction'
ART = 'assets/characters/hero/battle/weaponless_v2'
MASTER = [
 'assets/characters/hero/battle/idle_ready/sources/hero_battle_idle_ready_01__attempt_01.png',
 'assets/characters/hero/battle/step/sources/hero_battle_step_01__attempt_01.png',
]
# Semantic samples in the primary master, chosen after inspecting both masters.
# Filters separate material families inside each region; samples are actual RGB medoids.
REGIONS = {
 'hair': ([680,120,925,280], (0.035,.12,.25,1)),
 'skin': ([770,258,850,325], (.035,.12,.18,.66)),
 'scarf_blue': ([655,320,812,399], (.49,.65,.25,1)),
 'feather_blue': ([420,360,580,550], (.49,.65,.25,1)),
 'feather_red': ([350,390,610,590], (0,.065,.5,1)),
 'feather_cream': ([420,338,680,540], (.07,.16,.12,.49)),
 'feather_white': ([420,338,680,540], (0,1,0,.12)),
 'feather_olive': ([930,730,1080,920], (.13,.22,.12,.60)),
 'pants_brown': ([495,880,627,1010], (.025,.13,.15,.65)),
 'leather': ([400,520,485,610], (.025,.13,.12,.70)),
 'rope': ([654,570,840,624], (.06,.15,.23,.72)),
 'gold_ornaments': ([808,423,878,493], (.065,.15,.3,.85)),
 'shell_accessories': ([720,446,763,500], (.055,.16,.04,.4)),
 'outlines': ([338,300,1125,1190], (0,1,0,1)),
}

def palette():
    images=[Image.open(ROOT/p).convert('RGBA') for p in MASTER]
    materials={}
    for material,(region,limits) in REGIONS.items():
        samples=[]
        # Primary semantic regions anchor material identity. Secondary contributes
        # independently measured global color balance, never mixes skin and cloth.
        for pixel in images[0].crop(region).getdata():
            if pixel[3]<250: continue
            h,s,v=colorsys.rgb_to_hsv(*(c/255 for c in pixel[:3]))
            if limits[0]<=h<=limits[1] and limits[2]<=s<=limits[3] and (v<.20 if material=='outlines' else v>.18):
                samples.append(pixel[:3])
        if not samples: raise ValueError('Empty material sample: '+material)
        # Three luminance bands retain shadow/midtone/highlight relationships.
        samples.sort(key=lambda c:.2126*c[0]+.7152*c[1]+.0722*c[2])
        ramp=[]
        for lo,hi in ((.10,.30),(.40,.60),(.75,.95)):
            band=samples[int(len(samples)*lo):max(int(len(samples)*lo)+1,int(len(samples)*hi))]
            average=tuple(sum(c[n] for c in band)/len(band) for n in range(3))
            rgb=min(band,key=lambda c:sum((c[n]-average[n])**2 for n in range(3)))
            ramp.append('#%02x%02x%02x'%rgb)
        materials[material]={'shadow':ramp[0],'midtone':ramp[1],'highlight':ramp[2],
                             'source_region':region,'sample_count':len(samples)}
    def balance(im):
        # Same cloak envelope in both masters: excludes most hair, skin and blade.
        counts=Counter(); total=0
        for r,g,b,a in im.crop((335,335,1135,1005)).getdata():
            if a<250:continue
            h,s,v=colorsys.rgb_to_hsv(r/255,g/255,b/255);total+=1
            if .49<h<.66 and s>.32: counts['blue']+=1
            if (h<.065 or h>.97) and s>.5:counts['red']+=1
            if .07<h<.18 and s<.42 and v>.65:counts['cream_white']+=1
        return {k:round(v/max(1,total),5) for k,v in counts.items()}
    data={'schema_version':1,'character_id':'CHAR001','locked':True,
          'owner_approved_design_references':[{'path':p,'sha256':factory.sha(ROOT/p)} for p in MASTER],
          'lighting':'warm upper left, unchanged exposure and contrast',
          'materials':materials,'reference_cloak_balance':[balance(im) for im in images],
          'relationships':['cream/white feather bands remain broad between blue bands',
           'red feathers are sparse coral accents, not a dominant red mantle',
           'blue is muted teal/navy cloth, not electric blue',
           'hair warm chestnut, pants/leather dark brown, gold warm ochre',
           'shadows, midtones and highlights belong to their material ramps'],
          'validation':'semantic reference standard; metrics do not grant visual approval'}
    factory.write(BASE/'hero_battle_palette.json',data)
    swatch=Image.new('RGB',(850,len(materials)*48+40),(30,33,40));d=ImageDraw.Draw(swatch)
    d.text((15,12),'HERO LOCKED MATERIAL PALETTE - shadow / midtone / highlight',fill='white')
    for row,(name,entry) in enumerate(materials.items()):
        y=40+row*48;d.text((10,y+12),name,fill='white')
        for col,key in enumerate(('shadow','midtone','highlight')):
            x=200+col*210;d.rectangle((x,y,x+75,y+39),fill=entry[key]);d.text((x+82,y+13),entry[key],fill='white')
    swatch.save(BASE/'hero_battle_palette.png')
    return data

def init():
    palette()
    path=BASE/'queue.json';old=factory.read(path) if path.exists() else {'items':[]}
    existing={i['id']:i for i in old['items']};jobs=[]
    # Nine explicitly requested attack frames, then the missing recovery and
    # weaponless idle/step bases. Other characters stay on hold until Hero works.
    phases=[('attack_windup',n) for n in range(1,5)]+[('attack_execute',n) for n in range(1,6)]
    phases += [('attack_execute',6),('idle_ready',1),('step',1)]
    for state,n in phases:
        ident=f'CHAR001_weaponless_{state}_{n:02}'
        original=f'assets/characters/hero/battle/{state}/sources/hero_battle_{state}_{n:02}__attempt_01.png'
        if not (ROOT/original).exists():original=MASTER[0]
        jobs.append(existing.get(ident,{'id':ident,'character_id':'CHAR001','slug':'hero','kind':'battle',
          'state':state,'frame':n,'direction':'','status':'pending','attempts':0,
          'pose_reference':original,'output':f'{ART}/hero_battle_{state}_{n:02}__weaponless_v2.png',
          'target_dimensions':[256,256],'anchor':[128,240],'approval_status':'pending'}))
    factory.write(path,{'schema_version':1,'provider':'builtin_image_gen','items':jobs,'limits':{'max_attempts':3,'min_seconds_between_requests':1}})
    return {'items':len(jobs),'requested_attack_frames':9}

def next_job():
    q=factory.read(BASE/'queue.json')
    if any(i['status']=='generating' for i in q['items']):raise ValueError('Resolve active correction request first')
    for i in q['items']:
        if i['status'] not in ('pending','failed') or i['attempts']>=q['limits']['max_attempts']:continue
        if (ROOT/i['output']).exists():raise ValueError('Protected output')
        phase=factory.battle_pose('hero',i['state'],i['frame'])
        palette_data=factory.read(BASE/'hero_battle_palette.json')
        colors='; '.join(k+': '+','.join(v[t] for t in ('shadow','midtone','highlight')) for k,v in palette_data['materials'].items())
        prompt=f'''Use case: precise-object-edit. Output exactly ONE transparent pixel-art Hero battle body frame: {i['id']}. Input 1 is the POSE EDIT TARGET: preserve its exact dynamic swordsman anatomy, torso rotation, limb positions, ground baseline, head size and camera. Inputs 2 and 3 are OWNER-APPROVED MASTER DESIGN/COLOR references; their balanced subdued colors and detailed pixel rendering override the pose target's oversaturated colors. Input 4 is the locked material palette. Do not copy the pose target's excess electric blue or scarlet feathers. Preserve broad CREAM/WHITE feather bands, muted teal/navy bands, only sparse coral-red accents, olive accents, warm brown pants, chestnut hair, warm skin, rope belt and ochre gold. Same warm upper-left lighting. Material ramps: {colors}. Correct the pose target WITHOUT redesigning the costume or face.
CRITICAL: REMOVE THE ENTIRE EQUIPPED WEAPON from the CHARACTER BODY. No blade, hilt, guard, handle, pommel, shield or fake translucent weapon. The anatomical RIGHT hand is EMPTY but naturally curled in a firm cylindrical SWORD GRIP, thumb and fingers reconstructed cleanly. Preserve the original wrist and arm trajectory of a swordsman swinging a separately attached sword, not punching. No open flat right palm, damaged fingers or erased holes through the body. Left balancing hand follows the original pose. Blue arm marking stays on anatomical LEFT arm, never mirrored.
Action phase: {phase}. If this phase lacks an original target, use the master identity and draw that recovery pose in the same camera. ONE frame only, full body, right-facing three-quarter combat view. Keep body placement and size identical to input pose; stable two-foot baseline. At least 3 percent transparent margins; all fingers and feet fully visible. Native design 256x256, crisp pixel clusters, no smoothing. True transparent RGBA. No floor/shadow, text, poster, collage, effects, extra poses or extra characters. No weapon of any kind embedded in this body image.'''
        prompt+=' ABSOLUTE EMPTY-HAND CHECK: remove ALL remaining brown or gold objects protruding from either side of the gripping hand, including wooden handle remnants. Do not mistake the old sword handle for a belt strap. A clean curled hand with a small empty grip aperture is required. No object crosses the fist. FRAMING OVERRIDE: if the pose reference touches an edge, translate the WHOLE figure horizontally to center the complete silhouette at unchanged body size, and reconstruct the complete fingertips. Never crop a balancing hand. Leave at least 5 percent transparent margin on both sides.'
        if i.get('revision_note'):prompt+=' TARGETED CORRECTION: '+i['revision_note']
        i.update(status='generating',attempts=i['attempts']+1,prompt=prompt)
        factory.write(BASE/'queue.json',q)
        job={'id':i['id'],'arguments':{'prompt':prompt,'referenced_image_paths':[str(ROOT/i['pose_reference']),*(str(ROOT/p) for p in MASTER),str(BASE/'hero_battle_palette.png')],'transparent_background':True}}
        factory.write(BASE/f"requests/{i['id']}/attempt_{i['attempts']:02}.json",job)
        return job
    return None

def reject(ident,reason):
    q=factory.read(BASE/'queue.json');i=next(i for i in q['items'] if i['id']==ident)
    if i.get('approval_status')=='approved':raise ValueError('Protected approval')
    if i['status']=='generating' and not i.get('source_png'):
        raw=(ROOT/i['output']).parent/'sources'/f"{Path(i['output']).stem}__attempt_{i['attempts']:02}.png"
        if raw.exists():i['source_png']=raw.relative_to(ROOT).as_posix()
    i.setdefault('prior_candidates',[]).append({k:i.get(k) for k in ('output','source_png','sha256','normalization')})
    i['original_pose_reference']=i.get('original_pose_reference',i['pose_reference'])
    if i.get('source_png'):i['pose_reference']=i['source_png']
    i.update(status='failed',revision_note=reason,output=f"{ART}/hero_battle_{i['state']}_{i['frame']:02}__weaponless_v{i['attempts']+2}.png")
    factory.write(BASE/'queue.json',q)
    return {'id':ident,'status':'failed'}

def ingest(ident,source):
    q=factory.read(BASE/'queue.json');i=next(i for i in q['items'] if i['id']==ident)
    if i['status']!='generating':raise ValueError('Not active')
    dest=ROOT/i['output'];raw=dest.parent/'sources'/f"{dest.stem}__attempt_{i['attempts']:02}.png"
    if dest.exists():raise ValueError('Protected corrected output')
    raw.parent.mkdir(parents=True,exist_ok=True);(raw.parent/'.gdignore').touch()
    if raw.exists() and factory.sha(raw)!=factory.sha(source):raise ValueError('Protected source')
    if not raw.exists():shutil.copy2(source,raw)
    normal_queue=factory.read(ROOT/'game_factory/queue.json')
    with Image.open(raw) as im:native,norm=factory.normalize(im,i,normal_queue)
    native.save(dest)
    i.update(status='needs_review',source_png=raw.relative_to(ROOT).as_posix(),normalization=norm,
      sha256=factory.sha(dest),pixel_dimensions=list(native.size),orientation='right',layer='body',
      weapon_embedded=False,weaponless_visual_check='pending',palette_reference='game_factory/hero_correction/hero_battle_palette.json',
      pose_reference_sha256=factory.sha(ROOT/i['pose_reference']),anchor_review='pending_manual_grip_annotation')
    factory.write(dest.with_suffix('.json'),i);factory.write(BASE/'queue.json',q)
    for target in (Path('H:/shining force/skl-SF'),Path('H:/shining force/pixel-art/TASK-0070/v002')):
        for src in (dest,dest.with_suffix('.json'),raw):
            out=target/src.relative_to(ROOT);out.parent.mkdir(parents=True,exist_ok=True)
            if out.exists() and factory.sha(out)!=factory.sha(src):raise ValueError('Protected publication '+str(out))
            if not out.exists():shutil.copy2(src,out)
    return {'id':ident,'output':str(dest),'status':i['status']}

def register(annotations):
    """Register only existing corrected PNGs; annotate measured grips individually."""
    q=factory.read(BASE/'queue.json'); measured=factory.read(annotations)
    original_queue=factory.read(ROOT/'game_factory/queue.json');records={}
    for i in q['items']:
        if i['status']!='needs_review':raise ValueError('Incomplete correction '+i['id'])
        annotation=measured[i['state']+':'+str(i['frame']-1)]
        norm=i['normalization'];box=norm['source_bbox'];xy=norm['paste_position'];scale=norm['scale']
        point=annotation['source_grip']
        hand=[round(xy[n]+(point[n]-box[n])*scale,3) for n in (0,1)]
        record={'character_id':'CHAR001','animation_name':i['state'],'frame_index':i['frame']-1,
          'hand_anchor_x':hand[0],'hand_anchor_y':hand[1],
          'hand_rotation_degrees':annotation['rotation_degrees'],'weapon_scale':annotation.get('weapon_scale',2/3),
          'weapon_render_order':annotation.get('render_order','front'),'grip_type':'one_hand_sword',
          'hand_occlusion_rect':[round(hand[0])-5,round(hand[1])-5,10,10],
          'body_path':'res://'+i['output'],'body_sha256':factory.sha(ROOT/i['output']),
          'source_grip':point,'annotation_method':'individual visual source grip measurement transformed through native normalization',
          'body_ground_anchor':i['anchor'],'weaponless_visual_check':annotation['weaponless_visual_check'],
          'status':'needs_review'}
        with Image.open(ROOT/i['output']) as im:
            x,y=map(round,hand)
            if not (0<=x<im.width and 0<=y<im.height):raise ValueError('Grip outside native canvas')
            if im.crop((x-5,y-5,x+5,y+5)).getchannel('A').getbbox() is None:raise ValueError('Grip nowhere near visible hand')
        records[i['state']+':'+str(i['frame']-1)]=record
        factory.write((ROOT/i['output']).with_suffix('.equipment.json'),record)
        old=next(v for v in original_queue['items'] if v['slug']=='hero' and v['kind']=='battle' and v['state']==i['state'] and v['frame']==i['frame'])
        if old.get('approval_status')=='approved':raise ValueError('Approved production body cannot be replaced')
        if old['output']!=i['output']:
            old.setdefault('superseded_body_candidates',[]).append({k:old.get(k) for k in ('output','source_png','sha256','status')})
        old.update({k:i[k] for k in ('output','source_png','sha256','normalization','pixel_dimensions','orientation')})
        old.update(status='needs_review',weapon_embedded=False,weapon_anchors='game_factory/hero_correction/hero_weapon_anchors.json',
          palette_reference='game_factory/hero_correction/hero_battle_palette.json',revision_provider='builtin_image_gen',
          prompt=i['prompt'],generation_request=f"game_factory/hero_correction/requests/{i['id']}/attempt_{i['attempts']:02}.json")
    for old in original_queue['items']:
        if old['slug']!='hero' or old['kind']!='battle' or old.get('weapon_embedded') is False:continue
        if factory.safe(old['output']).exists():
            if old.get('approval_status')=='approved':raise ValueError('Approved production body needs a separate owner selection')
            old.setdefault('superseded_body_candidates',[]).append({k:old.get(k) for k in ('output','source_png','sha256','status')})
            old['output']=str(Path(old['output']).with_name(f"hero_battle_{old['state']}_{old['frame']:02}__weaponless_v2.png")).replace('\\','/')
            old['status']='pending'
            for field in ('source_png','sha256','normalization','validation_result'):old.pop(field,None)
        old['weapon_embedded']=False
        old['battle_body_policy']='no_embedded_equipment'
    factory.write(BASE/'hero_weapon_anchors.json',{'schema_version':1,'character_id':'CHAR001','frame_index_base':0,
      'coordinate_space':'native body PNG pixels; rotation from weapon blade pointing up, clockwise positive',
      'equipment_profile':'sword','frames':records,'approval_status':'pending_owner_visual_review'})
    factory.write(ROOT/'game_factory/queue.json',original_queue);factory.refresh()
    return {'registered_weaponless_frames':len(records),'distinct_grips':len(set((r['hand_anchor_x'],r['hand_anchor_y']) for r in records.values()))}

def qa():
    palette_data=factory.read(BASE/'hero_battle_palette.json')['materials']
    labels=list(palette_data)
    palette_image=Image.new('P',(1,1));rgb=[]
    for material in labels:
        for key in ('shadow','midtone','highlight'):
            value=palette_data[material][key].lstrip('#');rgb.extend(int(value[n:n+2],16) for n in (0,2,4))
    palette_image.putpalette(rgb+rgb[:3]*(256-len(rgb)//3))
    def metric(path):
        with Image.open(path) as im:
            im=im.convert('RGBA');data=im.tobytes();counts=Counter();sat={'blue':[],'red':[]};total=0
            mapped=im.convert('RGB').quantize(palette=palette_image,dither=Image.Dither.NONE).tobytes();materials=Counter()
            for n in range(0,len(data),16):
                r,g,b,a=data[n:n+4]
                if a<250:continue
                h,s,v=colorsys.rgb_to_hsv(r/255,g/255,b/255);total+=1
                index=mapped[n//4];materials[labels[index//3] if index<len(labels)*3 else labels[0]]+=1
                family='blue' if .49<h<.66 and s>.32 else 'red' if (h<.045 or h>.97) and s>.5 else None
                if family:counts[family]+=1;sat[family].append(s)
                if .07<h<.18 and s<.42 and v>.65:counts['cream_white']+=1
            return {'proportions':{k:round(counts[k]/max(1,total),5) for k in ('blue','red','cream_white')},
              'nearest_locked_material_proportions':{k:round(materials[k]/max(1,total),5) for k in labels},
              'mean_saturation':{k:round(sum(v)/max(1,len(v)),5) for k,v in sat.items()}}
    reference=[metric(ROOT/p) for p in MASTER];q=factory.read(BASE/'queue.json');frames=[];report=[]
    for i in q['items']:
        if i['status']!='needs_review':continue
        path=ROOT/i['output'];m=metric(ROOT/i['source_png']);warnings=[]
        for family in ('blue','red'):
            material='feather_'+family
            limit=max(r['nearest_locked_material_proportions'][material] for r in reference)*1.2+.007
            if m['nearest_locked_material_proportions'][material]>limit:warnings.append(material+'_proportion_exceeds_reference_envelope')
            if m['mean_saturation'][family]>max(r['mean_saturation'][family] for r in reference)+.08:warnings.append(family+'_saturation_exceeds_reference_envelope')
        with Image.open(path) as im:
            alpha=im.getchannel('A');bounds=alpha.getbbox()
            if im.size!=(256,256) or alpha.getextrema()[0]!=0:raise ValueError('Invalid native PNG')
            if bounds[3]!=240:warnings.append('ground_baseline_mismatch')
            if i['state'] in ('attack_windup','attack_execute'):
                display=Image.new('RGB',im.size,(32,41,54));display.paste(im,mask=alpha)
                frames.append(display.resize((512,512),Image.Resampling.NEAREST))
        report.append({'id':i['id'],'path':i['output'],'sha256':factory.sha(path),'native_dimensions':[256,256],
          'alpha':True,'native_bounds':bounds,'color_metrics':m,'diagnostic_warnings':warnings,
          'visual_weaponless_review':'requires_individual_source_review','identity_and_motion_approval':'pending_owner_review'})
    out=BASE/'previews';out.mkdir(exist_ok=True)
    if frames:frames[0].save(out/'hero_weaponless_attack_preview.gif',save_all=True,append_images=frames[1:],duration=140,loop=0,disposal=2)
    factory.write(out/'color_sequence_qa.json',{'references':reference,'frames':report,
      'method':'nearest locked material-ramp proportions plus hue/saturation; hair/pants are separate material ramps, not red feathers. This is a diagnostic, not semantic segmentation or visual approval.',
      'warning_policy':'review pose-dependent proportions visually before accepting or regenerating',
      'original_sources_preserved':True,'production_approval':False})
    return {'frames_checked':len(report),'warnings':{r['id']:r['diagnostic_warnings'] for r in report if r['diagnostic_warnings']}}

def main():
    p=argparse.ArgumentParser();p.add_argument('command',choices=['init','next','ingest','reject','register','qa']);p.add_argument('--id');p.add_argument('--source');p.add_argument('--reason');p.add_argument('--annotations');a=p.parse_args()
    result=init() if a.command=='init' else qa() if a.command=='qa' else next_job() if a.command=='next' else register(a.annotations) if a.command=='register' else reject(a.id,a.reason) if a.command=='reject' else ingest(a.id,a.source)
    print(json.dumps(result))

if __name__=='__main__':main()
