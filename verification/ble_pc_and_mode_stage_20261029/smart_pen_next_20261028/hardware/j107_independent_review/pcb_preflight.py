#!/usr/bin/env python3
"""Fail-closed candidate/project binding before native DRC. No manufacturing approval inferred."""
from pathlib import Path
import argparse, hashlib, json, re, subprocess, sys, datetime, os

def sha_bytes(b):return hashlib.sha256(b).hexdigest()
def sha(p):return sha_bytes(Path(p).read_bytes())
def canonical(v):return sha_bytes(json.dumps(v,sort_keys=True,separators=(',',':')).encode())
def sexp_end(t,start):
 depth=0;quoted=False;escaped=False
 for i in range(start,len(t)):
  c=t[i]
  if quoted:
   if escaped:escaped=False
   elif c=='\\':escaped=True
   elif c=='"':quoted=False
   continue
  if c=='"':quoted=True
  elif c=='(':depth+=1
  elif c==')':
   depth-=1
   if depth==0:return i+1
 raise ValueError('unbalanced S-expression')
def block(t,name,depth_wanted):
 depth=0;quoted=False;escaped=False;found=[];i=0
 while i<len(t):
  c=t[i]
  if quoted:
   if escaped:escaped=False
   elif c=='\\':escaped=True
   elif c=='"':quoted=False
  elif c=='"':quoted=True
  elif c=='(':
   m=re.compile(r'\(([^\s()]+)').match(t,i)
   if m and m.group(1)==name and depth==depth_wanted:found.append(t[i:sexp_end(t,i)])
   depth+=1
  elif c==')':depth-=1
  i+=1
 if len(found)>1:raise ValueError('duplicate '+name)
 return found[0] if found else None

def capture(pcb):
 pcb=Path(pcb)
 if not pcb.is_file():raise ValueError('missing PCB')
 paths={k:pcb.with_suffix('.'+s) for k,s in [('project','kicad_pro'),('custom_rules','kicad_dru'),('schematic','kicad_sch')]}
 for k,p in paths.items():
  if not p.is_file():raise ValueError('missing same-basename '+k+': '+str(p))
 j=json.loads(paths['project'].read_text());text=pcb.read_text();layers=block(text,'layers',1);general=block(text,'general',1);stack=block(text,'stackup',2)
 if not layers or not general:raise ValueError('missing native board configuration')
 names=re.findall(r'\(\d+\s+"([^"]+\.Cu)"',layers)
 if names!=['F.Cu','In1.Cu','In2.Cu','In3.Cu','In4.Cu','B.Cu']:raise ValueError('not expected six copper layers')
 thickness=float(re.search(r'\(thickness\s+([0-9.]+)\)',general).group(1))
 settings=j.get('board',{}).get('design_settings');nets=j.get('net_settings')
 if not isinstance(settings,dict) or not isinstance(nets,dict):raise ValueError('missing design/netclass configuration')
 if settings.get('drc_exclusions'):raise ValueError('DRC exclusions not allowed by this study gate')
 unqualified_defaults=re.findall(r'\((?:epsilon_r|loss_tangent)\s+[^)]+\)',stack or '')
 # Ignore only these explicitly unqualified material fields for the routing-layer lock.
 # Raw stack SHA and all present values are still reported. Never use them for impedance.
 known=re.sub(r'\((?:epsilon_r|loss_tangent)\s+[^)]+\)','',stack or '')
 known=' '.join(known.split()) if stack else None
 return {'pcb_path':str(pcb.resolve()),'pcb_sha256':sha(pcb),'project_path':str(paths['project'].resolve()),'project_sha256':sha(paths['project']),'custom_rules_path':str(paths['custom_rules'].resolve()),'custom_rules_sha256':sha(paths['custom_rules']),'schematic_sha256':sha(paths['schematic']),'net_settings_sha256':canonical(nets),'design_settings_sha256':canonical(settings),'native_layers_sha256':sha_bytes(layers.encode()),'copper_layers':names,'general_thickness_mm':thickness,'explicit_stackup_present':stack is not None,'stackup_raw_sha256':sha_bytes(stack.encode()) if stack else None,'stackup_known_geometry_sha256':sha_bytes(known.encode()) if known else None,'unqualified_material_values_present':unqualified_defaults}
