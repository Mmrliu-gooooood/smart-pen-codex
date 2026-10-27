"""Synthetic canonical-grid plumbing test, NOT real camera validation."""
import ctypes
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
class Synthetic(unittest.TestCase):
 def test_image_to_coordinate(self):
  with tempfile.TemporaryDirectory() as t:
   so=Path(t)/'vision.so'
   subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-pedantic','-shared','-fPIC',str(ROOT/'firmware/vision/canonical.c'),str(ROOT/'firmware/codec/anoto.c'),'-o',str(so)],check=True)
   lib=ctypes.CDLL(str(so));p=12;w=p*6
   for v in json.loads((ROOT/'tests/fixtures/microdots_vectors.json').read_text())[::8]:
    image=[255]*(w*w)
    for i,d in enumerate(v['directions']):
     dx,dy=[(0,-3),(-3,0),(3,0),(0,3)][d];cx=i%6*p+p//2+dx;cy=i//6*p+p//2+dy
     for x,y in [(0,0),(1,0),(-1,0),(0,1),(0,-1)]:image[(cy+y)*w+cx+x]=0
    img=(ctypes.c_uint8*len(image))(*image);out=(ctypes.c_uint8*36)()
    self.assertEqual(lib.pen_canonical_directions(img,p,out),0);self.assertEqual(list(out),v['directions'])
    x=ctypes.c_uint16();y=ctypes.c_uint16()
    self.assertEqual(lib.pen_anoto_decode(out,710,1000,*v['section'],ctypes.byref(x),ctypes.byref(y)),0);self.assertEqual([x.value,y.value],v['xy'])
   for color in [0,255]:
    img=(ctypes.c_uint8*(w*w))(*([color]*(w*w)));self.assertEqual(lib.pen_canonical_directions(img,p,out),-1)
if __name__=='__main__':unittest.main()
