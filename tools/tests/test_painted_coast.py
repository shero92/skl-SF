"""Native square-block paintings, story discovery, connected safe ground and real travel."""
from pathlib import Path
from collections import deque
import hashlib
import json
import sys
import subprocess
import unittest
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from prepare_hidden_island import inside

def _godot():
    try:
        path=json.loads((ROOT/'.agents/planner/config.json').read_text(encoding='utf-8')).get('godot_executable')
    except (OSError,ValueError):
        return False
    return isinstance(path,str) and Path(path).is_file()


class PaintedCoastTests(unittest.TestCase):
    def setUp(self):
        self.world=json.loads((ROOT/'map_factory/painted_worlds/hidden_island/v001/world.json').read_text(encoding='utf-8'))
    def test_sources_are_native_identity_copies_and_discoverable(self):
        m=json.loads((ROOT/'game_factory/environment/ART-0052/v003/manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(m['source_count'],6)
        self.assertEqual(len(self.world['zones']),6)
        for item in m['items']:
            for pk,hk in [('master_path','sha256'),('runtime_path','runtime_sha256'),('delivery_path','delivery_sha256')]:
                self.assertEqual(hashlib.sha256((ROOT/item[pk]).read_bytes()).hexdigest(),item[hk])
            im=Image.open(ROOT/item['master_path']);self.assertEqual(im.size,(1536,1024))
            self.assertEqual(im.convert('RGBA').getchannel('A').getextrema(),(255,255))
            for k in ['runtime_path','delivery_path']:
                exported=Image.open(ROOT/item[k]);self.assertEqual(exported.mode,'RGBA')
                self.assertEqual(exported.getchannel('A').getextrema(),(255,255))
                self.assertEqual(exported.convert('RGB').tobytes(),im.convert('RGB').tobytes())
            self.assertFalse(item['source_upscaled'])
        for p in ['AGENTS.md','INDEX.md','docs/INDEX.md','.agents/project/PROJECT.md']:
            self.assertIn('docs/story/INDEX.md' if p!='docs/INDEX.md' else 'story/INDEX.md',(ROOT/p).read_text(encoding='utf-8'))
        self.assertTrue((ROOT/'docs/design/STORY_CANON_AR.md').is_file())
        self.assertIn('Reef Friend',(ROOT/'docs/design/STORY_CANON_AR.md').read_text(encoding='utf-8'))
    def test_every_walk_cell_is_inside_an_authored_visible_surface_and_routes_connect(self):
        visited={self.world['default_zone']};queue=deque(visited)
        while queue:
            for p in self.world['zones'][queue.popleft()]['portals']:
                target=p['target']
                if target!='room' and target not in visited:visited.add(target);queue.append(target)
        self.assertEqual(visited,set(self.world['zones']))
        for zone in self.world['zones'].values():
            self.assertFalse(zone['navigation']['default']['walk'])
            for region in zone['navigation']['regions']:
                x,y,w,h=region['rect']
                for xx in range(x,x+w):
                    for yy in range(y,y+h):
                        self.assertTrue(any(all(inside((xx*32+dx,yy*32+dy),poly) for dx,dy in [(1,1),(31,1),(1,31),(31,31)]) for poly in zone['walk_polygons']))
            for portal in zone['portals']:
                if portal['target']!='room':self.assertIn(portal['target'],self.world['zones'])
            self.assertEqual(zone['story_phase'],'opening_before_storm_and_sword_reveal')
    def test_room_camera_and_default_route_are_retained(self):
        room=json.loads((ROOT/'map_factory/maps/hero_room_01/latest.json').read_text(encoding='utf-8'))
        self.assertEqual(self.world['camera_zoom'],room['camera']['zoom'])
        travel=json.loads((ROOT/'map_factory/worlds/seabreak_coast_01.json').read_text(encoding='utf-8'))
        self.assertEqual(travel['world_scene'],'res://scenes/world/painted_coast.tscn')
        self.assertEqual(self.world['geometry_reference']['room_trigger'],travel['room_exit_photo']['rect'])
        self.assertEqual(self.world['geometry_reference']['room_return'],travel['room_exit_photo']['return_position'])
    @unittest.skipUnless(_godot(),"configured godot_executable is not installed here")
    def test_actual_hero_walk_all_boundaries_and_room_return(self):
        config=json.loads((ROOT/'.agents/planner/config.json').read_text(encoding='utf-8'))
        proc=subprocess.run([config['godot_executable'],'--headless','--fixed-fps','60','--path',str(ROOT),
            '--script','res://tools/verify_painted_coast.gd'],capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=120)
        output=proc.stdout+proc.stderr
        self.assertEqual(proc.returncode,0,output)
        self.assertIn('PAINTED_COAST_WALK_AND_RETURN_OK',output)
        self.assertNotIn('SCRIPT ERROR:',output)

if __name__=='__main__':unittest.main()
