from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent;D=O/'mirror/smart_pen_next_20261028/hardware/camera_isolation_control_native_0628';F=O.parent/'smart_pen_next_20261028/hardware/camera_isolation_control_native_0628';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks={}
for s in ['verify','physical_native','reference_delta','aon_neck_screen','native_negative']:
 a=json.loads((O/f'raw/{s}_normal.json').read_text());b=json.loads((O/f'raw/{s}_optimized.json').read_text());checks[s]=a==b
 if a!=b:raise RuntimeError(s+' modes differ')
for mode in ['normal','optimized']:
 N=D/f'fresh_replay_{mode}/native';files=[p for p in (D/'native').rglob('*')if p.is_file()]
 if any(p.read_bytes()!=(N/p.relative_to(D/'native')).read_bytes()for p in files):raise RuntimeError('replay')
 if (D/'materialization.json').read_bytes()!=(N.parent/'materialization.json').read_bytes():raise RuntimeError('map')
checks['replay_both_modes_bytes']=True
checks['rollback_raw_parent_bytes']=(D/'native_negative/rollback/mainboard_revD.kicad_pcb').read_bytes()==(D.parent/'imu_control_native_0522/native/mainboard_revD.kicad_pcb').read_bytes()
rows=json.loads((O/'raw/frozen_initial_hashes.json').read_text());excluded=[r for r in rows if r['path'].startswith('__pycache__/')];assert len(excluded)==2;rows=[r for r in rows if not r['path'].startswith('__pycache__/')];assert len(rows)==800;checks['frozen_799_sources_and_manifest_unchanged']=all(sha(F/r['path'])==r['sha256']for r in rows);checks['excluded_generated_pyc_paths']=[r['path']for r in excluded]
neg=json.loads((O/'raw/native_negative_normal.json').read_text());checks['ten_cut_counts']={r['case']:r['DRC_counts']for r in neg}
(O/'raw/completion.json').write_text(json.dumps(checks,indent=2)+'\n')
if not all(v for v in checks.values()):raise RuntimeError(checks)
print(json.dumps(checks,indent=2))
