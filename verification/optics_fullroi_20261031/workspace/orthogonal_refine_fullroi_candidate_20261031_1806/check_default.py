"""Compile wrapper with gate definition OMITTED, compare positive output to active."""
import tempfile,subprocess,ctypes as C,sys,json
from pathlib import Path
from build import build,HERE,ROOT,V3
sys.path.insert(0,str(ROOT/'tests'))
from test_roi_vision import Config
from test_roi_opt import OptResult
with tempfile.TemporaryDirectory() as tmp:
 tmp=Path(tmp);build(tmp,False)
 subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-pedantic','-fPIC','-I'+str(HERE),'-I'+str(V3/'firmware/vision'),'-c',str(HERE/'candidate.c'),'-o',str(tmp/'3.o')],check=True)
 so=tmp/'default.so';subprocess.run(['cc','-shared',*[str(tmp/f'{i}.o') for i in range(4)],'-lm','-o',str(so)],check=True)
 lib=C.CDLL(str(so));lib.candidate_workspace_size.restype=C.c_size_t
 args=[C.POINTER(C.c_uint8),C.c_size_t,C.c_uint,C.c_uint,C.c_uint,C.POINTER(Config),C.c_void_p,C.POINTER(OptResult),C.c_void_p]
 lib.candidate_decode.argtypes=args
 lib.pen_roi_active_decode_opt.argtypes=args[:7]+[C.c_void_p,C.POINTER(OptResult)]
 rows=[]
 for name in ['001.pgm','control_000.pgm','048.pgm','050.pgm']:
  data=(HERE.parent/'optics_paper_screen_20261031_1752/decoder_probe'/name).read_bytes().split(b'\n',3)[3];im=(C.c_uint8*len(data)).from_buffer_copy(data);ws=(C.c_double*((lib.candidate_workspace_size()+7)//8))();other=(C.c_double*2736)();cfg=Config(710,1000,0,0);a=OptResult();b=OptResult();C.memset(C.byref(a),0xa5,C.sizeof(a));C.memset(C.byref(b),0xa5,C.sizeof(b))
  ra=lib.candidate_decode(im,len(data),200,200,200,C.byref(cfg),ws,C.byref(a),None);rb=lib.pen_roi_active_decode_opt(im,len(data),200,200,200,C.byref(cfg),other,None,C.byref(b))
  if ra!=rb or bytes(a)!=bytes(b):raise RuntimeError('default gate not exactactive '+name)
  rows.append({'image':name,'status':ra,'exact_active_bytes':True})
 print(json.dumps({'gate_definition':'omitted','rows':rows},indent=2))
