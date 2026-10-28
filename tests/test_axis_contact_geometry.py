"""Synthetic algebra only, not physical calibration or pose-solver evidence."""
import importlib.util
import math
from pathlib import Path
import random
import unittest
spec=importlib.util.spec_from_file_location('geometry',Path(__file__).parents[1]/'tools/calibration_geometry.py')
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
I=((1,0,0),(0,1,0),(0,0,1))

class AxisContactGeometry(unittest.TestCase):
 def solve(self, **changes):
  args=dict(rotation=I,translation=(0,0,8),axis_origin_camera=(2,3,7.7),
   axis_direction_camera=(0,0,1),paper_plane_camera=(0,0,1,-8),
   travel_interval_mm=(0,.65),contact=True,units='mm')
  args.update(changes)
  return g.axis_contact_on_paper(**args)
 def test_front(self):
  point,s=self.solve();self.assertEqual(point,(2,3,0));self.assertAlmostEqual(s,.3)
 def test_signed_axis_and_plane_conventions(self):
  point,s=self.solve(axis_direction_camera=(0,0,-1),travel_interval_mm=(-.65,0),paper_plane_camera=(0,0,-1,8))
  self.assertEqual(point,(2,3,0));self.assertAlmostEqual(s,-.3)
 def test_closed_endpoints_no_clamping(self):
  for s in (0,.5):
   self.assertEqual(self.solve(axis_origin_camera=(2,3,8-s),travel_interval_mm=(0,.5))[1],s)
  self.assertEqual(self.solve(axis_origin_camera=(2,3,8),travel_interval_mm=(0,0))[1],0)
  for z in (math.nextafter(8,math.inf), math.nextafter(7.5,-math.inf)):
   with self.assertRaises(ValueError):self.solve(axis_origin_camera=(2,3,z),travel_interval_mm=(0,.5))
 def test_d1_fixed_tip_lateral_error(self):
  for degrees in (30,45,60):
   a=math.radians(degrees);axis=(math.sin(a),0,math.cos(a))
   origin=(2-.3*axis[0],3,8-.3*axis[2])
   point,s=self.solve(axis_origin_camera=origin,axis_direction_camera=axis)
   self.assertAlmostEqual(s,.3);self.assertAlmostEqual(point[0],2)
   self.assertAlmostEqual(point[0]-origin[0],.3*math.sin(a))
 def test_random_rigid_pose_round_trip(self):
  rng=random.Random(328)
  for _ in range(200):
   a=rng.uniform(-1,1);c,s=math.cos(a),math.sin(a)
   ry=((c,0,s),(0,1,0),(-s,0,c))
   b=rng.uniform(-1,1);cb,sb=math.cos(b),math.sin(b)
   rx=((1,0,0),(0,cb,-sb),(0,sb,cb))
   r=tuple(tuple(sum(rx[i][k]*ry[k][j] for k in range(3)) for j in range(3)) for i in range(3))
   t=(rng.uniform(-3,3),rng.uniform(-3,3),20)
   expected=(rng.uniform(-2,2),rng.uniform(-2,2),0);normal=tuple(row[2] for row in r)
   point=tuple(sum(r[i][j]*expected[j] for j in range(3))+t[i] for i in range(3))
   axis=tuple((normal[i]+.3*r[i][0]-.2*r[i][1])/math.sqrt(1.13) for i in range(3))
   travel=rng.uniform(-.2,.6);origin=tuple(point[i]-travel*axis[i] for i in range(3))
   actual,inferred=self.solve(rotation=r,translation=t,axis_origin_camera=origin,
    axis_direction_camera=axis,travel_interval_mm=(-.2,.6),
    paper_plane_camera=normal+(-sum(normal[i]*t[i] for i in range(3)),))
   for x,y in zip(actual,expected):self.assertAlmostEqual(x,y)
   self.assertAlmostEqual(inferred,travel)
 def test_rejections(self):
  cases=[dict(contact=x) for x in (False,1,'yes',None)]
  cases += [dict(units='m'),dict(rotation=None),dict(rotation=I[:2]),
   dict(rotation=((-1,0,0),(0,1,0),(0,0,1))),dict(rotation=((2,0,0),(0,1,0),(0,0,1))),
   dict(rotation=((1,0,0),None,(0,0,1))),dict(axis_direction_camera=(0,0,0)),
   dict(axis_direction_camera=(0,0,2)),dict(axis_direction_camera=(1,0,0)),
   dict(axis_direction_camera=(math.sqrt(1-.01**2),0,.01)),
   dict(axis_origin_camera=(2,3,9)),dict(axis_origin_camera=(2,3,7)),
   dict(travel_interval_mm=(.65,0)),dict(travel_interval_mm=(0,)),
   dict(paper_plane_camera=(0,0,1,-9)),dict(paper_plane_camera=(0,1,0,-8)),
   dict(paper_plane_camera=(0,0,2,-16)),dict(translation=(0,0,-8),axis_origin_camera=(2,3,-8),paper_plane_camera=(0,0,1,8)),
   dict(min_abs_axis_normal=0),dict(min_abs_axis_normal=1.1),dict(min_abs_axis_normal=True),
   dict(axis_origin_camera=(True,0,8)),dict(min_abs_axis_normal=float('nan')),
   dict(rotation=((float('nan'),0,0),(0,1,0),(0,0,1))),
   dict(rotation=((1e308,0,0),(0,1e308,0),(0,0,1e308)))]
  for field in ('translation','axis_origin_camera','axis_direction_camera','paper_plane_camera','travel_interval_mm'):
   size=4 if field=='paper_plane_camera' else 2 if field=='travel_interval_mm' else 3
   for invalid in (float('nan'),float('inf'),-float('inf'),'1',10**1000):
    cases.append({field:(invalid,)+(0,)*(size-1)})
   cases.extend(({field:None},{field:()}))
  for changes in cases:
   with self.subTest(changes=changes),self.assertRaises(ValueError):self.solve(**changes)
 def test_contract_arguments_required(self):
  with self.assertRaises(TypeError):g.axis_contact_on_paper(I,(0,0,8),(0,0,8),(0,0,1),contact=True)

if __name__=='__main__':unittest.main()
