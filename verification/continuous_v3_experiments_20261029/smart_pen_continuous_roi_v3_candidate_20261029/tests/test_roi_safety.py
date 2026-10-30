"""Strict native ROI buffer contract and positive-fixture test (host gate)."""
from pathlib import Path
import subprocess
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
class RoiSafety(unittest.TestCase):
 def test_native(self):
  with tempfile.TemporaryDirectory() as tmp:
   exe=Path(tmp)/'roi-safety'
   subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-pedantic',str(ROOT/'tests/test_roi_safety.c'),str(ROOT/'firmware/vision/roi.c'),str(ROOT/'firmware/codec/anoto.c'),'-lm','-o',str(exe)],check=True)
   subprocess.run([str(exe),str(ROOT/'tests/fixtures/roi/reference.pgm')],check=True)
