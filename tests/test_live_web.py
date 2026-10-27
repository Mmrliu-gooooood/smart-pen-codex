"""Real original-web live journal integration; valid coordinates exist only in fixtures."""
import asyncio
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'software'))
source=os.environ.get('DIGITAL_PEN_SOURCE')
if source:sys.path.insert(0,source)
from pen_bridge import Journal,Packet
from upstream_web import build_app
@unittest.skipUnless(source and importlib.util.find_spec('cv2'),'requires explicit upstream source/dependencies')
class LiveTests(unittest.TestCase):
 def setUp(self):
  from fastapi.testclient import TestClient
  self.Client=TestClient;self.tmp=tempfile.TemporaryDirectory();self.db=Path(self.tmp.name)/'live.db'
  with Journal(self.db):pass
 def tearDown(self):self.tmp.cleanup()
 def app(self,**kw):return build_app(self.db,42,123,1,live=True,view_id='view1',poll_seconds=.01,idle_seconds=2,**kw)
 def put(self,seq,flags=3,page=1,session=123):
  with Journal(self.db) as j:j.accept(Packet(flags,42,session,seq,seq*10000,page,seq*1000,2000,900).encode())
 def wait_cursor(self,app,seq):
  until=time.monotonic()+3
  while app.state.pen_view.cursor<seq and time.monotonic()<until:time.sleep(.01)
  self.assertGreaterEqual(app.state.pen_view.cursor,seq)
 def test_live_order_undo_clear_restart_and_page(self):
  app=self.app()
  with self.Client(app) as c:
   self.assertTrue(c.get('/api/status').json()['running'])
   with c.websocket_connect('/ws') as ws:
    self.assertEqual(ws.receive_json()['type'],'hello');self.assertEqual(ws.receive_json()['strokes'],[])
    self.put(0);self.wait_cursor(app,0)
    self.assertEqual(ws.receive_json()['type'],'tip');opened=ws.receive_json();self.assertEqual(opened['type'],'open');self.assertEqual(len(opened['strokes'][0]),1)
    self.put(1);self.wait_cursor(app,1)
    self.assertEqual(ws.receive_json()['type'],'tip');self.assertEqual(len(ws.receive_json()['strokes'][0]),2)
    self.assertEqual(c.get('/api/session').json()['strokes'],[]) # no premature finalize
    self.put(2,flags=0);self.wait_cursor(app,2)
    self.assertEqual(ws.receive_json()['type'],'stroke');self.assertEqual(ws.receive_json()['type'],'tip');self.assertEqual(ws.receive_json()['strokes'],[])
    self.assertEqual(c.post('/api/session/undo').status_code,200)
    self.assertEqual(ws.receive_json()['type'],'undo');self.assertEqual(ws.receive_json()['strokes'],[])
    self.put(0);time.sleep(.04);self.assertEqual(c.get('/api/session').json()['strokes'],[])
   self.put(3,page=2);self.put(4,page=2);self.put(5,flags=0,page=2);self.wait_cursor(app,5)
   self.assertEqual(c.get('/api/session').json()['strokes'],[])
   self.put(6);self.put(7,flags=0);self.wait_cursor(app,7)
   self.assertEqual(len(c.get('/api/session').json()['strokes']),1)
   self.assertEqual(c.post('/api/session/clear').status_code,200)
   self.assertEqual(c.get('/api/session').json()['strokes'],[])
  # Process restart cannot re-add cleared or undone records.
  restarted=self.app()
  with self.Client(restarted) as c:
   time.sleep(.04);self.assertEqual(c.get('/api/session').json()['strokes'],[])
   self.assertEqual(restarted.state.pen_view.cursor,7)
   self.put(0,session=999);time.sleep(.04);self.assertEqual(c.get('/api/session').json()['strokes'],[])
   self.put(8);self.put(9,flags=0);self.wait_cursor(restarted,9)
   self.assertEqual(len(c.get('/api/session').json()['strokes']),1)
 def test_browser_reconnect_retains_open_process_restart_splits(self):
  app=self.app()
  with self.Client(app) as c:
   self.assertTrue(c.get('/api/status').json()['running'])
   with c.websocket_connect('/ws') as ws:
    ws.receive_json();ws.receive_json();self.put(0);self.wait_cursor(app,0)
    ws.receive_json();self.assertEqual(len(ws.receive_json()['strokes'][0]),1)
   with c.websocket_connect('/ws') as ws:
    self.assertEqual(ws.receive_json()['session']['strokes'],[])
    self.assertEqual(len(ws.receive_json()['strokes'][0]),1)
  restarted=self.app()
  with self.Client(restarted) as c:
   self.assertEqual(len(c.get('/api/session').json()['strokes']),1) # known restart loss
   self.put(1);self.put(2,flags=0);self.wait_cursor(restarted,2)
   self.assertEqual(len(c.get('/api/session').json()['strokes']),2)
 def test_finish_and_start_fence(self):
  app=self.app()
  with self.Client(app) as c:
   self.put(0);self.wait_cursor(app,0)
   self.assertEqual(c.post('/api/session/finish').status_code,200)
   data=c.get('/api/session').json();self.assertTrue(data['finished']);self.assertEqual(len(data['strokes']),1)
   self.put(1);self.wait_cursor(app,1)
   self.assertEqual(len(c.get('/api/session').json()['strokes']),1)
   self.assertEqual(c.post('/api/session/start',json={'mode':'free'}).status_code,200)
   self.assertEqual(c.get('/api/session').json()['strokes'],[])
   self.put(2);self.put(3,flags=0);self.wait_cursor(app,3)
   data=c.get('/api/session').json();self.assertEqual(len(data['strokes']),1);self.assertEqual(data['strokes'][0]['points'],[[2.0,2.0]])
 def test_view_lease_and_timeout_loss(self):
  from live_view import view_lease,LiveView
  from digital_pen.engine.session import WritingSession
  with view_lease(self.db,'exclusive'):
   with self.assertRaises(RuntimeError):
    with view_lease(self.db,'exclusive'):pass
  with view_lease(self.db,'exclusive'):pass
  session=WritingSession();session.start()
  view=LiveView(self.db,'timer',42,123,1,session,idle_seconds=.5)
  try:
   self.put(0);events=view.poll(now=10)
   self.assertFalse(any(e['type']=='stroke' for e in events))
   self.assertEqual(view.poll(now=10.4),[])
   events=view.poll(now=10.6)
   self.assertEqual([e['type'] for e in events],['stroke','open'])
   self.assertEqual(events[0]['boundary_reason'],'transport_timeout')
  finally:view.close()
 def test_invalid_bench_and_backpressure(self):
  app=self.app()
  with self.Client(app) as c:
   self.put(0,flags=4,page=0xffffffff);self.wait_cursor(app,0)
   self.assertEqual(c.get('/api/session').json()['strokes'],[])
   q=asyncio.Queue(maxsize=2);q.put_nowait({'type':'obsolete'});q.put_nowait({'type':'obsolete'})
   app.state.pen_service._offer(q,{'type':'stroke','id':999})
   self.assertEqual(q.get_nowait()['type'],'session');self.assertEqual(q.get_nowait()['type'],'open')
   self.assertEqual(q.qsize(),0)
if __name__=='__main__':unittest.main()
