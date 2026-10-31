from pathlib import Path
import os,subprocess,json,hashlib,tempfile,shutil
D=Path(__file__).resolve().parent;env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',XDG_CONFIG_HOME='/tmp/control-model-replay',XDG_CACHE_HOME='/tmp/control-model-cache');targets={'reference_check.py':['reference_checkpoint.json'],'plane_delta_final.py':['plane_delta_final.json'],'plane_islands_final.py':['plane_islands_final.json'],'newpaths_final.py':['newpaths_final.json'],'retained_reference_unions.py':['retained_reference_unions.json'],'clock_centerline.py':['clock_centerline.json'],'copper_metrics.py':['copper_metrics.json'],'collinear_screen.py':['collinear_screen.json']};out=[]
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for script,files in targets.items():
 before={f:h(D/f)for f in files};subprocess.run(['/usr/bin/python3','-O',str(D/script)],env=env,check=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);out.append({'script':script,'outputs_exact_normal_optimized':all(h(D/f)==v for f,v in before.items())})
with tempfile.TemporaryDirectory(prefix='control-junction-check-')as q:
 q=Path(q);(q/'final_candidate').mkdir();shutil.copy2(D/'final_candidate/mainboard_revD.kicad_pcb',q/'final_candidate/mainboard_revD.kicad_pcb')
 for n in ['junction_exact_delta.py','junction_reversible.ndiff']:shutil.copy2(D/n,q/n)
 subprocess.run(['/usr/bin/python3',str(q/'junction_exact_delta.py')],env=env,check=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);replay=json.loads((q/'junction_exact_delta.json').read_text())==json.loads((D/'junction_exact_delta.json').read_text())
r={'models':out,'junction_delta_fresh_allowlist_only_replay_equal':replay}
if not replay or not all(x['outputs_exact_normal_optimized']for x in out):raise RuntimeError(r)
(D/'model_replay.json').write_text(json.dumps(r,indent=2));print(r)
