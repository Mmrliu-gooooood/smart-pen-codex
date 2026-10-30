"""Direct codec semantics only (not image acquisition)."""
from pathlib import Path
import ctypes as C,json,numpy as np
p=Path(__file__).parent;lib=C.CDLL(str(p.resolve()/'audit.so'));dirs=np.load(p/'upstream_directions.npy');counts=0;errors=[]
lib.pen_anoto_decode.argtypes=[C.POINTER(C.c_uint8),C.c_uint16,C.c_uint16,C.c_uint8,C.c_uint8,C.POINTER(C.c_uint16),C.POINTER(C.c_uint16)]
for y in range(240,264):
 for x in range(120,144):
  window=np.ascontiguousarray(dirs[y:y+6,x:x+6]);xx=C.c_uint16();yy=C.c_uint16();code=lib.pen_anoto_decode(window.ctypes.data_as(C.POINTER(C.c_uint8)),710,1000,10,2,C.byref(xx),C.byref(yy));counts+=1
  if code or (xx.value,yy.value)!=(x,y):errors.append((x,y,code,xx.value,yy.value))
(p/'rolling_codec.json').write_text(json.dumps({'windows':counts,'errors':errors,'all_mod6_xy_phases':True,'scope':'Direct codec only, not image acquisition'},indent=2));assert not errors
