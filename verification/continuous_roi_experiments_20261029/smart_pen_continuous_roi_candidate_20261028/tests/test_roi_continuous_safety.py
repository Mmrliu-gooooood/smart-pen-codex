"""Native buffers and bounded traversal tests; sanitizer separately recorded."""
from pathlib import Path
import subprocess
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
class ContinuousSafety(unittest.TestCase):
 def test_native(self):
  with tempfile.TemporaryDirectory() as tmp:
   exe=Path(tmp)/'continuous-safety'
   subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-pedantic',str(ROOT/'tests/test_roi_continuous_safety.c'),str(ROOT/'firmware/vision/roi_continuous.c'),str(ROOT/'firmware/vision/roi_opt.c'),str(ROOT/'firmware/codec/anoto.c'),'-lm','-o',str(exe)],check=True)
   subprocess.run([str(exe),str(ROOT/'tests/fixtures/continuous/fov6_roi200_phase0.pgm')],check=True)
