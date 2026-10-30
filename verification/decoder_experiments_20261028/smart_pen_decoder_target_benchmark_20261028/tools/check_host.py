"""Pixel/oracle and failure-contract checks only; deliberately reports no host latency."""
from pathlib import Path
import ctypes as C,json,subprocess,tempfile
p=Path(__file__).resolve().parents[1]
class Config(C.Structure): _fields_=[('w',C.c_uint16),('h',C.c_uint16),('u',C.c_uint8),('v',C.c_uint8)]
class Result(C.Structure): _fields_=[('x',C.c_uint16),('y',C.c_uint16),('dots',C.c_uint16),('windows',C.c_uint16),('pitch',C.c_float),('angle',C.c_float),('residual',C.c_float),('directions',C.c_uint8*36)]
class Opt(C.Structure): _fields_=[('decoded',Result),('yscale',C.c_float),('candidates',C.c_uint32),('used_warm',C.c_uint8)]
class Prior(C.Structure): _fields_=[('valid',C.c_uint32),('pitch',C.c_float),('angle',C.c_float),('yscale',C.c_float)]
with tempfile.TemporaryDirectory() as tmp:
 t=Path(tmp);(t/'bridge.c').write_text('#include "roi_opt.h"\nsize_t ws_size(void){return sizeof(pen_roi_workspace);}\n')
 subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-shared','-fPIC','-I'+str(p/'vision'),str(t/'bridge.c'),str(p/'vision/roi_opt.c'),str(p/'codec/anoto.c'),'-lm','-o',str(t/'test.so')],check=True)
 lib=C.CDLL(str(t/'test.so'));lib.ws_size.restype=C.c_size_t
 lib.pen_roi_decode_opt.argtypes=[C.POINTER(C.c_uint8),C.c_size_t,C.c_uint,C.c_uint,C.c_uint,C.POINTER(Config),C.c_void_p,C.POINTER(Prior),C.POINTER(Opt)]
 ws=(C.c_double*((lib.ws_size()+7)//8))(); rows=[]
 for r in json.loads((p/'fixtures/manifest.json').read_text()):
  data=(p/'fixtures'/r['file']).read_bytes().split(b'\n255\n',1)[1]; pixels=(C.c_uint8*len(data)).from_buffer_copy(data);prior=Prior();cfg=Config(710,1000,10,2)
  for phase in ['cold','warm']:
   if phase=='warm' and not prior.valid: break
   out=Opt();C.memset(C.byref(out),0xa5,C.sizeof(out));before=bytes(out)
   rc=lib.pen_roi_decode_opt(pixels,len(data),r['width'],r['height'],r['width'],C.byref(cfg),ws,C.byref(prior),C.byref(out))
   assert rc==r['expected_status'],(r['file'],rc)
   if rc: assert bytes(out)==before and prior.valid==0
   else:
    assert [out.decoded.x,out.decoded.y]==[r['expected_x'],r['expected_y']]
    assert bool(out.used_warm)==(phase=='warm')
   rows.append(dict(fixture=r['file'],mode=phase,status=rc,oracle_pass=True))
 print(json.dumps(dict(scope='host functional only; NOT MCU speed or sensor accuracy',workspace_bytes=lib.ws_size(),records=rows),indent=2))
