"""Manifest local experimental evidence; does not publish anything."""
import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent
skip={'SHA256SUMS','MANIFEST.json','NEW_FILES.json'}
files=[]
for p in sorted(P.rglob('*')):
 if not p.is_file() or p.name in skip or '__pycache__' in p.parts:continue
 data=p.read_bytes();files.append(dict(path=str(p.relative_to(P)),bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
meta=dict(candidate='tilt_projective_v4_20261030',status='REJECTED_EXPERIMENT_NOT_INTEGRATED',synthetic_only=True,pushed=False,files=files,file_count=len(files),bytes=sum(x['bytes'] for x in files),frozen_v3_manifest_sha256=hashlib.sha256((P.parent/'smart_pen_continuous_roi_v3_candidate_20261029/verification/V3_SNAPSHOT.json').read_bytes()).hexdigest())
(P/'MANIFEST.json').write_text(json.dumps(meta,indent=2)+'\n')
(P/'SHA256SUMS').write_text(''.join(f'{x["sha256"]}  {x["path"]}\n' for x in files))
new=[x for x in files if not x['path'].startswith('source/') or x['path'] in ('source/firmware/vision/roi_projective.c','source/firmware/vision/roi_projective.h')]
(P/'NEW_FILES.json').write_text(json.dumps(dict(note='New experimental files only. Existing 394 copied baseline files are dependencies, unchanged. Publication review/allowlist remains separate; this file does not authorize upload.',files=new),indent=2)+'\n')
print('FROZEN',len(files),'files;',meta['bytes'],'bytes; new',len(new))
