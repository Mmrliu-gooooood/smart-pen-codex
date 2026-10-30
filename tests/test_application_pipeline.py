"""Actual C coordinator and pixels; mapper is an explicit test double, not real pose."""
import os, pathlib, subprocess, tempfile, unittest
from roi_opt_fixture import Render, render, vectors
ROOT=pathlib.Path(__file__).resolve().parents[1]
class ApplicationPipeline(unittest.TestCase):
 def test_supplied_frame_pipeline_and_fail_closed_contracts(self):
  v=vectors()[0]
  with tempfile.TemporaryDirectory() as tmp:
   t=pathlib.Path(tmp); (t/'frame.gray').write_bytes(render(v['directions'],Render(pitch=20,angle=0,scale_y=1)))
   sources=['application/pipeline.c','runtime/recorder.c','runtime/contact_power.c','storage/store.c','portable/pen.c','vision/roi_opt.c','codec/anoto.c']
   cmd=['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-pedantic']
   if os.environ.get('PEN_APP_TEST_NDEBUG')=='1': cmd+=['-DNDEBUG']
   if os.environ.get('PEN_APP_TEST_SANITIZERS')=='1': cmd+=['-O1','-fsanitize=address,undefined','-fno-omit-frame-pointer']
   cmd+=['-I'+str(ROOT/'firmware'/p) for p in ('application','runtime','storage','portable','vision')]
   cmd+=[str(ROOT/'firmware'/p) for p in sources]+[str(ROOT/'tests/test_application_pipeline.c'),'-lm','-o',str(t/'runner')]
   subprocess.run(cmd,check=True)
   subprocess.run([str(t/'runner'),str(t/'frame.gray'),*map(str,v['section']),*map(str,v['xy'])],check=True)
if __name__=='__main__':unittest.main()
