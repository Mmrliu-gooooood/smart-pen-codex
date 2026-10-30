from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent;S=D.parent/'gate_control_output_candidate';M=S/'manifest.json'
if hashlib.sha256(M.read_bytes()).hexdigest()!='70f161b643809f8c930c2b32bf82725be6ba742d52635171442646c5bfd6cf52':raise RuntimeError('Input freeze identity changed')
m=json.loads(M.read_text())
for name,h in m['files'].items():
 if hashlib.sha256((S/name).read_bytes()).hexdigest()!=h:raise RuntimeError('Frozen member changed '+name)
a=json.loads((D/'classification.json').read_text());o=json.loads((D/'classification_optimized.json').read_text())
if a!=o:raise RuntimeError('normal/-O mismatch')
if a['eligible_exact_merge_count']!=0 or a['new_tracks']!=973 or a['short_lt_100um']!=669 or len(a['collinear_pairs'])!=3:raise RuntimeError('Unexpected bounded result')
if any(not r['protected_contacts'] for r in a['collinear_pairs']):raise RuntimeError('Unprotected pair incorrectly rejected')
print(json.dumps({'input_manifest_sha256':hashlib.sha256(M.read_bytes()).hexdigest(),'all_100_frozen_members_unchanged':True,'input_pcb_sha256':a['input_pcb_sha256'],'eligible_merges':0,'native_board_created_or_modified':False,'all_copper_union_same_by_bit_identical_input':True,'DRC_fill_source_pad_and_AON_island_changes':None,'test_scope':'No merge was legal and no board changed. Prior independently frozen 28/41/0 and six-core-connected AON islands remain prior evidence; no new layout/check claim.'},indent=2))
