import asyncio
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'software'))
from pen_bridge import Packet,Journal
from ble_transport import fragment,decode_ack
from windows_ble import receive
class WindowsBleTests(unittest.TestCase):
 def test_mock_radio_ack_after_durable_commit(self):
  with tempfile.TemporaryDirectory() as t:
   db=Path(t)/'pen.sqlite';p=Packet(4,0x42454e43,123,0,100,0xffffffff,0,0,0)
   seen=[]
   class Client:
    def __init__(self,address,**kw):
     self.disconnect=kw['disconnected_callback'];self.is_connected=True
     assert address=='explicit-approved-address' and kw['pair'] is True
    async def __aenter__(self):return self
    async def __aexit__(self,*args):self.is_connected=False
    async def read_gatt_char(self,_):return b'SYNTHETIC BENCH ONLY'
    async def start_notify(self,_,cb):
     # A missing first fragment must never be ACKed.
     cb(None,fragment(p.encode(),0)[1])
     for f in fragment(p.encode(),0):cb(None,f)
    async def write_gatt_char(self,_,raw,response):
     assert response is True
     # Independent connection observes committed bytes before ACK write.
     with Journal(db) as j:
      assert j.ack(p.device,p.session)==0
      assert list(j.replay(p.device,p.session))==[p]
     seen.append(decode_ack(raw));self.disconnect(self)
    async def stop_notify(self,_):pass
   asyncio.run(receive('explicit-approved-address',p.device,db,True,Client))
   self.assertEqual(seen,[(123,0)])
 def test_synthetic_optin_required(self):
  with self.assertRaises(ValueError):asyncio.run(receive('a',42,'unused',False))
if __name__=='__main__':unittest.main()
