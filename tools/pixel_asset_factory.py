"""Local, review-gated built-in image_gen environment factory. See docs/PIXEL_ASSET_FACTORY.md."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import uuid

from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / 'tools/pixel_factory/config.json'
CATEGORIES = ('floor', 'wall', 'architecture', 'furniture', 'decor', 'lighting', 'plants', 'props', 'background')
LAYERS = ('background', 'ground', 'wall_base', 'wall_overlay', 'furniture', 'decor', 'lighting', 'foliage', 'prop_overlay')


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.tmp')
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')
    os.replace(tmp, path)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def stamp():
    return datetime.now(timezone.utc).isoformat()


def safe_path(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('Path escapes project root')
    return path


@contextmanager
def exclusive(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise ValueError('Factory already locked; inspect interrupted process before removing lock') from None
    try:
        os.write(fd, str(os.getpid()).encode())
        yield
    finally:
        os.close(fd)
        path.unlink()


def validate_spec(a):
    if not re.fullmatch(r'[A-Z][0-9]{2}', a['asset_id']):
        raise ValueError('Invalid plan ID')
    if not re.fullmatch(r'[a-z0-9_]+', a['asset_name']):
        raise ValueError('Invalid asset name')
    if a['category'] not in CATEGORIES or a['layer_type'] not in LAYERS:
        raise ValueError('Environment category/layer required')
    if a['orientation'] not in ('default', 'south', 'west', 'north', 'east'):
        raise ValueError('Invalid facing')
    for k in ('native_width', 'native_height', 'footprint_tiles_x', 'footprint_tiles_y'):
        if type(a[k]) is not int or a[k] <= 0 or a[k] > 4096:
            raise ValueError('Invalid positive integer: ' + k)
    if a['native_width'] % 64 or a['native_height'] % 64:
        raise ValueError('Sprite canvas must align to 64 px grid')
    if not (0 <= a['anchor_x'] <= a['native_width'] and 0 <= a['anchor_y'] <= a['native_height']):
        raise ValueError('Anchor outside canvas')
    if type(a['transparent_background']) is not bool:
        raise ValueError('Transparency must be boolean')


def key(a):
    return a['asset_id'] + '__' + a['orientation']


def filename(a):
    return (f"{a['asset_id']}__{a['category']}__{a['asset_name']}__{a['orientation']}__"
            f"{a['footprint_tiles_x']}x{a['footprint_tiles_y']}__{a['native_width']}x{a['native_height']}.png")


def prompt(a):
    return f"""Produce exactly ONE standalone PNG of ONE environment asset.
