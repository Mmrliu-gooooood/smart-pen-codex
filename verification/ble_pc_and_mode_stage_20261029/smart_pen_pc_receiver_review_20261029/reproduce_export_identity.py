"""Two separately bound local journals; no radio, same display label/device payload."""
from pathlib import Path
import os
import sys,tempfile,json
HERE=Path(__file__).resolve().parent;sys.dont_write_bytecode=True;sys.path.insert(0,os.environ.get('PC_SOURCE',str(HERE/'source')))
from pen_receiver.journal import Journal,Binding
from pen_receiver.protocol import Record
from pen_receiver.events import record_events
r=Record(3,42,1,0,10,9,123,456,900)
with tempfile.TemporaryDirectory() as t:
 outputs=[]
 for name,target in [('a','explicit-target-A'),('b','explicit-target-B')]:
  p=Path(t)/name;p.mkdir(mode=0o700)
  with Journal(p,Binding('same-local-label',target,42),create=True) as j:
   j.accept(r.encode());outputs.append(list(record_events(j.replay(1),j.metadata)))
 result={'distinct_journal_bindings':['explicit-target-A','explicit-target-B'],'export_events_identical':outputs[0]==outputs[1],'event_count_each':len(outputs[0]),'wire_VALID_still_blocked':all(x['UI_allowed'] is False and x['coordinate'] is None for rows in outputs for x in rows),'exported_keys':sorted(outputs[0][0]),'radio_executed':False}
 print(json.dumps(result,indent=2))
