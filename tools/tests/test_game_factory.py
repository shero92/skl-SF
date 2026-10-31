import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from PIL import Image

SPEC=importlib.util.spec_from_file_location('game_factory',Path(__file__).parents[1]/'game_factory.py')
factory=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(factory)

class GameFactoryTests(unittest.TestCase):
    def setUp(self):
        self.old=factory.ROOT
        sandbox=self.old/'.godot-runtime';sandbox.mkdir(exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=sandbox)
        factory.ROOT=Path(self.temp.name)
        for slug in factory.CHARACTERS:
            p=factory.ROOT/f'map_factory/references/characters/{slug}.png.png'
            p.parent.mkdir(parents=True,exist_ok=True);Image.new('RGB',(16,16),'blue').save(p)
        factory.build_queue()

    def tearDown(self):
        self.assertTrue(Path(self.temp.name).resolve().is_relative_to((self.old/'.godot-runtime').resolve()))
        factory.ROOT=self.old;self.temp.cleanup()

    def test_six_character_targets_and_only_existing_registry(self):
        q=factory.read(factory.ROOT/'game_factory/queue.json')['items']
        self.assertEqual(len(q),565)
        self.assertEqual(len({i['character_id'] for i in q}),6)
        self.assertEqual(sum(i['kind']=='map' for i in q),240)
        self.assertEqual(sum(i['kind']=='battle' for i in q),228)
        self.assertTrue(all(not c['animations'] for c in factory.read(factory.ROOT/'game_factory/character_manifest.json')['characters']))

    def test_reservation_survives_rebuild_and_cannot_duplicate(self):
        job=factory.next_job();factory.build_queue()
        with self.assertRaises(ValueError):factory.next_job()
        factory.fail(job['id'],'interrupted')
        retry=factory.next_job();self.assertEqual(job['id'],retry['id'])
        self.assertEqual(factory.read(factory.ROOT/'game_factory/queue.json')['items'][0]['attempts'],2)

    def test_ingest_preserves_raw_and_refuses_overwrite(self):
        job=factory.next_job();src=factory.ROOT/'test_fixture.png'
        image=Image.new('RGBA',(200,200));image.paste((20,60,180,255),(50,20,150,180));image.save(src)
        result=factory.ingest(job['id'],src)
        with Image.open(result['output']) as im:self.assertEqual(im.size,(96,96))
        before=factory.sha(result['output'])
        with self.assertRaises(ValueError):factory.ingest(job['id'],src)
        self.assertEqual(before,factory.sha(result['output']))
        manifest=factory.read(factory.ROOT/'game_factory/character_manifest.json')
        self.assertFalse(manifest['characters'][0]['animations']['map_down_idle']['complete'])

    def test_missing_reference_blocks_without_substitution(self):
        (factory.ROOT/'map_factory/references/characters/cely.png.png').unlink()
        # A fresh queue reflects a missing original reference.
        (factory.ROOT/'game_factory/queue.json').unlink();factory.build_queue()
        own=[i for i in factory.read(factory.ROOT/'game_factory/queue.json')['items'] if i['slug']=='cely']
        self.assertTrue(all(i['status']=='blocked' for i in own))
        self.assertTrue(factory.next_job('cely')['no_eligible_jobs'])

    def test_weapon_margin_does_not_center_character_by_silhouette(self):
        item=factory.read(factory.ROOT/'game_factory/queue.json')['items'][0]
        source=Image.new('RGBA',(200,200))
        source.paste((120,70,30,255),(90,30,140,180))
        source.paste((30,120,180,255),(12,60,30,130))  # sword extends left, above feet
        native,norm=factory.normalize(source,item,{'items':[]})
        self.assertAlmostEqual(norm['source_contact_x'],115,delta=1)
        strip=native.getchannel('A').crop((0,87,96,91)).getbbox()
        self.assertIsNotNone(strip)
        self.assertAlmostEqual((strip[0]+strip[2])/2,48,delta=1)
        self.assertGreaterEqual(native.getbbox()[0],0)

if __name__=='__main__':unittest.main()
