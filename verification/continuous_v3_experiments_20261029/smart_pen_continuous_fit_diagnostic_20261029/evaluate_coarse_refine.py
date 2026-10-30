import sys
sys.dont_write_bytecode=True
from pathlib import Path
import ctypes as C
import json,math,time
import numpy as np
HERE=Path(__file__).resolve().parent;V2=HERE.parent/'smart_pen_continuous_roi_candidate_20261028'
sys.path[:0]=[str(HERE),str(V2/'tests'),str(V2/'tools')]
from pixel_fit_prototype import refine,phase
from test_roi_vision import Config
from test_roi_continuous import Transform
from test_roi_opt import OptResult
from continuous_roi_sweep import project
lib=C.CDLL(str(HERE/'diagnostic_seeds.so'));lib.ws_size.restype=C.c_size_t
lib.extract_points.argtypes=[C.POINTER(C.c_uint8),C.c_void_p,C.POINTER(C.c_double),C.POINTER(C.c_uint)]
lib.validate_estimated_model.argtypes=[C.c_void_p,C.c_int,C.POINTER(Config),C.c_double,C.c_double,C.c_double,C.POINTER(OptResult),C.POINTER(Transform)]
lib.geometry_seeds.argtypes=[C.c_void_p,C.c_int,C.POINTER(C.c_double),C.c_uint]
ws=(C.c_double*((lib.ws_size()+7)//8))();cfg=Config(710,1000,10,2)
dirs=np.load(HERE.parent/'smart_pen_viewport_audit_20261028/upstream_directions.npy')
rows=json.loads((HERE/'results.json').read_text());results=[]
for r in rows:
 s=r['source'];im=(HERE/'pixels'/f'case_{r["index"]:03d}.pgm').read_bytes().split(b'\n',3)[3];image=(C.c_uint8*len(im)).from_buffer_copy(im)
 points=(C.c_double*256)();meta=(C.c_uint*5)();n=lib.extract_points(image,ws,points,meta);pixels=np.asarray(points).reshape(128,2)[:n].copy();assert np.allclose(pixels,r['points'])
 start=time.perf_counter();buf=(C.c_double*(64*3))();count=lib.geometry_seeds(ws,n,buf,64);proposals=[]
 for i in range(min(count,64)):
  guess=refine(pixels,*list(buf)[3*i:3*i+3])
  if guess is not None:proposals.append(guess)
 statistics={'seeds':count,'overflow':count>64};seconds=time.perf_counter()-start;accepted=[]
 for pitch,angle,ratio in proposals:
  out=OptResult();t=Transform();rc=lib.validate_estimated_model(ws,n,C.byref(cfg),pitch,angle,ratio,C.byref(out),C.byref(t))
  if rc==1:
   x,y=out.decoded.x,out.decoded.y;correct=list(out.decoded.directions)==dirs[y:y+6,x:x+6].reshape(-1).tolist();errors=[]
   for row in range(6):
    for col in range(6):
     px,py=project(x+col,y+row,s)
     errors.append(math.hypot(t.origin_x+meta[1]+t.x_dx*col+t.y_dx*row-(px-.5),t.origin_y+meta[1]+t.x_dy*col+t.y_dy*row-(py-.5)))
   accepted.append(dict(model=[pitch,angle,ratio],x=x,y=y,exact_symbols=correct,max_grid_error=max(errors),correct=bool(correct and max(errors)<=.1*60/s['fov'])))
 # Entirely post-hoc diagnosis: apply the same phase algorithm at actual render geometry.
 # This never initializes models() or C; it only separates search discretization from phase failure.
 p=60/s['fov'];a=math.radians(s.get('angle',0));co,si=math.cos(a),math.sin(a)
 u=(pixels[:,0]*co+pixels[:,1]*si)/p;v=(-pixels[:,0]*si+pixels[:,1]*co)/p;ox,oy=phase(u),phase(v)
 for _ in range(3):
  dx=u-ox-np.rint(u-ox);dy=v-oy-np.rint(v-oy);h=np.abs(dx)>np.abs(dy)
  if h.any():oy+=dy[h].mean()
  if (~h).any():ox+=dx[~h].mean()
 dx=u-ox-np.rint(u-ox);dy=v-oy-np.rint(v-oy);major=np.maximum(abs(dx),abs(dy));minor=np.minimum(abs(dx),abs(dy))
 result={'index':r['index'],'group':r['group'],'v2_status':r['status'],'roi':r['roi'],'dots':r['dots'],'true_complete_windows':r['oracle_diagnosis_only']['complete_true_windows'],'statistics':statistics,'proposal_count':len(proposals),'seconds_python':seconds,'proposals':proposals,'accepted':accepted,'disagree':len(set((x['x'],x['y']) for x in accepted))>1,'posthoc_true_geometry_phase_gate':bool(np.all((major>=.1)&(major<=.3)&(minor<=.065))),'posthoc_max_minor':float(minor.max()),'posthoc_min_major':float(major.min()),'posthoc_max_major':float(major.max())}
 results.append(result);print(r['index'],r['group'],r['status'],statistics,'strict_models',len(accepted),'wrong',sum(not x['correct'] for x in accepted),flush=True)
(HERE/'coarse_refine_results.json').write_text(json.dumps(results,indent=2))
