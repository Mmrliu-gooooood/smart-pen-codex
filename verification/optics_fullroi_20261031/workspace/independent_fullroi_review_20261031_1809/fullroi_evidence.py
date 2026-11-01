import ctypes as C,tempfile,sys,json
from pathlib import Path
from build import build,ROOT,HERE
sys.path.insert(0,str(ROOT/'tests'));from test_roi_vision import Config
from test_roi_opt import OptResult
p=HERE.parent/'optics_paper_screen_20261031_1752/decoder_probe/001.pgm';base=p.read_bytes().split(b'\n',3)[3];changed=bytearray(base)
for y in range(98,104):changed[y*200]=30
rows=[]
for enabled in [False,True]:
 with tempfile.TemporaryDirectory() as tmp:
  lib=C.CDLL(str(build(tmp,enabled)));lib.candidate_workspace_size.restype=C.c_size_t;fn=lib.candidate_decode;fn.argtypes=[C.c_void_p,C.c_size_t,C.c_uint,C.c_uint,C.c_uint,C.POINTER(Config),C.c_void_p,C.c_void_p,C.c_void_p];fn.restype=C.c_int
  for name,pixels in [('frozen_positive',base),('edge_ink_outside_central96',changed)]:
   im=(C.c_uint8*40000).from_buffer_copy(pixels);ws=(C.c_double*((lib.candidate_workspace_size()+7)//8))();out=OptResult();C.memset(C.byref(out),0xa5,C.sizeof(out));before=bytes(out);cfg=Config(710,1000,0,0);rc=fn(im,40000,200,200,200,C.byref(cfg),ws,C.byref(out),None)
   if (name=='frozen_positive' and rc!=0) or (name!='frozen_positive' and (rc!=-2 or bytes(out)!=before)) or bytes(im)!=bytes(pixels):raise RuntimeError('evidence preservation failed')
   rows.append({'enabled':enabled,'case':name,'status':rc,'input_unchanged':True,'failure_output_unchanged':rc!=0})
(HERE/'verification/fullroi_evidence.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))
