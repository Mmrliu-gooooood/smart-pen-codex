"""r12 offline isolated replay; hashes by default, --software and/or --native.
No radio, device, SDK install, external publication or source-tree writes.
Compiler products/SQLite journals/guard boards stay in disposable temporary copies.
"""
import argparse,collections,hashlib,json,math,os,shutil,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;H=Path('smart_pen_next_20261028/hardware');BLE='smart_pen_ble_transport_candidate_20261029';V1='smart_pen_pc_receiver_candidate_20261029';V2='smart_pen_pc_receiver_v2_candidate_20261029';PC='smart_pen_pc_receiver_review_20261029'
def need(v,m):
 if not v:raise RuntimeError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows():return json.loads((HERE/'SOURCE_SUBSET_SHA256.json').read_text())['files']
def verify():
 rr=rows()
 for r in rr:
  q=Path(r['path']);p=HERE/q;need(not q.is_absolute()and'..'not in q.parts and p.is_file()and not p.is_symlink(),'unsafe path');need(sha(p)==r['sha256']and p.stat().st_size==r['bytes'],str(q))
 for folder,file,counts in [('cam_on_independent_review','drc.json',[28,41,0]),('j107_independent_review','fresh_drc.json',[17,38,0])]:
  d=json.loads((HERE/H/folder/file).read_text());need([len(d[k])for k in ('violations','unconnected_items','schematic_parity')]==counts,'storedDRC')
 need((HERE/BLE/'frozen/board_provider_absent.c').read_text().find('return 0;')>=0,'board provider must remain absent')
 return len(rr)
def normalize(x,work):
 if isinstance(x,str):return x.replace(str(work),'<CAPSULE>').replace('/workspace/scratch/fe148e758944','<CAPSULE>')
 if isinstance(x,list):return[normalize(y,work)for y in x]
 if isinstance(x,dict):return{k:(sorted(v) if k in ('source_project_library_files_bit_identical_to_508e','source_project_library_files_bit_identical_to_1c49') else normalize(v,work))for k,v in x.items()if k!='checked_utc'}
 return x
def compare(a,b,label):
 if isinstance(a,bool)or a is None or isinstance(a,str):need(a==b,label+': '+str(a)+' != '+str(b))
 elif isinstance(a,(int,float)):need(isinstance(b,(int,float))and math.isclose(a,b,rel_tol=1e-8,abs_tol=1e-8),label)
 elif isinstance(a,list):
  need(isinstance(b,list)and len(a)==len(b),label)
  for i,(x,y)in enumerate(zip(a,b)):compare(x,y,label+'/'+str(i))
 elif isinstance(a,dict):
  need(isinstance(b,dict)and a.keys()==b.keys(),label)
  for k in a:compare(a[k],b[k],label+'/'+k)
 else:raise TypeError(label)
