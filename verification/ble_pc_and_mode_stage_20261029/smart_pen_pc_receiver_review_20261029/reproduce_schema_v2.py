"""Same ignored-insert trigger as V1, now expecting refusal before client creation."""
from pathlib import Path
import os,sys,asyncio,tempfile,sqlite3,json
HERE=Path(__file__).resolve().parent;SRC=Path(os.environ.get('PC_SOURCE',str(HERE/'source_v2'))).resolve();sys.dont_write_bytecode=True;sys.path[:0]=[str(SRC),str(SRC/'tests')]
from pen_receiver.journal import Journal,JournalError
from pen_receiver.receiver import receive
from test_receiver import B,yes
async def main():
 with tempfile.TemporaryDirectory() as t:
  p=Path(t)
  with Journal(p,B,create=True):pass
  db=sqlite3.connect(p/'records.sqlite3');db.execute('CREATE TRIGGER drop_record BEFORE INSERT ON records BEGIN SELECT RAISE(IGNORE); END');db.commit();db.close()
  before=(p/'records.sqlite3').read_bytes(); clients=[]
  def factory(*a,**k):clients.append(1);raise AssertionError('must not construct client')
  try:await receive(p,B,radio_authorized=True,os_pairing_authorized=True,confirm_local_approval=yes,client_factory=factory)
  except JournalError as e:reason=str(e)
  else:raise AssertionError('malformed schema accepted')
  db=sqlite3.connect(p/'records.sqlite3');rows=db.execute('SELECT count(*) FROM records').fetchone()[0];db.close()
  assert not clients and rows==0 and before==(p/'records.sqlite3').read_bytes()
  print(json.dumps(dict(rejected=reason,clients=0,ACK_writes=0,durable_rows=rows,file_unchanged=True,radio='none')))
asyncio.run(main())
