"""Independent schema2 mutations on explicitly artificial unit logs, never device data."""
from pathlib import Path
import os,sys,json,copy,tempfile,subprocess
HERE=Path(__file__).resolve().parent
SRC=Path(os.environ.get('PEN_BENCH_SOURCE',str(HERE.parent/'smart_pen_continuous_target_benchmark_20261029'))).resolve()
sys.path.insert(0,str(SRC/'tools'))
from test_serial_parser import Parser
from summarize_serial import summarize
base=Parser().rows()
def parse(a):return summarize(map(json.dumps,a))
passed=[]
for n in (1,3,10):
 r=parse(Parser().rows(n));assert not r['functional_failures'] and r['overall_pass'] is None and r['identity_verified'] is False;passed.append('repeat_'+str(n)+'_not_device_pass')
cases={}
for key,value in [('decode_us',float('nan')),('decode_us',float('inf')),('decode_us',-1),('decode_us',True),('decode_us',1.5),('repeat',True),('repeat',3),('fixture','unknown'),('decoder','unknown'),('mode','warm')]:
 a=copy.deepcopy(base);a[5][key]=value;cases[f'{key}_{value}']=a
for key,value in [('int64',4294967296),('int64','4294967297'),('int64',4294967297.0),('double',1.234),('double',float('nan'))]:
 a=copy.deepcopy(base);a[2][key]=value;cases[f'probe_{key}_{value}']=a
for key,value in [('timing_scope','core_only'),('cold_means','flushed_cache'),('hardware_providers',True),('manifest_sha256','bad'),('source_bundle_sha256','bad')]:
 a=copy.deepcopy(base);a[0][key]=value;cases['header_'+key]=a
for kind in ('missing','duplicate','missing_memory','missing_complete','reordered'):
 a=copy.deepcopy(base)
 if kind=='missing':del a[5]
 if kind=='duplicate':a.insert(5,copy.deepcopy(a[5]))
 if kind=='missing_memory':del a[6]
 if kind=='missing_complete':a.pop()
 if kind=='reordered':a[5],a[7]=a[7],a[5]
 cases[kind]=a
for name,a in cases.items():
 try:parse(a)
 except (ValueError,KeyError):passed.append(name)
 else:raise AssertionError('accepted '+name)
for key in ('paper_to_frame','frame_to_paper','directions','crop'):
 a=copy.deepcopy(base);r=next(x for x in a if x.get('status')==0);r[key][0]+=1;assert parse(a)['functional_failures'];passed.append('oracle_'+key)
a=copy.deepcopy(base);r=next(x for x in a if x.get('status')==0);r['paper_to_frame'][0]=float('inf')
try:parse(a)
except ValueError:passed.append('nonfinite_transform')
else:raise AssertionError('accepted inf transform')
with tempfile.TemporaryDirectory() as t:
 p=Path(t)/'artificial.jsonl';p.write_text('\n'.join(map(json.dumps,base))+'\n')
 r=subprocess.run([sys.executable,str(SRC/'tools/summarize_serial.py'),str(p)],capture_output=True,text=True);assert r.returncode==2 and json.loads(r.stdout)['overall_pass'] is None;passed.append('CLI_exit2_unverified')
print(json.dumps({'cases':len(passed),'passed':passed,'device_measurements':False},indent=2))
