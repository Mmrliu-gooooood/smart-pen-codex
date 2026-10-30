from pathlib import Path
import subprocess,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]
class RefineV3Safety(unittest.TestCase):
 def test_native_default_and_overflow(self):
  with tempfile.TemporaryDirectory() as tmp:
   for cap in (64,1):
    exe=Path(tmp)/f'v3-{cap}'
    subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-pedantic',f'-DPEN_ROI_REFINE_MAX_SEEDS={cap}',str(ROOT/'tests/test_roi_refine_v3_safety.c'),str(ROOT/'firmware/vision/roi_continuous.c'),str(ROOT/'firmware/codec/anoto.c'),'-lm','-o',str(exe)],check=True)
    subprocess.run([str(exe),str(ROOT/'tests/fixtures/continuous/fov6_roi200_phase0.pgm')],check=True)
