import ctypes as C,json
from pathlib import Path
P=Path(__file__).resolve().parent
class Config(C.Structure):_fields_=[('w',C.c_uint16),('h',C.c_uint16),('u',C.c_uint8),('v',C.c_uint8)]
class Diag(C.Structure):_fields_=[('cold',C.c_uint32),('seeds',C.c_uint32),('iterations',C.c_uint32),('refined',C.c_uint32)]
class Seed(C.Structure):_fields_=[('pitch',C.c_double),('angle',C.c_double),('ratio',C.c_double)]
class Guard(C.Structure):_fields_=[('a',C.c_uint64*8),('seeds',Seed*64),('b',C.c_uint64*8)]
lib=C.CDLL(str(P/'review.so'));lib.core_ws_size.restype=C.c_size_t
lib.pen_roi_decode_refined_transform.argtypes=[C.POINTER(C.c_uint8),C.c_size_t,C.c_uint,C.c_uint,C.c_uint,C.POINTER(Config),C.c_void_p,C.POINTER(Seed),C.c_void_p,C.c_void_p,C.POINTER(Diag)]
ws=(C.c_double*((lib.core_ws_size()+7)//8))();cfg=Config(710,1000,10,2);rows=[]
for pitch in range(3,9):
 im=bytearray([240])*40000
 for y in range(6):
  for x in range(6):
   cx,cy=80+x*pitch,80+y*pitch
   for dx,dy in ((0,0),(1,0),(0,1)):im[(cy+dy)*200+cx+dx]=30
 arr=(C.c_uint8*40000).from_buffer_copy(im);g=Guard();C.memset(C.byref(g),0x7c,C.sizeof(g));out=(C.c_uint8*68)();t=(C.c_double*6)();C.memset(out,165,C.sizeof(out));C.memset(t,165,C.sizeof(t));before=bytes(out),bytes(t);d=Diag()
 rc=lib.pen_roi_decode_refined_transform(arr,40000,200,200,200,C.byref(cfg),ws,g.seeds,out,t,C.byref(d))
 assert rc!=0 and (bytes(out),bytes(t))==before
 assert all(x==0x7c7c7c7c7c7c7c7c for x in list(g.a)+list(g.b))
 rows.append({'pitch':pitch,'status':rc,'cold':d.cold,'seeds':d.seeds,'iterations':d.iterations,'refined':d.refined})
 if d.seeds==65:
  (P/f'overflow_pitch{pitch}.pgm').write_bytes(b'P5\n200 200\n255\n'+im)
print(rows);(P/'overflow_probe.json').write_text(json.dumps(rows,indent=2))
