"""Mechanical ART-0054 export and measurements; never redraws source artwork."""
import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
META = ROOT / 'game_factory/environment/ART-0054/v001'
MASTER = 'assets_hd/hero/map_sf_down_idle/v001/hero_map_sf_down_idle_01_master.png'
NATIVE = '.agents/graphics/deliveries/ART-0054/hero_map_sf_down_idle_01.png'

def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()

def put(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')

def main():
    im = Image.open(ROOT / MASTER)
    assert im.mode == 'RGBA'
    alpha = im.getchannel('A')
    box = alpha.point(lambda a: 255 if a >= 128 else 0).getbbox()
    assert alpha.getextrema() == (0, 255)
    assert min(box[:2]) > 0 and box[2] < im.width and box[3] < im.height
    # One independently generated subject, trimmed only for export alignment.
    # Original master is preserved byte-for-byte, including its original canvas.
    figure = im.crop(box)
    size = (round(figure.width * 80 / figure.height), 80)
    small = figure.resize(size, Image.Resampling.NEAREST)
    frame = Image.new('RGBA', (96, 96))
    offset = (48 - size[0] // 2, 90 - size[1])
    frame.paste(small, offset)
    frame.save(ROOT / NATIVE)
    review = Image.new('RGBA', (480, 192), '#6c746a')
    for x, height in ((40, 80), (185, 112), (345, 144)):
        view = figure.resize((round(figure.width * height / figure.height), height), Image.Resampling.NEAREST)
        review.alpha_composite(view, (x, 175-height))
    review.save(META / 'native_scale_review.png')
    item = {'frame_id': 'hero_map_sf_down_idle_01', 'master_path': MASTER,
            'sha256': sha(MASTER), 'pixel_size': list(im.size), 'mode': im.mode,
            'alpha_extrema': list(alpha.getextrema()), 'bounds_alpha_128': list(box),
            'body_canvas_size': list(im.size), 'character_ground_anchor': [(box[0]+box[2])/2,box[3]],
            'anchor_method': 'bottom centre of alpha-128 bounds; placement convention, not anatomical socket',
            'native_path': NATIVE, 'native_sha256': sha(NATIVE), 'native_size': [96,96],
            'native_figure_height': 80, 'native_ground_anchor': [48,90],
            'facing': 'down', 'pose': 'idle', 'weapon_present': False,
            'weapon_hand_anchor': None, 'hand_rotation': None, 'weapon_scale': None,
            'weapon_render_order': None, 'attack_phase': None, 'frame_duration': None,
            'socket_status': 'not_applicable_unarmed_map_idle',
            'native_review_path': 'game_factory/environment/ART-0054/v001/native_scale_review.png',
            'quality_status': 'technical_checks_passed', 'production_active': False,
            'integration_status': 'independent_frame_delivered_not_animation_set'}
    data = {'schema_version': 1, 'request_id': 'ART-0054', 'task_id': 'TASK-0171',
            'category': 'hero', 'delivery_branch': 'codex/art-0054-hero-map',
            'owner_approved': True, 'approval_basis': 'owner_automatic_20261111',
            'tool': 'built-in image_gen', 'model': 'unknown', 'cost_usd': None,
            'references': json.loads((META / 'reference_receipt.json').read_text(encoding='utf-8')),
            'production_active': False, 'prompt_text': (META/'prompt.txt').read_text(encoding='utf-8'),
            'owner_override': '2026-11-13: hero only, no sword; supersedes request weapon instruction',
            'rejected_attempts': [], 'items': [item], 'files': [{'path': NATIVE, 'sha256':sha(NATIVE)}]}
    put(META / 'manifest.json', data)
    put(ROOT / '.agents/graphics/deliveries/ART-0054/manifest.json', data)
    print(json.dumps(item, indent=2))

if __name__ == '__main__':
    main()
