"""Synthetic-only actual full-input candidate replay. Truth is post-return only."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import ctypes as C, json, hashlib, tempfile, argparse, collections, time
OUT=Path(__file__).resolve().parent; CAND=OUT.parent; WORK=CAND.parent
ROOT=WORK/'publication_20261031/target_repo'
V3=ROOT/'verification/continuous_v3_experiments_20261029/smart_pen_continuous_roi_v3_candidate_20261029'
PROBE=WORK/'optics_paper_screen_20261031_1752/decoder_probe'
sys.path[:0]=[str(CAND),str(V3/'tools'),str(V3/'tests')]
from build import build
from test_roi_opt import OptResult
from test_roi_vision import Config
from continuous_roi_sweep import render,project,RefineStats
from roi_opt_fixture import Render,render as isolated_render
import numpy as np
class Guard:
 def __init__(self,n,fill=0xa5):
  self.n=n; self.buf=(C.c_double*((n+32+7)//8))();C.memset(C.addressof(self.buf),0x5c,C.sizeof(self.buf));self.ptr=C.addressof(self.buf)+16;C.memset(self.ptr,fill,n)
 def data(self):return C.string_at(self.ptr,self.n)
 def check(self):
  assert C.string_at(C.addressof(self.buf),16)==b'\\'*16 and C.string_at(self.ptr+self.n,C.sizeof(self.buf)-16-self.n)==b'\\'*(C.sizeof(self.buf)-16-self.n),'canary modified'
def generate(s,D):
 source=D
 if s['group']=='fake_dots':source=np.random.default_rng(s['seed']).integers(0,4,D.shape,dtype=np.uint8)
 if s['group']=='two_windows':
  d=D[240:246,120:132].copy()
  if s['kind']=='conflict':d[:,6:12]=D[500:506,300:306]
  return np.frombuffer(isolated_render(d.reshape(-1).tolist(),Render(columns=12,pitch=8,tx=100,ty=100,radius=1/6,width=200,height=200)),dtype=np.uint8).reshape(200,200)
 if s['group']=='corrupt_code':
  source=D.copy()
  for x,y,delta in s['changed_cells']:source[y,x]=(int(source[y,x])+delta)%4
 im=render(source,s)
 if s.get('kind')=='mirror':im=np.ascontiguousarray(im[:,::-1])
 if s.get('kind')=='quarter_turn':im=np.ascontiguousarray(np.rot90(im))
 return im

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--enabled',type=int,choices=[0,1],required=True);ap.add_argument('--targeted',action='store_true');a=ap.parse_args()
 hashes={}
 def read(p):
  b=p.read_bytes();hashes[str(p)]=hashlib.sha256(b).hexdigest();return b
 probe=json.loads(read(PROBE/'results.json'))+json.loads(read(PROBE/'controls_results.json'));truth=json.loads(read(PROBE/'summary.json'))['truth'];read(PROBE/'MANIFEST.json')
 cases=[]
 for r in probe:
  pgm=read(PROBE/r['pgm']);pixels=pgm.split(b'\n',3)[3]
  assert hashlib.sha256(pgm).hexdigest()==r['pgm_sha256'] and hashlib.sha256(pixels).hexdigest()==r['pixel_sha256']
  if not a.targeted or r['pgm'] in ['control_000.pgm','control_001.pgm','control_006.pgm','control_007.pgm','control_012.pgm','control_013.pgm','049.pgm','050.pgm','000.pgm','015.pgm','030.pgm']:
   cases.append(('probe',r['pgm'],r,pixels))
 D=None
 if not a.targeted:
  dp=ROOT/'verification/continuous_roi_experiments_20261029/smart_pen_viewport_audit_20261028/upstream_directions.npy';read(dp);D=np.load(dp)
  for dataset in ['continuous','v3_adversarial']:
   for i,s in enumerate(json.loads(read(V3/f'verification/{dataset}/results.json'))):cases.append((dataset,str(i),s,None))
 for base in [V3/'firmware',V3/'tests',V3/'tools']:
  for p in base.rglob('*'):
   if p.is_file() and p.suffix in ['.c','.h','.py']:read(p)
 for p in [ROOT/'firmware/vision/roi_opt.c',ROOT/'firmware/vision/roi_opt.h',ROOT/'firmware/vision/roi.h',ROOT/'firmware/codec/anoto.c',ROOT/'firmware/codec/anoto.h',ROOT/'firmware/codec/sequences.h']:read(p)
 candidate_hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [CAND/'candidate.c',CAND/'candidate.h',CAND/'build.py',Path(__file__)]}
 results=[]
 with tempfile.TemporaryDirectory(prefix='fullroi-replay-') as tmp:
  path=build(Path(tmp),bool(a.enabled));lib=C.CDLL(str(path))
  for n in ['candidate_workspace_size','candidate_result_size','candidate_diagnostics_size']:getattr(lib,n).restype=C.c_size_t
  assert lib.candidate_result_size()==C.sizeof(OptResult) and lib.candidate_diagnostics_size()==C.sizeof(RefineStats)
  fn=lib.candidate_decode;fn.argtypes=[C.c_void_p,C.c_size_t,C.c_uint,C.c_uint,C.c_uint,C.POINTER(Config),C.c_void_p,C.c_void_p,C.c_void_p];fn.restype=C.c_int
  active=lib.pen_roi_active_decode_opt;active.argtypes=fn.argtypes[:7]+[C.c_void_p,C.c_void_p];active.restype=C.c_int
  for dataset,key,s,pixels in cases:
   if pixels is None:
    pixels=generate(s,D).tobytes();assert hashlib.sha256(pixels).hexdigest()==s['sha256'],'historical image hash drift'
   image=Guard(len(pixels));C.memmove(image.ptr,pixels,len(pixels));ws=Guard(lib.candidate_workspace_size(),0);out=Guard(C.sizeof(OptResult));diag=Guard(C.sizeof(RefineStats),0)
   cfg=Config(710,1000,*(truth['section'] if dataset=='probe' else s.get('section',(10,2))))
   start=time.monotonic();rc=fn(image.ptr,len(pixels),200,200,200,C.byref(cfg),ws.ptr,out.ptr,diag.ptr);elapsed=time.monotonic()-start
   for g in [image,ws,out,diag]:g.check()
   if not a.enabled:
    baseline=Guard(C.sizeof(OptResult));aws=Guard(lib.candidate_workspace_size(),0)
    arc=active(image.ptr,len(pixels),200,200,200,C.byref(cfg),aws.ptr,None,baseline.ptr)
    baseline.check();aws.check();assert arc==rc and baseline.data()==out.data(),'OFF differed from exact active result/status'
   assert image.data()==pixels,'input modified'
   assert not rc or out.data()==b'\xa5'*out.n,'rejected output modified'
   correct=False;decoded=None;support=None
   if rc==0:
    result=OptResult.from_buffer_copy(out.data());d=result.decoded;decoded=dict(x=d.x,y=d.y,directions=list(d.directions),pitch=d.pitch_px,ratio=result.y_scale,angle=d.angle_deg,dots=d.dots,windows=d.windows)
    if dataset=='probe':correct=[d.x,d.y]==truth['xy'] and list(d.directions)==truth['directions']
    else:
     match=list(d.directions)==D[d.y:d.y+6,d.x:d.x+6].reshape(-1).tolist();support=True;omitted=set(map(tuple,s.get('omit',[])))
     for y in range(d.y,d.y+6):
      for x in range(d.x,d.x+6):
       dx,dy=((0,-1),(-1,0),(1,0),(0,1))[D[y,x]]
       for rx in [-1/6,1/6]:
        for ry in [-1/6,1/6]:
         xx,yy=project(x+dx/6+rx,y+dy/6+ry,s);support &= 0<=xx<200 and 0<=yy<200 and (x,y) not in omitted
     correct=bool(match and support and not s.get('must_reject',False))
   classification='reject' if rc else 'correct_accept' if correct else 'wrong_or_quality_accept'
   r=dict(dataset=dataset,key=key,group=s['group'],status=rc,classification=classification,must_reject=s.get('must_reject',False),sha256=hashlib.sha256(pixels).hexdigest(),decoded=decoded,full_input_support=support,host_seconds=elapsed,canaries_ok=True,input_unchanged=True,rejected_output_unchanged=True,diagnostics={k:getattr(RefineStats.from_buffer_copy(diag.data()),k) for k,_ in RefineStats._fields_})
   if dataset=='probe':r.update(active_status=s['status'],active_classification=s['classification'])
   else:r.update(archived_v3_status=s['status'],archived_v3_correct=s.get('correct'),semantics='full200x200, no edge removal, max128 components; not V3 96/80 crop')
   results.append(r);print(dataset,key,rc,classification,flush=True)
 for p,h in hashes.items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,'changed source/input '+p
 summary=dict(enabled=a.enabled,targeted=a.targeted,total=len(results),counts=dict(collections.Counter(r['classification'] for r in results)),datasets={ds:dict(collections.Counter(r['classification'] for r in results if r['dataset']==ds)) for ds in sorted(set(r['dataset'] for r in results))},must_reject_accepts=sum(r['must_reject'] and r['status']==0 for r in results),source_input_sha256=hashes,candidate_at_build_sha256=candidate_hashes,scope='actual full200x200 input; no crop/prior/oracle to C; post-return symbol and conservative full-dot support; no transform output ABI so no transform error assertion')
 suffix=('targeted_' if a.targeted else '')+('on' if a.enabled else 'off');(OUT/f'{suffix}_results.json').write_text(json.dumps(results,indent=2)+'\n');(OUT/f'{suffix}_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 failures=[]
 if a.targeted:
  for r in results:
   want='reject' if r['key'] in ['000.pgm','015.pgm','030.pgm'] else 'correct_accept'
   if r['classification']!=want:failures.append(r['key'])
 else:
  failures=[r['key'] for r in results if r['classification']=='wrong_or_quality_accept']
  if not a.enabled:failures += [r['key'] for r in results if r['dataset']=='probe' and r['status']!=r['active_status']]
 print(json.dumps({k:v for k,v in summary.items() if k!='source_input_sha256'}),flush=True);print('FAILED EXPECTATIONS',failures,flush=True);return int(bool(failures))
if __name__=='__main__':sys.exit(main())
