"""Frozen vectors generated with source HEAD 0f8b569 py-microdots a4_fixed.
128 canonical windows across four sections; 710x1000 grid incl. edges.
Not optical images, pose accuracy, missing-dot or rotated-image tests.
"""
import ctypes
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]
class Codec(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp = tempfile.TemporaryDirectory()
  lib = Path(cls.tmp.name)/'codec.so'
  subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-pedantic','-shared','-fPIC',str(ROOT/'firmware/codec/anoto.c'),'-o',str(lib)],check=True)
  cls.decode = ctypes.CDLL(str(lib)).pen_anoto_decode
  cls.decode.argtypes = [ctypes.POINTER(ctypes.c_uint8),ctypes.c_uint16,ctypes.c_uint16,ctypes.c_uint8,ctypes.c_uint8,ctypes.POINTER(ctypes.c_uint16),ctypes.POINTER(ctypes.c_uint16)]
 @classmethod
 def tearDownClass(cls): cls.tmp.cleanup()
 def test_reference(self):
  for v in json.loads((ROOT/'tests/fixtures/microdots_vectors.json').read_text()):
   d=(ctypes.c_uint8*36)(*v['directions']);x=ctypes.c_uint16(65535);y=ctypes.c_uint16(65535)
   self.assertEqual(self.decode(d,710,1000,*v['section'],ctypes.byref(x),ctypes.byref(y)),0)
   self.assertEqual([x.value,y.value],v['xy'])
   self.assertEqual(self.decode(d,710,1000,(v['section'][0]+1)%63,v['section'][1],ctypes.byref(x),ctypes.byref(y)),-1)
 def test_fail_closed(self):
  d=(ctypes.c_uint8*36)(*[4]*36);x=ctypes.c_uint16(999);y=ctypes.c_uint16(888)
  for w,h in [(710,1000),(5,1000),(4097,1000)]:
   self.assertEqual(self.decode(d,w,h,0,0,ctypes.byref(x),ctypes.byref(y)),-1)
   self.assertEqual((x.value,y.value),(999,888))
if __name__=='__main__': unittest.main()
