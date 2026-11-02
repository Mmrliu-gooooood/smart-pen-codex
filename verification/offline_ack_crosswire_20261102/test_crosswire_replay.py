"""Model-only actual C storage ↔ SP/BLE wire ↔ SQLite durable host regression.
No Bluetooth radio, board provider, or production adapter is implemented here.
"""
import ctypes as C
import hashlib
import json
import pathlib
import sqlite3
import subprocess
import sys
import tempfile
import unittest
ROOT=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'source/software'))
from pen_bridge import Packet, Journal
from ble_transport import Reassembler, fragment, encode_ack, decode_ack
DEVICE=42
SESSION=2**64-1

def packet(seq=0,session=SESSION,device=DEVICE,x=123):
 return Packet(3,device,session,seq,seq*10000,1,x,-456,900)

def exact_ack_after_commit(journal,raw,approved_device):
 """Executable proposed adapter contract, TEST ONLY, not product wiring.
 Reject wrong device before insert; return an exact offered-sequence ACK only
 after FULL commit establishes a contiguous frontier at/above that sequence.
 Radio authentication/connection epoch must additionally be enforced by provider.
 """
 p=Packet.decode(raw)
 if p.device!=approved_device:raise ValueError('unapproved device')
 through=journal.accept(raw)
 if through is None or through<p.seq:return None
 return encode_ack(p.session,p.seq)

class CrosswireTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.build=tempfile.TemporaryDirectory();lib=pathlib.Path(cls.build.name)/'fixture.so'
  subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-pedantic','-shared','-fPIC',
   '-I'+str(ROOT/'source/firmware/portable'),'-I'+str(ROOT/'source/firmware/storage'),
   str(ROOT/'source/firmware/portable/pen.c'),str(ROOT/'source/firmware/storage/store.c'),
   str(ROOT/'flash_fixture.c'),'-o',str(lib)],check=True)
  cls.c=C.CDLL(str(lib))
  cls.c.fixture_boot.argtypes=cls.c.fixture_reset.argtypes=[C.c_uint32]
  cls.c.fixture_begin.argtypes=[C.c_uint64]
  cls.c.fixture_append.argtypes=cls.c.fixture_offer.argtypes=[C.POINTER(C.c_uint8)]
  cls.c.fixture_ack.argtypes=[C.c_uint64,C.c_uint32,C.c_int]
  cls.c.fixture_cut.argtypes=[C.c_int,C.c_int]
  cls.c.fixture_reclaim.argtypes=[C.c_int]
  cls.c.fixture_used.restype=C.c_size_t
  cls.c.fixture_image.argtypes=[C.POINTER(C.c_uint8)]
 @classmethod
 def tearDownClass(cls):cls.build.cleanup()
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.db=pathlib.Path(self.tmp.name)/'host.sqlite'
  self.assertEqual(self.c.fixture_reset(DEVICE),0)
 def tearDown(self):self.tmp.cleanup()
 def seed(self,count=3):
  self.assertEqual(self.c.fixture_begin(SESSION),0)
  for seq in range(count):
   raw=packet(seq).encode();self.assertEqual(self.c.fixture_append((C.c_uint8*48).from_buffer_copy(raw)),0)
  self.c.fixture_stop()
 def offer(self):
  raw=(C.c_uint8*48)();status=self.c.fixture_offer(raw)
  self.assertIn(status,[0,1]);return bytes(raw) if status==0 else None
 def ack(self,raw,auth=1):
  session,seq=decode_ack(raw);return self.c.fixture_ack(session,seq,auth)
 def image(self):
  out=(C.c_uint8*1024)();self.c.fixture_image(out);return bytes(out)
 def assert_pending_not_reclaimable(self):
  before=self.image();self.assertEqual(self.c.fixture_reclaim(1),-3)
  self.assertEqual(self.image(),before);self.assertEqual(self.c.fixture_erases(),0)
 def test_radio_fragments_host_commit_exact_ack_and_reclaim(self):
  self.seed()
  with Journal(self.db) as j:
   for seq in range(3):
    raw=self.offer();r=Reassembler();out=None
    for i,f in enumerate(fragment(raw,seq&65535)):out=r.accept(f,i*.01)
    self.assertEqual(out,raw)
    a=exact_ack_after_commit(j,out,DEVICE)
    with sqlite3.connect(self.db) as observer:
     self.assertEqual(observer.execute('SELECT through_seq FROM frontiers').fetchone()[0],seq)
    self.assertEqual(self.ack(a),0)
   self.assertIsNone(self.offer())
  self.assertEqual(self.c.fixture_reclaim(0),-3)
  self.assertEqual(self.c.fixture_reclaim(1),0);self.assertEqual(self.c.fixture_used(),0)
  with Journal(self.db) as j:self.assertEqual(list(j.replay(DEVICE,SESSION)),[packet(i) for i in range(3)])
 def test_host_commit_then_disconnect_reboot_replays_without_duplicate_rows(self):
  self.seed()
  with Journal(self.db) as j:exact_ack_after_commit(j,self.offer(),DEVICE) # lost ACK
  self.assertEqual(self.c.fixture_boot(DEVICE),0);self.assert_pending_not_reclaimable()
  with Journal(self.db) as j:
   raw=self.offer();self.assertEqual(Packet.decode(raw).seq,0)
   self.assertEqual(self.ack(exact_ack_after_commit(j,raw,DEVICE)),0)
   self.assertEqual(j.db.execute('SELECT COUNT(*) FROM packets').fetchone()[0],1)
   self.assertEqual(Packet.decode(self.offer()).seq,1)
 def test_host_process_exit_after_full_commit_before_ack(self):
  self.seed(1);raw=self.offer()
  code="from pen_bridge import Journal; import os,sys; j=Journal(sys.argv[1]); j.accept(bytes.fromhex(sys.argv[2])); os._exit(73)"
  import os
  env=dict(os.environ);env['PYTHONPATH']=str(ROOT/'source/software')
  child=subprocess.run([sys.executable,'-c',code,str(self.db),raw.hex()],env=env,check=False)
  self.assertEqual(child.returncode,73)
  self.assertEqual(self.c.fixture_boot(DEVICE),0);self.assert_pending_not_reclaimable()
  with Journal(self.db) as j:
   self.assertEqual(list(j.replay(DEVICE,SESSION)),[packet()])
   self.assertEqual(self.ack(exact_ack_after_commit(j,self.offer(),DEVICE)),0)
   self.assertEqual(j.db.execute('SELECT COUNT(*) FROM packets').fetchone()[0],1)
  self.assertIsNone(self.offer())
 def test_host_commit_exception_rolls_back_row_and_frontier(self):
  self.seed(1);raw=self.offer()
  class FailedCommit:
   def __init__(self,db):self.db=db
   def __getattr__(self,name):return getattr(self.db,name)
   def commit(self):raise sqlite3.OperationalError('injected commit failure')
  with Journal(self.db) as j:
   original=j.db;j.db=FailedCommit(original)
   with self.assertRaises(sqlite3.OperationalError):exact_ack_after_commit(j,raw,DEVICE)
   j.db=original
   self.assertEqual(j.db.execute('SELECT COUNT(*) FROM packets').fetchone()[0],0)
   self.assertEqual(j.db.execute('SELECT COUNT(*) FROM frontiers').fetchone()[0],0)
  with Journal(self.db) as j:self.assertIsNone(j.ack(DEVICE,SESSION))
  self.assert_pending_not_reclaimable()
 def test_cumulative_frontier_is_not_an_exact_ack(self):
  self.seed()
  with Journal(self.db) as j:
   for i in range(3):j.accept(packet(i).encode())
   raw=self.offer();self.assertEqual(j.accept(raw),2)
   # Naive cumulative host response is correctly rejected by current C store.
   before=self.image();self.assertEqual(self.ack(encode_ack(SESSION,2)),-3)
   self.assertEqual(self.image(),before)
   for seq in range(3):
    raw=self.offer();a=exact_ack_after_commit(j,raw,DEVICE)
    self.assertEqual(decode_ack(a),(SESSION,seq));self.assertEqual(self.ack(a),0)
   self.assertIsNone(self.offer());self.assertEqual(self.c.fixture_reclaim(1),0)
 def test_every_ack_program_cut_replays_durable_host_record(self):
  for cut in range(12):
   with self.subTest(cut=cut):
    self.assertEqual(self.c.fixture_reset(DEVICE),0);self.seed(1)
    with Journal(self.db) as j:a=exact_ack_after_commit(j,self.offer(),DEVICE)
    self.c.fixture_cut(cut,-1);self.assertEqual(self.ack(a),-1)
    self.assertEqual(self.c.fixture_erases(),0);self.assertEqual(self.c.fixture_boot(DEVICE),0)
    self.assert_pending_not_reclaimable()
    with Journal(self.db) as j:
     self.assertEqual(self.ack(exact_ack_after_commit(j,self.offer(),DEVICE)),0)
     self.assertEqual(j.db.execute('SELECT COUNT(*) FROM packets').fetchone()[0],1)
    self.assertIsNone(self.offer());self.assertEqual(self.c.fixture_reclaim(1),0)
 def test_ack_sync_failure_never_erases_unstored_host_data(self):
  for syncs in (0,1):
   with self.subTest(syncs=syncs):
    self.assertEqual(self.c.fixture_reset(DEVICE),0);self.seed(1)
    with Journal(self.db) as j:a=exact_ack_after_commit(j,self.offer(),DEVICE)
    self.c.fixture_cut(-1,syncs);self.assertEqual(self.ack(a),-1)
    self.assertEqual(self.c.fixture_erases(),0);self.assertEqual(self.c.fixture_boot(DEVICE),0)
    raw=self.offer()
    # Model programs immediately: failure after final ACK! may already persist.
    self.assertEqual(raw is None,syncs==1)
    with Journal(self.db) as j:
     self.assertEqual(list(j.replay(DEVICE,SESSION)),[packet()])
     if raw is not None:self.assertEqual(self.ack(exact_ack_after_commit(j,raw,DEVICE)),0)
    self.assertEqual(self.c.fixture_reclaim(1),0)
 def test_host_write_failure_produces_no_ack_and_no_reclaim(self):
  self.seed(1);raw=self.offer();before=self.image()
  with Journal(self.db) as j:
   j.db.execute('PRAGMA query_only=ON')
   with self.assertRaises(sqlite3.OperationalError):exact_ack_after_commit(j,raw,DEVICE)
   self.assertIsNone(j.ack(DEVICE,SESSION));self.assertEqual(list(j.replay(DEVICE,SESSION)),[])
  self.assertEqual(self.image(),before);self.assert_pending_not_reclaimable()
 def test_conflicting_duplicate_never_acknowledges_different_content(self):
  self.seed(1);raw=self.offer()
  with Journal(self.db) as j:
   j.accept(packet(x=999).encode())
   with self.assertRaises(ValueError):exact_ack_after_commit(j,raw,DEVICE)
   self.assertEqual(list(j.replay(DEVICE,SESSION)),[packet(x=999)])
  self.assert_pending_not_reclaimable()
 def test_wrong_device_rejected_before_host_commit(self):
  self.seed(1)
  with Journal(self.db) as j:
   with self.assertRaises(ValueError):exact_ack_after_commit(j,self.offer(),DEVICE+1)
   self.assertEqual(j.db.execute('SELECT COUNT(*) FROM packets').fetchone()[0],0)
  self.assert_pending_not_reclaimable()
 def test_wrong_session_auth_or_unoffered_ack_cannot_erase(self):
  self.seed(1);self.assertEqual(self.ack(encode_ack(SESSION,0)),-3)
  raw=self.offer()
  with Journal(self.db) as j:a=exact_ack_after_commit(j,raw,DEVICE)
  before=self.image()
  self.assertEqual(self.ack(a,auth=0),-3)
  self.assertEqual(self.ack(encode_ack(SESSION-1,0)),-3)
  self.assertEqual(self.image(),before);self.assert_pending_not_reclaimable()
 def test_host_gap_does_not_generate_ack_for_higher_sequence(self):
  with Journal(self.db) as j:
   self.assertIsNone(exact_ack_after_commit(j,packet(2).encode(),DEVICE))
   self.assertEqual(decode_ack(exact_ack_after_commit(j,packet(0).encode(),DEVICE)),(SESSION,0))
   self.assertEqual(decode_ack(exact_ack_after_commit(j,packet(1).encode(),DEVICE)),(SESSION,1))
   self.assertEqual(decode_ack(exact_ack_after_commit(j,packet(2).encode(),DEVICE)),(SESSION,2))

if __name__=='__main__':unittest.main(verbosity=2)
