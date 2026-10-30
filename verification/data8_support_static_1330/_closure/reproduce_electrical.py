from pathlib import Path
import subprocess,os,json,hashlib,time,sys
D=Path(__file__).resolve().parent;W=Path(sys.argv[1]).resolve();O=Path(sys.argv[2]).resolve();O.mkdir(parents=True,exist_ok=True);H=W/'smart_pen_next_20261028/hardware';env={**os.environ,'PYTHONPATH':str(D/'electrical_audit'),'POSTR28_AUDIT_LOG':str(O/'python_audit.jsonl'),'ELECTRICAL_RECONSTRUCTION':str(W),'PYTHONDONTWRITEBYTECODE':'1','QT_QPA_PLATFORM':'offscreen'};rows=json.loads((O/'RUNS.json').read_text())if(O/'RUNS.json').exists()else[]
for name in ['data_bias_relocate_1242','review_data_bias_1312']:
 scripts=['run_checks.py','source_check.py','verify.py','physical.py','raw_delta.py','reference_classification.py','pre_via_reference.py','reference_interaction.py','replay_rollback.py','negative.py']
 if name.startswith('review'):scripts.insert(1,'independent_exact.py')
 for script in scripts:
  for opt in ([False] if script=='run_checks.py'else[False,True]):
   if any(x['name']==name and x['script']==script and x['optimized']==opt and x['exit']==0 for x in rows):continue
   key=name+'__'+script[:-3]+('__O'if opt else'');cmd=['/usr/bin/python3']+(['-O']if opt else[])+[str(H/name/script)];t=time.time();r=subprocess.run(cmd,cwd=W,env=env,capture_output=True,timeout=900);(O/(key+'.stdout')).write_bytes(r.stdout);(O/(key+'.stderr')).write_bytes(r.stderr);x={'name':name,'script':script,'optimized':opt,'exit':r.returncode,'seconds':time.time()-t,'stdout_sha256':hashlib.sha256(r.stdout).hexdigest()};rows.append(x);(O/'RUNS.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(x),flush=True)
   if r.returncode:raise RuntimeError(key+' failed '+r.stderr.decode(errors='replace')[-1500:])
print('ALL_ELECTRICAL_PASS')
