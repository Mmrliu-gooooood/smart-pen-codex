from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent;B=D.parent/'imu_j107_clock_native_0405/native';N=D/'native';R=D/'replay/native';X=D/'native_negative/rollback'
def req(c,s):
 if not c:raise RuntimeError(s)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for p in N.rglob('*'):
 if p.is_file():
  q=R/p.relative_to(N);req(q.is_file()and p.read_bytes()==q.read_bytes(),'replayfile');rows.append(str(p.relative_to(N)))
req((X/'mainboard_revD.kicad_pcb').read_bytes()==(B/'mainboard_revD.kicad_pcb').read_bytes(),'native raw rollback exact')
req(json.loads((D/'verification.json').read_text())==json.loads((D/'verification_optimized.json').read_text()),'normalO verify')
req(json.loads((D/'negative.json').read_text())==json.loads((D/'negative_optimized.json').read_text()),'normalO negative')
print(json.dumps({'replay_all_native_files_byte_equal':rows,'native_freshfill_rollback_raw_byte_equal':True,'parent_sha256':sha(B/'mainboard_revD.kicad_pcb'),'candidate_sha256':sha(N/'mainboard_revD.kicad_pcb'),'normal_optimized_verification_equal':True,'normal_optimized_native_negative_equal':True},indent=2))
