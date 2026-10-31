from pathlib import Path
import shutil,subprocess,json,hashlib,os
D=Path(__file__).resolve().parent;out=D/'refill_validation';shutil.copytree(D/'final_candidate',out);src=D/'final_candidate/mainboard_revD.kicad_pcb';dst=out/src.name;h=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();before=h(src);rows=[]
for flag in [[],['-O']]:
 subprocess.run(['/usr/bin/python3',*flag,str(D/'fill_one.py'),str(dst)],check=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'));rows.append({'mode':'optimized'if flag else'normal','sha256':h(dst)})
r={'native_refill_reload_bytes_equal':all(x['sha256']==before for x in rows),'original_sha256':before,'passes':rows,'scope':'Independent project-matched mirror; final source never refilled in place during validation.'};(D/'final_fill_reload.json').write_text(json.dumps(r,indent=2));print(r)
if not r['native_refill_reload_bytes_equal']:raise RuntimeError('refill changed bytes')
