"""Multiple independently encoded overlapping windows must agree."""
import ctypes as C
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from roi_fixture import Render, render
from test_roi_vision import Config, Result
ROOT=Path(__file__).resolve().parents[1]
class Consensus(unittest.TestCase):
 def test_overlapping_windows(self):
  v=json.loads((ROOT/'tests/fixtures/roi_seven.json').read_text())
  with tempfile.TemporaryDirectory() as tmp:
   so=Path(tmp)/'roi.so'
   subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-pedantic','-shared','-fPIC',str(ROOT/'firmware/vision/roi.c'),str(ROOT/'firmware/codec/anoto.c'),'-lm','-o',str(so)],check=True)
   lib=C.CDLL(str(so));decode=lib.pen_roi_decode
   decode.argtypes=[C.POINTER(C.c_uint8),C.c_size_t,C.c_uint,C.c_uint,C.c_uint,C.POINTER(Config),C.POINTER(Result)]
   for angle in (-9,0,13):
    spec=Render(columns=7,pitch=18,angle=angle,noise=10,tx=42.3,ty=30.2,width=220,height=220)
    pixels=render(v['directions'],spec);arr=(C.c_uint8*len(pixels)).from_buffer_copy(pixels)
    out=Result();cfg=Config(710,1000,*v['section'])
    self.assertEqual(decode(arr,len(pixels),spec.width,spec.height,spec.width,C.byref(cfg),C.byref(out)),0)
    self.assertEqual([out.x,out.y],v['xy']);self.assertEqual(out.dots,49);self.assertEqual(out.windows,4)
