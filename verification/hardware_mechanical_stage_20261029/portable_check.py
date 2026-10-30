"""Local r10 verification, never manufacturing approval. Originals stay unchanged.
Default: hashes, current four-package closure, native XML/layout evidence contracts.
--native: installed KiCad9 CLI+pcbnew, faithful original audits/negative tests in temp.
--mechanical: installed FreeCAD, original RevC/RevD solid checks in temp, with one
historical absolute JSON source path rebound to the same-hash packaged PCB.
No downloads, vendor PDFs, devices, fabrication, procurement or remote writes.
"""
import argparse,collections,hashlib,json,math,os,re,shutil,subprocess,sys,tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
HERE=Path(__file__).resolve().parent
H=Path('smart_pen_next_20261028/hardware');M=Path('smart_pen_mechanics_next_20261028/mechanical')
C=Path('smart_pen_next_20261028/docs/electronics/gate_input_release_dependencies/closure.json')
def require(ok,msg):
 if not ok:raise RuntimeError(msg)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
 rows=json.loads((HERE/'SOURCE_SUBSET_SHA256.json').read_text())['files']
 for r in rows:
  rel=Path(r['path']);p=HERE/rel;require(not rel.is_absolute() and '..' not in rel.parts and p.is_file() and not p.is_symlink(),'unsafe path')
  require(p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],r['path'])
 closure=json.loads((HERE/C).read_text());members=0
 for folder,meta in closure['complete_current_verification_packages'].items():
  root=HERE/'smart_pen_next_20261028'/folder;require(sha(root/'manifest.json')==meta['manifest_sha256'],'manifest pin')
  m=json.loads((root/'manifest.json').read_text());files=m.get('files',m)
  require(len(files)==meta['members'],'manifest count')
  for n,h in files.items():require(sha(root/n)==(h['sha256'] if isinstance(h,dict) else h),'closure '+n)
  members+=len(files)
 require(members==413,'413 direct closure')
 for n,h in closure['external_provenance_allowlist'].items():require(sha(HERE/'smart_pen_next_20261028'/n)==h,'extra '+n)
 for n in closure['external_evidence_not_in_publication']:require(not (HERE/'smart_pen_next_20261028'/n).exists(),'vendor original should not be bundled')
 root=ET.parse(HERE/H/'gate_input_local_routing/fresh.xml').getroot();entities=root.findall('./components/comp');endpoints=root.findall('./nets/net/node');require(len(entities)==102 and len(endpoints)==356,'source102/356')
 drc=json.loads((HERE/H/'gate_input_independent_review/drc.json').read_text());require([len(drc[k]) for k in ('violations','unconnected_items','schematic_parity')]==[135,54,0],'historical DRC')
 return len(rows)
def normalize(x,work):
 if isinstance(x,str):return x.replace(str(work),'<CAPSULE>').replace('/workspace/scratch/fe148e758944','<CAPSULE>')
 if isinstance(x,list):return [normalize(y,work) for y in x]
 if isinstance(x,dict):return {k:normalize(v,work) for k,v in x.items() if k!='checked_utc'}
 return x