LOCK_FIELDS=['project_sha256','custom_rules_sha256','net_settings_sha256','design_settings_sha256','native_layers_sha256','copper_layers','general_thickness_mm','explicit_stackup_present','stackup_known_geometry_sha256']
def verify(pcb,lock,mode='routing'):
 a=capture(pcb)
 for k in LOCK_FIELDS:
  if k not in lock:raise ValueError('lock is missing '+k)
  if a[k]!=lock[k]:raise ValueError('configuration mismatch: '+k)
 q=lock.get('manufacturing_qualification',{})
 blockers=[]
 if not a['explicit_stackup_present']:blockers.append('explicit_stackup_missing')
 for k in ['manufacturer_selected','layer_tolerances_confirmed','mask_and_material_confirmed','DFM_confirmed','quotation_confirmed','impedance_process_confirmed']:
  if q.get(k) is not True:blockers.append(k)
 record=q.get('confirmation_record')
 if not record or not Path(record).is_file() or sha(record)!=q.get('confirmation_record_sha256'):blockers.append('valid_manufacturer_confirmation_record_missing')
 a.update(status='ROUTING_CONFIGURATION_BOUND',manufacturing_approved=not blockers,manufacturing_blockers=blockers,impedance_calculation_allowed=False,lock_sha256=canonical(lock),checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
 if mode=='manufacturing' and blockers:raise ValueError('NOFAB: '+', '.join(blockers))
 return a

def native_env():
 env=os.environ.copy()
 for key,leaf in [('XDG_CONFIG_HOME','config'),('XDG_CACHE_HOME','cache'),('XDG_DATA_HOME','data')]:
  path=Path('/tmp/rebuild-kicad')/leaf;path.mkdir(parents=True,exist_ok=True);env[key]=str(path)
 return env

def main():
 ap=argparse.ArgumentParser();ap.add_argument('pcb');ap.add_argument('--lock',required=True);ap.add_argument('--mode',choices=['routing','manufacturing'],default='routing');ap.add_argument('--report',required=True);ap.add_argument('--run-drc',action='store_true');a=ap.parse_args();out=Path(a.report).resolve();out.parent.mkdir(parents=True,exist_ok=True)
 try:
  lock=json.loads(Path(a.lock).read_text());r=verify(a.pcb,lock,a.mode)
  if a.run_drc:
   env=native_env();version=subprocess.run(['kicad-cli','--version'],env=env,capture_output=True,text=True,check=True).stdout.strip()
   if version!=lock.get('native_cli_version'):raise ValueError('native CLI version mismatch or missing lock')
   r.update(native_cli_version=version,tool_sha256=sha(__file__),drc_options=['--all-track-errors','--schematic-parity','--severity-all','--exit-code-violations','--format','json'])
   p=Path(a.pcb).resolve();native=out.with_suffix('.native_drc.json');cmd=['kicad-cli','pcb','drc','--all-track-errors','--schematic-parity','--severity-all','--exit-code-violations','--format','json','-o',str(native),str(p)]
   run=subprocess.run(cmd,cwd=str(p.parent),capture_output=True,text=True,env=env);out.with_suffix('.native_drc.log').write_text(run.stdout+run.stderr)
   after=verify(a.pcb,lock,a.mode)
   if r['pcb_sha256']!=after['pcb_sha256'] or r['schematic_sha256']!=after['schematic_sha256']:raise ValueError('native inputs changed during DRC')
   r.update(native_command=cmd,native_exit_code=run.returncode,native_report=str(native),post_configuration_unchanged=True)
   if not native.is_file():raise ValueError('native DRC report absent')
   out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2));return run.returncode
  out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2));return 0
 except Exception as e:
  r={'status':'REJECTED_BEFORE_ACCEPTANCE','reason':str(e),'manufacturing_approved':False};out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r));return 2
if __name__=='__main__':sys.exit(main())
