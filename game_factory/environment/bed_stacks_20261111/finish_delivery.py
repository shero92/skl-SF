"""Create a checksum receipt for this task's allowlist, never include audit-context copies."""
from pathlib import Path
import hashlib
import json
ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
receipt=BASE/'delivery_receipt.json'
directories=['assets_hd/furniture/double_bed_south/v001','assets_hd/background/sea_stack_islands/v001',
    '.agents/graphics/deliveries/ART-0048','.agents/graphics/deliveries/ART-0049',
    'game_factory/environment/ART-0048/v001','game_factory/environment/ART-0049/v001',
    'game_factory/environment/bed_stacks_20261111']
files=set()
for relative in directories:
    for p in (ROOT/relative).rglob('*'):
        if p.is_file() and p!=receipt and p.suffix not in {'.uid','.import','.pyc'} and '__pycache__' not in p.parts:
            files.add(p)
for relative in ['.agents/tasks/TASK-0159_art_double_bed_sea_stacks.md',
    '.agents/graphics/requests/ART-0048_hero_room_double_bed_three_quarter.md',
    '.agents/graphics/requests/ART-0049_hero_room_sea_stack_islands.md',
    'map_factory/metadata/source_art_index.json','docs/SOURCE_ART_CATALOG.md']:
    files.add(ROOT/relative)
result=dict(task_id='TASK-0159',delivery_branch='codex/art-0048-0049-bed-stacks',destination=str(ROOT),
    owner_main_checkout_written=False,generation_calls=4,selected_assets=2,nonselected_attempts=2,
    request_complete={'ART-0048':True,'ART-0049':False},task_status='blocked',cache_required=False,
    owner_approved=True,approval_basis='owner_automatic_20261111',production_active=False,
    limitations=['Cluster source height743 below required760; exact cluster output intentionally absent.',
        'No room integration or map/collision calibration. Prior branch context excluded from receipt.'],
    files=[dict(path=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(files)])
receipt.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print('Receipt files:',len(files),'plus receipt itself; only these task files may be staged.')
