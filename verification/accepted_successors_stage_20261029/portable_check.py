#!/usr/bin/env python3
"""Manifest-only offline verifier and isolated bounded replay. Never invokes hardware/network."""
from pathlib import Path
import argparse,collections,hashlib,json,os,shutil,subprocess,sys,tempfile
D=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def need(ok,msg):
 if not ok:raise RuntimeError(msg)
def run(cmd,cwd):
 p=subprocess.run([str(x) for x in cmd],cwd=str(cwd),capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','ASAN_OPTIONS':'detect_leaks=0'},timeout=600)
 need(p.returncode==0,'Command failed: '+str(cmd)+'\n'+p.stdout+'\n'+p.stderr)
 return p.stdout

def quick():
 s=json.loads((D/'SOURCE_SUBSET_SHA256.json').read_text());count=0
 for r in s['files']:
  p=D/r['path'];need(not p.is_symlink(),'symlink');b=p.read_bytes();need(len(b)==r['bytes']and sha(b)==r['sha256'],'payload mismatch '+r['path']);count+=1
 need(sha((D/'smart_pen_next_20261028/hardware/j202_low_speed_reference_candidate/native/mainboard_revD.kicad_pcb').read_bytes())=='9a0335443167a4395431cb78abfab959893060d82a7b4da9e5fcd861bc40c038','accepted board mismatch')
 return {'source_files_verified':count,'accepted_native':'9a0335443167a4395431cb78abfab959893060d82a7b4da9e5fcd861bc40c038','NOFAB':True}
def materialize(w,args):
 for r in json.loads((D/'SOURCE_SUBSET_SHA256.json').read_text())['files']:
  p=w/r['path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((D/r['path']).read_bytes())
 deps=json.loads((D/'DEPENDENCY_LINKS.json').read_text())['files']
 if not args.native:return 0
 if args.repo_root:root=Path(args.repo_root);field='repo_path'
 else:
  root=Path(args.publication_root)if args.publication_root else next((x for x in D.parents if(x/'verified_revisions_r12/LOCAL_PUBLICATION_UNION_INDEX.json').is_file()),None);field='local_source'
  need(root is not None,'Supply --repo-root or --publication-root for native dependencies')
 for r in deps:
  b=(root/r[field]).read_bytes();need(len(b)==r['bytes']and sha(b)==r['sha256'],'dependency mismatch '+r[field]);p=w/r['capsule_path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
 return len(deps)
def software(w):
 c=w/'smart_pen_camera_capture_v2_candidate_20261029';out=run([sys.executable,c/'tools/test_host.py'],c)
 r=w/'smart_pen_camera_v2_independent_review_20261029_1824';shutil.copytree(c,r/'candidate');u=c/'third_party/esp32-camera';runs=[]
 for flags in [['-O1','-fsanitize=address,undefined','-g'],['-O2','-DNDEBUG']]:
  binary=w/('table-'+str(len(runs)));cmd=['gcc','-std=c11','-Wall','-Wextra','-Werror','-Wno-unused-parameter','-Wno-unused-variable']+flags+[f'-I{x}'for x in[c/'tests/stubs',u/'driver/include',u/'driver/private_include',u/'sensors/private_include']]+[r/'test_table_contract.c',u/'driver/sensor.c','-o',binary]
  run(cmd,r);s=run([binary],r);need('PASS 26829 independent checks' in s,'independent check count');runs.append(s.strip())
 return {'author_eight_host_groups':out.strip().splitlines(),'independent_table_modes':runs,'SDK_builds':'Not rerun in packaging; preserved fresh independent two-build evidence','real_device':'Never run; defaultOFF and empty profile retained'}
def native(w):
 h=w/'smart_pen_next_20261028/hardware';results={}
 for folder,script in [('mems_layered_independent_review','check.py'),('imu_irq_independent_review','verify.py'),('imu_i2c_independent_review','verify.py'),('j202_ground_independent_review','verify.py'),('j202_low_speed_independent_review','verify.py')]:
  f=h/folder;normal=json.loads(run(['/usr/bin/python3',f/script],f));opt=json.loads(run(['/usr/bin/python3','-O',f/script],f));need(normal==opt,'normal/-O mismatch '+folder);results[folder]={'normal_optimized_equal':True,'report':normal}
 for name in ['head_vio_port_name_erratum_v2','j202_reference_numeric_erratum']:
  f=w/'smart_pen_next_20261028/docs/electronics'/name;a=json.loads(run(['/usr/bin/python3',f/'check.py'],f));b=json.loads(run(['/usr/bin/python3','-O',f/'check.py'],f));need(a==b,'erratum mode mismatch');results[name]=a
 f=h/'j202_low_speed_independent_review';o=w/'fresh_drc.json';cmd=['kicad-cli','pcb','drc','--format','json','--exit-code-violations','--all-track-errors','--schematic-parity','--severity-all','-o',str(o),str(f/'native/mainboard_revD.kicad_pcb')];p=subprocess.run(cmd,cwd=str(f),capture_output=True,text=True,timeout=600);need(p.returncode==5,'Expected actual NOFAB DRC exit5, got '+str(p.returncode));j=json.loads(o.read_text());old=json.loads((f/'preflight.native_drc.json').read_text())
 def findings(v):
  # Item list ordering is not significant; no findings or geometry fields removed.
  a=[]
  for x in v:
   x=dict(x)
   if 'items'in x:x['items']=sorted(x['items'],key=lambda z:json.dumps(z,sort_keys=True))
   a.append(json.dumps(x,sort_keys=True))
  return collections.Counter(a)
 diff={}
 for k in ['violations','unconnected_items','schematic_parity']:
  a,b=findings(j[k]),findings(old[k]);diff[k]={'removed_from_historical':[json.loads(x)for x in (b-a).elements()],'added_relative_to_historical':[json.loads(x)for x in (a-b).elements()]}
 counts=[len(j[k])for k in ['violations','unconnected_items','schematic_parity']]
 same=all(not v['removed_from_historical']and not v['added_relative_to_historical']for v in diff.values())
 results['fresh_DRC']={'counts':counts,'historical_counts':[len(old[k])for k in ['violations','unconnected_items','schematic_parity']],'exit_code':p.returncode,'complete_finding_multisets_equal':same,'differences':diff,'command':cmd,'fresh_tool_version':j.get('kicad_version'),'historical_tool_version':old.get('kicad_version'),'decision':'NOFAB; record tool-produced finding drift, never infer copper repair from a count or representative-item change','native_pcb_unchanged':sha((f/'native/mainboard_revD.kicad_pcb').read_bytes())=='9a0335443167a4395431cb78abfab959893060d82a7b4da9e5fcd861bc40c038'}
 return results
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--software',action='store_true');ap.add_argument('--native',action='store_true');ap.add_argument('--publication-root');ap.add_argument('--repo-root');ap.add_argument('--output');a=ap.parse_args();res=quick()
 if a.software or a.native:
  with tempfile.TemporaryDirectory(prefix='smartpen-r13-')as tmp:
   w=Path(tmp);res['prior_dependency_files']=materialize(w,a)
   if a.software:res['software']=software(w)
   if a.native:res['native']=native(w)
 s=json.dumps(res,ensure_ascii=False,indent=2)+'\n'
 if a.output:Path(a.output).write_text(s)
 print(s)
