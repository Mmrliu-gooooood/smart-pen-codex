import sys,json,ctypes as C,subprocess,tempfile
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent;sys.path[:0]=[str(P/'source/tests'),str(P/'source/tools')]
from test_roi_opt import OptResult
from test_roi_vision import Config
class Result(C.Structure):_fields_=[('abi',C.c_uint32),('roi',OptResult),('left',C.c_uint16),('top',C.c_uint16),('width',C.c_uint16),('height',C.c_uint16),('H',C.c_double*9),('I',C.c_double*9)]
class Diag(C.Structure):_fields_=[(k,C.c_uint32) for k in ('components','retained','coarse','seeds','iterations','models','overflow')]
with tempfile.TemporaryDirectory() as td:
 libpath=Path(td)/'lib.so';subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-pedantic','-shared','-fPIC',str(P/'source/firmware/vision/roi_projective.c'),str(P/'source/firmware/codec/anoto.c'),'-lm','-o',str(libpath)],check=True)
 lib=C.CDLL(str(libpath));f=lib.pen_roi_decode_projective_v4;f.argtypes=[C.c_void_p,C.c_size_t,C.c_uint,C.c_uint,C.c_uint,C.POINTER(Config),C.c_void_p,C.POINTER(Result),C.POINTER(Diag)]
 ws=(C.c_double*5120)();rows=[]
 for s in json.loads((P/'baseline_eight.json').read_text()):
  name=f'tilt{s["camera_tilt_deg"]}_phase{s["phase"]}.pgm';im=np.frombuffer((P.parent/'smart_pen_optical_sampling_audit_20261030'/name).read_bytes().split(b'\n',3)[3],np.uint8).copy();r=Result();d=Diag();cfg=Config(710,1000,10,2);status=f(im.ctypes.data,40000,200,200,200,C.byref(cfg),ws,C.byref(r),C.byref(d));rec=dict(image=name,status=status,diagnostics={k:getattr(d,k) for k,_ in d._fields_})
  if status==0:rec.update(x=r.roi.decoded.x,y=r.roi.decoded.y,directions=list(r.roi.decoded.directions),H=list(r.H),roi=[r.left,r.top,r.width,r.height])
  rows.append(rec);print(rec,flush=True)
 (P/'candidate_eight.json').write_text(json.dumps(rows,indent=2)+'\n')
