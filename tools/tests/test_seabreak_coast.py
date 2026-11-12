"""Coastal world connectivity, immutable source reuse and real room/world round trip."""
from pathlib import Path
from collections import deque
import hashlib
import json
import sys
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from battle_godot_harness import run_godot
from map_factory_cli import get_latest,asset_catalog,validate_room

class SeabreakCoastTests(unittest.TestCase):
    def setUp(self):
        self.map=get_latest(ROOT,'seabreak_coast_01')
        self.world=json.loads((ROOT/'map_factory/worlds/seabreak_coast_01.json').read_text(encoding='utf-8'))
        self.walk=set()
        for region in self.map['navigation']['regions']:
            x,y,w,h=region['rect']
            self.walk.update((xx,yy) for xx in range(x,x+w) for yy in range(y,y+h))
    def test_landmarks_are_connected_and_water_stays_closed(self):
        validate_room(self.map,asset_catalog(ROOT),'seabreak_coast_01')
        self.assertEqual(self.map['canvas_size'],[6144,4096])
        self.assertFalse(self.map['navigation']['default']['walk'])
        start=tuple(int(v//64) for v in self.world['player_spawn'])
        seen={start};queue=deque([start])
        while queue:
            x,y=queue.popleft()
            for p in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
                if p in self.walk and p not in seen:seen.add(p);queue.append(p)
        for landmark in self.world['landmarks']:
            self.assertIn(tuple(landmark['cell']),seen,landmark['name'])
        self.assertGreater(len(seen),2000)
        self.assertNotIn((0,0),self.walk)
        self.assertNotIn((95,63),self.walk)
        self.assertEqual(self.walk.intersection(map(tuple,self.world['decorative_obstacle_cells'])),set())
    def test_grass_native_sources_are_exact_and_previous_versions_survive(self):
        receipt=json.loads((ROOT/'map_factory/worlds/seabreak_source_reuse.json').read_text(encoding='utf-8'))
        for row in receipt['existing_art_reused']:
            self.assertEqual(hashlib.sha256((ROOT/row['runtime_path']).read_bytes()).hexdigest(),row['sha256'])
            self.assertEqual(row['request_id'],'ART-0041')
        self.assertEqual(receipt['new_generation_calls'],0)
        versions=ROOT/'map_factory/maps/seabreak_coast_01/versions'
        self.assertTrue((versions/'v0001.json').is_file())
        self.assertTrue((versions/'v0002.json').is_file())
        self.assertTrue(any(x['id']=='G13' for x in self.map['tile_overrides']))
    def test_actual_hero_walk_and_room_round_trip(self):
        code,output=run_godot('res://tools/verify_seabreak_coast.gd',timeout=120)
        self.assertEqual(code,0,output)
        self.assertIn('SEABREAK_COAST_WALK_AND_ROUNDTRIP_OK',output)
        self.assertNotIn('SCRIPT ERROR:',output)

if __name__=='__main__':unittest.main()
