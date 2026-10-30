"""Offline r9 host replay in disposable copies. No SDK/device/network actions.
Default: self-contained 95 frozen benchmark/review artifacts.
--source-dependencies additionally verifies the exact r8 closure and reruns geometry extraction.
All generated C libraries/executables and artificial logs stay in TemporaryDirectory.
"""
import argparse,hashlib,json,os,re,shutil,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
BENCH='smart_pen_continuous_v3_target_benchmark_20261029'
REVIEW='smart_pen_continuous_v3_target_review_20261029'
def require(ok,msg):
 if not ok:raise RuntimeError(msg)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
 rows=json.loads((HERE/'SOURCE_SUBSET_SHA256.json').read_text())['files']
 for r in rows:
  rel=Path(r['path']);p=HERE/rel
  require(not rel.is_absolute() and '..' not in rel.parts and p.is_file() and not p.is_symlink() and p.resolve().is_relative_to(HERE),'unsafe input')
  require(p.stat().st_size==r['bytes'] and digest(p)==r['sha256'],r['path'])
 return len(rows)
def compare(a,b,label):
 if isinstance(a,bool) or a is None or isinstance(a,str):require(a==b,label)
 elif isinstance(a,(int,float)):require(isinstance(b,(int,float)) and abs(a-b)<=1e-9*max(1,abs(a)),label)
 elif isinstance(a,list):
  require(isinstance(b,list) and len(a)==len(b),label)
  for i,(x,y) in enumerate(zip(a,b)):compare(x,y,label+'/'+str(i))
 elif isinstance(a,dict):
  require(isinstance(b,dict) and a.keys()==b.keys(),label)
  for k in a:compare(a[k],b[k],label+'/'+k)
 else:raise TypeError(label)
def dependency_root(arg):
 if arg:return Path(arg).resolve()
 relative=json.loads((HERE/'DEPENDENCY_LINKS.json').read_text())['source_experiments_repo_path']
 candidates=[HERE.parent/Path(relative).name,HERE.parents[2]/'verified_revisions_r8'/relative]
 for p in candidates:
  if p.is_dir():return p
 raise RuntimeError('r8 dependency root missing; pass --dependency-root PATH (no fetching is attempted)')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source-dependencies',action='store_true');ap.add_argument('--dependency-root');args=ap.parse_args()
 count=verify();report={'scope':'host-only synthetic verification, not S3 execution/libc-runtime/FPS/physical safety','source_evidence_files_verified':count,'device_measured':False,'target_sdk_rebuilt':False,'frozen_files_unchanged':True,'format_runtime_on_actual_target':'not run'}
 with tempfile.TemporaryDirectory(prefix='smartpen-r9-check-') as td:
  work=Path(td)
  for name in (BENCH,REVIEW):shutil.copytree(HERE/name,work/name)
  bench,review=work/BENCH,work/REVIEW
  env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PEN_BENCH_SOURCE=str(bench))
  def run(script):
   result=subprocess.run([sys.executable,str(script)],cwd=work,env=env,text=True,capture_output=True)
   require(result.returncode==0,script.name+'\n'+result.stdout+result.stderr);return result
  if args.source_dependencies:
   root=dependency_root(args.dependency_root);deps=json.loads((HERE/'DEPENDENCY_LINKS.json').read_text())['files']
   for r in deps:
    source=root/r['capsule_path'];require(source.is_file() and not source.is_symlink() and digest(source)==r['sha256'] and source.stat().st_size==r['bytes'],'r8 '+r['capsule_path'])
    if r['purpose']=='geometry source extraction':
     dest=work/r['capsule_path'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(source.read_bytes())
   run(bench/'tools/prepare_independent_geometry.py')
   require((bench/'fixtures/independent_geometry.json').read_bytes()==(HERE/BENCH/'fixtures/independent_geometry.json').read_bytes(),'r8 geometry extraction bytes')
   report['r8_exact_dependency_files_verified']=len(deps);report['r8_generator_manifest_extraction_byte_exact']=True
  else:report['r8_generator_manifest_extraction_byte_exact']='not requested; frozen extracted geometry used'
  for tool in ('prepare_v3_oracles.py','freeze_legacy_oracles.py'):
   run(bench/'tools'/tool);require((bench/'fixtures/manifest.json').read_bytes()==(HERE/BENCH/'fixtures/manifest.json').read_bytes(),'recomputed '+tool)
  report['post_return_v3_and_legacy_oracles_byte_exact']=True
  run(bench/'tools/embed_fixtures.py')
  for rel in ('main/fixtures.h','verification/build-inputs.json'):
   require((bench/rel).read_bytes()==(HERE/BENCH/rel).read_bytes(),'palette/source binding '+rel)
  report['palette_RLE_header_and_source_binding_byte_exact']=True
  host=json.loads(run(bench/'tools/check_host.py').stdout)
  compare(json.loads((HERE/BENCH/'verification/host-functional.json').read_text()),host,'host')
  compare(json.loads((HERE/REVIEW/'host_functional.json').read_text()),host,'independent host')
  require(len(host['records'])==18,'host count');report['host_functional_records_passed']=18
  (review/'host_functional.json').write_text(json.dumps(host,indent=2)+'\n')
  geometry=json.loads(run(bench/'tools/check_geometry.py').stdout)
  compare(json.loads((HERE/BENCH/'verification/independent-geometry.json').read_text()),geometry,'author geometry')
  report['author_geometry_checked']=True
  tests=run(bench/'tools/test_serial_parser.py');log=tests.stdout+tests.stderr
  require(re.search(r'Ran 16 tests\b',log) and '\nOK\n' in log,log);report['author_parser_tests_passed']=16
  negatives=json.loads(run(review/'run_parser_negatives.py').stdout)
  compare(json.loads((HERE/REVIEW/'parser_negatives.log').read_text()),negatives,'independent parser')
  require(negatives['cases']==41,'negative count');report['independent_parser_cases_passed']=41
  geometry=json.loads(run(review/'check_geometry.py').stdout)
  compare(json.loads((HERE/REVIEW/'geometry.log').read_text()),geometry,'independent geometry')
  require(geometry['points']==180,'geometry count');report['independent_geometry_points_passed']=180
  mock=json.loads(run(review/'run_actual_main.py').stdout)
  compare(json.loads((HERE/REVIEW/'actual_main_mock.log').read_text()),mock,'actual main host mock')
  require(len(mock)==8 and all(r['passed'] for r in mock),'mock count');report['actual_main_host_cases']=mock
  report['mock_clock_warning']='Artificial +123 clocks test call boundaries only; no mock serial data is published as target measurements.'
  report['sanitizer_scope']='Host ASAN/UBSAN included; LeakSanitizer disabled by original reviewed script.'
 require(verify()==count,'post-run frozen check')
 print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