def compare(a,b,label):
 if isinstance(a,bool) or a is None or isinstance(a,str):require(a==b,label)
 elif isinstance(a,(int,float)):require(isinstance(b,(int,float)) and math.isclose(a,b,rel_tol=1e-8,abs_tol=1e-8),label)
 elif isinstance(a,list):
  require(isinstance(b,list) and len(a)==len(b),label)
  for i,(x,y) in enumerate(zip(a,b)):compare(x,y,label+'/'+str(i))
 elif isinstance(a,dict):
  require(isinstance(b,dict) and a.keys()==b.keys(),label)
  for k in a:compare(a[k],b[k],label+'/'+k)
 else:raise TypeError(label)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--native',action='store_true');ap.add_argument('--mechanical',action='store_true');args=ap.parse_args();count=verify()
 report={'scope':'local synthetic/native geometry replay only; NOFAB, no physical/electrical/safety qualification','original_files_verified':count,'hardware_direct_closure_members':413,'historical_DRC':[135,54,0],'native_source_entities':102,'native_source_pin_endpoints':356,'native_run_requested':args.native,'mechanical_run_requested':args.mechanical,'device_or_external_actions':False,'all_originals_unchanged':True,'full_ancestor_build_chain_rebuilt':False}
 if args.native or args.mechanical:
  with tempfile.TemporaryDirectory(prefix='smartpen-r10-') as td:
   work=Path(td)
   for name in ('smart_pen_next_20261028','smart_pen_mechanics_next_20261028'):shutil.copytree(HERE/name,work/name)
   env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',XDG_CONFIG_HOME=str(work/'xdg/config'),XDG_CACHE_HOME=str(work/'xdg/cache'),XDG_DATA_HOME=str(work/'xdg/data'))
   for p in ('xdg/config','xdg/cache','xdg/data'): (work/p).mkdir(parents=True,exist_ok=True)
   def command(cmd,allowed=(0,),cwd=work):
    p=subprocess.run(cmd,cwd=cwd,env=env,text=True,capture_output=True)
    require(p.returncode in allowed,str(cmd)+'\n'+p.stdout+p.stderr);return p
   def run(rel,opt=False,extra=()):return command([sys.executable]+(['-O'] if opt else [])+[str(work/rel),*extra])
   def parsed(p):return json.loads(p.stdout)
   def same(rel,actual):compare(normalize(json.loads((HERE/rel).read_text()),work),normalize(actual,work),str(rel))
   if args.native:
    version=command(['kicad-cli','--version']).stdout.strip();require(version=='9.0.2','requires frozen KiCad9.0.2 for exact regression');report['kicad_version']=version
    review=H/'gate_input_independent_review';gate=H/'gate_input_local_routing';native=[]
    # Hash-checking source_rules must run before any temporary output regeneration.
    for opt in (False,True):
     same(review/'source_rules.json',parsed(run(review/'source_rules.py',opt)));native.append('source_rules'+('_O' if opt else ''))
     same(gate/'measure_normal.json',parsed(run(gate/'measure_and_bind.py',opt)));native.append('measure_binding'+('_O' if opt else ''))
     same(review/'audit.json',parsed(run(review/'audit.py',opt)));native.append('independent_actual_copper'+('_O' if opt else ''))
     same(review/'config_negative.json',parsed(run(review/'config_negative.py',opt)));native.append('configuration5_negatives'+('_O' if opt else ''))
    negatives=parsed(run(review/'negative_tests.py'));expected_neg=json.loads((HERE/review/'negative_results.json').read_text());require(len(negatives)==14,'7x2 negative count');message_differences=[]
    for actual,expected in zip(negatives,expected_neg):
     require(actual.keys()==expected.keys() and all(actual[k]==expected[k] for k in ('case','optimized','exit')),'negative identity/exit')
     if actual['error']!=expected['error']:
      prefix='Explicit serialized copper net changed '
      require(actual['case']=='wrong_C301_pad' and all(x['error'].startswith(prefix) for x in (actual,expected)),'unexpected negative reason difference '+repr(actual)+' vs '+repr(expected))
      def raw_nets(path):
       text=path.read_text();names={int(n):v for n,v in re.findall(r'\(net (\d+) "([^"\n]+)"\)',text)};out={}
       for block in re.findall(r'\n\t\((?:segment|via)\n.*?\n\t\)',text,re.S):
        uid=re.search(r'\(uuid "([^"\n]+)"\)',block);net=re.search(r'\(net (\d+)\)',block)
        if uid and net:out[uid[1]]=names[int(net[1])]
       return out
      before_nets=raw_nets(work/review/'native_snapshot/mainboard_revD.kicad_pcb');bad_nets=raw_nets(work/review/'guard_boards/wrong_C301_pad.kicad_pcb')
      changed={u for u in before_nets.keys()&bad_nets.keys() if before_nets[u]!=bad_nets[u]}
      require(all(x['error'][len(prefix):] in changed for x in (actual,expected)),'negative UUID not in actual changed-net set')
      message_differences.append({'case':actual['case'],'optimized':actual['optimized'],'historical_error':expected['error'],'current_error':actual['error'],'actual_changed_serialized_net_UUIDs':sorted(changed),'interpretation':'same exact mutation, exit1, same serialized-net rejection; unordered set selects first UUID, both UUIDs independently verified in actual mutated changed-net set; no byte-equality claim'})
    # Fresh actual native DRC, with full project/config/libraries, to a new report.
    pcb=work/gate/'mainboard_revD.kicad_pcb';fresh=work/'fresh_drc.json'
    command(['kicad-cli','pcb','drc','--all-track-errors','--schematic-parity','--severity-all','--exit-code-violations','--format','json','-o',str(fresh),str(pcb)],allowed=(5,),cwd=pcb.parent)
    drc=json.loads(fresh.read_text());require([len(drc[k]) for k in ('violations','unconnected_items','schematic_parity')]==[135,54,0],'fresh DRC')
    historical=json.loads((HERE/gate/'drc.json').read_text())
    def keys(report):return collections.Counter((v['type'],v.get('description'),v.get('severity'),tuple(sorted(i.get('uuid','') for i in v.get('items',[])))) for v in report['violations'])
    require(keys(historical)==keys(drc),'fresh violation identity')
    ercfile=work/'fresh_erc.json';sch=work/gate/'mainboard_revD.kicad_sch'
    command(['kicad-cli','sch','erc','--format','json','--severity-all','--exit-code-violations','-o',str(ercfile),str(sch)],allowed=(5,),cwd=sch.parent)
    erc=json.loads(ercfile.read_text());v=[x for sheet in erc['sheets'] for x in sheet['violations']];require(len(v)==1 and v[0]['severity']=='warning' and 'VBUS_5V' in str(v),'inherited ERC warning')
    report['native_replay']={'original_scripts_normal_and_optimized':native,'independent_negative_cases':7,'independent_negative_runs':14,'configuration_negative_cases_each_mode':5,'negative_message_differences':message_differences,'negative_results':negatives,'fresh_DRC':[135,54,0],'fresh_DRC_exit':5,'fresh_violation_type_item_UUID_multiset_equal':True,'fresh_ERC_errors':0,'fresh_ERC_inherited_warnings':1,'fresh_ERC_exit':5,'manufacturing_approved':False,'JP301':'OPEN'}
   if args.mechanical:
    revc=M/'contact_oblique_harness_revC_0038';revd=M/'common_datum_bench_revD_0100'
    # Parameterization only in a disposable JSON copy, never frozen source/code.
    contract=work/revd/'native_contract.json';before=sha(contract);j=json.loads(contract.read_text());source=work/H/'gate_input_local_routing/mainboard_revD.kicad_pcb';require(sha(source)==j['sha256'],'same ae805 board')
    j['source']=str(source);contract.write_text(json.dumps(j,indent=2)+'\n');after=sha(contract)
    reruns=[]
    for opt in (False,True):
     run(revc/'verify.py',opt);out=json.loads((work/revc/('verify_optimized.json' if opt else 'verify_normal.json')).read_text());same(revc/'verify_normal.json',out);reruns.append('RevC'+('_O' if opt else ''))
     run(revd/'verify.py',opt);out=json.loads((work/revd/('verify_optimized.json' if opt else 'verify_normal.json')).read_text());same(revd/'verify_normal.json',out);reruns.append('RevD'+('_O' if opt else ''))
    report['mechanical_replay']={'original_solid_checks':reruns,'negative_old_RevB_housing_intersection_detected':True,'RevD_preinstalled_forks_negative_detected':True,'RevD_original_power_touch_negative_detected':True,'fixture_parts':38,'STEP_solids':38,'calibration_and_strain_or_fatigue_qualified':False,'bench_not_19mm_product':True,'input_path_adapter':{'relative_path':str(revd/'native_contract.json'),'original_sha256':before,'derived_sha256':after,'changed_field':'source only; destination absolute TemporaryDirectory path, exact same ae805 file SHA','derived_file_is_temporary_only':True}}
 require(verify()==count,'post-run source closure')
 print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
