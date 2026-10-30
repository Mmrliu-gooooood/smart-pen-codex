"""Freeze independently checked current-frame fixtures for separate target build."""
import ctypes as C
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tests'))
from test_roi_continuous import ContinuousROI

def main():
 ContinuousROI.setUpClass();test=ContinuousROI();test.setUp();rows=[]
 try:
  for file,expected,label in [('fov5_roi200_phase0.pgm',0,'profile_c_5mm'),('fov6_roi200_phase0.pgm',0,'profile_c_6mm'),('fov7_roi200_phase0.pgm',0,'profile_c_7mm'),('extended_rot45.pgm',0,'recovered_rotation_45'),('v3_no_complete_window.pgm',-3,'no_complete_observed_window'),('case_063.pgm',-2,'deep_edge_ink'),('extended_dense9.pgm',-2,'excess_density_outside_fov_scope')]:
   path=ROOT/'tests/fixtures/continuous'/file;pgm=path.read_bytes();pixels=pgm.split(b'\n',3)[3];rc,out=test.call(pixels)
   assert rc==expected,(file,rc,expected)
   row=dict(path=str(path.relative_to(ROOT)),label=label,pgm_sha256=hashlib.sha256(pgm).hexdigest(),pixel_sha256=hashlib.sha256(pixels).hexdigest(),width=200,height=200,stride=200,paper_width=710,paper_height=1000,section=[10,2],expected_status=expected)
   if not rc:
    row.update(x=out.roi.decoded.x,y=out.roi.decoded.y,directions=list(out.roi.decoded.directions),crop=[out.left,out.top,out.width,out.height],dots=out.roi.decoded.dots,windows=out.roi.decoded.windows,edge_components=out.edge_components,edge_pixels=out.edge_pixels,attempts=out.crop_attempts,paper_to_frame=list(out.paper_to_frame),frame_to_paper=list(out.frame_to_paper),transform_numeric_tolerance=1e-5,refine_seeds=out.refine_seeds,refine_iterations=out.refine_iterations,refine_models=out.refine_models,candidates=out.roi.candidates)
   rows.append(row)
 finally:ContinuousROI.tearDownClass()
 (ROOT/'verification/continuous_target_fixture_manifest.json').write_text(json.dumps({'synthetic_only':True,'note':'Expected fitted transforms are replay oracles, independently geometrically verified by test_roi_continuous.py and continuous_roi_sweep.py. C receives pixels/config only. No prior. No target execution.','fixtures':rows},indent=2))
if __name__=='__main__':main()