Asset {a['asset_id']}: {a['title']}; category {a['category']}; identity {a['identity']}.
Specific shape/material instructions: {a['details']}.
Native game canvas {a['native_width']}x{a['native_height']} pixels. Ground footprint
{a['footprint_tiles_x']}x{a['footprint_tiles_y']} square tiles, 64x64 pixels per tile.
Anchor (pixel coordinates from top-left): {a['anchor_x']}, {a['anchor_y']}.
Facing: {a['orientation']}. Square-grid player-facing top-down / three-quarter RPG
camera; match the original room reference. Never diamond 2:1 isometric.
Reference priority: original room for camera/materials; approved floor for scale,
palette and pixel density; approved same-identity view for proportions only.
Independently redraw the facing; do not rotate or mirror another sprite.
Warm upper-left sunlight, subtle lower-right shading. Golden sandstone, pale worn
stone, warm polished wood, blue and gold textiles, lush readable foliage as relevant.
Premium handcrafted crisp pixel art, controlled detail and palette, hard pixel edges.
Fill the specified canvas without clipping; keep ground contact at the anchor.
Layer: {a['layer_type']}. Transparency required: {a['transparent_background']}.
{'Seamless square floor, subtle seams, no thick borders or heavy bevel.' if a['category'] == 'floor' else 'Single isolated object; no detached cast shadow outside its sprite.'}
No collage, contact sheet, atlas, text, labels, checkerboard, watermark, UI, characters,
unrelated objects, multiple assets, background scene, blur, smoothing, anti-aliasing,
soft painting, photorealism or 3D render appearance. Return one image only.
"""


def validate_png(path, a):
    errors = []
    try:
        with Image.open(path) as im:
            im.load()
            if im.format != 'PNG':
                errors.append('not_png')
            if im.size != (a['native_width'], a['native_height']):
                errors.append('wrong_dimensions')
            rgba = im.convert('RGBA')
            lo, hi = rgba.getchannel('A').getextrema()
            if hi == 0:
                errors.append('empty_image')
            if a['transparent_background'] and lo == 255:
                errors.append('missing_transparency')
            if a['category'] == 'floor' and lo != 255:
                errors.append('floor_not_opaque')
            colors = rgba.getcolors(rgba.width * rgba.height)
            metrics = {'unique_colors': len(colors) if colors else None, 'alpha_min': lo, 'alpha_max': hi,
                       'native_size': list(im.size), 'pixel_style_review_required': True}
    except (OSError, ValueError, Image.DecompressionBombError):
        errors.append('invalid_image')
    return {'passed': not errors, 'errors': errors, 'metrics': locals().get('metrics', {}),
            'visual_checks': 'pending_owner: silhouette, labels, single-object, perspective, palette, seams'}


class Factory:
    def __init__(self, config=DEFAULT_CONFIG, root=ROOT):
        self.root = Path(root).resolve()
        self.config_path = Path(config)
        self.c = read(config)
        self.plan = read(safe_path(self.root, self.c['plan']))['assets']
        seen = set()
        for a in self.plan:
            validate_spec(a)
            if key(a) in seen:
                raise ValueError('Duplicate asset/facing')
            seen.add(key(a))
        self.out = safe_path(self.root, self.c['output'])
        if self.out == self.root:
            raise ValueError('Output cannot be project root')
        if type(self.c['max_requests']) is not int or self.c['max_requests'] < 1:
            raise ValueError('Positive max_requests required')

    def asset(self, asset_id, orientation=None):
        found = [a for a in self.plan if a['asset_id'] == asset_id and (orientation is None or a['orientation'] == orientation)]
        if len(found) != 1:
            raise ValueError('Select exactly one asset and orientation')
        return found[0]

    def references(self):
        refs = self.c['references']
        if not any(r['role'] == 'original_room' for r in refs):
            raise ValueError('Original room reference required')
        result = []
        for r in refs:
            p = safe_path(self.root, r['path'])
            if digest(p) != r['sha256']:
                raise ValueError('Reference hash mismatch: ' + r['path'])
            with Image.open(p) as im:
                if im.format != 'PNG':
                    raise ValueError('Reference must be PNG')
            result.append(r)
        return result

    def fingerprint(self):
        return hashlib.sha256(json.dumps({'config': self.c, 'plan': self.plan}, sort_keys=True).encode()).hexdigest()

    def compile(self):
        for folder in (*CATEGORIES, 'metadata', 'previews', 'failed', 'approved', 'prompts', 'logs'):
            (self.out / folder).mkdir(parents=True, exist_ok=True)
        for a in self.plan:
            (self.out / 'prompts' / (key(a) + '.txt')).write_text(prompt(a), encoding='utf-8', newline='\n')
        for r in self.c['references']:
            if r['role'] != 'approved_floor' or not r.get('asset_id') or not r.get('approved_by'):
                continue
            a = self.asset(r['asset_id'])
            marker = self.out / 'approved' / (key(a) + '.json')
            if marker.exists():
                continue
            source = safe_path(self.root, r['path'])
            if digest(source) != r['sha256'] or not validate_png(source, a)['passed']:
                raise ValueError('Approved floor import failed validation')
            dest = self.out / 'approved' / filename(a)
            if dest.exists():
                raise ValueError('Approved destination already exists')
            shutil.copyfile(source, dest)
            m = dict(a, filename=dest.relative_to(self.out).as_posix(), sha256=digest(dest),
                     generation_status='completed', approval_status='approved',
                     approved_by=r['approved_by'], reference_assets_used=[r],
                     prompt_used='Existing owner-approved asset; no generation', notes='Imported byte-for-byte')
            write(marker, m)
            write(dest.with_suffix('.json'), m)
            write(self.out / 'metadata' / (key(a) + '.json'), m)
        write(self.out / 'manifest.json', {'assets': self.plan, 'count': len(self.plan), 'fingerprint': self.fingerprint()})

    def prepare(self, a, test=False):
        """Reserve ONE tool call and write the exact image_gen arguments. No network client."""
        self.references()
        self.compile()
        if (self.out / 'approved' / (key(a) + '.json')).exists():
            raise ValueError('Approved asset is immutable')
        status = self.out / 'metadata' / (key(a) + '.json')
        if status.exists() and read(status).get('approval_status') == 'approved':
            raise ValueError('Approved asset is immutable')
        budget_path = self.out / 'logs/budget.json'
        budget = read(budget_path) if budget_path.exists() else {'reserved_tool_calls': 0}
        if budget['reserved_tool_calls'] >= self.c['max_requests']:
            raise ValueError('Tool request limit reached')
        if not test:
            self.check_gate()
        active = list((self.out / a['category'] / key(a)).glob('*/request.json'))
        previous = active + list((self.out / 'failed' / key(a)).glob('*/request.json'))
        for request in active:
            if read(request)['execution'] == 'pending_builtin_image_gen':
                raise ValueError('Previous request still pending; ingest or fail it first')
        if len(previous) >= self.c.get('max_attempts_per_asset', 3):
            raise ValueError('Asset retry limit reached')
        budget['reserved_tool_calls'] += 1
        write(budget_path, budget)
        attempt = self.out / a['category'] / key(a) / uuid.uuid4().hex
        attempt.mkdir(parents=True)
        refs = list(self.c['references'])
        arguments = {'prompt': prompt(a), 'transparent_background': a['transparent_background'],
                     'referenced_image_paths': [str(safe_path(self.root, r['path'])) for r in refs]}
        identities = set()
        for marker in sorted((self.out / 'approved').glob('*__*.json')):
            other = read(marker)
            if other.get('identity') == a['identity'] and other['filename'] not in identities:
                path = safe_path(self.out, other['filename'])
                if digest(path) != other['sha256']:
                    raise ValueError('Approved reference hash mismatch')
                identities.add(other['filename'])
                arguments['referenced_image_paths'].append(str(path))
                refs.append({'role': 'approved_identity', 'path': str(path), 'sha256': digest(path)})
                break
        write(attempt / 'request.json', {'asset': a, 'arguments': arguments, 'references': refs,
              'test': test, 'created_at': stamp(), 'fingerprint': self.fingerprint(),
              'execution': 'pending_builtin_image_gen', 'cost_usd': None})
        return attempt / 'request.json'

    def fail(self, request_path, notes):
        path = Path(request_path).resolve()
        if not path.is_relative_to(self.out):
            raise ValueError('Request outside output')
        req = read(path)
        if req['execution'] != 'pending_builtin_image_gen':
            raise ValueError('Request already consumed')
        req.update(execution='failed_builtin_image_gen', notes=notes)
        write(path, req)
        a = req['asset']
        dest = self.out / 'failed' / key(a) / path.parent.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(path.parent), str(dest))
        write(self.out / 'metadata' / (key(a) + '.json'), dict(a, generation_status='needs_regeneration',
              approval_status='pending', notes=notes))

    def ingest(self, request_path, source, execution_id):
        """Accept the saved result of exactly one built-in tool request, then validate."""
        request_path = Path(request_path).resolve()
        if not request_path.is_relative_to(self.out):
            raise ValueError('Request outside factory output')
        req = read(request_path)
        if req['execution'] != 'pending_builtin_image_gen':
            raise ValueError('Request already consumed')
        if req['fingerprint'] != self.fingerprint():
            raise ValueError('Request config/plan changed')
        a = req['asset']
        validate_spec(a)
        if a != self.asset(a['asset_id'], a['orientation']):
            raise ValueError('Request specification differs from plan')
        if (self.out / 'approved' / (key(a) + '.json')).exists():
            raise ValueError('Approved asset is immutable')
        attempt = request_path.parent
        req.update(execution='ingested_builtin_image_gen', execution_id=execution_id)
        write(request_path, req)
        meta = dict(a, prompt_used=req['arguments']['prompt'], reference_assets_used=req['references'],
                    tool='image_gen', execution_id=execution_id, approval_status='pending',
                    generation_status='validating', created_at=stamp(), cost_usd=None, notes='')
        status_path = self.out / 'metadata' / (key(a) + '.json')
        target = attempt / filename(a)
        try:
            shutil.copyfile(source, attempt / 'source.png')
            with Image.open(source) as im:
                im.load()
                if im.format != 'PNG':
                    raise ValueError('Built-in output must be PNG')
                if a['transparent_background'] and im.convert('RGBA').getchannel('A').getextrema()[0] == 255:
                    raise ValueError('Source has no real transparency; padding cannot create background removal')
                expected = (a['native_width'], a['native_height'])
                if im.size != expected:
                    if not self.c['normalize_nearest']:
                        raise ValueError('Wrong native dimensions')
                    resized = ImageOps.contain(im.convert('RGBA'), expected, Image.Resampling.NEAREST)
                    if not a['transparent_background'] and resized.size != expected:
                        raise ValueError('Opaque aspect mismatch; no stretching/cropping')
                    canvas = Image.new('RGBA', expected)
                    canvas.alpha_composite(resized, ((expected[0] - resized.width) // 2, expected[1] - resized.height))
                    meta['normalization'] = {'source_size': list(im.size), 'target_size': list(expected), 'filter': 'NEAREST_CONTAIN'}
                    im = canvas
                im.convert('RGBA').save(target)
            qa = validate_png(target, a)
            meta.update(validation=qa, filename=target.relative_to(self.out).as_posix(), sha256=digest(target))
            if not qa['passed']:
                raise ValueError(', '.join(qa['errors']))
            self.previews(a, target, attempt)
            meta['generation_status'] = 'validated_pending_review'
            write(target.with_suffix('.json'), meta)
            write(status_path, meta)
            group_complete = all(
                (self.out / 'metadata' / (key(item) + '.json')).exists() and
                read(self.out / 'metadata' / (key(item) + '.json')).get('generation_status') in
                ('validated_pending_review', 'completed')
                for item in self.plan if item['category'] == a['category'])
            if req['test']:
                self.godot(a, target, attempt)
                write(self.out / 'test_gate.json', {'tool': 'image_gen', 'execution_id': execution_id,
                      'filename': meta['filename'], 'sha256': meta['sha256'], 'godot': True,
                      'fingerprint': self.fingerprint(), 'time': stamp()})
            elif group_complete:
                self.godot(a, target, attempt)
            return meta
        except Exception as e:
            meta.update(generation_status='needs_regeneration', notes=str(e) if isinstance(e, ValueError) else type(e).__name__)
            failed = self.out / 'failed' / key(a) / attempt.name
            failed.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(attempt), str(failed))
            if target.name in [p.name for p in failed.iterdir()]:
                meta['filename'] = (failed / target.name).relative_to(self.out).as_posix()
            write(failed / 'failure.json', meta)
            write(status_path, meta)
            raise ValueError(meta['notes']) from None

    def check_gate(self):
        path = self.out / 'test_gate.json'
        if not path.exists():
            raise ValueError('Batch locked: ingest one built-in test and pass Godot QA first')
        gate = read(path)
        if gate.get('tool') != 'image_gen' or not gate.get('godot') or gate['fingerprint'] != self.fingerprint():
            raise ValueError('Test gate stale or wrong provider')
        if digest(safe_path(self.out, gate['filename'])) != gate['sha256']:
            raise ValueError('Test asset changed')

    def previews(self, a, path, attempt):
        im = Image.open(path).convert('RGBA')
        dest = self.out / 'previews' / key(a) / attempt.name
        dest.mkdir(parents=True, exist_ok=True)
        if a['category'] in ('floor', 'wall'):
            for n in ((5, 10) if a['category'] == 'floor' else (3,)):
                sheet = Image.new('RGBA', (im.width * n, im.height * n))
                for y in range(n):
                    for x in range(n):
                        sheet.alpha_composite(im, (x * im.width, y * im.height))
                sheet.save(dest / f'repeat_{n}.png')
        room = Image.new('RGBA', (768, 768))
        floor_ref = next((r for r in self.c['references'] if r['role'] == 'approved_floor'), None)
        with Image.open(safe_path(self.root, floor_ref['path']) if floor_ref else path) as tile:
            tile = tile.convert('RGBA').resize((64, 64), Image.Resampling.NEAREST)
            for y in range(12):
                for x in range(12):
                    room.alpha_composite(tile, (x * 64, y * 64))
        x, y = 384 - a['anchor_x'], 512 - a['anchor_y']
        room.alpha_composite(im, (x, y))
        room.save(dest / 'placement.png')
        draw = ImageDraw.Draw(room)
        draw.rectangle((384, 512 - a['footprint_tiles_y'] * 64, 384 + a['footprint_tiles_x'] * 64 - 1,
                        511), outline='red', width=2)
        room.save(dest / 'footprint.png')
        views = []
        for m in (self.out / 'metadata').glob('*.json'):
            other = read(m)
            if other.get('identity') == a['identity'] and other.get('generation_status') == 'validated_pending_review':
                views.append(other)
        views = [v for v in views if key(v) != key(a)] + [dict(a, filename=path.relative_to(self.out).as_posix())]
        if len(views) > 1:
            sheet = Image.new('RGBA', (sum(v['native_width'] for v in views), max(v['native_height'] for v in views)))
            offset = 0
            for v in sorted(views, key=lambda v: v['orientation']):
                with Image.open(safe_path(self.out, v['filename'])) as sprite:
                    sheet.alpha_composite(sprite.convert('RGBA'), (offset, 0))
                offset += v['native_width']
            sheet.save(dest / 'directions.png')

    def godot(self, a, path, attempt, capture=True):
        refs = self.references()
        floor = next((r for r in refs if r['role'] == 'approved_floor'), None)
        qa_dir = attempt / 'godot_qa'
        qa_dir.mkdir(exist_ok=True)
        spec = {'sprite': str(path), 'floor': str(safe_path(self.root, floor['path'])) if floor else str(path),
                'width': a['native_width'], 'height': a['native_height'], 'anchor': [a['anchor_x'], a['anchor_y']],
                'output': str(qa_dir), 'base_path': self.c['base_map'], 'is_floor': a['category'] == 'floor'}
        spec['candidates'] = []
        for item in self.plan:
            if item['category'] != a['category']:
                continue
            status = self.out / 'metadata' / (key(item) + '.json')
            if status.exists():
                m = read(status)
                if m.get('generation_status') in ('validated_pending_review', 'completed'):
                    spec['candidates'].append({'path': str(safe_path(self.out, m['filename'])),
                                               'anchor': [m['anchor_x'], m['anchor_y']], 'id': key(item)})
        write(qa_dir / 'input.json', spec)
        env = dict(os.environ, APPDATA=str(self.out / 'logs/godot_user'))
        Path(env['APPDATA']).mkdir(parents=True, exist_ok=True)
        result = subprocess.run([self.c['godot_executable'], '--headless', '--path', str(self.root),
                                 '--script', 'res://tools/pixel_factory/assembly_test.gd', '--', str(qa_dir / 'input.json')],
                                 capture_output=True, text=True, timeout=120, env=env)
        (qa_dir / 'stdout.txt').write_text(result.stdout + result.stderr, encoding='utf-8', newline='\n')
        receipt = qa_dir / 'receipt.json'
        if result.returncode or not receipt.exists() or not read(receipt).get('passed'):
            raise ValueError('Godot Map Factory assembly QA failed')
        if capture:
            result = subprocess.run([self.c['godot_executable'], '--path', str(self.root),
                                     '--script', 'res://tools/pixel_factory/assembly_test.gd', '--',
                                     str(qa_dir / 'input.json'), 'capture'], capture_output=True, text=True,
                                     timeout=120, env=env)
            (qa_dir / 'capture.txt').write_text(result.stdout + result.stderr, encoding='utf-8', newline='\n')
            if result.returncode or not (qa_dir / 'room.png').exists() or not read(receipt).get('passed'):
                raise ValueError('Rendered Godot room capture failed')
            original = next(r for r in refs if r['role'] == 'original_room')
            with Image.open(safe_path(self.root, original['path'])) as ref, Image.open(qa_dir / 'room.png') as room:
                sheet = Image.new('RGB', (3072, 1152), '#20202a')
                for im, x in ((ref, 0), (room, 1536)):
                    fitted = ImageOps.contain(im, (1536, 1152), Image.Resampling.NEAREST)
                    sheet.paste(fitted, (x, (1152 - fitted.height) // 2))
                sheet.save(qa_dir / 'source_vs_godot.png')

    def batch(self):
        self.check_gate()
        for a in self.plan:
            s = self.out / 'metadata' / (key(a) + '.json')
            if s.exists() and read(s).get('generation_status') in ('validated_pending_review', 'completed'):
                continue
            return self.prepare(a)  # Codex executes one built-in call, ingests, then repeats.
        return None

    def review(self, a, decision, reviewer, notes):
        status = self.out / 'metadata' / (key(a) + '.json')
        m = read(status)
        if m.get('approval_status') == 'approved':
            raise ValueError('Approved assets are immutable')
        p = safe_path(self.out, m['filename'])
        if digest(p) != m['sha256'] or not validate_png(p, a)['passed']:
            raise ValueError('Asset changed or failed validation')
        if decision == 'approve':
            m.update(approval_status='approved', generation_status='completed', reviewed_by=reviewer, notes=notes, reviewed_at=stamp())
            dest = self.out / 'approved' / filename(a)
            if dest.exists():
                raise ValueError('Approved destination exists')
            shutil.copyfile(p, dest)
            m['filename'] = dest.relative_to(self.out).as_posix()
            write(dest.with_suffix('.json'), m)
            write(self.out / 'approved' / (key(a) + '.json'), m)
        else:
            m.update(approval_status='rejected', generation_status='needs_regeneration', notes=notes, reviewed_by=reviewer)
            dest = self.out / 'failed' / key(a) / p.parent.name
            dest.mkdir(parents=True, exist_ok=True)
            shutil.move(str(p), str(dest / p.name))
            m['filename'] = (dest / p.name).relative_to(self.out).as_posix()
        write(status, m)
        write((dest if decision == 'approve' else dest / p.name).with_suffix('.json'), m)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config', type=Path, default=DEFAULT_CONFIG)
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('compile')
    sub.add_parser('preflight')
    sub.add_parser('next')
    ingest = sub.add_parser('ingest')
    ingest.add_argument('request', type=Path)
    ingest.add_argument('source', type=Path)
    ingest.add_argument('--execution-id', required=True, help='Actual built-in tool call/output ID')
    fail = sub.add_parser('fail')
    fail.add_argument('request', type=Path)
    fail.add_argument('--notes', required=True)
    for name in ('prepare', 'approve', 'reject'):
        s = sub.add_parser(name)
        s.add_argument('asset_id')
        s.add_argument('--orientation')
        if name == 'prepare':
            s.add_argument('--test', action='store_true')
        else:
            s.add_argument('--reviewer', required=True)
            s.add_argument('--notes', required=True)
    args = p.parse_args()
    try:
        f = Factory(args.config)
        with exclusive(f.out / 'factory.lock'):
            if args.command == 'compile':
                f.compile()
                print(f'Compiled {len(f.plan)} independent prompts')
            elif args.command == 'preflight':
                print(json.dumps({'tool_required': 'image_gen', 'references': f.references(),
                      'note': 'Tool availability is checked by Codex, not by a Python API client.'}))
            elif args.command == 'next':
                print(f.batch() or 'Queue complete')
            elif args.command == 'ingest':
                print(json.dumps(f.ingest(args.request, args.source, args.execution_id)))
            elif args.command == 'fail':
                f.fail(args.request, args.notes)
            elif args.command == 'prepare':
                print(f.prepare(f.asset(args.asset_id, args.orientation), args.test))
            else:
                f.review(f.asset(args.asset_id, args.orientation), args.command, args.reviewer, args.notes)
    except (ValueError, OSError, subprocess.SubprocessError) as e:
        print('Factory stopped: ' + str(e))
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
