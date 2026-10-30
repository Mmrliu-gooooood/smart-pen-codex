"""r11 offline frozen gate/CAD replay. Originals stay byte-exact.
Default hashes/contracts only. --native/--mechanical use installed KiCad9.0.2 and/or
FreeCAD1.0, exact r10 files materialized in a disposable sibling-project layout.
No network, installation, device access, procurement, fabrication or source edits.
"""
import argparse,collections,hashlib,json,math,os,shutil,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;H=Path('smart_pen_next_20261028/hardware');M=Path('smart_pen_mechanics_next_20261028/mechanical');E=Path('smart_pen_next_20261028/docs/electronics')
def need(ok,msg):
 if not ok:raise RuntimeError(msg)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
 rows=json.loads((HERE/'SOURCE_SUBSET_SHA256.json').read_text())['files']
 for r in rows:
  rel=Path(r['path']);p=HERE/rel;need(not rel.is_absolute() and '..' not in rel.parts and p.is_file() and not p.is_symlink(),'unsafe source')
  need(sha(p)==r['sha256'] and p.stat().st_size==r['bytes'],str(rel))
 d=json.loads((HERE/H/'gate_full_independent_review/drc.json').read_text());need([len(d[k]) for k in ('violations','unconnected_items','schematic_parity')]==[28,41,0],'historical DRC');need(sum(v['type']=='shorting_items' for v in d['violations'])==9,'9 shorts remain')
 return len(rows)
def root(arg):
 if arg:return Path(arg).resolve()
 prefix=json.loads((HERE/'DEPENDENCY_LINKS.json').read_text())['source_experiments_repo_path']
 for p in (HERE.parent/Path(prefix).name,HERE.parents[2]/'verified_revisions_r10'/prefix):
  if p.is_dir():return p
 raise RuntimeError('r10 dependency root missing; pass --dependency-root PATH; no fetching attempted')
def normalized(x,work,ignore_cad_hash=False):
 if isinstance(x,str):return x.replace(str(work),'<CAPSULE>').replace('/workspace/scratch/fe148e758944','<CAPSULE>')
 if isinstance(x,list):return [normalized(v,work,ignore_cad_hash) for v in x]
 if isinstance(x,dict):return {k:normalized(v,work,ignore_cad_hash) for k,v in x.items() if k!='checked_utc' and not(ignore_cad_hash and k=='CAD_sha256')}
 return x
