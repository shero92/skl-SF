#!/usr/bin/env python3
"""Validate ChatGPT sprite-delivery byte integrity using PNG header, not pixel viewing."""
from pathlib import Path
import json,hashlib,struct,sys
root=Path(__file__).resolve().parent
manifest=json.loads((root/'manifest.json').read_text(encoding='utf8'))
entries=manifest['assets']+manifest['original_source_crops']
for row in entries:
 p=root/row['path']
 if not p.is_file():raise SystemExit(f'MISSING {p}')
 data=p.read_bytes()
 if data[:8]!=bytes.fromhex('89504e470d0a1a0a') or data[12:16]!=b'IHDR':raise SystemExit(f'BAD_PNG {p}')
 width,height=struct.unpack('>II',data[16:24])
 if [width,height]!=row['pixel_size']:raise SystemExit(f'BAD_DIMS {p}')
 if data[25] not in (4,6):raise SystemExit(f'NOT_ALPHA_PNG {p}')
 if hashlib.sha256(data).hexdigest()!=row['sha256']:raise SystemExit(f'BAD_SHA256 {p}')
print(f'PASS: {len(entries)} RGBA PNG files, correct native dimensions and SHA-256. Visual QA is NOT included.')
