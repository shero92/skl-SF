"""Publish conservative prop-foot navigation and remove walls that crossed the intended roads."""
from pathlib import Path
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import map_factory_cli as factory
from build_seabreak_coast import ROOT,MAP,SIZE,LANDMARKS,ROUTES,corridor,ellipse,spans

def main():
    snap=factory.get_latest(ROOT,MAP)
    if snap['version']!=2:raise SystemExit('Refinement requiresv0002; never overwrite published revisions.')
    reserved=set().union(*(corridor(p,3) for p in ROUTES))
    for _,p,_ in LANDMARKS:reserved.update(ellipse(*p,4,4))
    floors={(x,y) for y,row in enumerate(snap['floor_footprint']['row_spans']) for a,b in row for x in range(a,b+1)}
    blocked=set();annotations=[];changes=[]
    for layer in factory.LAYERS:
        for part in snap[layer]:
            ident=part['id'];x,y=int(part['x']//64),int(part['y']//64)
            if ident in ['W027','W028'] and any((xx,y) in reserved for xx in range(x-2,x+3)):
                changes.append(dict(op='remove_block',instance_id=part['instance_id']))
                continue
            cells=set()
            if ident in ['W027','W028','F09_south','A017','A011']:
                cells={(x+dx,y) for dx in [-1,0,1]}
            elif ident=='A005':
                cells={(x+dx,y) for dx in [-4,-3,-2,2,3,4]}
            elif ident in ['A012','V025','V026','P08','P05','V030','V031']:
                cells={(x,y)}
            cells &= floors
            if cells:
                blocked.update(cells)
                annotations.append(dict(instance_id=part['instance_id'],blocked_cells=[list(p) for p in sorted(cells)],
                    method='conservative authored grid-foot annotation; arch has two pier groups with open centre',review_status='needs_review'))
    walk=floors-blocked
    nav=dict(snap['navigation']);nav['regions']=[]
    for y,row in enumerate(spans(walk)):
        for i,(start,end) in enumerate(row):
            nav['regions'].append(dict(id=f'coast_feet_{y}_{i}',rect=[start,y,end-start+1,1],allow=['walk'],
                surface='other',floor_height=0,ceiling_height=None,review_status='needs_review'))
    changes.append(dict(op='set_property',key='navigation',value=nav))
    patch=dict(manifest_version=1,map_id=MAP,base_version=2,base_sha256=factory.digest_json(snap),source_image=snap['source_image'],
        note='Keep roads clear of crossing walls; close decorative prop bases and arch piers while preserving its walk-through centre.',changes=changes)
    p=ROOT/'map_factory/maps'/MAP/'patches/v0003.json'
    p.write_text(json.dumps(patch,indent=2)+'\n',encoding='utf-8',newline='\n')
    factory.apply(ROOT,p)
    p=ROOT/'map_factory/worlds/seabreak_coast_01.json';world=json.loads(p.read_text())
    world['walk_cells']=len(walk);world['decorative_obstacle_cells']=[list(p) for p in sorted(blocked)]
    world['prop_navigation_annotations']=annotations
    p.write_text(json.dumps(world,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Publishedv0003:',len(changes)-1,'crossing walls removed;',len(blocked),'closed prop cells;',len(walk),'walkable cells.')
if __name__=='__main__':main()
