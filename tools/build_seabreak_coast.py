"""Author a connected coastal world from existing independent catalog parts. No art generation."""
from pathlib import Path
from collections import deque
import json
import math
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import map_factory_cli as factory

ROOT=Path(__file__).resolve().parents[1]
MAP='seabreak_coast_01'
CELL=64
SIZE=[96,64]
LANDMARKS=[
    ('Sanctuary Gate',[18,12],[11,7]),
    ('Compass Court',[42,25],[15,10]),
    ('Palm Gardens',[72,18],[13,9]),
    ('Beacon Terrace',[77,47],[11,9]),
    ('Sunken Archive',[29,48],[15,8]),
    ('Quiet Overlook',[11,37],[6,5]),
]
ROUTES=[[(18,15),(24,15),(31,23),(42,25)],[(48,25),(59,25),(66,18),(72,18)],
    [(74,23),(76,34),(77,47)],[(72,49),(56,49),(42,47),(29,48)],
    [(40,32),(40,40),(29,48)],[(22,46),(15,43),(11,37)]]

def ellipse(cx,cy,rx,ry):
    return {(x,y) for y in range(cy-ry,cy+ry+1) for x in range(cx-rx,cx+rx+1)
            if ((x-cx)/rx)**2+((y-cy)/ry)**2<=1}

def corridor(points,radius=2):
    cells=set()
    for (x0,y0),(x1,y1) in zip(points,points[1:]):
        n=max(abs(x1-x0),abs(y1-y0))*4
        for i in range(n+1):
            x=round(x0+(x1-x0)*i/n);y=round(y0+(y1-y0)*i/n)
            cells.update((x+dx,y+dy) for dx in range(-radius,radius+1) for dy in range(-radius,radius+1))
    return cells

def spans(cells):
    rows=[]
    for y in range(SIZE[1]):
        xs=sorted(x for x,yy in cells if yy==y);row=[]
        for x in xs:
            if row and row[-1][1]+1==x:row[-1][1]=x
            else:row.append([x,x])
        rows.append(row)
    return rows

