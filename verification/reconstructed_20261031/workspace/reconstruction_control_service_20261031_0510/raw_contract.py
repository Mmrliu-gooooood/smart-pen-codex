from pathlib import Path
from collections import Counter
import json,hashlib
from native_blocks import blocks
D=Path(__file__).resolve().parent;a=(D/'native/mainboard_revD.kicad_pcb').read_text();b=(D/'final_candidate/mainboard_revD.kicad_pcb').read_text()
def nonzones(s):return Counter(q for _,_,q in blocks(s)if not q.startswith('(zone'))
A,B=nonzones(a),nonzones(b);missing=list((A-B).elements());added=list((B-A).elements());kinds=Counter(x.split()[0][1:]for x in added)
checks={'all_old_nonzone_raw_blocks_exact':not missing,'added_only_tracks_vias':kinds=={'segment':476,'via':7},'parent_sha':hashlib.sha256(a.encode()).hexdigest()=='6882360bd2e0ace9957ef9382d0ba5c5b1f9c9cd04501f9710f9f87456ce7e08','selected_sha':hashlib.sha256(b.encode()).hexdigest()=='7522ff428329ffdac9a5ea5222c4c2b6e29e60d67fc4b31977396abac7c279d1'}
r={'checks':checks,'old_blocks':sum(A.values()),'new_blocks':sum(B.values()),'added_kinds':dict(kinds),'missing_block_kinds':[x.split()[0]for x in missing],'scope':'Complete exact top-level non-zone raw blocks, including all footprint/pad subfields, project board settings, old copper, drawings/text/native service labels. Filled zone material separately measured; no claim unchanged PDN.'};(D/('raw_contract_optimized.json'if not __debug__ else'raw_contract.json')).write_text(json.dumps(r,indent=2));print(r)
if not all(checks.values()):raise RuntimeError(checks)
