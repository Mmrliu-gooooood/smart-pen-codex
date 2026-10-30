"""Independent artificial-log rejection tests; no target measurements."""
from pathlib import Path
import os,sys,json,copy,subprocess,tempfile
HERE=Path(__file__).resolve().parent
SRC=Path(os.environ.get('PEN_BENCH_SOURCE',str(HERE.parent/'smart_pen_decoder_target_benchmark_20261028'))).resolve()
sys.path.insert(0,str(SRC/'tools'))
from summarize_serial import summarize
manifest=json.loads((SRC/'fixtures/manifest.json').read_text())
def rows(n=3):
 a=[{'type':'header','schema':1},{'type':'runtime_config','repeats':n}]
 for f in manifest:
  for r in range(n):
   for mode in ['cold','warm'] if f['expected_status']==0 else ['cold']:
    a.append(dict(type='decode',placement='internal',fixture=f['file'],repeat=r,mode=mode,status=f['expected_status'],x=f['expected_x'],y=f['expected_y'],used_warm=int(mode=='warm'),decode_us=123,verdict='correct_coordinate' if f['expected_status']==0 else 'expected_nofit',failure_output_preserved=True,failure_prior_cleared=True))
 a.extend([dict(type='skip',placement='psram',reason='not_opted_in'),dict(type='complete')]);return a
def parse(a):return summarize(map(json.dumps,a))
passed=[]
for n in [1,3,10]:
 r=parse(rows(n));assert r['identity_verified'] is False and r['overall_pass'] is None and not r['functional_failures'];passed.append(f'repeats_{n}_no_device_pass')
cases={}
for field,val in [('decode_us',float('nan')),('decode_us',float('inf')),('decode_us',-1),('decode_us',True),('decode_us',1.5),('repeat',True),('repeat',3),('fixture','unknown'),('placement','unknown'),('mode','warm')]:
 a=rows();a[2][field]=val;cases[f'{field}_{val}']=a
a=rows();a.insert(-1,dict(a[2],fixture='unknown'));cases['extra_unknown']=a
a=rows();a[2].update(status=0,x=999,y=999,used_warm=0,verdict='correct_coordinate');cases['wrong_oracle']=a
a=rows();del a[2];cases['missing_one']=a
a=rows();a.insert(2,dict(a[2]));cases['duplicate']=a
a=rows();a.insert(2,{'type':'unrecognized'});cases['unknown_json']=a
a=rows();a[0],a[2]=a[2],a[0];cases['header_order']=a
a=rows();i=next(i for i,r in enumerate(a) if r.get('mode')=='warm');a[i],a[i-1]=a[i-1],a[i];cases['warm_before_cold']=a
for name,a in cases.items():
 try:parse(a)
 except (ValueError,KeyError):passed.append(name)
 else:raise AssertionError('accepted '+name)
a=rows();i=next(i for i,r in enumerate(a) if r.get('status')==0);a[i]['x']+=1;a[i]['verdict']='unexpected_success';assert len(parse(a)['functional_failures'])==1;passed.append('honest_wrong_coordinate_failure')
with tempfile.TemporaryDirectory() as t:
 p=Path(t)/'artificial.jsonl';p.write_text('\n'.join(map(json.dumps,rows()))+'\n')
 r=subprocess.run([sys.executable,str(SRC/'tools/summarize_serial.py'),str(p)],capture_output=True,text=True);assert r.returncode==2 and json.loads(r.stdout)['overall_pass'] is None;passed.append('CLI_no_identity_exit2')
print(json.dumps({'cases':len(passed),'passed':passed,'target_measurements':False},indent=2))
