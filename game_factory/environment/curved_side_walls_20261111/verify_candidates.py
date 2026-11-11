"""Verify evidence and the honest failed production gate; never promote candidates."""
from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for art in ['ART-0044','ART-0045']:
    folder=ROOT/'game_factory/environment'/art/'v001'
    manifest=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    assert manifest['status']=='requested' and manifest['source_count']==0
    assert manifest['files']==[] and manifest['items']==[] and not manifest['production_active']
    assert not (ROOT/manifest['requested_output_path']).exists()
    receipt=json.loads((folder/'godot_review_receipt.json').read_text(encoding='utf-8'))
    assert receipt['actual_viewport'] and not receipt['requested4x_gate_passed']
    assert receipt['manifest_sha256']==sha(folder/'manifest.json')
    assert receipt['review_script_sha256']==sha(BASE/'review.gd')
    assert receipt['render_sha256']==sha(folder/'godot_candidate_review.png')
    for item in manifest['rejected_attempts']:
        assert not item['requested_4x_gate_passed'] and not item['production_active']
        assert min(item['actual_source_pixels_per_native_pixel'])<4
        for path_key,hash_key in [('source_path','sha256'),('delivery_candidate_path','sha256'),('native_review_path','native_review_sha256'),
                                  ('reference_crop_path','reference_crop_sha256'),('comparison_path','comparison_sha256')]:
            assert sha(ROOT/item[path_key])==item[hash_key],item[path_key]
    result=dict(evidence_hashes_verified=True,actual_viewport_verified=True,requested4x_gate_passed=False,
        qualified_production_count=0,production_active=False,owner_approved=True,quality_status='needs_regeneration')
    (folder/'verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(art,'evidence verified; qualification intentionally FAILED,0production outputs')
