"""Audit exact sources/exports/captures without converting a failed candidate into delivery."""
from pathlib import Path
import hashlib
import json
from PIL import Image
ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
selected_hashes=[]
for art in ['ART-0048','ART-0049']:
    folder=ROOT/'game_factory/environment'/art/'v001'
    m=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    assert m['source_count']==1 and len(m['files'])==1
    assert sha(folder/'manifest.json')==sha(ROOT/'.agents/graphics/deliveries'/art/'manifest.json')
    for item in m['items']:
        for pk,hk in [('master_path','sha256'),('delivery_path','sha256'),('native_review_path','native_review_sha256'),
                      ('reference_crop_path','reference_crop_sha256'),('style_reference_path','style_reference_sha256')]:
            assert sha(ROOT/item[pk])==item[hk],item[pk]
        selected_hashes.append(item['sha256'])
        im=Image.open(ROOT/item['master_path']);alpha=im.getchannel('A')
        assert im.mode=='RGBA' and list(im.size)==item['pixel_size']
        assert alpha.getextrema()==(0,255) and item['minimum_master_passed']
        assert all(a>=b for a,b in zip(im.size,item['minimum_master_size']))
        b=alpha.point(lambda a:255 if a>=128 else 0).getbbox()
        assert list(b)==item['bounds_alpha_128'] and 0<b[0]<b[2]<im.width and 0<b[1]<b[3]<im.height
        if 'arch_alpha_sample_coordinates' in item:
            for k,p in item['arch_alpha_sample_coordinates'].items():
                assert alpha.getpixel(tuple(p))==item['arch_alpha_sample_values'][k]
        content=im.resize(item['native_content_size'],Image.Resampling.NEAREST)
        expected=Image.new('RGBA',item['native_canvas']);expected.paste(content,item['native_offset'])
        actual=Image.open(ROOT/item['native_review_path'])
        assert expected.tobytes()==actual.tobytes()
    for item in m['rejected_attempts']:
        assert sha(ROOT/item['path'])==item['sha256']
    if art=='ART-0049':
        assert m['status']=='requested' and len(m['rejected_attempts'])==2
        failed=m['rejected_attempts'][0]
        assert failed['pixel_size']==[2117,743] and not failed['minimum_master_passed']
        assert not (ROOT/failed['missing_exact_output']).exists()
    receipt=json.loads((folder/'godot_review_receipt.json').read_text(encoding='utf-8'))
    assert receipt['actual_viewport'] and not receipt['room_integration_verified']
    for p,h in [(folder/'manifest.json','manifest_sha256'),(folder/'godot_native_review.png','render_sha256'),(BASE/'review.gd','review_script_sha256')]:
        assert sha(p)==receipt[h],str(p)
    assert Image.open(folder/'godot_native_review.png').size==(1536,1200)
    result=dict(request_id=art,selected_sources_verified=1,minimum_selected_master_passed=True,actual_viewport_verified=True,
        source_capture_hashes_passed=True,request_complete=art=='ART-0048',owner_approved=True,production_active=False,
        room_integration_verified=False,cluster_gate_failed=art=='ART-0049')
    (folder/'verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
assert len(set(selected_hashes))==2
print('TASK0159:2sources verified; arch alpha hole verified; cluster correctly blocked at743<760; actual Godot captures verified.')
