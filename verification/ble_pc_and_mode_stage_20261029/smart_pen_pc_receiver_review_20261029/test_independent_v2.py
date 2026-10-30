"""Independent adversarial cases. Only temporary DBs and MockClient; no radio."""
from pathlib import Path
import sys,os,asyncio,threading,tempfile,sqlite3,dataclasses,unittest
from contextlib import suppress
HERE=Path(__file__).resolve().parent;SRC=Path(os.environ.get('PC_SOURCE',str(HERE/'source_v2'))).resolve();sys.dont_write_bytecode=True;sys.path[:0]=[str(SRC),str(SRC/'tests')]
from pen_receiver.journal import Journal,JournalError,Binding
from pen_receiver.receiver import receive
from pen_receiver.events import record_events
from pen_receiver.protocol import fragments,Reassembler
from test_receiver import MockClient,B,R,yes

class Independent(unittest.IsolatedAsyncioTestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name);self.clients=[]
 def tearDown(self):self.tmp.cleanup()
 async def run_receiver(self,script,**kw):
  def factory(*a,**kwargs):
   c=MockClient(*a,**kwargs);c.script=script;self.clients.append(c);return c
  args=dict(radio_authorized=True,os_pairing_authorized=True,confirm_local_approval=yes,client_factory=factory,create=True);args.update(kw)
  await asyncio.wait_for(receive(self.path,B,**args),5)
 async def send_wait(self,c):
  for f in fragments(R.encode()):c.send(f)
  await c.ack_event.wait();c.drop()
 async def test_trigger_before_open_no_radio_or_ack(self):
  with Journal(self.path,B,create=True):pass
  db=sqlite3.connect(self.path/'records.sqlite3');db.execute('CREATE TRIGGER swallow BEFORE INSERT ON records BEGIN SELECT RAISE(IGNORE); END');db.commit();db.close();before=(self.path/'records.sqlite3').read_bytes()
  with self.assertRaises(JournalError):await self.run_receiver(self.send_wait)
  self.assertFalse(self.clients);self.assertEqual(before,(self.path/'records.sqlite3').read_bytes())
 async def test_trigger_added_after_open_no_ack(self):
  async def script(c):
   db=sqlite3.connect(self.path/'records.sqlite3');db.execute('CREATE TRIGGER swallow BEFORE INSERT ON records BEGIN SELECT RAISE(IGNORE); END');db.commit();db.close()
   for f in fragments(R.encode()):c.send(f)
  with self.assertRaises(JournalError):await self.run_receiver(script)
  self.assertEqual(self.clients[0].writes,[])
 async def test_post_commit_row_disappears_no_ack(self):
  class Proxy:
   def __init__(self,db):self.db=db
   def __getattr__(self,k):return getattr(self.db,k)
   def execute(self,sql,*a):
    result=self.db.execute(sql,*a)
    if sql=='COMMIT':self.db.execute('DELETE FROM main.records')
    return result
  class LostRowJournal(Journal):
   def accept(self,raw):self.db=Proxy(self.db);return super().accept(raw)
  with self.assertRaises(JournalError):await self.run_receiver(self.send_wait,journal_factory=LostRowJournal)
  self.assertEqual(self.clients[0].writes,[])
 async def test_post_commit_read_error_preserves_and_no_ack(self):
  class Proxy:
   def __init__(self,db):self.db=db;self.committed=False
   def __getattr__(self,k):return getattr(self.db,k)
   def execute(self,sql,*a):
    if self.committed and sql.startswith('SELECT device,session,seq,raw,typeof'):raise sqlite3.OperationalError('postcommit read fault')
    result=self.db.execute(sql,*a)
    if sql=='COMMIT':self.committed=True
    return result
  class FailReadJournal(Journal):
   def accept(self,raw):self.db=Proxy(self.db);return super().accept(raw)
  with self.assertRaises(sqlite3.OperationalError):await self.run_receiver(self.send_wait,journal_factory=FailReadJournal)
  self.assertEqual(self.clients[0].writes,[])
  with Journal(self.path,B) as j:self.assertEqual(list(j.replay(R.session)),[R])
 async def test_repeated_cancel_waits_worker(self):
  started,release,finished=threading.Event(),threading.Event(),threading.Event();closed_early=[]
  class Slow(Journal):
   def accept(self,raw):
    started.set()
    if not release.wait(3):raise RuntimeError('test timeout')
    try:return super().accept(raw)
    finally:finished.set()
   def close(self):
    if started.is_set() and not finished.is_set():closed_early.append(True)
    super().close()
  task=asyncio.create_task(self.run_receiver(self.send_wait,journal_factory=Slow))
  self.assertTrue(await asyncio.to_thread(started.wait,2))
  for _ in range(3):task.cancel();await asyncio.sleep(.005)
  self.assertFalse(finished.is_set());self.assertFalse(closed_early);release.set()
  with self.assertRaises(asyncio.CancelledError):await task
  self.assertFalse(closed_early);self.assertEqual(self.clients[0].writes,[])
  with Journal(self.path,B) as j:self.assertEqual(list(j.replay(R.session)),[R])
 async def test_overflow_during_commit_no_ack(self):
  started,release=threading.Event(),threading.Event()
  class Slow(Journal):
   def accept(self,raw):
    started.set()
    if not release.wait(3):raise RuntimeError('test timeout')
    return super().accept(raw)
  async def script(c):
   for f in fragments(R.encode()):c.send(f)
   await asyncio.to_thread(started.wait,2)
   for _ in range(4):c.send(fragments(R.encode())[0])
   release.set()
  with self.assertRaises(RuntimeError):await self.run_receiver(script,journal_factory=Slow,queue_size=3)
  self.assertEqual(self.clients[0].writes,[])
  with Journal(self.path,B) as j:self.assertEqual(list(j.replay(R.session)),[R])
 async def test_two_targets_same_label_export_distinct(self):
  events=[]
  for name,target in [('a','target-A'),('b','target-B')]:
   p=self.path/name;p.mkdir(mode=0o700)
   with Journal(p,Binding('same-label',target,R.device),create=True) as j:
    j.accept(R.encode());events.append(list(record_events(j.replay(R.session),j.metadata)))
  self.assertNotEqual(events[0][0]['source_namespace'],events[1][0]['source_namespace'])
  for rows in events:
   self.assertTrue(all(e['UI_allowed'] is False and e['coordinate'] is None for e in rows))
   self.assertEqual(len({e['source_namespace'] for e in rows}),1)
 def test_reverse_between_second_and_third_fragment(self):
  f=fragments(R.encode());a=Reassembler();a.accept(f[0],10);a.accept(f[1],11)
  with self.assertRaises(ValueError):a.accept(f[2],10.5)
 def test_clock_nonfinite_and_reset_high_water(self):
  f=fragments(R.encode())
  for now in [float('nan'),float('inf'),-float('inf'),9]:
   with self.subTest(now=now):
    a=Reassembler();a.accept(f[0],10);a.reset()
    with self.assertRaises(ValueError):a.accept(f[0],now)
if __name__=='__main__':unittest.main(verbosity=2)
