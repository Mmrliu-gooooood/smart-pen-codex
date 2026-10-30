"""Fast fixed-image cold replay: no image generation and no answer-derived input."""
import sys,json,ctypes as C,subprocess,tempfile,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parent;OPT=ROOT/'smart_pen_vision_opt_20261028'
sys.path.insert(0,str(OPT/'tests'))
from test_roi_vision import Config
from test_roi_opt import OptResult,Prior
manifest=json.loads((P/'regression_manifest.json').read_text());results=[]
with tempfile.TemporaryDirectory() as temp:
 t=Path(temp);(t/'bridge.c').write_text('#include "roi_opt.h"\nsize_t ws_size(void){return sizeof(pen_roi_workspace);}\n')
 subprocess.run(['cc','-std=c11','-O2','-shared','-fPIC','-I'+str(OPT/'firmware/vision'),str(t/'bridge.c'),str(OPT/'firmware/vision/roi_opt.c'),str(OPT/'firmware/codec/anoto.c'),'-lm','-o',str(t/'replay.so')],check=True)
 lib=C.CDLL(str(t/'replay.so'));lib.ws_size.restype=C.c_size_t;ws=(C.c_double*((lib.ws_size()+7)//8))()
 lib.pen_roi_decode_opt.argtypes=[C.POINTER(C.c_uint8),C.c_size_t,C.c_uint,C.c_uint,C.c_uint,C.POINTER(Config),C.c_void_p,C.POINTER(Prior),C.POINTER(OptResult)]
 cfg=Config(*manifest['paper_config'])
 for row in manifest['fixtures']:
  magic,dims,maximum,pixels=(P/row['fixture']).read_bytes().split(b'\n',3);w,h=map(int,dims.split());assert magic==b'P5' and maximum==b'255' and len(pixels)==w*h;assert hashlib.sha256(pixels).hexdigest()==row['image_sha256']
  img=(C.c_uint8*len(pixels)).from_buffer_copy(pixels);out=OptResult();C.memset(C.byref(out),165,C.sizeof(out));before=bytes(out)
  status=lib.pen_roi_decode_opt(img,len(pixels),w,h,w,C.byref(cfg),ws,None,C.byref(out));expected=row['cold'];assert status==expected['status'],(row['fixture'],status,expected)
  if status==0:assert (out.decoded.x,out.decoded.y)==(expected['x'],expected['y'])
  else:assert bytes(out)==before
  results.append({'fixture':row['fixture'],'status':status,'passed':True})
(P/'regression_replay.json').write_text(json.dumps({'count':len(results),'passed':len(results),'cold_prior':'NULL','results':results},indent=2));print(f'{len(results)}/{len(results)} fixed fixtures matched status/coordinate/hash/output-preservation oracle')
