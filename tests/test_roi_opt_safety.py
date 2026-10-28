"""Native optimized-ROI buffer/state contract; participates in full host gate."""
from pathlib import Path
import subprocess
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
class RoiOptSafety(unittest.TestCase):
 def test_native(self):
  with tempfile.TemporaryDirectory() as tmp:
   exe=Path(tmp)/'opt-safety'
   subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-pedantic',str(ROOT/'tests/test_roi_opt_safety.c'),str(ROOT/'firmware/vision/roi_opt.c'),str(ROOT/'firmware/codec/anoto.c'),'-lm','-o',str(exe)],check=True)
   subprocess.run([str(exe),str(ROOT/'tests/fixtures/roi/reference.pgm')],check=True)
