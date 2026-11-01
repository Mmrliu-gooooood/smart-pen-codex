import unittest
from model import project
class GeometryTests(unittest.TestCase):
 def test_front_parallel(self):
  self.assertEqual(project(1,2,10,100,0),(10.0,20.0))
from model import jacobian
class JacobianTests(unittest.TestCase):
 def test_known_center_tilt(self):
  a,b,c,d=jacobian(0,0,10,100,60)
  self.assertAlmostEqual(a,10);self.assertEqual(b,0);self.assertEqual(c,0);self.assertAlmostEqual(d,5)
 def test_behind_camera_rejected(self):
  with self.assertRaises(ValueError):project(0,-20,10,100,90)
from model import screen
class ScreenTests(unittest.TestCase):
 def test_front_parallel_feasible_sampling(self):
  r=screen(.5,.2,1/6,10,400,0)
  self.assertEqual(r['spacing_x_min_px'],20)
  self.assertAlmostEqual(r['window_width_px'],110.6666666667)
  self.assertEqual(r['screen_reasons'],[])
 def test_too_small_sampling(self):
  self.assertIn('cold_pitch_x',screen(.1,.2,1/6,40,250,0)['screen_reasons'])
 def test_merging_dots(self):
  self.assertIn('worst_case_ink_overlap',screen(.5,.5,.3,10,400,0)['screen_reasons'])
 def test_window_outside(self):
  self.assertIn('roi_window_envelope',screen(3,.2,1/6,5,1000,0)['screen_reasons'])
 def test_delta_unsupported(self):
  self.assertIn('displacement_contract',screen(.5,.2,.35,10,400,0)['screen_reasons'])
class CropTests(unittest.TestCase):
 def test_same_sampling_different_crop(self):
  active=screen(.6,.2,1/6,20,500,0,roi_px=256)
  archived=screen(.6,.2,1/6,20,500,0,roi_px=96)
  self.assertEqual(active['screen_reasons'],[])
  self.assertEqual(archived['screen_reasons'],[])
  wide=screen(1.,.2,1/6,20,500,0,roi_px=96)
  self.assertIn('roi_window_envelope',wide['screen_reasons'])
 def test_finite_difference_jacobian(self):
  x,y,s,f,t=1.,2.,20.,500.,30.
  a,b,c,d=jacobian(x,y,s,f,t);e=1e-5
  u0,v0=project(x,y,s,f,t);ux,vx=project(x+e,y,s,f,t);uy,vy=project(x,y+e,s,f,t)
  for expected,observed in [(a,(ux-u0)/e),(b,(uy-u0)/e),(c,(vx-v0)/e),(d,(vy-v0)/e)]:self.assertAlmostEqual(expected,observed,places=5)
class InvalidTests(unittest.TestCase):
 def test_nonfinite_refused(self):
  with self.assertRaises(ValueError):project(float('nan'),0,10,100,0)
  with self.assertRaises(ValueError):screen(.5,.2,1/6,10,400,0,speed_mm_s=-1)
 def test_independent_tilt_oracle_transposed(self):
  u,v=project(1,-2,10,400,60)
  self.assertAlmostEqual(u,48.379590959047,places=10)
  self.assertAlmostEqual(v,-48.379590959047,places=10)
  a,b,c,d=jacobian(1,-2,10,400,60)
  self.assertAlmostEqual(a,48.379590959047,places=10)
  self.assertAlmostEqual(b,-5.067514787535,places=10)
  self.assertAlmostEqual(d,29.257310267059,places=10)
class ReviewRegressions(unittest.TestCase):
 def test_true_minor_singular_value(self):
  r=screen(1,.2,1/6,10,202.26828274309696,45)
  self.assertIn('dot_minor_under_2px_proxy',r['engineering_proxy_rejects'])
 def test_extreme_depth_fail_closed(self):
  with self.assertRaises(ValueError):jacobian(0,0,1e-300,100,0)

if __name__=='__main__': unittest.main()
