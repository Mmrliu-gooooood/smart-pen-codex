import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'software'))
from pen_bridge import Packet
from ble_transport import Reassembler,fragment,encode_ack,decode_ack
class BleTests(unittest.TestCase):
 def setUp(self):self.p=Packet(3,42,123,0,100,1,10,-20,900);self.f=fragment(self.p.encode(),0)
 def test_roundtrip_and_ack(self):
  r=Reassembler();self.assertIsNone(r.accept(self.f[0],0));self.assertIsNone(r.accept(self.f[1],0.1));self.assertEqual(r.accept(self.f[2],0.2),self.p.encode());self.assertEqual(decode_ack(encode_ack(123,0)),(123,0))
 def test_loss_reorder_timeout_reconnect(self):
  for sequence in [[(0,0),(2,.1)],[(0,0),(1,3)],[(1,0)]]:
   r=Reassembler()
   with self.assertRaises(ValueError):
    for i,t in sequence:r.accept(self.f[i],t)
   for i in range(3):out=r.accept(self.f[i],4+i*.1)
   self.assertEqual(out,self.p.encode())
  r=Reassembler();r.accept(self.f[0],0);r.reset()
  with self.assertRaises(ValueError):r.accept(self.f[1],.1)
 def test_corrupt_and_transfer(self):
  for i in range(20):
   a=bytearray(encode_ack(123,0));a[i]^=1
   with self.assertRaises(ValueError):decode_ack(a)
  r=Reassembler()
  with self.assertRaises(ValueError):
   for f in fragment(self.p.encode(),1):r.accept(f)
if __name__=='__main__':unittest.main()
