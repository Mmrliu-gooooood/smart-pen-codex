"""Real bench C wire/ACK implementation against host framing; no BLE hardware."""
import ctypes as C
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'software'))
from ble_transport import encode_ack,fragment
from pen_bridge import Packet
class BenchWireTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();so=Path(cls.tmp.name)/'bench.so'
  subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-pedantic','-shared','-fPIC','-I'+str(ROOT/'firmware/portable'),str(ROOT/'firmware/bench_idf/main/bench_wire.c'),str(ROOT/'firmware/portable/pen.c'),'-o',str(so)],check=True)
  cls.lib=C.CDLL(str(so));cls.lib.bench_ack.argtypes=[C.POINTER(C.c_uint8),C.c_size_t]+[C.c_bool]*5+[C.c_uint64,C.c_uint32]
  cls.lib.bench_fragment.argtypes=[C.POINTER(C.c_uint8),C.c_uint32,C.c_uint,C.POINTER(C.c_uint8)]
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def ack(self,raw,security=(1,1,1,1,1),session=2**64-1,seq=65537):
  return self.lib.bench_ack((C.c_uint8*len(raw))(*raw),len(raw),*security,session,seq)
 def test_ack_security_boundaries(self):
  raw=encode_ack(2**64-1,65537);self.assertEqual(self.ack(raw),1)
  self.assertEqual(self.ack(raw,seq=65538),0)
  self.assertEqual(self.ack(raw,seq=65536),-1)
  self.assertEqual(self.ack(raw,session=1),-1)
  for i in range(5):
   sec=[True]*5;sec[i]=False;self.assertEqual(self.ack(raw,security=sec),-1)
  for i in range(20):
   b=bytearray(raw);b[i]^=1;self.assertEqual(self.ack(b),-1)
  self.assertEqual(self.ack(raw[:-1]),-1)
 def test_fragment_crosswire(self):
  for seq in [0,1,65535,65536,2**32-1]:
   raw=Packet(4,0x42454e43,2**64-1,seq,100,2**32-1,-123,456,0).encode()
   expected=fragment(raw,seq&65535);packet=(C.c_uint8*48)(*raw);out=(C.c_uint8*20)()
   for i in range(3):
    self.assertEqual(self.lib.bench_fragment(packet,seq,i,out),0);self.assertEqual(bytes(out),expected[i])
   self.assertEqual(self.lib.bench_fragment(packet,seq,3,out),-1)
if __name__=='__main__':unittest.main()
