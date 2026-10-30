"""Deterministic offline crosswire against actual frozen C codec/core, no radio."""
from pathlib import Path
import sys,os,ctypes as C,tempfile,subprocess,random,json
HERE=Path(__file__).resolve().parent
SRC=Path(os.environ.get('PC_SOURCE',str(HERE/'source'))).resolve()
BLE=Path(os.environ.get('BLE_SOURCE',str(HERE.parent/'smart_pen_ble_transport_candidate_20261029'))).resolve()
sys.dont_write_bytecode=True;sys.path.insert(0,str(SRC))
from pen_receiver.protocol import Record,fragments,encode_ack,Reassembler
code=r'''
#include "pen_ble_core.h"
#include <string.h>
struct ctx {unsigned n;uint8_t*out;};
static int sink(void*c,const uint8_t*b,size_t n,uint64_t e){struct ctx*x=c;if(n!=20||e!=11||x->n>=3)return -1;memcpy(x->out+20*x->n++,b,20);return 0;}
int wire(uint8_t*out,uint32_t device,uint64_t session,uint32_t seq,uint64_t stamp,uint32_t page,int32_t x,int32_t y,uint16_t confidence,uint8_t flags){pen_sample p={.device=device,.session=session,.seq=seq,.timestamp_us=stamp,.page=page,.x_um=x,.y_um=y,.confidence=confidence,.flags=flags};return pen_encode(out,&p);}
int decode(const uint8_t*b){pen_sample p;return pen_decode(&p,b);}
int transfer(const uint8_t*b,const uint8_t*ack,uint8_t*out){pen_ble_core c;pen_ble_core_init(&c);pen_link_security s={1,1,1,1,11};pen_ble_core_link(&c,&s,16);pen_ble_core_subscribe(&c,1);struct ctx x={0,out};if(pen_ble_core_send(&c,b,48,11,1,sink,&x)||x.n!=3)return -8;return pen_ble_core_receive(&c,ack,20,2);}
'''
with tempfile.TemporaryDirectory() as t:
 p=Path(t);(p/'bridge.c').write_text(code)
 includes=[BLE/'include']+[BLE/'frozen'/x for x in ['application','runtime','storage','portable','vision','codec']]
 subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-shared','-fPIC',*['-I'+str(x) for x in includes],str(p/'bridge.c'),str(BLE/'src/pen_ble_core.c'),str(BLE/'frozen/portable/pen.c'),'-o',str(p/'wire.so')],check=True)
 lib=C.CDLL(str(p/'wire.so'));bp=C.POINTER(C.c_uint8);lib.wire.argtypes=[bp,C.c_uint32,C.c_uint64,C.c_uint32,C.c_uint64,C.c_uint32,C.c_int32,C.c_int32,C.c_uint16,C.c_uint8];lib.transfer.argtypes=[bp,bp,bp];lib.decode.argtypes=[bp]
 rng=random.Random(20261029)
 for k in range(500):
  r=Record(rng.randrange(8),rng.randrange(2**32),rng.randrange(1,2**64),rng.randrange(2**32),rng.randrange(2**64),rng.randrange(1,2**32),rng.randrange(-2**31,2**31),rng.randrange(-2**31,2**31),rng.randrange(1001))
  raw=r.encode();c=(C.c_uint8*48)();assert lib.wire(c,r.device,r.session,r.seq,r.timestamp_us,r.page,r.x_um,r.y_um,r.confidence,r.flags)==0 and bytes(c)==raw
  ack=(C.c_uint8*20).from_buffer_copy(encode_ack(r.session,r.seq));frames=(C.c_uint8*60)();assert lib.transfer(c,ack,frames)==0
  fs=[bytes(frames)[i*20:(i+1)*20] for i in range(3)];assert fs==fragments(raw)
  a=Reassembler()
  for i,f in enumerate(fs):got=a.accept(f,now=i*.01)
  assert got==raw
 for i in range(48):
  bad=bytearray(raw);bad[i]^=1;b=(C.c_uint8*48).from_buffer_copy(bad);assert lib.decode(b)!=0
  try:Record.decode(bad)
  except ValueError:pass
  else:raise AssertionError('CRC accepted')
 for i in range(20):
  bad=bytearray(encode_ack(r.session,r.seq));bad[i]^=1;ab=(C.c_uint8*20).from_buffer_copy(bad);assert lib.transfer(c,ab,frames)!=0
print(json.dumps({'random_actual_C_Python_packet_fragment_ack_cases':500,'record_byte_corruption_rejected':48,'actual_C_ACK_byte_corruption_rejected':20,'radio_executed':False},indent=2))
