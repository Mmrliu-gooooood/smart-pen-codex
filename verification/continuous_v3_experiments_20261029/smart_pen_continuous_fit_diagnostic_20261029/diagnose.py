"""Stage/root-cause diagnosis. Oracle geometry used only AFTER pixel decode."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import ctypes as C
import json,hashlib,math,time
import numpy as np
HERE=Path(__file__).resolve().parent;V2=HERE.parent/'smart_pen_continuous_roi_candidate_20261028'
sys.path.insert(0,str(V2/'tools'));sys.path.insert(0,str(V2/'tests'))
from continuous_roi_sweep import render
from test_roi_continuous import FrameResult
from test_roi_vision import Config
fields='calls residual_fail span_fail duplicate complete_windows codec_fail codec_ok no_complete no_decoded ambiguous model_ok'.split()
class Trace(C.Structure):_fields_=[(k,C.c_uint) for k in fields]
lib=C.CDLL(str(HERE/'diagnostic.so'));lib.ws_size.restype=C.c_size_t
lib.pen_roi_decode_continuous.argtypes=[C.POINTER(C.c_uint8),C.c_size_t,C.c_uint,C.c_uint,C.c_uint,C.POINTER(Config),C.c_void_p,C.POINTER(FrameResult)]
lib.extract_points.argtypes=[C.POINTER(C.c_uint8),C.c_void_p,C.POINTER(C.c_double),C.POINTER(C.c_uint)]
ws=(C.c_double*((lib.ws_size()+7)//8))();cfg=Config(710,1000,10,2)
dirs=np.load(HERE.parent/'smart_pen_viewport_audit_20261028/upstream_directions.npy')
rows=json.loads((V2/'verification/continuous/results.json').read_text())
cases=[(i,r) for i,r in enumerate(rows) if r['group'] in ('fractional_fov','rotation')]
results=[];(HERE/'pixels').mkdir(exist_ok=True)
for number,(index,s) in enumerate(cases):
 im=render(dirs,s);assert hashlib.sha256(im.tobytes()).hexdigest()==s['sha256']
 ptr=im.ctypes.data_as(C.POINTER(C.c_uint8));out=FrameResult();C.memset(C.byref(out),165,C.sizeof(out));before=bytes(out)
 lib.trace_reset();start=time.perf_counter();status=lib.pen_roi_decode_continuous(ptr,40000,200,200,200,C.byref(cfg),ws,C.byref(out));seconds=time.perf_counter()-start
 assert status==s['status'] and (status==0 or bytes(out)==before)
 trace=Trace();lib.trace_get(C.byref(trace));points=(C.c_double*256)();meta=(C.c_uint*5)();n=lib.extract_points(ptr,ws,points,meta)
 assert n>=36
 pixel=np.asarray(points).reshape(128,2)[:n].copy();side,left,edges,edgepixels,prepared=meta
 # Post-hoc true geometry membership and diagnostics. Not supplied to C.
 p=60/s['fov'];a=math.radians(s.get('angle',0));co,si=math.cos(a),math.sin(a)
 corner=pixel+left+.5;u=(corner[:,0]-100)/p;v=(corner[:,1]-100)/p
 true=np.stack((co*u+si*v+s['ox']+100/p,-si*u+co*v+s['oy']+100/p),axis=1)
 cells=np.rint(true).astype(int);offset=true-cells;abs_offset=np.abs(offset);axis=abs_offset.argmax(axis=1)
 predicted=np.where(axis==0,np.where(offset[:,0]<0,1,2),np.where(offset[:,1]<0,0,3))
 exact=predicted==dirs[cells[:,1],cells[:,0]]
 occupied=set(map(tuple,cells));complete=[]
 for x,y in occupied:
  if all((x+c,y+r) in occupied for r in range(6) for c in range(6)):complete.append([x,y])
 record={'index':index,'group':s['group'],'fov':s['fov'],'angle':s.get('angle',0),'phase':s.get('phase'),
         'status':status,'seconds':seconds,'trace':{k:getattr(trace,k) for k in fields},'roi':side,'dots':n,'prepared_dots':prepared,
         'oracle_diagnosis_only':{'symbols_correct':int(exact.sum()),'detected_dots':n,'duplicate_true_cells':n-len(occupied),'complete_true_windows':len(complete),'max_true_minor':float(abs_offset.min(axis=1).max()),'min_true_major':float(abs_offset.max(axis=1).min()),'max_true_major':float(abs_offset.max(axis=1).max())},
         'points':pixel.tolist(),'source':s,'image_sha256':hashlib.sha256(im.tobytes()).hexdigest()}
 if status==0:record['decoded_xy']=[out.roi.decoded.x,out.roi.decoded.y]
 (HERE/'pixels'/f'case_{index:03d}.pgm').write_bytes(b'P5\n200 200\n255\n'+im.tobytes())
 results.append(record);(HERE/'results.json').write_text(json.dumps(results,indent=2))
 print(f'{number+1}/{len(cases)} idx={index} status={status} residual_rejected={trace.residual_fail}/{trace.calls} true_complete={len(complete)} exact={int(exact.sum())}/{n}',flush=True)
print('DONE',len(results))
