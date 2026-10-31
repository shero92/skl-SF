"""Independent weapon registry and pivot-aware PNG ingest. No generation API."""
import argparse
from pathlib import Path
import shutil
from PIL import Image
from tools import game_factory as g

ROOT=g.ROOT
BASE=ROOT/'game_factory/weapons'

def init():
    BASE.mkdir(parents=True,exist_ok=True)
    for category in ('swords','axes','spears','bows','staffs','shields'):
        (ROOT/'assets/weapons'/category).mkdir(parents=True,exist_ok=True)
    jobs=[]
    master=ROOT/'assets/characters/hero/battle/idle_ready/sources/hero_battle_idle_ready_01__attempt_01.png'
    for ident,description in (
      ('WPN_HERO_BASIC_SWORD','Reproduce the exact original Hero sword in the reference: pale blue steel blade with subtle gold ornamental engraving, warm bronze-gold crossguard and pommel, brown wrapped grip. Reference only for THIS SWORD, no hand or character.'),
      ('WPN_IRON_SWORD','A compatible second equipment option for a runtime swap test: simple cool silver/iron straight blade, dark gunmetal crossguard and pommel, charcoal leather grip, NO gold filigree or saturated blue. Visibly different from the ornate Hero sword while matching its pixel density, overall blade length and one-handed grip proportions.')):
        prompt=f'Use case: stylized-concept. Exactly ONE isolated pixel-art sword equipment PNG. {description} Full weapon only, blade straight UP vertically, handle and pommel below, frontal/flat battle sprite view. Symmetrical centerline, centered on transparent canvas. Native target128x192, sharp native pixel clusters, no smoothing. Blade tip around y=12, crossguard around y=140, grip center around y=158, pommel around y=180 on native design. Warm upper-left light matching reference, rich but controlled shading. Leave transparent margins around the whole sword. No hand, character, body, floor, cast shadow, effects, label, border, collage or multiple weapons. One sword only, true transparent RGBA.'
        job={'id':ident,'arguments':{'prompt':prompt,'referenced_image_paths':[str(master)],'transparent_background':True}}
        g.write(BASE/f'requests/{ident}.json',job);jobs.append(job)
    if not (BASE/'catalog.json').exists():g.write(BASE/'catalog.json',{'schema_version':1,'weapons':{}})
    return [j['id'] for j in jobs]

