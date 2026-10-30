"""Real upstream API test; requires DIGITAL_PEN_SOURCE path and PC dependencies."""
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'software'))
source=os.environ.get('DIGITAL_PEN_SOURCE')
if source:sys.path.insert(0,source)
from pen_bridge import Packet,Journal
from upstream_web import build_app
@unittest.skipUnless(source and importlib.util.find_spec('cv2'),'set DIGITAL_PEN_SOURCE and install upstream PC dependencies')
class UpstreamTests(unittest.TestCase):
 def test_actual_rest_websocket_export(self):
  from fastapi.testclient import TestClient
  with tempfile.TemporaryDirectory() as t:
   db=Path(t)/'pen.sqlite'
   with Journal(db) as j:
    for seq,flags,page in [(0,3,1),(1,3,1),(2,0,1),(3,3,2),(4,3,2),(5,0,2),(6,3,1)]:
     j.accept(Packet(flags,42,123,seq,seq*10000,page,seq*1000,2000,900).encode())
   app=build_app(db,42,123,1)
   with TestClient(app) as client:
    data=client.get('/api/session').json()
    self.assertEqual(len(data['strokes']),2)
    self.assertEqual(data['strokes'][0]['points'],[[0.0,2.0],[1.0,2.0]])
    self.assertEqual(data['strokes'][1]['points'],[[6.0,2.0]])
    self.assertEqual(client.get('/api/pen/provenance').json()['page'],1)
    self.assertEqual(client.get('/api/export.svg').status_code,200)
    with client.websocket_connect('/ws') as ws:
     hello=ws.receive_json();self.assertEqual(hello['type'],'hello');self.assertEqual(len(hello['session']['strokes']),2)
     self.assertEqual(client.post('/api/session/undo').status_code,200)
     self.assertEqual(ws.receive_json()['type'],'undo')
if __name__=='__main__':unittest.main()