def compare(a,b,label):
 if isinstance(a,bool) or a is None or isinstance(a,str):need(a==b,label)
 elif isinstance(a,(int,float)):need(isinstance(b,(int,float)) and math.isclose(a,b,rel_tol=1e-8,abs_tol=1e-8),label)
 elif isinstance(a,list):
  need(isinstance(b,list) and len(a)==len(b),label)
  for i,(x,y) in enumerate(zip(a,b)):compare(x,y,label+'/'+str(i))
 elif isinstance(a,dict):
  need(isinstance(b,dict) and a.keys()==b.keys(),label)
  for k in a:compare(a[k],b[k],label+'/'+k)
 else:raise TypeError(label)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--native',action='store_true');ap.add_argument('--mechanical',action='store_true');ap.add_argument('--dependency-root');a=ap.parse_args();n=verify()
 report=dict(scope='native/synthetic geometry only; NOFAB, no physical/electrical/dynamic qualification',original_files_verified=n,device_or_external_operations=False,full_history_build_chain_rebuilt=False,historical_DRC=[28,41,0],real_short_findings_remaining=9,frozen_source_unchanged=True)
 if a.native or a.mechanical:
  dep_root=root(a.dependency_root);deps=json.loads((HERE/'DEPENDENCY_LINKS.json').read_text())['files']
  for d in deps:
   f=dep_root/d['capsule_path'];need(f.is_file() and not f.is_symlink() and sha(f)==d['sha256'] and f.stat().st_size==d['bytes'],'r10 '+d['capsule_path'])
  report['exact_r10_dependencies_verified']=len(deps)
  with tempfile.TemporaryDirectory(prefix='smartpen-r11-') as td:
   work=Path(td)
   for name in ('smart_pen_next_20261028','smart_pen_mechanics_next_20261028'):shutil.copytree(HERE/name,work/name)
   for d in deps:
    dest=work/d['capsule_path'];need(not dest.exists(),'dependency collision');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((dep_root/d['capsule_path']).read_bytes())
   env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',XDG_CONFIG_HOME=str(work/'xdg/config'),XDG_CACHE_HOME=str(work/'xdg/cache'),XDG_DATA_HOME=str(work/'xdg/data'))
   for p in ('xdg/config','xdg/cache','xdg/data'):(work/p).mkdir(parents=True,exist_ok=True)
   def cmd(args,allowed=(0,),cwd=work):
    p=subprocess.run(args,cwd=cwd,env=env,text=True,capture_output=True);need(p.returncode in allowed,str(args)+'\n'+p.stdout+p.stderr);return p
   def run(rel,opt=False,extra=()):return cmd([sys.executable]+(['-O'] if opt else [])+[str(work/rel),*extra])
   def parsed(p):return json.loads(p.stdout)
   def same(rel,value,cad=False):compare(normalized(json.loads((HERE/rel).read_text()),work,cad),normalized(value,work,cad),str(rel))
   if a.native:
    review=H/'gate_full_independent_review';candidate=H/'gate_control_output_candidate';version=cmd(['kicad-cli','--version']).stdout.strip();need(version=='9.0.2','frozen KiCad9.0.2 required');checks=[]
    for opt in (False,True):
     for name,expected in [('source_rules','source_rules'),('audit','audit'),('main_feed','main_feed'),('output_isolation','output_isolation'),('geometry_risk','geometry_risk'),('plane_contacts','plane_contacts'),('rule_areas','rule_areas')]:
      same(review/(expected+'.json'),parsed(run(review/(name+'.py'),opt)));checks.append(name+('_O' if opt else ''))
    for name,expected in [('measure','measure'),('qod_branch','qod_branch'),('negative_main_bridge','negative_main_bridge')]:same(review/(expected+'.json'),parsed(run(review/(name+'.py'))));checks.append(name)
    refill=parsed(run(review/'refill.py'));same(review/'refill.json',refill);same(review/'audit.json',parsed(run(review/'audit.py',extra=(str(work/review/'guard_boards/fresh_refill.kicad_pcb'),))))
    rebuilt=parsed(run(review/'rebuild.py'));ra=parsed(run(review/'audit.py',extra=(str(work/review/'guard_boards/rebuilt_from_delta.kicad_pcb'),)));expected=json.loads((HERE/review/'rebuild_audit.json').read_text());need(ra['pcb']==sha(work/review/'guard_boards/rebuilt_from_delta.kicad_pcb'),'rebuilt identity');expected.pop('pcb');rb=dict(ra);rb.pop('pcb');compare(expected,rb,'explicit rebuilt geometry/connectivity')
    collinear=H/'gate_collinear_maintenance_candidate'
    for opt in (False,True):same(collinear/'classification.json',parsed(run(collinear/'classify_collinear.py',opt)));same(collinear/'unchanged.json',parsed(run(collinear/'verify_unchanged.py',opt)))
    same(E/'gate_test_access_hold/node_map.json',parsed(run(E/'gate_test_access_hold/check_map.py')))
    pcb=work/candidate/'mainboard_revD.kicad_pcb';drcfile=work/'fresh_drc.json';cmd(['kicad-cli','pcb','drc','--all-track-errors','--schematic-parity','--severity-all','--exit-code-violations','--format','json','-o',str(drcfile),str(pcb)],allowed=(5,),cwd=pcb.parent)
    drc=json.loads(drcfile.read_text());need([len(drc[k]) for k in ('violations','unconnected_items','schematic_parity')]==[28,41,0],'fresh28/41/0')
    def keys(d):return collections.Counter((v['type'],v.get('severity'),v.get('description'),tuple(sorted(i.get('uuid','') for i in v.get('items',[])))) for v in d['violations'])
    need(keys(drc)==keys(json.loads((HERE/review/'drc.json').read_text())),'fresh violation identity');need(sum(v['type']=='shorting_items' for v in drc['violations'])==9,'9 real shorts')
    ercfile=work/'fresh_erc.json';cmd(['kicad-cli','sch','erc','--format','json','--severity-all','--exit-code-violations','-o',str(ercfile),str(pcb.with_suffix('.kicad_sch'))],allowed=(5,),cwd=pcb.parent)
    erc=json.loads(ercfile.read_text());v=[x for s in erc['sheets'] for x in s['violations']];need(len(v)==1 and v[0]['severity']=='warning' and 'VBUS_5V' in str(v),'ERC boundary warning')
    report['native_replay']=dict(kicad_version=version,original_checks=checks,main_bridge_negative_modes=2,all_seven_corrupt_mutations_rerun=False,seven_corrupt_mutation_evidence='retained frozen historical evidence, not this minimal replay',fresh_refill_audit=True,ae805_delta_rebuild_audit=True,rebuilt_serialization_sha256=rebuilt['reconstructed_pcb_sha256'],rebuild_bit_identity_required=False,fresh_DRC=[28,41,0],fresh_DRC_exit=5,fresh_ERC_errors=0,fresh_ERC_warnings=1,real_shorts=9,all_fresh_violation_UUID_multiset_equal=True,collinear_legal_merges=0,new_tracks=973,new_vias=32,short_tracks_lt_0p1mm=669,manufacturing_approved=False,probe_contact_qualified=False)
   if a.mechanical:
    joint=M/'gate508e_joint_screen_0247';clamp=M/'gate508e_clamp_copper_0254';generated=[]
    for opt in (False,True):
     run(joint/'screen.py',opt);fresh=json.loads((work/joint/('optimized.json' if opt else 'results.json')).read_text());same(joint/'results.json',fresh,True)
     need(fresh['studies']['RevD']['probe_budget_hits'],'finite tip negative required')
     generated.append(dict(optimized=opt,CAD_sha256={k:v['CAD_sha256'] for k,v in fresh['studies'].items()}))
     run(clamp/'check.py',opt);out=json.loads((work/clamp/('optimized.json' if opt else 'results.json')).read_text());same(clamp/'results.json',out)
    report['mechanical_replay']=dict(joint_normal_and_optimized_numerics_matched=True,clamp_normal_and_optimized_matched=True,finite_flat_probe_tip_collision_preserved=True,CAD_serialization_hash_excluded_from_numeric_comparison=True,generated_temporary_CAD_hashes=generated,frozen_delivered_CAD_hashes={k:sha(HERE/joint/(k+'_gate508e.FCStd')) for k in ('RevC','RevD')},clamp_min_zone_clearance_mm=0.05,clamp_mechanical_force_or_wear_qualified=False,final_19mm_shell=False)
  for d in deps:need(sha(dep_root/d['capsule_path'])==d['sha256'],'post dependency hash')
 need(verify()==n,'post original hash');print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
