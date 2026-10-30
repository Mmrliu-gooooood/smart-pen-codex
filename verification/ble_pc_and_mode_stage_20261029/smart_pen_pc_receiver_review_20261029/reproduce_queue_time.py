"""Real asyncio/worker queue test with synthetic radio callbacks, no device."""
from pathlib import Path
import os
import sys,tempfile,asyncio,threading,time,dataclasses,json
HERE=Path(__file__).resolve().parent;SRC=Path(os.environ.get('PC_SOURCE',str(HERE/'source'))).resolve();sys.dont_write_bytecode=True;sys.path[:0]=[str(SRC),str(SRC/'tests')]
from pen_receiver.journal import Journal
from pen_receiver.receiver import receive
from pen_receiver.protocol import fragments
from test_receiver import MockClient,B,R,yes
async def main():
 started,release=threading.Event(),threading.Event();holder=[];span=[]
 class SlowJournal(Journal):
  def accept(self,raw):
   if not started.is_set():
    started.set()
    if not release.wait(5):raise RuntimeError('test timeout')
   return super().accept(raw)
 async def script(c):
  for f in fragments(R.encode()):c.send(f)
  await asyncio.to_thread(started.wait,2)
  f=fragments(dataclasses.replace(R,seq=1,timestamp_us=20).encode());t=time.monotonic();c.send(f[0]);await asyncio.sleep(2.1)
  c.send(f[1]);c.send(f[2]);span.append(time.monotonic()-t);release.set()
  await asyncio.sleep(.3);c.drop()
 def factory(*a,**kw):
  c=MockClient(*a,**kw);c.script=script;holder.append(c);return c
 with tempfile.TemporaryDirectory() as tmp:
  await asyncio.wait_for(receive(Path(tmp),B,radio_authorized=True,os_pairing_authorized=True,confirm_local_approval=yes,client_factory=factory,create=True,journal_factory=SlowJournal),6)
  print(json.dumps({'second_record_fragment_span_s':span[0],'ACK_count':len(holder[0].writes),'timeout_s':2,'radio':'mock only'}))
asyncio.run(main())
