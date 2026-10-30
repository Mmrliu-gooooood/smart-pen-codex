"""Exact byte-level cold/warm old ABI equivalence: new TU vs frozen V3."""
import sys
sys.dont_write_bytecode=True
import ctypes as C,json,subprocess,tempfile,hashlib
from pathlib import Path
import numpy as np
from binding import Decoder,Config,OptResult
P=Path(__file__).resolve().parent;A=P.parent/'smart_pen_viewport_audit_20261028';F=P.parent/'smart_pen_continuous_roi_v3_candidate_20261029'
class Prior(C.Structure):_fields_=[('valid',C.c_uint32),('pitch_px',C.c_float),('angle_deg',C.c_float),('y_scale',C.c_float)]
with Decoder() as new,tempfile.TemporaryDirectory() as td:
 path=Path(td)/'old.so';subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-pedantic','-shared','-fPIC',str(F/'firmware/vision/roi_opt.c'),str(F/'firmware/codec/anoto.c'),'-lm','-o',str(path)],check=True);old=C.CDLL(str(path));rows=[]
 args=[C.c_void_p,C.c_size_t,C.c_uint,C.c_uint,C.c_uint,C.POINTER(Config),C.c_void_p,C.POINTER(Prior),C.POINTER(OptResult)]
 for lib in (new.lib,old):lib.pen_roi_decode_opt.argtypes=args;lib.pen_roi_decode_opt.restype=C.c_int
 ws1=(C.c_double*5120)();ws2=(C.c_double*5120)();cfg=Config(710,1000,10,2)
 for s in json.loads((A/'regression_manifest.json').read_text())['fixtures']:
  head,dims,maxval,pix=(A/s['fixture']).read_bytes().split(b'\n',3);w,h=map(int,dims.split());assert hashlib.sha256(pix).hexdigest()==s['image_sha256'];im=(C.c_uint8*len(pix)).from_buffer_copy(pix)
  a,b=OptResult(),OptResult();C.memset(C.byref(a),165,C.sizeof(a));C.memset(C.byref(b),165,C.sizeof(b))
  ra=new.lib.pen_roi_decode_opt(im,len(pix),w,h,w,C.byref(cfg),ws1,None,C.byref(a));rb=old.pen_roi_decode_opt(im,len(pix),w,h,w,C.byref(cfg),ws2,None,C.byref(b));assert ra==rb==s['cold']['status'] and bytes(a)==bytes(b)
  warm=False
  if not ra:
   pa=Prior(1,a.decoded.pitch_px,a.decoded.angle_deg,a.y_scale);pb=Prior.from_buffer_copy(bytes(pa))
   ra=new.lib.pen_roi_decode_opt(im,len(pix),w,h,w,C.byref(cfg),ws1,C.byref(pa),C.byref(a));rb=old.pen_roi_decode_opt(im,len(pix),w,h,w,C.byref(cfg),ws2,C.byref(pb),C.byref(b));assert ra==rb==0 and bytes(a)==bytes(b) and bytes(pa)==bytes(pb);warm=True
  assert bytes(im)==pix;rows.append(dict(fixture=s['fixture'],cold_identical=True,warm_tested=warm,warm_identical=True if warm else None))
 (P/'legacy44_results.json').write_text(json.dumps(rows,indent=2)+'\n');print('PASS',len(rows),'legacy cold cases, matching warm calls for successful cold cases')
