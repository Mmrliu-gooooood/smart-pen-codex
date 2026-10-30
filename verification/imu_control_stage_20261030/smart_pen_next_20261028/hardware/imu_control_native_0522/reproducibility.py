from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent;N=D/'native';RP=D/'replay/native';B=D.parent/'pressure_joint_native_0433/native';X=D/'native_negative/rollback'
def req(c,m):
 if not c:raise RuntimeError(m)
req((D/'materialization.json').read_bytes()==(D/'replay/materialization.json').read_bytes(),'materialization map byte equal')
files=[]
for f in N.rglob('*'):
 if f.is_file():req((RP/f.relative_to(N)).read_bytes()==f.read_bytes(),'native replay '+str(f));files.append(str(f.relative_to(N)))
req({str(f.relative_to(N))for f in N.rglob('*')if f.is_file()}=={str(f.relative_to(RP))for f in RP.rglob('*')if f.is_file()},'replayfilelist')
req((B/'mainboard_revD.kicad_pcb').read_bytes()==(X/'mainboard_revD.kicad_pcb').read_bytes(),'freshfill backout raw exact')
checks={}
for name in['verification','physical','reference_delta','aon_neck_screen','negative','source_contract']:
 req(json.loads((D/(name+'.json')).read_text())==json.loads((D/(name+'_optimized.json')).read_text()),'normalO '+name);checks[name]=True
print(json.dumps({'status':'NATIVE_REPLAY_AND_ROLLBACK_BYTE_VERIFIED','all_native_resource_files_replayed_byte_equal':files,'materialization_map_replay_byte_equal':True,'freshfill_native_backout_raw_equals_parent':True,'parent_sha':hashlib.sha256((B/'mainboard_revD.kicad_pcb').read_bytes()).hexdigest(),'candidate_sha':hashlib.sha256((N/'mainboard_revD.kicad_pcb').read_bytes()).hexdigest(),'normal_optimized_checks_equal':checks,'format_boundary':'No property-block restoration or normalized-only caveat needed for this parent: both inverse-prefill and actual freshfill backout match raw parent bytes.'},indent=2))
