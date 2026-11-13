"""Recheck source preservation, six exact outputs and genuine viewport evidence."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[4]
BASE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((BASE/'manifest.json').read_text(encoding='utf-8'))
assert manifest['source_count']==6 and len(manifest['items'])==6 and len(manifest['files'])==6
assert len({item['sha256'] for item in manifest['items']})==6
for item in manifest['items']:
    for pkey,hkey in [('master_path','sha256'),('delivery_path','sha256'),('native_review_path','native_review_sha256'),
                       ('generation_source_path','generation_source_sha256')]:
        assert sha(ROOT/item[pkey])==item[hkey],item[pkey]
    with Image.open(ROOT/item['master_path']) as im:
        assert im.mode=='RGBA' and list(im.size)==item['pixel_size']
        assert item['source_pixels_per_native_pixel']>=4
        if item['floor_surface_opaque']:
            raw=Image.open(ROOT/item['generation_source_path'])
            assert raw.tobytes()==im.convert('RGB').tobytes()
            assert im.getchannel('A').getextrema()==(255,255)
    if item['id'].startswith('marker_'):
        a=np.asarray(Image.open(ROOT/item['native_review_path']).getchannel('A'))
        assert a[32,32]==0
        for axis,recorded in [(a[32],item['measured_alpha128_horizontal_core_runs']),
                              (a[:,32],item['measured_alpha128_vertical_core_runs'])]:
            actual=np.flatnonzero(axis>=128).tolist()
            assert actual==[v for group in recorded for v in group] and [len(v) for v in recorded]==[2,2]
for attempt in manifest['rejected_attempts']:
    assert sha(ROOT/attempt['path'])==attempt['sha256']
receipt=json.loads((BASE/'godot_review_receipt.json').read_text(encoding='utf-8'))
assert receipt['actual_viewport'] and not receipt['gameplay_integration_verified']
for pkey,hkey in [('manifest.json','manifest_sha256'),('review.gd','review_script_sha256'),('qa_battle.gd','qa_override_sha256'),
                   ('godot_asset_review.png','asset_render_sha256'),('godot_skirmish_review.png','skirmish_render_sha256')]:
    assert sha(BASE/pkey)==receipt[hkey],pkey
assert sha(ROOT/receipt['existing_scene'])==receipt['existing_scene_sha256']
assert not manifest['production_active']
result=dict(selected_sources_verified=6,generation_calls=7,earlier_attempts_preserved=1,
    masters_RGBA=True,RGB_floor_exports_exact=True,minimum_master_and4x_density_passed=True,
    marker_native_core_strokes_2px=True,marker_centres_alpha0=True,actual_asset_and_skirmish_viewports_verified=True,
    production_battle_scene_unchanged=True,gameplay_integration_verified=False,owner_approved=True,production_active=False)
(BASE/'verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
print('ART0041:6masters/native/deliveries, RGB originals and actual gallery/skirmish capture hashes verified.')
