"""Verify selected sources, retained attempt, exact deliveries and real Godot evidence."""
from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for art in ['ART-0042','ART-0043']:
    folder=ROOT/'game_factory/environment'/art/'v001'
    manifest=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    receipt=json.loads((folder/'godot_review_receipt.json').read_text(encoding='utf-8'))
    assert receipt['actual_viewport'] and receipt['manifest_sha256']==sha(folder/'manifest.json')
    assert receipt['review_script_sha256']==sha(BASE/'review.gd')
    assert receipt['render_sha256']==sha(folder/'godot_native_review.png')
    for item in manifest['items']:
        for key,expected in [('master_path','sha256'),('delivery_path','sha256'),('native_review_path','native_review_sha256'),
                             ('reference_crop_path','reference_crop_sha256'),('comparison_path','comparison_sha256')]:
            assert sha(ROOT/item[key])==item[expected],item[key]
    for item in manifest['rejected_attempts']:
        assert sha(ROOT/item['path'])==item['sha256']
    result=dict(source_delivery_native_reference_hashes_verified=True,actual_godot_viewport_verified=True,
        manifest_sha256=sha(folder/'manifest.json'),owner_approved=True,approval_basis='owner_automatic_20261111',
        production_active=False,room_placement_collision_and_joins_verified=False)
    (folder/'verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(art,'verified master/delivery/native/reference/attempt and real Godot hashes')