def find_dependency(d,publication_root,repo_root):
 candidates=[]
 if repo_root:candidates.append(Path(repo_root)/d['repo_path'])
 if publication_root:candidates.append(Path(publication_root)/d['local_source'])
 candidates.extend([HERE.parents[1]/d['repo_path'],HERE.parents[2]/d['local_source']])
 for f in candidates:
  if f.is_file()and not f.is_symlink()and sha(f)==d['sha256']and f.stat().st_size==d['bytes']:return f
 raise RuntimeError('Missing exact dependency '+d['repo_path']+'; --publication-root local package parent or --repo-root assembled checkout; no fetching attempted')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--software',action='store_true');ap.add_argument('--native',action='store_true');ap.add_argument('--publication-root');ap.add_argument('--repo-root');a=ap.parse_args();n=verify();deps=json.loads((HERE/'DEPENDENCY_LINKS.json').read_text())['files']
 report=dict(scope='offline host/synthetic and native static evidence only, NOFAB; not radio/device/durable-powerloss qualification',original_files_verified=n,device_or_network_operations=False,source_byte_exact=True,full_history_generators_rerun=False,PC_V1='failed historical minimal reproducer, not recommended',historical_hardware_DRC={'CAM_ON':[28,41,0],'J107':[17,38,0]})
 if a.software or a.native:
  with tempfile.TemporaryDirectory(prefix='smartpen-r12-')as td:
   work=Path(td)
   for r in rows():
    dst=work/r['path'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(HERE/r['path'],dst)
   env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',XDG_CONFIG_HOME=str(work/'xdg/config'),XDG_CACHE_HOME=str(work/'xdg/cache'),XDG_DATA_HOME=str(work/'xdg/data'))
   for k in ('XDG_CONFIG_HOME','XDG_CACHE_HOME','XDG_DATA_HOME'):Path(env[k]).mkdir(parents=True,exist_ok=True)
   checks=[]
   def cmd(args,cwd=work,extra=None,allowed=(0,)):
    e=env.copy();e.update(extra or{});p=subprocess.run(list(map(str,args)),cwd=cwd,env=e,text=True,capture_output=True);need(p.returncode in allowed,'Command failed '+str(args)+'\n'+p.stdout+p.stderr);checks.append(dict(command=[str(x).replace(str(work),'<CAPSULE>')for x in args],returncode=p.returncode,stdout_sha256=hashlib.sha256(p.stdout.encode()).hexdigest(),stderr_sha256=hashlib.sha256(p.stderr.encode()).hexdigest()));return p
   def run(rel,opt=False,extra=None,args=()):return cmd([sys.executable]+(['-O']if opt else[])+[work/rel,*args],extra=extra)
   def parsed(p):return json.loads(p.stdout)
   def same(rel,value):compare(normalize(json.loads((HERE/rel).read_text()),work),normalize(value,work),str(rel))
   if a.software:
    # All receive() calls below inject MockClient; no Bleak installation/import needed.
    p=run(Path(BLE)/'tools/test_host.py');need(all(x in p.stdout for x in ['normal','ndebug','asan_ubsan']),'BLE3modes')
    r_env={'PEN_BLE_REVIEW_SOURCE':str(work/BLE),'PEN_BLE_FROZEN_SOURCE':str(work/BLE/'frozen'),'PEN_BLE_REVIEW_OUTPUT':str(work/'generated_ble_review')}
    for suite in ['extra','actor_extra','idf_extra']:run(Path(BLE)/'review'/('run_'+suite+'.py'),extra=r_env)
    for opt in(False,True):
     p=cmd([sys.executable]+(['-O']if opt else[])+['-W','error','-m','unittest','discover','-s','tests','-v'],cwd=work/V2);need('Ran 45 tests'in p.stderr and '\nOK'in p.stderr,'V2author45')
     p=run(Path(PC)/'test_independent_v2.py',opt,{'PC_SOURCE':str(work/V2)});need('Ran 9 tests'in p.stderr and '\nOK'in p.stderr,'independent9')
    cmd([sys.executable,work/V2/'tools/crosswire.py','--ble-source',work/BLE])
    fuzz=parsed(run(Path(PC)/'run_wire_fuzz.py',extra={'PC_SOURCE':str(work/V2),'BLE_SOURCE':str(work/BLE)}));need(fuzz=={'random_actual_C_Python_packet_fragment_ack_cases':500,'record_byte_corruption_rejected':48,'actual_C_ACK_byte_corruption_rejected':20,'radio_executed':False},'C500')
    regressions={}
    for label,src in [('V1',V1),('V2',V2)]:
     e={'PC_SOURCE':str(work/src)};schema='reproduce_schema_ack.py'if label=='V1'else'reproduce_schema_v2.py';s=parsed(run(Path(PC)/schema,extra=e));identity=parsed(run(Path(PC)/'reproduce_export_identity.py',extra=e));queue=parsed(run(Path(PC)/'reproduce_queue_time.py',extra=e));need(queue['second_record_fragment_span_s']>=2.0,'timeout fixture span')
     if label=='V1':need(s['ACK_writes']==1 and s['durable_rows']==0 and identity['export_events_identical']and queue['ACK_count']==2,'three real historical failures')
     else:need(s['ACK_writes']==0 and s['durable_rows']==0 and s['clients']==0 and s['file_unchanged']and not identity['export_events_identical']and queue['ACK_count']==1,'V2regressions')
     need(identity['wire_VALID_still_blocked'],'UI gate');regressions[label]={'schema':s,'identity':identity,'callback_time':queue}
    report['software_replay']=dict(BLE_author_modes=['normal','ndebug','asan_ubsan'],BLE_independent_suites=['core','actor','IDF_API_stub'],BLE_independent_modes=['normal','ndebug','asan'],BLE_IDF_mock_scenarios_per_mode=5,PC_author_tests_per_mode=45,PC_independent_tests_per_mode=9,PC_modes=['normal','optimized'],crosswire=fuzz,three_defect_regressions=regressions,SDK_rebuilt_this_replay=False,SDK_evidence='frozen author/reviewer two IDF configurations retained; no build outputs copied',radio_executed=False,Windows_SC_MITM_powerloss_tested=False,NO_SENSOR_UI_allowed=False)
   if a.native:
    paths={d['capsule_path']:find_dependency(d,a.publication_root,a.repo_root)for d in deps}
    for d in deps:
     dest=work/d['capsule_path'];need(not dest.exists(),'dependency collision');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(paths[d['capsule_path']],dest)
    version=cmd(['kicad-cli','--version']).stdout.strip();need(version=='9.0.2','KiCad9.0.2 required');report['exact_prior_union_dependencies_verified']=len(deps)
    cam=H/'cam_on_independent_review';j=H/'j107_independent_review';h=H/'j107_current_revB_harness/harness_contract';native_results={}
    # First fresh native DRC/source export, so replay cannot silently trust stale frozen XML/results.
    def violations(q):return collections.Counter(json.dumps({**v,'items':sorted(v.get('items',[]),key=lambda z:json.dumps(z,sort_keys=True))},sort_keys=True)for v in q['violations'])
    for rel,file,counts in [(cam,'drc.json',[28,41,0]),(j,'fresh_drc.json',[17,38,0])]:
     pcb=work/rel/'native/mainboard_revD.kicad_pcb';out=work/rel/file;expected=json.loads((HERE/rel/file).read_text());p=cmd(['kicad-cli','pcb','drc','--all-track-errors','--schematic-parity','--severity-all','--exit-code-violations','--format','json','-o',out,pcb],cwd=pcb.parent,allowed=(5,));q=json.loads(out.read_text());need([len(q[k])for k in('violations','unconnected_items','schematic_parity')]==counts and violations(q)==violations(expected),'freshDRCfullmultiset')
     cmd(['kicad-cli','sch','export','netlist','--format','kicadxml','-o',work/rel/'fresh.xml',pcb.with_suffix('.kicad_sch')],cwd=pcb.parent)
     # XML export includes runtime dates/path: downstream source/endpoint/native-MPN checks consume this fresh XML.
     native_results[rel.name]=dict(fresh_DRC=counts,exit=5,full_violation_multiset_identical=True,actual_short_findings=sum(v['type']=='shorting_items'for v in q['violations']))
    for opt in(False,True):
     for name,out in [('independent_checks','independent_checks'),('audit_gate','full_audit'),('verify_maintenance','maintenance'),('track_statistics','statistics'),('verify_source_refill','source_refill')]:same(cam/(out+'.json'),parsed(run(cam/(name+'.py'),opt)))
     for name,out in [('independent_checks','independent_normal'),('audit_gate','audit_gate_normal'),('verify_j107','verify_j107_normal'),('ground_tail_counterfactual','ground_tail_counterfactual_normal'),('local_plane_corridors','local_plane_corridors_normal'),('verify_source_refill','verify_source_refill_normal')]:same(j/(out+'.json'),parsed(run(j/(name+'.py'),opt)))
     hv=parsed(run(h/'test_mapping.py',opt));same(H/'j107_current_revB_harness/harness_contract'/('test_optimized.json'if opt else'test_normal.json'),hv);need(len(hv['cases'])==9 and all(x['passed']for x in hv['cases']),'harness9')
    for rel,script in [(cam,'maintenance_negatives'),(j,'negative_j107')]:
     neg=parsed(run(rel/(script+'.py')));same(rel/'negative_results.json',neg);need(len(neg)==8 and all(x['exit']==1 for x in neg),'8explicitnegative');native_results[rel.name]['mutation_rejections']=8
    before=json.loads((work/cam/'drc.json').read_text());after=json.loads((work/j/'fresh_drc.json').read_text());need(not violations(after)-violations(before) and sum((violations(before)-violations(after)).values())==11,'11removed0added')
    # Original contract generator is optional history but exact old JSON is included in closure.
    run(h/'build_contract.py');need((work/h/'power_mode_mapping.json').read_bytes()==(HERE/h/'power_mode_mapping.json').read_bytes(),'harness exact rebuild')
    report['native_replay']=dict(kicad_version=version,cases=native_results,checks_normal_optimized=True,new_review_sources_not_modified=True,full_finding_delta_removed=11,full_finding_delta_added=0,harness_cases_per_mode=9,harness_rebuilt_exact=True,current_power_RevB_three_pin_mapping='1:1 EN1/EN2/GND',legacy_four_pin_pin3='CE_PERMISSION_EXTERNAL, explicitly incompatible',manufacturing_released=False,physical_harness_released=False,dynamic_or_plane_ampacity_qualified=False,CAM_ON_tracks=[44,9],CAM_ON_sub_0p1mm_tracks=[28,0],whole_previous_batch_sub_0p1mm_tracks=[669,641],J107_GND_components=[12,11],in_plane_AON_to_IMU_paths='pre-existing nonpassing cases remain nonpassing; not a pass')
    for d in deps:need(sha(paths[d['capsule_path']])==d['sha256'],'postdependencyhash')
   report['commands']=checks
 need(verify()==n,'postoriginalhash');print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
