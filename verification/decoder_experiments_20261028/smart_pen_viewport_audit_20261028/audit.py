"""Synthetic rolling-paper viewport audit. No geometry/answer supplied to decoder."""
import sys, json, hashlib, subprocess, ctypes as C, time
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
ROOT=Path(__file__).resolve().parent.parent; OUT=Path(__file__).resolve().parent
UP=ROOT/'smart_pen_original_20261028'; OPT=ROOT/'smart_pen_vision_opt_20261028'
sys.path[:0]=[str(UP/'点阵笔资料/py_microdots_develop'),str(OPT/'tests')]
from microdots import anoto_6x6_a4_fixed as codec
from test_roi_vision import Config
from test_roi_opt import Prior, OptResult
bridge=OUT/'bridge.c'
bridge.write_text('#include "roi_opt.c"\nsize_t audit_ws_size(void){return sizeof(pen_roi_workspace);}\nint audit_detect(const uint8_t*g,unsigned w,unsigned h,pen_roi_workspace*ws){return detect(g,w,h,w,ws->points,ws);}\n')
subprocess.run(['cc','-std=c11','-O2','-shared','-fPIC','-I'+str(OPT/'firmware/vision'),str(bridge),str(OPT/'firmware/codec/anoto.c'),'-lm','-o',str(OUT/'audit.so')],check=True)
lib=C.CDLL(str(OUT/'audit.so'));lib.audit_ws_size.restype=C.c_size_t
ws=(C.c_double*((lib.audit_ws_size()+7)//8))()
lib.pen_roi_decode_opt.argtypes=[C.POINTER(C.c_uint8),C.c_size_t,C.c_uint,C.c_uint,C.c_uint,C.POINTER(Config),C.c_void_p,C.POINTER(Prior),C.POINTER(OptResult)]
lib.audit_detect.argtypes=[C.POINTER(C.c_uint8),C.c_uint,C.c_uint,C.c_void_p]
section=(10,2); bits=codec.encode_bitmatrix((1000,710),section); dirs=(bits[:,:,0]+2*bits[:,:,1]).astype(np.uint8)
np.save(OUT/'upstream_directions.npy',dirs)
cfg=Config(710,1000,*section); rng=np.random.default_rng(20261028)
# Full continuous paper, profile C (pitch .3, offset .05, radius .05 mm).
# Four-by-four subpixel area sampling; top-left camera raster canonicalized.
def render(fov,ox,oy):
 p=60/fov; image=np.full((200,200),240,dtype=np.uint8); centers=[]
 for y in range(int(oy)-2,int(oy+200/p)+3):
  for x in range(int(ox)-2,int(ox+200/p)+3):
   dx,dy=((0,-1),(-1,0),(1,0),(0,1))[dirs[y,x]]
   cx=(x-ox+dx/6)*p; cy=(y-oy+dy/6)*p; r=p/6
   x0=max(0,int(np.floor(cx-r))-1); x1=min(200,int(np.ceil(cx+r))+1)
   y0=max(0,int(np.floor(cy-r))-1); y1=min(200,int(np.ceil(cy+r))+1)
   if x1<=x0 or y1<=y0:continue
   yy,xx=np.mgrid[y0:y1,x0:x1]; cov=np.zeros_like(xx)
   for sy in range(4):
    for sx in range(4): cov+=((xx+(sx+.5)/4-cx)**2+(yy+(sy+.5)/4-cy)**2 <= r*r)
   image[y0:y1,x0:x1]=np.minimum(image[y0:y1,x0:x1],240-np.rint(210*cov/16).astype(np.uint8))
 return image

def decode(im,prior):
 im=np.ascontiguousarray(im); ptr=im.ctypes.data_as(C.POINTER(C.c_uint8)); result=OptResult(); C.memset(C.byref(result),165,C.sizeof(result)); before=bytes(result)
 start=time.perf_counter(); status=lib.pen_roi_decode_opt(ptr,im.size,im.shape[1],im.shape[0],im.shape[1],C.byref(cfg),ws,C.byref(prior),C.byref(result)); duration=time.perf_counter()-start
 assert status==0 or bytes(result)==before
 assert status==0 or prior.valid==0
 record={'status':status,'seconds':duration}
 if status==0:record.update(x=result.decoded.x,y=result.decoded.y,dots=result.decoded.dots,windows=result.decoded.windows,pitch=result.decoded.pitch_px,angle=result.decoded.angle_deg,warm=bool(result.used_warm_start),candidates=result.candidates)
 return record,result
records=[]
for fov in (5,6,7):
 for phase in range(36):
  ox=120+phase%6+float(rng.uniform(0,1));oy=240+phase//6+float(rng.uniform(0,1)); full=render(fov,ox,oy)
  for size in (200,96,80,64):
   start=(200-size)//2; im=full[start:start+size,start:start+size]; prior=Prior(); cold,result=decode(im,prior)
   rec={'fov_mm':fov,'size':size,'phase':phase,'ox_cells':ox,'oy_cells':oy,'image_sha256':hashlib.sha256(im.tobytes()).hexdigest(),'cold':cold}
   if cold['status']==0:
    x,y=cold['x'],cold['y']; actual=list(result.decoded.directions); expected=dirs[y:y+6,x:x+6].reshape(-1).tolist()
    # Independent ground truth: decoded window inside this viewport + exact encoded symbols.
    p=60/fov; left=ox+start/p;top=oy+start/p;right=left+size/p;bottom=top+size/p
    rec['correct']=actual==expected and left-1/3<=x and x+5<=right+1/3 and top-1/3<=y and y+5<=bottom+1/3
    warm,_=decode(im,prior);rec['warm']=warm;rec['warm']['correct']=warm['status']==0 and (warm['x'],warm['y'])==(x,y)
   if phase in (0,17) or cold['status']==0 and not any(r['fov_mm']==fov and r['size']==size and r['cold']['status']==0 for r in records):
    name=f'fov{fov}_roi{size}_phase{phase}.pgm'; (OUT/name).write_bytes(f'P5\n{size} {size}\n255\n'.encode()+im.tobytes());rec['fixture']=name
   records.append(rec)
   (OUT/'results.json').write_text(json.dumps(records,indent=2))
  print(f'fov={fov} phase={phase} statuses={[r["cold"]["status"] for r in records[-4:]]}',flush=True)
summary=[]
for fov in (5,6,7):
 for size in (200,96,80,64):
  group=[r for r in records if r['fov_mm']==fov and r['size']==size]; counts=Counter(r['cold']['status'] for r in group)
  summary.append({'fov_mm':fov,'roi':size,'n':len(group),'counts':dict(counts),'false_success':sum(not r['correct'] for r in group if r['cold']['status']==0),'warm_success':sum(r.get('warm',{}).get('status')==0 for r in group),'warm_false':sum(not r['warm']['correct'] for r in group if 'warm' in r)})
provenance={'upstream_commit':subprocess.check_output(['git','-C',str(UP),'rev-parse','HEAD'],text=True).strip(),'optimized_commit':subprocess.check_output(['git','-C',str(OPT),'rev-parse','HEAD'],text=True).strip(),'seed':20261028,'section':section,'generator_sha256':{str(p.relative_to(UP)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((UP/'点阵笔资料/py_microdots_develop/microdots').glob('*.py'))},'profile_sha256':hashlib.sha256((UP/'digital_pen_ov5640/pc/configs/pattern.yaml').read_bytes()).hexdigest(),'synthetic_only':True}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2));(OUT/'provenance.json').write_text(json.dumps(provenance,indent=2));print(json.dumps(summary,indent=2))
