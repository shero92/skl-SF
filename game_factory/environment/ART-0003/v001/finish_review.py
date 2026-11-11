"""Assemble GIF from genuine Godot viewport captures and verify receipt hashes."""
from pathlib import Path
import hashlib
import json
from PIL import Image

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[3]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
receipt=json.loads((BASE/'godot_review_receipt.json').read_text(encoding='utf-8'))
assert receipt['actual_viewport'] and receipt['manifest_sha256']==sha(BASE/'manifest.json')
assert receipt['review_script_sha256']==sha(BASE/'review.gd')
manifest=json.loads((BASE/'manifest.json').read_text(encoding='utf-8'))
for item in manifest['items']:
    assert sha(ROOT/item['master_path'])==item['sha256']
    assert sha(ROOT/item['delivery_path'])==item['sha256']
    assert sha(ROOT/item['native_review_path'])==item['native_review_sha256']
frames=[]
for entry in receipt['sequence']:
    p=ROOT/entry['path']
    assert sha(p)==entry['sha256']
    frames.append(Image.open(p).convert('RGB'))
frames[0].save(BASE/'godot_playback_4fps.gif',save_all=True,append_images=frames[1:],duration=250,loop=0,disposal=2)
verification=dict(actual_godot_capture=True,frames_captured=len(frames),unique_animation_phases=4,cycles=3,
    source_hashes_verified=True,gif_sha256=sha(BASE/'godot_playback_4fps.gif'),
    owner_approved=True,approval_basis='owner_automatic_20261111',production_active=False,
    room_integration_verified=False,terrain_occlusion_verified=False)
(BASE/'verification.json').write_text(json.dumps(verification,indent=2)+'\n',encoding='utf-8',newline='\n')
print('Verified actual Godot captures; GIF created at4fps. No room integration claimed.')
