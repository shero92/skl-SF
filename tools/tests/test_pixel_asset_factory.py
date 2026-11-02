"""Offline safety/state tests. Fixture images are not claimed as generated art."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pixel_asset_factory as factory


class FactoryTests(unittest.TestCase):
    def setUp(self):
        temp_root = factory.ROOT / 'assets_generated/logs/test_temp'
        temp_root.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=temp_root)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.a = factory.read(factory.ROOT / 'tools/pixel_factory/plan.json')['assets'][3]
        self.a = dict(self.a, asset_id='G04')
        Image.new('RGBA', (64, 64), '#dcb765').save(self.root / 'ref.png')
        factory.write(self.root / 'plan.json', {'assets': [self.a]})
        self.c = dict(plan='plan.json', output='output', references=[{
            'role': 'original_room', 'path': 'ref.png', 'sha256': factory.digest(self.root / 'ref.png')}],
            max_requests=3, normalize_nearest=True, godot_executable='unused', base_map='unused')
        self.config = self.root / 'config.json'
        factory.write(self.config, self.c)
        self.f = factory.Factory(self.config, self.root)

    def ingest(self, request=None, source=None):
        return self.f.ingest(request or self.f.prepare(self.a, test=True), source or self.root / 'ref.png', 'fixture-execution')

    def test_plan_unique_all_facings_and_bed_footprint(self):
        plan = factory.Factory().plan
        self.assertEqual(len(plan), 128)
        self.assertEqual(len({factory.key(a) for a in plan}), 128)
        beds = [a for a in plan if a['identity'] == 'royal_wooden_bed']
        self.assertEqual({a['orientation'] for a in beds}, {'south', 'west', 'north', 'east'})
        self.assertEqual([(a['footprint_tiles_x'], a['footprint_tiles_y']) for a in beds], [(3, 4), (4, 3), (3, 4), (4, 3)])
        self.assertEqual(len({factory.prompt(a) for a in plan}), 128)

    def test_missing_gate_blocks_batch_before_reservation(self):
        with self.assertRaisesRegex(ValueError, 'Batch locked'):
            self.f.batch()
        self.assertFalse((self.f.out / 'logs/budget.json').exists())

    def test_reference_hash_prevents_reservation(self):
        (self.root / 'ref.png').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            self.f.prepare(self.a, test=True)
        self.assertFalse((self.f.out / 'logs/budget.json').exists())

    def test_no_duplicate_inflight_request(self):
        self.f.prepare(self.a, test=True)
        with self.assertRaisesRegex(ValueError, 'still pending'):
            self.f.prepare(self.a, test=True)

    def test_failure_preserves_log_and_reservation(self):
        req = self.f.prepare(self.a, test=True)
        self.f.fail(req, 'tool unavailable')
        self.assertFalse(req.exists())
        self.assertEqual(len(list((self.f.out / 'failed').glob('**/request.json'))), 1)
        self.assertEqual(factory.read(self.f.out / 'logs/budget.json')['reserved_tool_calls'], 1)
        self.assertEqual(factory.read(self.f.out / 'metadata/G04__default.json')['generation_status'], 'needs_regeneration')

    def test_budget_cap_persists_across_restart(self):
        self.c['max_requests'] = 1
        factory.write(self.config, self.c)
        self.f = factory.Factory(self.config, self.root)
        self.f.fail(self.f.prepare(self.a, test=True), 'fixture')
        self.f = factory.Factory(self.config, self.root)
        with self.assertRaisesRegex(ValueError, 'limit reached'):
            self.f.prepare(self.a, test=True)

    def test_invalid_source_quarantined(self):
        bad = self.root / 'bad.png'
        bad.write_bytes(b'not an image')
        with self.assertRaises(ValueError):
            self.ingest(source=bad)
        self.assertEqual(len(list((self.f.out / 'failed').glob('**/failure.json'))), 1)
        self.assertFalse((self.f.out / 'test_gate.json').exists())

    def test_ingest_native_metadata_preview_and_gate(self):
        with patch.object(self.f, 'godot'):
            meta = self.ingest()
        self.assertEqual(meta['approval_status'], 'pending')
        self.assertEqual(meta['tool'], 'image_gen')
        self.assertTrue(meta['validation']['passed'])
        self.assertEqual(len(list((self.f.out / 'previews').glob('**/repeat_*.png'))), 2)
        self.f.check_gate()
        Image.new('RGBA', (64, 64), 'red').save(self.f.out / meta['filename'])
        with self.assertRaisesRegex(ValueError, 'changed'):
            self.f.check_gate()

    def test_approved_asset_never_replaced(self):
        with patch.object(self.f, 'godot'):
            self.ingest()
        self.f.review(self.a, 'approve', 'owner-fixture', 'fixture only')
        marker = self.f.out / 'approved/G04__default.json'
        approved = factory.read(marker)
        before = factory.digest(self.f.out / approved['filename'])
        with self.assertRaisesRegex(ValueError, 'immutable'):
            self.f.prepare(self.a, test=True)
        with self.assertRaisesRegex(ValueError, 'immutable'):
            self.f.review(self.a, 'reject', 'fixture', 'fixture')
        self.assertEqual(before, factory.digest(self.f.out / approved['filename']))

    def test_native_downscale_recorded(self):
        Image.new('RGBA', (1024, 1024), '#c8b566').save(self.root / 'big.png')
        with patch.object(self.f, 'godot'):
            meta = self.ingest(source=self.root / 'big.png')
        self.assertEqual(meta['normalization']['filter'], 'NEAREST_CONTAIN')
        with Image.open(self.f.out / meta['filename']) as image:
            self.assertEqual(image.size, (64, 64))

    def test_grid_alpha_and_empty_checks(self):
        a = dict(self.a, transparent_background=True, category='props')
        self.assertIn('missing_transparency', factory.validate_png(self.root / 'ref.png', a)['errors'])
        Image.new('RGBA', (64, 64)).save(self.root / 'empty.png')
        self.assertIn('empty_image', factory.validate_png(self.root / 'empty.png', a)['errors'])
        with self.assertRaisesRegex(ValueError, '64 px'):
            factory.validate_spec(dict(self.a, native_width=65))

    def test_path_escape_and_lock_exclusion(self):
        with self.assertRaisesRegex(ValueError, 'escapes'):
            factory.safe_path(self.root, '../outside')
        with factory.exclusive(self.root / 'lock'):
            with self.assertRaisesRegex(ValueError, 'locked'):
                with factory.exclusive(self.root / 'lock'):
                    pass

    def test_consumed_request_cannot_be_reused(self):
        req = self.f.prepare(self.a, test=True)
        with patch.object(self.f, 'godot'):
            self.ingest(req)
        with self.assertRaisesRegex(ValueError, 'consumed'):
            self.ingest(req)


if __name__ == '__main__':
    unittest.main()