def ingest(ident,source,grip):
    if ident not in ('WPN_HERO_BASIC_SWORD','WPN_IRON_SWORD'):raise ValueError('Unknown weapon job')
    dest=ROOT/f'assets/weapons/swords/{ident.lower()}_v001.png'
    if dest.exists():raise ValueError('Protected weapon output')
    raw=dest.parent/'sources'/f'{dest.stem}__source.png';raw.parent.mkdir(parents=True,exist_ok=True)
    (raw.parent/'.gdignore').touch()
    if raw.exists() and g.sha(raw)!=g.sha(source):raise ValueError('Protected raw weapon')
    if not raw.exists():shutil.copy2(source,raw)
    with Image.open(raw) as im:
        im=im.convert('RGBA');a=im.getchannel('A').point(lambda v:0 if v<=1 else v);im.putalpha(a);box=a.getbbox()
        if not box or a.getextrema()[0]!=0:raise ValueError('Weapon requires transparency')
        if min(box[0],box[1],im.width-box[2],im.height-box[3])<2:raise ValueError('Clipped weapon source')
        crop=im.crop(box);scale=min(112/crop.width,176/crop.height)
        size=(round(crop.width*scale),round(crop.height*scale));xy=((128-size[0])//2,8)
        native=Image.new('RGBA',(128,192));native.alpha_composite(crop.resize(size,Image.Resampling.NEAREST),xy);native.save(dest)
    pivot=[round(xy[0]+(grip[0]-box[0])*scale,3),round(xy[1]+(grip[1]-box[1])*scale,3)]
    data={'asset_id':ident,'category':'swords','texture_path':'res://'+dest.relative_to(ROOT).as_posix(),
      'pixel_dimensions':[128,192],'grip_pivot':pivot,'blade_axis':'negative_y','display_scale':.9,
      'compatible_profiles':['sword'],'status':'needs_review','approval_status':'pending','sha256':g.sha(dest),
      'source_png':raw.relative_to(ROOT).as_posix(),'source_sha256':g.sha(raw),'grip_source':list(grip),
      'grip_annotation':'manual visual source measurement','layer':'equipment','anchor':pivot,
      'normalization':{'scale':scale,'source_bbox':list(box),'paste_position':list(xy)}}
    g.write(dest.with_suffix('.json'),data);catalog=g.read(BASE/'catalog.json');catalog['weapons'][ident]=data;g.write(BASE/'catalog.json',catalog)
    for target in (Path('H:/shining force/skl-SF'),Path('H:/shining force/pixel-art/TASK-0070/v002')):
        for src in (dest,dest.with_suffix('.json'),raw):
            out=target/src.relative_to(ROOT);out.parent.mkdir(parents=True,exist_ok=True)
            if out.exists() and g.sha(out)!=g.sha(src):raise ValueError('Protected destination')
            if not out.exists():shutil.copy2(src,out)
    return data

def register_anchors(slug,annotation_file):
    """Common equipment contract for all six; annotations are individual, never inferred."""
    if slug not in g.CHARACTERS:raise ValueError('Unapproved character')
    profiles=g.read(BASE/'profiles.json');cid=f'CHAR{g.CHARACTERS.index(slug)+1:03}'
    profile=profiles['character_profiles'][cid]
    if profile=='natural':return {'character_id':cid,'profile':profile,'body_only':True}
    if profile not in profiles['profiles']:raise ValueError('Equipment category must be reviewed from original reference before registering anchors')
    annotations=g.read(annotation_file);q=g.read(ROOT/'game_factory/queue.json');frames={}
    for i in q['items']:
        if i['slug']!=slug or i['kind']!='battle' or i['status'] not in ('needs_review','approved') or i.get('weapon_embedded') is not False:continue
        key=i['state']+':'+str(i['frame']-1)
        if key not in annotations:raise ValueError('Missing individually measured grip '+key)
        record=dict(annotations[key]);required=('hand_anchor_x','hand_anchor_y','hand_rotation_degrees','weapon_scale','weapon_render_order','grip_type')
        if any(k not in record for k in required):raise ValueError('Incomplete attachment '+key)
        if record['grip_type']!=profiles['profiles'][profile]['grip_type']:raise ValueError('Incompatible grip profile')
        with Image.open(g.safe(i['output'])) as im:
            if not (0<=record['hand_anchor_x']<im.width and 0<=record['hand_anchor_y']<im.height):raise ValueError('Grip outside body canvas')
        record.update(character_id=cid,animation_name=i['state'],frame_index=i['frame']-1,
          body_path='res://'+i['output'],body_sha256=g.sha(g.safe(i['output'])),status='needs_review')
        frames[key]=record
    if not frames:raise ValueError('No generated weaponless bodies to register')
    dest=ROOT/f'game_factory/characters/{slug}/weapon_anchors.json'
    if dest.exists() and g.read(dest).get('approval_status')=='approved':raise ValueError('Protected approved anchors')
    g.write(dest,{'schema_version':1,'character_id':cid,'equipment_profile':profile,'frame_index_base':0,
      'frames':frames,'approval_status':'pending_owner_visual_review'})
    g.refresh()
    return {'path':str(dest),'frames':len(frames),'profile':profile}

if __name__=='__main__':
    import json
    p=argparse.ArgumentParser();p.add_argument('command',choices=['init','ingest','register-anchors']);p.add_argument('--id');p.add_argument('--source');p.add_argument('--grip-x',type=float);p.add_argument('--grip-y',type=float);p.add_argument('--character');p.add_argument('--annotations');a=p.parse_args()
    print(json.dumps(init() if a.command=='init' else register_anchors(a.character,a.annotations) if a.command=='register-anchors' else ingest(a.id,a.source,(a.grip_x,a.grip_y))))
