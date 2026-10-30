import importlib.util
from pathlib import Path
import math
import unittest
spec=importlib.util.spec_from_file_location('calibration',Path(__file__).parents[1]/'tools/calibration_geometry.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
I=[[1,0,0],[0,1,0],[0,0,1]]
class CalibrationGeometry(unittest.TestCase):
 def test_front(self):self.assertEqual(m.nib_on_paper(I,[-10,-20,8],[2,3,8],contact=True),(12,23,0))
 def test_tilted(self):
  a=math.radians(50);c,s=math.cos(a),math.sin(a);R=[[c,0,s],[0,1,0],[-s,0,c]]
  true=[2,3,0];t=[-1,1,10];q=[sum(R[i][j]*true[j] for j in range(3))+t[i] for i in range(3)]
  got=m.nib_on_paper(R,t,q,contact=True)
  for x,y in zip(got,true):self.assertAlmostEqual(x,y)
 def test_no_contact(self):
  with self.assertRaises(ValueError):m.nib_on_paper(I,[0,0,8],[0,0,8],contact=False)
 def test_plane_error(self):
  with self.assertRaises(ValueError):m.nib_on_paper(I,[0,0,8],[0,0,9],contact=True)
 def test_reflection(self):
  with self.assertRaises(ValueError):m.nib_on_paper([[-1,0,0],[0,1,0],[0,0,1]],[0,0,8],[0,0,8],contact=True)
 def test_scale_not_rotation(self):
  with self.assertRaises(ValueError):m.nib_on_paper([[2,0,0],[0,1,0],[0,0,1]],[0,0,8],[0,0,8],contact=True)
 def test_nan(self):
  with self.assertRaises(ValueError):m.nib_on_paper(I,[0,0,8],[0,float('nan'),8],contact=True)
 def test_negative_depth(self):
  with self.assertRaises(ValueError):m.nib_on_paper(I,[0,0,-8],[0,0,-8],contact=True)
if __name__=='__main__':unittest.main()