def make_definition():
    floors=set();islands=[]
    for _,p,r in LANDMARKS:
        cells=ellipse(*p,*r);islands.append(cells);floors.update(cells)
    paths=set().union(*(corridor(p) for p in ROUTES));floors.update(paths)
    reserved=set().union(*(corridor(p,3) for p in ROUTES))
    for _,p,_ in LANDMARKS:reserved.update(ellipse(*p,4,4))
    reserved.update((x,y) for x in range(15,22) for y in range(7,18))
    blocked=set();counter=0
    data=dict(schema_version=2,description='Seabreak Coast: six connected sanctuary terraces above a living sea; owner brief2026-11-12.',
        background_color='#238ac6',canvas_size=[6144,4096],tile_size=CELL,size=SIZE,ground_offset=[0,0],
        floor_ids=['G01','G02','G04','G07','G10'],tile_overrides=[],
        background_objects=[],ground_overlays=[],back_objects=[],objects=[],front_objects=[],effects=[],
        occlusion_mode='world_y_sort',camera={'x':1184,'y':928,'zoom':1.0},
        ocean={'tile_size':512,'fps':4,'sky_height':0},
        visual_qa={'status':'needs_review'},change_note='Owner-requested explorable exterior; six connected reusable-piece islands, no changes to Hero Room history.')
    def place(ident,x,y,scale=1,layer='objects',block=False):
        nonlocal counter
        counter+=1
        item=dict(id=ident,instance_id=f'Seabreak_{ident}_{counter:04}',x=float(x),y=float(y),scale=scale,
                  collision={'enabled':False},shadow={'type':'none'})
        data[layer].append(item)
        if block:
            cell=(int(x//CELL),int(y//CELL))
            if cell not in reserved:blocked.add(cell)
        return item
    # Cliff faces below the southern contour of each separate island, never fake terrain polygons.
    for index,cells in enumerate(islands):
        for x in range(min(x for x,y in cells)+1,max(x for x,y in cells),4):
            ys=[y for xx,y in cells if xx==x]
            if ys:place(['E025','E026','E027'][index%3],x*CELL+32,(max(ys)+1)*CELL+126,1.0,'background_objects')
    # Place long-range silhouettes in the sea, spaced asymmetrically rather than a repeated wall.
    for ident,x,y,scale in [('E036',480,460,2.4),('E039',2860,470,0.75),('E038',3200,560,1.0),
            ('E037',5660,680,2.7),('E040',5870,1820,0.9),('E039',370,2010,0.8),
            ('E038',5740,3570,1.2),('E036',3700,3880,1.8),('E040',490,3560,0.8)]:
        place(ident,x,y,scale,'background_objects')
    for x,y in sorted(floors,key=lambda p:(p[1],p[0])):
        n=((x*73856093)^(y*19349663))&0xffffffff
        tile='G%02d'%(1+n%12)
        if (x,y) in paths and not any((x,y) in island for island in islands):tile=['G05','G10'][n%2]
        data['tile_overrides'].append({'x':x,'y':y,'id':tile})
    # Six distinct destinations: gate, compass court, palm grove, beacon ring, archive and quiet lookout.
    place('A018',1184,610,0.75,'back_objects')
    place('A19',1184,915,0.9,'ground_overlays')
    place('D03',42*CELL+32,25*CELL+160,1.5,'ground_overlays')
    for cx,cy in [(42,25),(77,47)]:
        for dx,dy in [(-5,-3),(5,-3),(-5,3),(5,3)]:
            place('A012' if cx==42 else 'A017',(cx+dx)*CELL+32,(cy+dy)*CELL+48,0.8 if cx==42 else 0.6,block=True)
    for cx in [22,27,32,37]:
        place('A011',cx*CELL+32,45*CELL+48,0.9,block=True)
    place('A005',29*CELL+32,44*CELL+48,1.2,'back_objects')
    for cx,cy in [(39,28),(45,28),(70,19),(74,19),(74,49),(80,49),(26,49),(32,49),(10,38)]:
        place('F09_south',cx*CELL+32,cy*CELL+40,0.9,block=True)
    for cx,cy in [(12,10),(24,10),(67,16),(76,15),(79,20),(68,21),(74,44),(81,45),(22,51),(35,51),(9,35),(13,35)]:
        place('V030' if cx%2 else 'V031',cx*CELL+32,cy*CELL+48,1.6,block=True)
    # Plant banks follow edges and leave a generous reserved route through every destination.
    for index,(name,(cx,cy),(rx,ry)) in enumerate(LANDMARKS):
        cells=islands[index]
        for x,y in sorted(cells):
            if (x,y) in reserved or (x*17+y*29)%13:continue
            if min(abs(x-cx)/rx,abs(y-cy)/ry)<0.25 and index!=2:continue
            ident=['V025','V026','P08','P05','V030','V031'][(x*3+y+index)%6]
            place(ident,x*CELL+32,y*CELL+52,1.0 if ident not in ['V030','V031'] else 1.5,block=True)
        # Low broken stone clusters frame destinations without enclosing the route.
        for dx in [-rx+3,rx-3]:place('W027' if dx<0 else 'W028',(cx+dx)*CELL+32,(cy-2)*CELL+32,0.8,'back_objects')
    # Stone posts on the exposed bridges provide a visible route over the water.
    bridges=paths-set().union(*islands)
    for x,y in sorted(bridges):
        if x%4==0 and (x,y-1) not in bridges:
            place('A20',x*CELL+32,y*CELL+20,0.65)
    walk=floors-blocked
    regions=[]
    for y,row in enumerate(spans(walk)):
        for i,(start,end) in enumerate(row):
            regions.append(dict(id=f'coast_row_{y}_{i}',rect=[start,y,end-start+1,1],allow=['walk'],
                surface='stone',floor_height=0,ceiling_height=None,review_status='needs_review'))
    data['floor_footprint']={'row_spans':spans(floors)}
    data['navigation']=dict(schema_version=1,origin=[0,0],cell_size=CELL,grid_size=SIZE,
        default={'walk':False,'fly':False,'swim':False},regions=regions,obstacles=[],links=[])
    world=dict(schema_version=1,map_id=MAP,player_spawn=[1184,992],
        room_scene='res://scenes/main.tscn',world_scene='res://scenes/world/seabreak_coast.tscn',
        room_exit_photo={'rect':[704,864,128,64],'return_position':[768,832]},
        room_exit_factory={'rect':[688,824,160,32],'return_position':[768,784]},
        world_return_rect=[1088,576,192,128],camera_limits=[0,0,6144,4096],
        landmarks=[dict(id=name.lower().replace(' ','_'),name=name,cell=p,radius=r) for name,p,r in LANDMARKS],
        route_waypoints=[list(p) for route in ROUTES for p in route],
        floor_cells=len(floors),walk_cells=len(walk),decorative_obstacle_cells=[list(p) for p in sorted(blocked)],
        source='owner brief and existing independent catalog assets; no generated composite or character changes')
    return data,world

def main():
    if (ROOT/'map_factory/maps'/MAP).exists():
        raise SystemExit('Immutable map already exists; use a new patch revision, never rewritev0001.')
    data,world=make_definition()
    snap=factory.normalize_existing(data,MAP)
    snap['source_image']={'path':None,'sha256':None,'status':'owner_text_brief_20261112_existing_parts'}
    snap['change_note']=data['change_note']
    factory.write_revision(ROOT,MAP,snap,factory.registry(ROOT))
    out=ROOT/'map_factory/worlds/seabreak_coast_01.json';out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(world,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(MAP,world['floor_cells'],'floor cells;',world['walk_cells'],'walk cells;',sum(len(data[k]) for k in factory.LAYERS),'placed pieces')

if __name__=='__main__':main()
