import dataclasses
import json
import subprocess
import sys
import unittest
from pen_receiver.events import record_events
from pen_receiver.protocol import Record
from pen_receiver.identity import source_namespace

BINDING={"peer_scope":"one", "target":"test", "device":42}
METADATA={"binding":BINDING,"source_namespace":source_namespace(BINDING)}


class EventCliTests(unittest.TestCase):
    def test_no_sensor_valid_never_a_formal_point(self):
        r=Record(7,42,2**64-1,0,2**64-1,8,123,456,1000)
        seq=[r,dataclasses.replace(r,seq=2,timestamp_us=1),
             dataclasses.replace(r,seq=3,timestamp_us=2,flags=0,page=0,x_um=0,y_um=0)]
        events=list(record_events(seq,METADATA))
        self.assertEqual([x['type'] for x in events],['BEGIN','DIAGNOSTIC','END','BEGIN','DIAGNOSTIC','END','DIAGNOSTIC'])
        self.assertTrue(all(x['UI_allowed'] is False and x['coordinate'] is None for x in events))
        d=events[1]
        self.assertEqual(d['flags'],7);self.assertTrue(d['wire_VALID'])
        self.assertFalse(d['calibrated_physical_tip_VALID'])
        self.assertEqual(json.loads(json.dumps(d))['timestamp_us'],str(2**64-1))
        self.assertEqual(list(record_events([],METADATA)),[])

    def test_default_and_incomplete_connect_no_radio(self):
        p=subprocess.run([sys.executable,'-m','pen_receiver'],capture_output=True,text=True)
        self.assertEqual(p.returncode,0);self.assertIn('no radio',p.stdout)
        p=subprocess.run([sys.executable,'-m','pen_receiver','connect','--state-dir','/nonexistent',
                          '--target','AA:BB:CC:DD:EE:FF','--peer-scope','one','--device','42'],capture_output=True,text=True)
        self.assertEqual(p.returncode,2);self.assertIn('no radio started',p.stderr)
