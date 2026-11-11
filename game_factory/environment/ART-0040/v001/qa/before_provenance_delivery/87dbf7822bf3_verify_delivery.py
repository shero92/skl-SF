"""Read-only source/delivery/native/actual-Godot receipt checks."""
from pathlib import Path
import hashlib
import json
from PIL import Image

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[3]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
d=json.loads((BASE/'manifest.json').read_text(encoding='utf-8'))
receipt=json.loads((BASE/'godot_review_receipt.json').read_text(encoding='utf-8'))
assert receipt['actual_viewport'] and receipt['manifest_sha256']==sha(BASE/'manifest.json')
assert receipt['review_script_sha256']==sha(BASE/'review.gd')
assert receipt['render_sha256']==sha(BASE/'godot_native_review.png')
for item in d['items']:
    assert sha(ROOT/item['master_path'])==item['sha256']
    assert sha(ROOT/item['delivery_path'])==item['sha256']
    assert sha(ROOT/item['native_review_path'])==item['native_review_sha256']
    with Image.open(ROOT/item['master_path']) as im:
        assert im.mode=='RGBA' and list(im.size)==item['pixel_size']
        assert im.getchannel('A').getextrema()[0]==0
        assert im.getpixel(tuple(item['origin']))[3]>=128
for attempt in d['rejected_attempts']:
    assert sha(ROOT/attempt['path'])==attempt['sha256']
result=dict(source_count=1,generation_count=2,earlier_nonselected_attempts=1,technical_halo_rejections=0,
    rgba=True,source_native_delivery_hashes_verified=True,actual_godot_capture_verified=True,
    source_mount_point_visible=True,room_mount_calibrated=False,production_active=False,
    owner_approved=True,approval_basis='owner_automatic_20261111')
(BASE/'verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
print('ART0040 source/native/delivery/earlier-attempt and actual Godot capture hashes verified.')
