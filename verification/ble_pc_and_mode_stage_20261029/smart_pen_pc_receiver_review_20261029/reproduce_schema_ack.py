"""Offline adversarial database fixture; no BLE import/device connection."""
from pathlib import Path
import os
import sys,tempfile,sqlite3,asyncio,json
HERE=Path(__file__).resolve().parent;SRC=Path(os.environ.get('PC_SOURCE',str(HERE/'source'))).resolve();sys.dont_write_bytecode=True
sys.path[:0]=[str(SRC),str(SRC/'tests')]
from pen_receiver.journal import Journal
from pen_receiver.receiver import receive
from pen_receiver.protocol import fragments
from test_receiver import MockClient,B,R,yes
async def main():
 with tempfile.TemporaryDirectory() as tmp:
  p=Path(tmp)
  with Journal(p,B,create=True):pass
  db=sqlite3.connect(p/'records.sqlite3');db.execute('CREATE TRIGGER drop_record BEFORE INSERT ON records BEGIN SELECT RAISE(IGNORE); END');db.commit();db.close()
  holder=[]
  async def script(c):
   for f in fragments(R.encode()):c.send(f)
   await c.ack_event.wait();c.drop()
  def factory(*a,**kw):
   c=MockClient(*a,**kw);c.script=script;holder.append(c);return c
  await asyncio.wait_for(receive(p,B,radio_authorized=True,os_pairing_authorized=True,confirm_local_approval=yes,client_factory=factory),3)
  db=sqlite3.connect(p/'records.sqlite3');count=db.execute('SELECT count(*) FROM records').fetchone()[0];db.close()
  print(json.dumps({'ACK_writes':len(holder[0].writes),'durable_rows':count,'radio':'mock only'}))
asyncio.run(main())
