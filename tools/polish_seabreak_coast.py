"""Reuse two ART-0041 native grass tiles and publish a new immutable terrain revision."""
from pathlib import Path
from copy import deepcopy
import hashlib
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import map_factory_cli as factory
from build_seabreak_coast import ROOT,MAP,LANDMARKS,ROUTES,corridor

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    # The native PNGs are committed with this task; the producer branch is provenance, not a runtime dependency.
    catalog_path=ROOT/'map_factory/metadata/asset_index.json'
    catalog=json.loads(catalog_path.read_text(encoding='utf-8'))
    template=next(a for a in catalog['assets'] if a['id']=='G01')
    provenance=[]
    for ident,suffix in [('G13','a'),('G14','b')]:
        rel=f'map_factory/parts/floors/{ident}_Coastal_Grass_{suffix.upper()}.png'
        native=ROOT/rel
        if not native.is_file():
            raise SystemExit('Missing preserved ART-0041 native export: '+rel)
        original_master=f'assets_hd/floor/skirmish_field/v001/field_grass_{suffix}.png'
        source=dict(kind='reused_independent_image_gen_asset',request_id='ART-0041',
            delivery_branch='codex/art-0041-skirmish-tiles',pull_request='https://github.com/shero92/skl-SF/pull/188',
            master_path=original_master,master_pixel_size=[1254,1254],
            master_sha256='7742a517c424a3d5775d18a687599a019d8859202ce6bc0c3937ba8fd5dacbcf' if suffix=='a' else
                json.loads((ROOT/'map_factory/worlds/grass_source_receipt.json').read_text())['field_grass_b_master_sha256'],
            sha256=sha(native),native_export_method='original ART-0041 whole-canvas nearest-neighbour64x64 export; byte-identical reuse')
        provenance.append(dict(asset_id=ident,runtime_path=rel,**source))
        found=next((a for a in catalog['assets'] if a['id']==ident),None)
        if found:
            assert found['texture_path']=='res://'+rel and found['source']['sha256']==sha(native)
            continue
        record=deepcopy(template)
        record.update(id=ident,name='Coastal Grass '+suffix.upper(),subtype='grass',texture_path='res://'+rel,
            source=source,tags=['grass','floor','seabreak','ART-0041'],owner_approved=True,
            approval_basis='owner_automatic_20261111',qa_notes='Existing independently generated grass tile reused, not regenerated. Native seam review in ART-0041 delivery.',
            qa_approval=dict(approved_by='owner',approved_on='2026-11-11',scope='owner automatic visual approval; technical native export verified',
                record='docs/OWNER_AUTOMATIC_ART_APPROVAL_20261111.md',sha256=sha(native)))
        catalog['assets'].append(record)
    catalog['asset_count']=len(catalog['assets'])
    catalog_path.write_text(json.dumps(catalog,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
    snap=factory.get_latest(ROOT,MAP)
    if snap['version']!=1:raise SystemExit('Terrain polish already published; use a fresh revision for further edits.')
    road=set().union(*(corridor(route,2) for route in ROUTES))
    changes=[]
    for entry in snap['tile_overrides']:
        x,y=entry['x'],entry['y']
        plaza=any((x-p[0])**2+(y-p[1])**2<=(7 if i in [1,3] else 3)**2 for i,(_,p,r) in enumerate(LANDMARKS))
        if (x,y) not in road and not plaza:
            changes.append(dict(op='set_tile',x=x,y=y,id='G13' if (x*3+y)%5 else 'G14'))
    manifest=dict(manifest_version=1,map_id=MAP,base_version=1,base_sha256=factory.digest_json(snap),
        note='Reuse approved ART-0041 grass sources around stone roads and landmark plazas. Preservev0001.',
        source_image=snap['source_image'],changes=changes)
    patch=ROOT/'map_factory/maps'/MAP/'patches/v0002.json';patch.parent.mkdir(exist_ok=True)
    patch.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
    factory.apply(ROOT,patch)
    out=ROOT/'map_factory/worlds/seabreak_source_reuse.json'
    out.write_text(json.dumps(dict(new_generation_calls=0,existing_art_reused=provenance),indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Published grass terrainv0002:',len(changes),'existing-grass cells; no source image changes.')
if __name__=='__main__':main()
